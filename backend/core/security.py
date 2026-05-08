from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from backend.core.config import get_settings
from backend.core.exceptions import UnauthorizedException

ALGORITHM = "HS256"


# ------------------------------------------------------------------
# Password hashing
# ------------------------------------------------------------------


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


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
