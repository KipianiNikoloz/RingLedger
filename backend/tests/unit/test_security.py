from __future__ import annotations

import unittest

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


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
            secret_key="local-secret",
            expires_minutes=30,
        )
        payload = decode_access_token(token, secret_key="local-secret")
        self.assertEqual(payload["sub"], "user-1")
        self.assertEqual(payload["email"], "fighter@example.com")
        self.assertEqual(payload["role"], "fighter")


if __name__ == "__main__":
    unittest.main()
