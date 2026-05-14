from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from backend.auth.schemas import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse
from backend.core.config import get_settings
from backend.core.exceptions import BadRequestException, ConflictException, ForbiddenException, UnauthorizedException
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario, UsuarioRol


def login(uow: UnitOfWork, body: LoginRequest) -> TokenResponse:
    """Authenticate a user and issue a JWT access token + refresh token.

    Verifies credentials against the stored password hash, generates a
    signed access token (with role claim) and a refresh token, persists
    the SHA-256 hash of the refresh token in the database, and returns
    the full token pair.

    Does NOT commit; the caller (router) is responsible for that.

    Args:
        uow: The per-request UnitOfWork with registered repositories.
        body: Validated login credentials.

    Returns:
        TokenResponse with access_token, refresh_token, token_type, expires_in.

    Raises:
        UnauthorizedException: If the email does not exist or the password
            does not match (same message to prevent user enumeration).
    """
    settings = get_settings()

    # 1. Look up user by email
    usuario = uow.repos.usuarios.get_by_email(body.email)

    # 2. Validate existence and password — unified error prevents user enumeration
    if usuario is None or not verify_password(body.password, usuario.password_hash):
        raise UnauthorizedException(detail="Credenciales inválidas")

    # 3. Check account is active — return 403 so the client can distinguish
    #    "wrong credentials" (401) from "account disabled" (403)
    if not usuario.activo:
        raise ForbiddenException(detail="Cuenta desactivada")

    # 4. Resolve primary role (first assigned role, fallback to CLIENT)
    rol = usuario.roles[0].rol_codigo if usuario.roles else "CLIENT"

    # 5. Generate tokens
    access_token = create_access_token(str(usuario.id), data={"role": rol})
    refresh_token = create_refresh_token(str(usuario.id))

    # 6. Hash refresh token for secure storage (never store the raw JWT)
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    # 7. Persist hashed refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    uow.repos.refresh_tokens.create(
        usuario_id=usuario.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    # 8. Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


def refresh_tokens(uow: UnitOfWork, body: RefreshRequest) -> TokenResponse:
    """Rotate a refresh token and issue a new access + refresh token pair.

    Validates the presented refresh token (JWT signature + expiration, then BD
    state), applies token rotation (revoke old, persist new), and returns the
    fresh pair. Detects replay attacks by checking ``revoked_at``: if the token
    was already revoked, ALL active tokens for that user are invalidated and
    HTTP 401 is raised.

    Does NOT commit; the caller (router) is responsible for that.

    Args:
        uow: The per-request UnitOfWork with registered repositories.
        body: Validated refresh request containing the raw JWT string.

    Returns:
        TokenResponse with a new access_token, refresh_token, token_type,
        and expires_in.

    Raises:
        UnauthorizedException: If the token is invalid, expired, not found in
            BD, or a replay attack is detected.
    """
    settings = get_settings()

    # 3.2 — Verify JWT signature and expiration (fails fast without a BD hit)
    payload = verify_token(body.refresh_token)

    # 3.3 — Ensure the token carries the "refresh" type claim
    if payload.get("type") != "refresh":
        raise UnauthorizedException(detail="Token inválido")

    # 3.4 — Look up the hashed token in BD
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    stored = uow.repos.refresh_tokens.get_by_hash(token_hash)
    if stored is None:
        raise UnauthorizedException(detail="Token inválido")

    # 3.5 — Replay attack detection: token already revoked → invalidate entire family
    if stored.revoked_at is not None:
        uow.repos.refresh_tokens.revoke_all_for_user(stored.usuario_id)
        raise UnauthorizedException(
            detail="Sesión invalidada por seguridad. Por favor inicie sesión nuevamente."
        )

    # 3.6 — Load user and resolve primary role
    usuario = uow.repos.usuarios.get(int(payload["sub"]))
    if usuario is None:
        raise UnauthorizedException(detail="Usuario no encontrado")
    rol = usuario.roles[0].rol_codigo if usuario.roles else "CLIENT"

    # Generate new token pair
    new_access = create_access_token(str(usuario.id), data={"role": rol})
    new_refresh = create_refresh_token(str(usuario.id))

    # 3.7 — Revoke the consumed token
    uow.repos.refresh_tokens.revoke(stored.id)

    # 3.8 — Persist the new refresh token hash and return the response
    new_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    uow.repos.refresh_tokens.create(
        usuario_id=usuario.id,
        token_hash=new_hash,
        expires_at=expires_at,
    )

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


def register(uow: UnitOfWork, body: RegisterRequest) -> Usuario:
    """Register a new user with CLIENT role.

    Validates email uniqueness, hashes the password, creates the user
    and assigns the CLIENT role — all within the same transaction.
    Does NOT commit; the caller (router / UoW context) is responsible
    for that.

    Args:
        uow: The per-request UnitOfWork with registered repositories.
        body: Validated registration data.

    Returns:
        The newly created Usuario instance (with relationships loaded).

    Raises:
        ConflictException: If the email is already registered.
    """
    # 1. Check email uniqueness
    existing = uow.repos.usuarios.get_by_email(body.email)
    if existing is not None:
        raise ConflictException(detail="El email ya está registrado")

    # 2. Hash password
    password_hash = hash_password(body.password)

    # 3. Create user
    usuario = Usuario(
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        password_hash=password_hash,
    )
    uow.repos.usuarios.add(usuario)

    # 4. Assign CLIENT role
    usuario_rol = UsuarioRol(
        usuario_id=usuario.id,
        rol_codigo="CLIENT",
    )
    uow.repos.usuarios.session.add(usuario_rol)
    uow.repos.usuarios.session.flush()
    uow.repos.usuarios.session.refresh(usuario)

    return usuario


def logout(uow: UnitOfWork, body: LogoutRequest, current_user: Usuario) -> None:
    """Revoke the refresh token to close the user's session.

    Verifies that the presented refresh token exists in BD, is not already
    revoked, and belongs to the authenticated user, then marks it as revoked.
    Does NOT commit; the caller (router) is responsible for that.

    Args:
        uow: The per-request UnitOfWork with registered repositories.
        body: Validated logout request containing the raw refresh token string.
        current_user: The authenticated user extracted from the Bearer access token.

    Raises:
        BadRequestException: If the token is not found, already revoked, or
            belongs to a different user.
    """
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    stored = uow.repos.refresh_tokens.get_by_hash(token_hash)

    if stored is None:
        raise BadRequestException(detail="Refresh token inválido")

    if stored.revoked_at is not None:
        raise BadRequestException(detail="Refresh token ya revocado")

    if stored.usuario_id != current_user.id:
        raise BadRequestException(detail="Refresh token inválido")

    uow.repos.refresh_tokens.revoke(stored.id)
