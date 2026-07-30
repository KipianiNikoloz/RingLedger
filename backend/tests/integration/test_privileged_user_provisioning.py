from __future__ import annotations

from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_session
from app.main import create_app
from app.models.enums import UserRole
from app.models.user import User


class PrivilegedUserProvisioningTests(TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, future=True)
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

    def test_public_registration_is_fighter_only_and_rejects_role_field(self) -> None:
        response = self.client.post(
            "/auth/register",
            json={"email": "fighter@example.com", "password": "secure-passphrase"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["role"], "fighter")

        rejected = self.client.post(
            "/auth/register",
            json={"email": "attacker@example.com", "password": "secure-passphrase", "role": "admin"},
        )
        self.assertEqual(rejected.status_code, 422)

    def test_only_admin_can_create_privileged_users(self) -> None:
        admin = self._insert_user("admin@example.com", UserRole.ADMIN)
        promoter = self._insert_user("promoter@example.com", UserRole.PROMOTER)
        payload = {"email": "management@example.com", "password": "secure-passphrase", "role": "management"}

        forbidden = self.client.post("/admin/users", headers=self._headers(promoter), json=payload)
        self.assertEqual(forbidden.status_code, 403)

        created = self.client.post("/admin/users", headers=self._headers(admin), json=payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["role"], "management")
        self.assertNotIn("password", created.json())

        duplicate = self.client.post("/admin/users", headers=self._headers(admin), json=payload)
        self.assertEqual(duplicate.status_code, 409)

    def _insert_user(self, email: str, role: UserRole) -> User:
        with self.SessionLocal() as session:
            user = User(email=email, password_hash=hash_password("secure-passphrase"), role=role)
            session.add(user)
            session.commit()
            session.refresh(user)
            session.expunge(user)
            return user

    def _headers(self, user: User) -> dict[str, str]:
        token = create_access_token(
            subject=str(user.id),
            email=user.email,
            role=user.role.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )
        return {"Authorization": f"Bearer {token}"}

    def _override_get_session(self):
        with self.SessionLocal() as session:
            yield session


def test_bootstrap_first_admin_is_repeat_safe() -> None:
    from app.services.auth_service import AuthService

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        service = AuthService(session)
        first, created = service.bootstrap_first_admin(email="root@example.com", password="secure-passphrase")
        session.commit()
        second, replay_created = service.bootstrap_first_admin(email="root@example.com", password="different-passphrase")
        assert created is True
        assert replay_created is False
        assert first.id == second.id
        assert session.scalar(select(User).where(User.role == UserRole.ADMIN)) == first
    engine.dispose()
