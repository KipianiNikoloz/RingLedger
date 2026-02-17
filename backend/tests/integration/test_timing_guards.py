from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.domain.time_rules import to_ripple_epoch
from app.models.enums import EscrowKind, UserRole
from app.models.escrow import Escrow
from app.models.user import User
from app.services.bout_service import BoutService


class TimingGuardIntegrationTests(unittest.TestCase):
    def test_finish_and_cancel_timing_guards(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        try:
            with Session(engine) as session:
                promoter_id = self._insert_user(session, "promoter.time@example.test", UserRole.PROMOTER)
                fighter_a_id = self._insert_user(session, "fighter.time.a@example.test", UserRole.FIGHTER)
                fighter_b_id = self._insert_user(session, "fighter.time.b@example.test", UserRole.FIGHTER)

                event = datetime(2026, 2, 20, 10, 15, 0, tzinfo=UTC)
                service = BoutService(session=session)
                bout = service.create_bout_draft(
                    promoter_user_id=promoter_id,
                    fighter_a_user_id=fighter_a_id,
                    fighter_b_user_id=fighter_b_id,
                    event_datetime_utc=event,
                    promoter_owner_address="rPromoterTiming",
                    fighter_a_destination="rFighterATiming",
                    fighter_b_destination="rFighterBTiming",
                    show_a_drops=1_000_000,
                    show_b_drops=1_000_000,
                    bonus_a_drops=250_000,
                    bonus_b_drops=250_000,
                )

                self.assertEqual(
                    self._as_utc(bout.finish_after_utc),
                    datetime(2026, 2, 20, 12, 15, 0, tzinfo=UTC),
                )
                self.assertEqual(
                    self._as_utc(bout.cancel_after_utc),
                    datetime(2026, 2, 27, 10, 15, 0, tzinfo=UTC),
                )

                escrows = session.scalars(select(Escrow).where(Escrow.bout_id == bout.id)).all()
                self.assertEqual(len(escrows), 4)
                expected_finish_ripple = to_ripple_epoch(self._as_utc(bout.finish_after_utc))
                expected_cancel_ripple = to_ripple_epoch(self._as_utc(bout.cancel_after_utc))
                self.assertTrue(all(escrow.finish_after_ripple == expected_finish_ripple for escrow in escrows))

                for escrow in escrows:
                    if escrow.kind in {EscrowKind.BONUS_A, EscrowKind.BONUS_B}:
                        self.assertEqual(escrow.cancel_after_ripple, expected_cancel_ripple)
                    else:
                        self.assertIsNone(escrow.cancel_after_ripple)
        finally:
            Base.metadata.drop_all(bind=engine)
            engine.dispose()

    def test_rejects_naive_event_datetime(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        try:
            with Session(engine) as session:
                promoter_id = self._insert_user(session, "promoter.naive@example.test", UserRole.PROMOTER)
                fighter_a_id = self._insert_user(session, "fighter.naive.a@example.test", UserRole.FIGHTER)
                fighter_b_id = self._insert_user(session, "fighter.naive.b@example.test", UserRole.FIGHTER)

                service = BoutService(session=session)
                naive_event = datetime(2026, 2, 20, 10, 15, 0)
                with self.assertRaises(ValueError):
                    service.create_bout_draft(
                        promoter_user_id=promoter_id,
                        fighter_a_user_id=fighter_a_id,
                        fighter_b_user_id=fighter_b_id,
                        event_datetime_utc=naive_event,
                        promoter_owner_address="rPromoterNaive",
                        fighter_a_destination="rFighterANaive",
                        fighter_b_destination="rFighterBNaive",
                        show_a_drops=1_000_000,
                        show_b_drops=1_000_000,
                        bonus_a_drops=250_000,
                        bonus_b_drops=250_000,
                    )
        finally:
            Base.metadata.drop_all(bind=engine)
            engine.dispose()

    @staticmethod
    def _insert_user(session: Session, email: str, role: UserRole) -> uuid.UUID:
        user = User(id=uuid.uuid4(), email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
        session.add(user)
        session.flush()
        return user.id

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


if __name__ == "__main__":
    unittest.main()
