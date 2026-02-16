from __future__ import annotations

import random
import sys
from pathlib import Path
import unittest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.money import drops_to_xrp, xrp_to_drops


class MoneyPropertyTests(unittest.TestCase):
    def test_drop_round_trip_for_many_values(self) -> None:
        rng = random.Random(20260216)
        for _ in range(1_000):
            drops = rng.randint(0, 10_000_000_000)
            self.assertEqual(xrp_to_drops(drops_to_xrp(drops)), drops)


if __name__ == "__main__":
    unittest.main()

