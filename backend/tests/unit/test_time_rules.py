from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
import unittest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.time_rules import (
    compute_bonus_cancel_after,
    compute_finish_after,
    from_ripple_epoch,
    to_ripple_epoch,
)


class TimeRuleUnitTests(unittest.TestCase):
    def test_finish_after_rule(self) -> None:
        event = datetime(2026, 2, 16, 12, 0, 0, tzinfo=UTC)
        self.assertEqual(compute_finish_after(event), datetime(2026, 2, 16, 14, 0, 0, tzinfo=UTC))

    def test_bonus_cancel_after_rule(self) -> None:
        event = datetime(2026, 2, 16, 12, 0, 0, tzinfo=UTC)
        self.assertEqual(compute_bonus_cancel_after(event), datetime(2026, 2, 23, 12, 0, 0, tzinfo=UTC))

    def test_ripple_epoch_round_trip(self) -> None:
        now_utc = datetime(2026, 2, 16, 18, 0, 0, tzinfo=UTC)
        ripple = to_ripple_epoch(now_utc)
        decoded = from_ripple_epoch(ripple)
        self.assertEqual(decoded, now_utc)


if __name__ == "__main__":
    unittest.main()

