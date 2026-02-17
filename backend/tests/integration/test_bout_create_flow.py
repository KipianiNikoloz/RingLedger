from __future__ import annotations

import unittest


class BoutCreateIntegrationTests(unittest.TestCase):
    @unittest.skip("Pending database fixture setup and service wiring.")
    def test_create_bout_creates_four_planned_escrows(self) -> None:
        self.fail("Not implemented")


if __name__ == "__main__":
    unittest.main()
