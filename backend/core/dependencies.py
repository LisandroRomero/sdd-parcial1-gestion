from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from backend.core.database import engine, get_session
from backend.core.exceptions import AppException, ForbiddenException, UnauthorizedException
from backend.core.security import verify_token
from backend.core.uow import UnitOfWork
from backend.refreshtokens.repository import RefreshTokenRepository
from backend.usuarios.model import Usuario
from backend.usuarios.repository import UsuarioRepository, UsuarioRolRepository


# ------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> Usuario:
    """FastAPI dependency that returns the authenticated user.

    Extracts the JWT from the ``Authorization: Bearer <token>`` header,
    verifies it, and returns the corresponding ``Usuario`` from the
    database.

    Raises:
        UnauthorizedException: If the header is missing or the token is
            invalid/expired.
    """
    if authorization is None:
        raise UnauthorizedException(detail="Token de acceso requerido")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedException(detail="Formato de token inválido")

    payload = verify_token(token)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise UnauthorizedException(detail="Token inválido: sin subject")

    usuario = session.get(Usuario, int(user_id_str))
    if usuario is None:
        raise UnauthorizedException(detail="Usuario no encontrado")

    return usuario


# ------------------------------------------------------------------
# Authorization (RBAC)
# ------------------------------------------------------------------


def require_role(*roles: str):
    """Dependency factory that restricts access to users with specific roles.

    Usage::

        @router.get("/admin/dashboard")
        def admin_dashboard(
            current_user: Usuario = Depends(require_role("admin")),
        ):
            ...

    Args:
        *roles: One or more role codes that are allowed access.

    Returns:
        A FastAPI dependency that returns the current user if they have
        at least one of the required roles.
    """

    def _require_role(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        user_role_codes = {ur.rol_codigo for ur in current_user.roles}
        if not user_role_codes.intersection(roles):
            raise ForbiddenException(
                detail=f"Se requiere uno de los roles: {', '.join(roles)}",
            )
        return current_user

    return _require_role


# ------------------------------------------------------------------
# Unit of Work (per-request)
# ------------------------------------------------------------------


def _register_repos(uow: UnitOfWork) -> None:
    """Register all known repositories with the UnitOfWork."""
    uow.repos.register("usuarios", UsuarioRepository)
    uow.repos.register("usuario_roles", UsuarioRolRepository)
    uow.repos.register("refresh_tokens", RefreshTokenRepository)


def get_uow() -> Generator[UnitOfWork, None, None]:
    """FastAPI dependency that provides a per-request UnitOfWork.

    The UoW is automatically entered on request start and exited on
    request completion. HTTPExceptions are intentional business responses
    (401, 403, 409, …); any writes made before raising them are committed
    so that security-critical side-effects (e.g. token revocation on a
    replay-attack detection) are persisted even though FastAPI returns a
    non-2xx status.

    Unexpected exceptions trigger a rollback, preserving data integrity.

    Usage::

        @router.post("/usuarios")
        def crear_usuario(
            uow: UnitOfWork = Depends(get_uow),
            ...
        ):
            uow.repos.usuarios.add(new_user)
            uow.commit()
    """

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    _register_repos(uow)
    try:
        yield uow
    except (HTTPException, AppException):
        # Intentional business error — commit any writes made before raising
        # (e.g. revoking all tokens on replay-attack detection).
        uow.session.commit()
        raise
    except Exception:
        uow.session.rollback()
        raise
    finally:
        uow.session.close()
