from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.admin import service as admin_service
from backend.admin.repository import AdminRepository
from backend.admin.schemas import (
    EstadoUsuarioUpdate,
    UsuarioAdminListRead,
    UsuarioAdminRead,
    UsuarioAdminUpdate,
)
from backend.core.database import engine
from backend.core.dependencies import require_role
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.refreshtokens.repository import RefreshTokenRepository
from backend.usuarios.repository import UsuarioRepository, UsuarioRolRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Local UoW factory — registers admin + the shared repositories it depends on
# ---------------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork for the admin module.

    Registers the repositories required by admin service functions:
    - ``admin``          → AdminRepository (list/get users)
    - ``usuarios``       → UsuarioRepository (count_by_role for RN-RB04)
    - ``usuario_roles``  → UsuarioRolRepository (delete_all_for_user)
    - ``refresh_tokens`` → RefreshTokenRepository (revoke_all_for_user)
    """

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("admin", lambda s: AdminRepository(s))
    uow.repos.register("usuarios", lambda s: UsuarioRepository(s))
    uow.repos.register("usuario_roles", lambda s: UsuarioRolRepository(s))
    uow.repos.register("refresh_tokens", lambda s: RefreshTokenRepository(s))
    try:
        yield uow
    except (HTTPException, AppException):
        uow.session.commit()
        raise
    except Exception:
        uow.session.rollback()
        raise
    finally:
        uow.session.close()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/usuarios",
    response_model=UsuarioAdminListRead,
    summary="List users (admin)",
)
def list_usuarios_admin(
    buscar: Optional[str] = Query(default=None, description="Search by name or email"),
    rol: Optional[str] = Query(default=None, description="Filter by role code"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    uow: UnitOfWork = Depends(_get_uow),
    _: object = Depends(require_role("ADMIN")),
) -> UsuarioAdminListRead:
    """Return a paginated list of all users with optional search and role filter."""
    return admin_service.list_usuarios(uow, buscar=buscar, rol=rol, page=page, size=size)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioAdminRead,
    summary="Update user profile and/or roles (admin)",
)
def update_usuario_admin(
    usuario_id: int,
    body: UsuarioAdminUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: object = Depends(require_role("ADMIN")),
) -> UsuarioAdminRead:
    """Update a user's profile fields and/or role list.

    Enforces RN-RB04: the last ADMIN cannot be demoted.
    Revoking roles invalidates all active sessions for the affected user.
    """
    result = admin_service.update_usuario(uow, usuario_id, body)
    uow.commit()
    return result


@router.patch(
    "/usuarios/{usuario_id}/estado",
    response_model=UsuarioAdminRead,
    summary="Toggle user active state (admin)",
)
def toggle_estado_usuario(
    usuario_id: int,
    body: EstadoUsuarioUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: object = Depends(require_role("ADMIN")),
) -> UsuarioAdminRead:
    """Activate or deactivate a user account.

    Deactivating immediately revokes all active refresh tokens.
    """
    result = admin_service.toggle_estado(uow, usuario_id, body)
    uow.commit()
    return result
