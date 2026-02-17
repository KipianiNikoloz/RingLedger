from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta

PBKDF2_ITERATIONS = 390_000


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(token: str) -> bytes:
    padding = "=" * ((4 - len(token) % 4) % 4)
    return base64.urlsafe_b64decode(token + padding)


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    if len(password) < 8:
        raise ValueError("password_too_short")
    local_salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), local_salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${local_salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iter_raw, salt_hex, hash_hex = encoded_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    rounds = int(iter_raw)
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), rounds).hex()
    return hmac.compare_digest(computed, hash_hex)


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
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "email": email,
        "role": role,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    header_enc = _b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_enc = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    message = f"{header_enc}.{payload_enc}".encode("ascii")
    signature = hmac.new(secret_key.encode("utf-8"), message, hashlib.sha256).digest()
    return f"{header_enc}.{payload_enc}.{_b64url_encode(signature)}"


def decode_access_token(token: str, *, secret_key: str, now: datetime | None = None) -> dict[str, str | int]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid_token_format")

    header_enc, payload_enc, sig_enc = parts
    expected_signature = hmac.new(
        secret_key.encode("utf-8"), f"{header_enc}.{payload_enc}".encode("ascii"), hashlib.sha256
    ).digest()
    if not hmac.compare_digest(expected_signature, _b64url_decode(sig_enc)):
        raise ValueError("invalid_token_signature")

    payload = json.loads(_b64url_decode(payload_enc).decode("utf-8"))
    current_ts = int((now or datetime.now(UTC)).timestamp())
    if current_ts >= int(payload["exp"]):
        raise ValueError("token_expired")
    return payload
