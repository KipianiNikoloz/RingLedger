from __future__ import annotations

import random
import unittest
from datetime import UTC, datetime

from app.domain.time_rules import from_ripple_epoch, to_ripple_epoch


class TimePropertyTests(unittest.TestCase):
    def test_epoch_conversion_round_trip_for_many_values(self) -> None:
        rng = random.Random(7)
        for _ in range(1_000):
            timestamp = rng.randint(946_684_800, 2_208_988_800)  # 2000-01-01 through 2040-01-01
            dt = datetime.fromtimestamp(timestamp, tz=UTC)
            self.assertEqual(from_ripple_epoch(to_ripple_epoch(dt)), dt)


if __name__ == "__main__":
    unittest.main()
