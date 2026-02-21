from __future__ import annotations

import unittest
import uuid
from datetime import UTC, datetime

from app.models.enums import EscrowKind, EscrowStatus
from app.services.bout_service import BoutService


class _RecordingSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.added_all: list[object] = []

    def add(self, value: object) -> None:
        self.added.append(value)

    def flush(self) -> None:
        for value in self.added:
            if hasattr(value, "id") and getattr(value, "id") is None:
                setattr(value, "id", uuid.uuid4())

    def add_all(self, values: list[object]) -> None:
        self.added_all.extend(values)


class BoutEscrowPlanningUnitTests(unittest.TestCase):
    def test_bout_service_plans_exactly_four_escrows(self) -> None:
        session = _RecordingSession()
        service = BoutService(session=session)  # type: ignore[arg-type]
        event = datetime(2026, 2, 16, 19, 0, 0, tzinfo=UTC)
        promoter_id = uuid.uuid4()
        fighter_a_id = uuid.uuid4()
        fighter_b_id = uuid.uuid4()

        bout = service.create_bout_draft(
            promoter_user_id=promoter_id,
            fighter_a_user_id=fighter_a_id,
            fighter_b_user_id=fighter_b_id,
            event_datetime_utc=event,
            promoter_owner_address="rPromoter",
            fighter_a_destination="rFighterA",
            fighter_b_destination="rFighterB",
            show_a_drops=1_200_000,
            show_b_drops=1_400_000,
            bonus_a_drops=300_000,
            bonus_b_drops=350_000,
        )

        self.assertIsNotNone(bout.id)
        self.assertEqual(len(session.added_all), 4)

        escrows = session.added_all
        kinds = {escrow.kind for escrow in escrows}
        self.assertSetEqual(
            kinds,
            {EscrowKind.SHOW_A, EscrowKind.SHOW_B, EscrowKind.BONUS_A, EscrowKind.BONUS_B},
        )
        self.assertTrue(all(escrow.status == EscrowStatus.PLANNED for escrow in escrows))

        for escrow in escrows:
            self.assertEqual(escrow.bout_id, bout.id)
            if escrow.kind in {EscrowKind.BONUS_A, EscrowKind.BONUS_B}:
                self.assertIsNotNone(escrow.cancel_after_ripple)
            else:
                self.assertIsNone(escrow.cancel_after_ripple)


if __name__ == "__main__":
    unittest.main()
