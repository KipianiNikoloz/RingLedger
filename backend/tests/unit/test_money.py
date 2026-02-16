from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
import unittest

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.money import drops_to_xrp, ensure_valid_drops, xrp_to_drops


class MoneyUnitTests(unittest.TestCase):
    def test_xrp_to_drops_exact(self) -> None:
        self.assertEqual(xrp_to_drops("1"), 1_000_000)
        self.assertEqual(xrp_to_drops("0.000001"), 1)

    def test_xrp_to_drops_reject_fractional_drop(self) -> None:
        with self.assertRaises(ValueError):
            xrp_to_drops("0.0000001")

    def test_round_trip(self) -> None:
        original_drops = 123_456_789
        xrp = drops_to_xrp(original_drops)
        self.assertEqual(xrp_to_drops(xrp), original_drops)

    def test_ensure_valid_drops(self) -> None:
        self.assertEqual(ensure_valid_drops(0), 0)
        self.assertEqual(ensure_valid_drops(10), 10)
        with self.assertRaises(ValueError):
            ensure_valid_drops(-1)
        with self.assertRaises(TypeError):
            ensure_valid_drops(Decimal("1"))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

