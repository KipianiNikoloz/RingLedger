from __future__ import annotations

import uuid
from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.bout import Bout
from app.models.enums import EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.fighter_profile import FighterProfile
from app.models.user import User


@dataclass(frozen=True)
class UserFixture:
    id: uuid.UUID
    email: str
    role: UserRole


class ManagementEndpointTests(TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

        self.init_db_patcher = patch("app.main.init_db")
        self.init_db_patcher.start()
        self.app = create_app()
        self.app.dependency_overrides[get_session] = self._override_get_session
        self.client = TestClient(self.app)
        self.client.__enter__()

    def tearDown(self) -> None:
        self.client.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        self.init_db_patcher.stop()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_fighter_can_upsert_profile_and_duplicate_address_is_rejected(self) -> None:
        fighter_a = self._insert_user("fighter.profile.a@example.test", UserRole.FIGHTER)
        fighter_b = self._insert_user("fighter.profile.b@example.test", UserRole.FIGHTER)
        promoter = self._insert_user("promoter.profile@example.test", UserRole.PROMOTER)

        response = self.client.put(
            "/fighters/me",
            headers=self._auth_headers(fighter_a.id, fighter_a.email, fighter_a.role),
            json={"display_name": "Fighter A", "xrpl_address": "rAAAAAAAAAAAAAAAAAAAAAAAA"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["display_name"], "Fighter A")
        self.assertEqual(response.json()["xrpl_address"], "rAAAAAAAAAAAAAAAAAAAAAAAA")

        update_response = self.client.put(
            "/fighters/me",
            headers=self._auth_headers(fighter_a.id, fighter_a.email, fighter_a.role),
            json={"display_name": "Fighter Alpha", "xrpl_address": "rBBBBBBBBBBBBBBBBBBBBBBBB"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["display_name"], "Fighter Alpha")

        duplicate_response = self.client.put(
            "/fighters/me",
            headers=self._auth_headers(fighter_b.id, fighter_b.email, fighter_b.role),
            json={"display_name": "Fighter B", "xrpl_address": "rBBBBBBBBBBBBBBBBBBBBBBBB"},
        )
        self.assertEqual(duplicate_response.status_code, 409)
        self.assertEqual(
            duplicate_response.json()["detail"],
            "XRPL address is already assigned to another fighter profile.",
        )

        forbidden_response = self.client.put(
            "/fighters/me",
            headers=self._auth_headers(promoter.id, promoter.email, promoter.role),
            json={"display_name": "Promoter", "xrpl_address": "rCCCCCCCCCCCCCCCCCCCCCCCC"},
        )
        self.assertEqual(forbidden_response.status_code, 403)

    def test_promoter_creates_bout_and_reads_are_role_scoped(self) -> None:
        promoter = self._insert_user("promoter.create@example.test", UserRole.PROMOTER)
        fighter_a = self._insert_user("fighter.create.a@example.test", UserRole.FIGHTER)
        fighter_b = self._insert_user("fighter.create.b@example.test", UserRole.FIGHTER)
        outsider = self._insert_user("fighter.outsider@example.test", UserRole.FIGHTER)
        admin = self._insert_user("admin.create@example.test", UserRole.ADMIN)
        self._insert_profile(fighter_a.id, "Fighter A", "rAAAAAAAAAAAAAAAAAAAAAAAA")
        self._insert_profile(fighter_b.id, "Fighter B", "rBBBBBBBBBBBBBBBBBBBBBBBB")

        create_response = self.client.post(
            "/bouts",
            headers=self._auth_headers(promoter.id, promoter.email, promoter.role),
            json={
                "fighter_a_user_id": str(fighter_a.id),
                "fighter_b_user_id": str(fighter_b.id),
                "event_datetime_utc": "2026-02-18T20:00:00Z",
                "promoter_owner_address": "rCCCCCCCCCCCCCCCCCCCCCCCC",
                "show_a_drops": 2_000_000,
                "show_b_drops": 2_500_000,
                "bonus_a_drops": 500_000,
                "bonus_b_drops": 750_000,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        self.assertEqual(created["bout_status"], "draft")
        self.assertEqual(len(created["escrows"]), 4)
        self.assertTrue(all(escrow["escrow_status"] == EscrowStatus.PLANNED for escrow in created["escrows"]))

        bout_id = created["bout_id"]
        promoter_list = self.client.get(
            "/bouts", headers=self._auth_headers(promoter.id, promoter.email, promoter.role)
        )
        self.assertEqual(promoter_list.status_code, 200)
        self.assertEqual([bout["bout_id"] for bout in promoter_list.json()["bouts"]], [bout_id])

        fighter_list = self.client.get(
            "/bouts", headers=self._auth_headers(fighter_a.id, fighter_a.email, fighter_a.role)
        )
        self.assertEqual(fighter_list.status_code, 200)
        self.assertEqual([bout["bout_id"] for bout in fighter_list.json()["bouts"]], [bout_id])

        outsider_list = self.client.get(
            "/bouts", headers=self._auth_headers(outsider.id, outsider.email, outsider.role)
        )
        self.assertEqual(outsider_list.status_code, 200)
        self.assertEqual(outsider_list.json()["bouts"], [])

        hidden_detail = self.client.get(
            f"/bouts/{bout_id}",
            headers=self._auth_headers(outsider.id, outsider.email, outsider.role),
        )
        self.assertEqual(hidden_detail.status_code, 404)

        admin_detail = self.client.get(
            f"/bouts/{bout_id}", headers=self._auth_headers(admin.id, admin.email, admin.role)
        )
        self.assertEqual(admin_detail.status_code, 200)
        self.assertEqual(admin_detail.json()["bout_id"], bout_id)

    def test_bout_create_requires_fighter_profiles_without_partial_persistence(self) -> None:
        promoter = self._insert_user("promoter.partial@example.test", UserRole.PROMOTER)
        fighter_a = self._insert_user("fighter.partial.a@example.test", UserRole.FIGHTER)
        fighter_b = self._insert_user("fighter.partial.b@example.test", UserRole.FIGHTER)
        self._insert_profile(fighter_a.id, "Fighter A", "rAAAAAAAAAAAAAAAAAAAAAAAA")

        response = self.client.post(
            "/bouts",
            headers=self._auth_headers(promoter.id, promoter.email, promoter.role),
            json={
                "fighter_a_user_id": str(fighter_a.id),
                "fighter_b_user_id": str(fighter_b.id),
                "event_datetime_utc": "2026-02-18T20:00:00Z",
                "promoter_owner_address": "rCCCCCCCCCCCCCCCCCCCCCCCC",
                "show_a_drops": 2_000_000,
                "show_b_drops": 2_500_000,
                "bonus_a_drops": 500_000,
                "bonus_b_drops": 750_000,
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"], "Bout fighters must exist, have fighter role, and have fighter profiles."
        )

        with Session(self.engine) as session:
            self.assertEqual(len(session.scalars(select(Bout)).all()), 0)
            self.assertEqual(len(session.scalars(select(Escrow)).all()), 0)

    def _override_get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def _insert_user(self, email: str, role: UserRole) -> UserFixture:
        with Session(self.engine) as session:
            user_id = uuid.uuid4()
            user = User(id=user_id, email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
            session.add(user)
            session.commit()
            return UserFixture(id=user_id, email=email, role=role)

    def _insert_profile(self, user_id: uuid.UUID, display_name: str, xrpl_address: str) -> None:
        with Session(self.engine) as session:
            session.add(FighterProfile(user_id=user_id, display_name=display_name, xrpl_address=xrpl_address))
            session.commit()

    def _auth_headers(self, user_id: uuid.UUID, email: str, role: UserRole) -> dict[str, str]:
        token = create_access_token(
            subject=str(user_id),
            email=email,
            role=role.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        return {"Authorization": f"Bearer {token}"}
