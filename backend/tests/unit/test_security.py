from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

TEST_JWT_SECRET = "local-secret-with-32-byte-minimum-0001"


class SecurityUnitTests(unittest.TestCase):
    def test_password_hash_and_verify(self) -> None:
        encoded = hash_password("correct-horse-battery-staple")
        self.assertTrue(verify_password("correct-horse-battery-staple", encoded))
        self.assertFalse(verify_password("wrong-password", encoded))

    def test_jwt_issue_and_decode(self) -> None:
        token = create_access_token(
            subject="user-1",
            email="fighter@example.com",
            role="fighter",
            secret_key=TEST_JWT_SECRET,
            expires_minutes=30,
        )
        payload = decode_access_token(token, secret_key=TEST_JWT_SECRET)
        self.assertEqual(payload["sub"], "user-1")
        self.assertEqual(payload["email"], "fighter@example.com")
        self.assertEqual(payload["role"], "fighter")

    def test_password_verify_supports_legacy_pbkdf2_format(self) -> None:
        legacy_hash = hash_password("correct-horse-battery-staple", salt=b"0123456789abcdef")
        self.assertTrue(verify_password("correct-horse-battery-staple", legacy_hash))
        self.assertFalse(verify_password("wrong-password", legacy_hash))

    def test_decode_access_token_rejects_expired_token(self) -> None:
        issued_at = datetime.now(UTC)
        token = create_access_token(
            subject="user-1",
            email="fighter@example.com",
            role="fighter",
            secret_key=TEST_JWT_SECRET,
            expires_minutes=1,
            now=issued_at,
        )

        with self.assertRaises(ValueError):
            decode_access_token(token, secret_key=TEST_JWT_SECRET, now=issued_at + timedelta(minutes=2))


if __name__ == "__main__":
    unittest.main()
