from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from backend.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from backend.core.config import get_settings
from backend.core.exceptions import ConflictException, UnauthorizedException
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
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

    # 3. Resolve primary role
    rol = usuario.roles[0].rol_codigo if usuario.roles else "CLIENT"

    # 4. Generate tokens
    access_token = create_access_token(str(usuario.id), data={"role": rol})
    refresh_token = create_refresh_token(str(usuario.id))

    # 5. Hash refresh token for secure storage (never store the raw JWT)
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    # 6. Persist hashed refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    uow.repos.refresh_tokens.create(
        usuario_id=usuario.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    # 7. Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
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
