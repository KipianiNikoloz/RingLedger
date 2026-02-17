from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.models.bout import Bout
from app.models.enums import EscrowKind, EscrowStatus, UserRole
from app.models.escrow import Escrow
from app.models.user import User
from app.services.bout_service import BoutService


class BoutCreateIntegrationTests(unittest.TestCase):
    def test_create_bout_creates_four_planned_escrows(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        try:
            with Session(engine) as session:
                promoter_id = self._insert_user(session, "promoter@example.test", UserRole.PROMOTER)
                fighter_a_id = self._insert_user(session, "fighter.a@example.test", UserRole.FIGHTER)
                fighter_b_id = self._insert_user(session, "fighter.b@example.test", UserRole.FIGHTER)

                event = datetime(2026, 2, 16, 20, 30, 0, tzinfo=UTC)
                service = BoutService(session=session)
                created = service.create_bout_draft(
                    promoter_user_id=promoter_id,
                    fighter_a_user_id=fighter_a_id,
                    fighter_b_user_id=fighter_b_id,
                    event_datetime_utc=event,
                    promoter_owner_address="rPromoterAddress",
                    fighter_a_destination="rFighterADestination",
                    fighter_b_destination="rFighterBDestination",
                    show_a_drops=2_000_000,
                    show_b_drops=2_500_000,
                    bonus_a_drops=500_000,
                    bonus_b_drops=750_000,
                )

                persisted_bout = session.scalar(select(Bout).where(Bout.id == created.id))
                self.assertIsNotNone(persisted_bout)
                assert persisted_bout is not None
                self.assertEqual(persisted_bout.status.value, "draft")

                escrows = session.scalars(select(Escrow).where(Escrow.bout_id == created.id)).all()
                self.assertEqual(len(escrows), 4)
                self.assertSetEqual(
                    {escrow.kind for escrow in escrows},
                    {EscrowKind.SHOW_A, EscrowKind.SHOW_B, EscrowKind.BONUS_A, EscrowKind.BONUS_B},
                )
                self.assertTrue(all(escrow.status == EscrowStatus.PLANNED for escrow in escrows))
                self.assertTrue(all(escrow.owner_address == "rPromoterAddress" for escrow in escrows))

                amounts = {escrow.kind: escrow.amount_drops for escrow in escrows}
                self.assertEqual(amounts[EscrowKind.SHOW_A], 2_000_000)
                self.assertEqual(amounts[EscrowKind.SHOW_B], 2_500_000)
                self.assertEqual(amounts[EscrowKind.BONUS_A], 500_000)
                self.assertEqual(amounts[EscrowKind.BONUS_B], 750_000)

                for escrow in escrows:
                    if escrow.kind in {EscrowKind.BONUS_A, EscrowKind.BONUS_B}:
                        self.assertIsNotNone(escrow.cancel_after_ripple)
                    else:
                        self.assertIsNone(escrow.cancel_after_ripple)
        finally:
            Base.metadata.drop_all(bind=engine)
            engine.dispose()

    @staticmethod
    def _insert_user(session: Session, email: str, role: UserRole) -> uuid.UUID:
        user = User(id=uuid.uuid4(), email=email, password_hash="pbkdf2_sha256$1$00$00", role=role)
        session.add(user)
        session.flush()
        return user.id


if __name__ == "__main__":
    unittest.main()
