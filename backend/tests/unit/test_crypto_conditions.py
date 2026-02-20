from __future__ import annotations

import unittest

from app.crypto_conditions import generate_preimage_hex, make_condition_hex, make_fulfillment_hex, verify_fulfillment


class CryptoConditionsUnitTests(unittest.TestCase):
    def test_generate_preimage_produces_distinct_32_byte_values(self) -> None:
        first = generate_preimage_hex()
        second = generate_preimage_hex()

        self.assertEqual(len(first), 64)
        self.assertEqual(len(second), 64)
        self.assertNotEqual(first, second)

    def test_condition_and_fulfillment_round_trip(self) -> None:
        preimage = generate_preimage_hex()
        fulfillment = make_fulfillment_hex(preimage)
        condition = make_condition_hex(preimage)

        self.assertTrue(verify_fulfillment(condition_hex=condition, fulfillment_hex=fulfillment))

    def test_verify_fulfillment_rejects_mismatch(self) -> None:
        preimage = generate_preimage_hex()
        condition = make_condition_hex(preimage)
        wrong = make_fulfillment_hex(generate_preimage_hex())

        self.assertFalse(verify_fulfillment(condition_hex=condition, fulfillment_hex=wrong))


if __name__ == "__main__":
    unittest.main()
