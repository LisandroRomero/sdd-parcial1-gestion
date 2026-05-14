from __future__ import annotations

from math import ceil
from typing import Optional

from backend.admin.schemas import (
    EstadoUsuarioUpdate,
    UsuarioAdminListRead,
    UsuarioAdminRead,
    UsuarioAdminUpdate,
)
from backend.core.exceptions import BadRequestException, NotFoundException
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario, UsuarioRol


# ---------------------------------------------------------------------------
# Internal serialization helper
# ---------------------------------------------------------------------------


def _to_read(usuario: Usuario) -> UsuarioAdminRead:
    """Convert a ``Usuario`` ORM instance to ``UsuarioAdminRead``.

    Extracts role codes from the relationship instead of using
    ``model_validate`` because ``roles`` is a list of ``UsuarioRol``
    objects, not strings.
    """
    return UsuarioAdminRead(
        id=usuario.id,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        activo=usuario.activo,
        roles=[ur.rol_codigo for ur in usuario.roles],
        created_at=usuario.created_at,
    )


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------


def list_usuarios(
    uow: UnitOfWork,
    buscar: Optional[str] = None,
    rol: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> UsuarioAdminListRead:
    """Return a paginated list of users filtered by search term and/or role.

    Args:
        uow: Per-request UnitOfWork with admin repository registered.
        buscar: Optional text to search in nombre, apellido, email.
        rol: Optional role code to filter users by.
        page: 1-indexed page number.
        size: Number of items per page.

    Returns:
        Paginated ``UsuarioAdminListRead`` response.
    """
    offset = (page - 1) * size
    items, total = uow.repos.admin.list_usuarios(
        buscar=buscar,
        rol=rol,
        limit=size,
        offset=offset,
    )
    pages = ceil(total / size) if total > 0 else 0
    return UsuarioAdminListRead(
        items=[_to_read(u) for u in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


def update_usuario(
    uow: UnitOfWork,
    usuario_id: int,
    body: UsuarioAdminUpdate,
) -> UsuarioAdminRead:
    """Update a user's profile data and/or role assignments.

    Business rules enforced:
    - RN-RB04: the last user with the ADMIN role cannot have that role removed.
      If the incoming ``body.roles`` does not include "ADMIN" and the current
      user is the only ADMIN in the system, raise 400.
    - Changing roles invalidates all existing refresh tokens (D3 in design.md).

    Args:
        uow: Per-request UnitOfWork.
        usuario_id: PK of the user to update.
        body: Partial update — any field may be None (no-op for that field).

    Returns:
        Updated ``UsuarioAdminRead``.

    Raises:
        NotFoundException: If the user does not exist.
        BadRequestException: If RN-RB04 would be violated.
    """
    usuario = uow.repos.admin.get_by_id(usuario_id)
    if usuario is None:
        raise NotFoundException(detail="Usuario no encontrado")

    # --- Role update -------------------------------------------------------
    if body.roles is not None:
        current_roles = {ur.rol_codigo for ur in usuario.roles}

        # RN-RB04: prevent removing the last ADMIN
        if "ADMIN" in current_roles and "ADMIN" not in body.roles:
            admin_count = uow.repos.usuarios.count_by_role("ADMIN")
            if admin_count <= 1:
                raise BadRequestException(
                    detail="No es posible quitar el rol ADMIN al único administrador del sistema"
                )

        # Replace all existing role assignments
        uow.repos.usuario_roles.delete_all_for_user(usuario_id)
        uow.session.flush()

        for rol_codigo in body.roles:
            uow.session.add(UsuarioRol(usuario_id=usuario_id, rol_codigo=rol_codigo))
        uow.session.flush()

        # Revoke all active refresh tokens so the user must re-authenticate
        # with the new role on next login (D3 in design.md).
        uow.repos.refresh_tokens.revoke_all_for_user(usuario_id)

    # --- Profile field updates ---------------------------------------------
    if body.nombre is not None:
        usuario.nombre = body.nombre
    if body.apellido is not None:
        usuario.apellido = body.apellido
    if body.email is not None:
        usuario.email = body.email

    uow.session.add(usuario)
    uow.session.flush()
    uow.session.refresh(usuario)

    return _to_read(usuario)


def toggle_estado(
    uow: UnitOfWork,
    usuario_id: int,
    body: EstadoUsuarioUpdate,
) -> UsuarioAdminRead:
    """Activate or deactivate a user account.

    When deactivating (``activo=False``), all active refresh tokens are revoked
    so the user is immediately logged out of all sessions (D3 in design.md).

    Args:
        uow: Per-request UnitOfWork.
        usuario_id: PK of the user to update.
        body: ``{ activo: bool }``

    Returns:
        Updated ``UsuarioAdminRead``.

    Raises:
        NotFoundException: If the user does not exist.
    """
    usuario = uow.repos.admin.get_by_id(usuario_id)
    if usuario is None:
        raise NotFoundException(detail="Usuario no encontrado")

    usuario.activo = body.activo
    uow.session.add(usuario)
    uow.session.flush()

    if not body.activo:
        # Revoke all active sessions so the disabled user is kicked out
        uow.repos.refresh_tokens.revoke_all_for_user(usuario_id)

    uow.session.refresh(usuario)
    return _to_read(usuario)
