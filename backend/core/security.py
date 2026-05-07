from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from backend.core.config import get_settings
from backend.core.exceptions import UnauthorizedException

_pwd_ctx = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)

ALGORITHM = "HS256"


# ------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt (cost factor 12)."""
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return _pwd_ctx.verify(plain, hashed)


# ------------------------------------------------------------------
# JWT token creation & verification
# ------------------------------------------------------------------


def _get_settings():
    return get_settings()


def create_access_token(subject: str, data: dict | None = None) -> str:
    """Create a signed JWT access token with short TTL.

    Args:
        subject: The user identifier (typically user id as string).
        data: Additional claims to include in the payload.

    Returns:
        Encoded JWT string.
    """
    settings = _get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access",
    }
    if data:
        payload.update(data)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a signed JWT refresh token with longer TTL.

    Args:
        subject: The user identifier (typically user id as string).

    Returns:
        Encoded JWT string.
    """
    settings = _get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Decode and verify a JWT token.

    Args:
        token: The encoded JWT string.

    Returns:
        Decoded payload as a dict.

    Raises:
        UnauthorizedException: If the token is expired, malformed, or
            has an invalid signature.
    """
    settings = _get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(detail="Token expirado")
    except jwt.InvalidTokenError:
        raise UnauthorizedException(detail="Token inválido")
