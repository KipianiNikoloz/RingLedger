from __future__ import annotations

import unittest
import uuid

from fastapi import HTTPException

from app.api.dependencies import get_current_actor
from app.core.config import settings
from app.core.security import create_access_token
from app.models.enums import UserRole


class ApiDependenciesAuthUnitTests(unittest.TestCase):
    def test_get_current_actor_parses_valid_bearer_token(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(
            subject=str(user_id),
            email="admin@example.test",
            role=UserRole.ADMIN.value,
            secret_key=settings.jwt_secret,
            expires_minutes=settings.jwt_exp_minutes,
        )

        actor = get_current_actor(authorization=f"Bearer {token}")
        self.assertEqual(actor.user_id, user_id)
        self.assertEqual(actor.role, UserRole.ADMIN)
        self.assertEqual(actor.email, "admin@example.test")

    def test_get_current_actor_rejects_missing_header(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            get_current_actor(authorization=None)
        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
