from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from jwt import DecodeError, InvalidSignatureError, InvalidTokenError
from passlib.context import CryptContext

PBKDF2_ITERATIONS = 390_000
JWT_ALGORITHM = "HS256"
PASSWORD_CONTEXT = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=PBKDF2_ITERATIONS,
)


def _legacy_hash_password(password: str, *, salt: bytes | None = None) -> str:
    local_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), local_salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${local_salt.hex()}${digest.hex()}"


def _verify_legacy_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iter_raw, salt_hex, hash_hex = encoded_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    rounds = int(iter_raw)
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), rounds).hex()
    return hmac.compare_digest(computed, hash_hex)


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    if len(password) < 8:
        raise ValueError("password_too_short")

    # Preserve deterministic salt support for compatibility tests and legacy tooling.
    if salt is not None:
        return _legacy_hash_password(password, salt=salt)
    return PASSWORD_CONTEXT.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    if encoded_hash.startswith("pbkdf2_sha256$"):
        return _verify_legacy_password(password, encoded_hash)
    try:
        return PASSWORD_CONTEXT.verify(password, encoded_hash)
    except (ValueError, TypeError):
        return False


def create_access_token(
    *,
    subject: str,
    email: str,
    role: str,
    secret_key: str,
    expires_minutes: int,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, *, secret_key: str, now: datetime | None = None) -> dict[str, str | int]:
    if token.count(".") != 2:
        raise ValueError("invalid_token_format")
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "email", "role", "iat", "exp"], "verify_exp": False},
        )
    except InvalidSignatureError as exc:
        raise ValueError("invalid_token_signature") from exc
    except DecodeError as exc:
        raise ValueError("invalid_token_format") from exc
    except InvalidTokenError as exc:
        raise ValueError("invalid_token") from exc

    try:
        exp_ts = int(payload["exp"])
    except (TypeError, ValueError, KeyError) as exc:
        raise ValueError("invalid_token") from exc

    current_ts = int((now or datetime.now(UTC)).timestamp())
    if current_ts >= exp_ts:
        raise ValueError("token_expired")

    return payload
