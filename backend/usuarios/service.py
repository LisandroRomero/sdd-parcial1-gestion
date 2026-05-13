from __future__ import annotations

from datetime import datetime

from backend.core.exceptions import BadRequestException, NotFoundException
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario, UsuarioRol
from backend.usuarios.schemas import AssignRolesRequest, PerfilRead, PerfilUpdate


def assign_roles(
    uow: UnitOfWork,
    usuario_id: int,
    body: AssignRolesRequest,
    current_user: Usuario,
) -> Usuario:
    """Replace all roles of a user with the provided list (REPLACE semantics).

    Business rules:
    - RN-RB04: if ADMIN is NOT in the new role list, and the target user
      currently has ADMIN, and they are the last admin in the system
      (count_by_role("ADMIN") <= 1) → raise BadRequestException.

    Args:
        uow: Active Unit of Work (session and repositories available).
        usuario_id: ID of the user whose roles will be replaced.
        body: Validated request containing the new list of role codes.
        current_user: The authenticated admin performing the operation.

    Returns:
        The updated Usuario with refreshed roles.

    Raises:
        NotFoundException: If the target user does not exist.
        BadRequestException: If RN-RB04 would be violated.
    """
    # 1. Fetch target user
    usuario: Usuario | None = uow.repos.usuarios.get(usuario_id)
    if usuario is None:
        raise NotFoundException(detail=f"Usuario con id={usuario_id} no encontrado")

    # 2. RN-RB04: prevent removing the last ADMIN
    if "ADMIN" not in body.roles:
        user_role_codes = {ur.rol_codigo for ur in usuario.roles}
        if "ADMIN" in user_role_codes:
            admin_count: int = uow.repos.usuarios.count_by_role("ADMIN")
            if admin_count <= 1:
                raise BadRequestException(
                    detail=(
                        "No se puede quitar el rol ADMIN: "
                        "este usuario es el único administrador del sistema (RN-RB04)"
                    )
                )

    # 3. Delete all existing role assignments for the user
    uow.repos.usuario_roles.delete_all_for_user(usuario_id)
    uow.session.flush()

    # 4. Create new UsuarioRol entries
    for rol_codigo in body.roles:
        nuevo_rol = UsuarioRol(
            usuario_id=usuario_id,
            rol_codigo=rol_codigo,
            asignado_por_id=current_user.id,
        )
        uow.session.add(nuevo_rol)

    uow.session.flush()

    # 5. Refresh and return
    uow.session.refresh(usuario)
    return usuario


def get_perfil(uow: UnitOfWork, usuario_id: int) -> PerfilRead:
    """Return the full profile for the authenticated user.

    Loads ``roles`` and ``direcciones`` relationships.  Only active
    addresses (``deleted_at IS NULL``) are included in the response —
    the filtering is delegated to the ``PerfilRead`` validator.

    Args:
        uow: Active Unit of Work.
        usuario_id: ID of the authenticated user.

    Returns:
        ``PerfilRead`` with roles (as string codes) and active addresses.

    Raises:
        NotFoundException: If the user does not exist.
    """
    usuario: Usuario | None = uow.repos.usuarios.get(usuario_id)
    if usuario is None:
        raise NotFoundException(detail=f"Usuario con id={usuario_id} no encontrado")

    # Ensure relationships are loaded within the active session
    uow.session.refresh(usuario)
    return PerfilRead.model_validate(usuario)


def update_perfil(
    uow: UnitOfWork,
    usuario_id: int,
    data: PerfilUpdate,
) -> PerfilRead:
    """Update the authenticated user's own profile.

    Only ``nombre``, ``apellido``, and ``telefono`` may be modified.
    ``email``, ``password_hash``, and ``roles`` are NEVER touched.

    Args:
        uow: Active Unit of Work.
        usuario_id: ID of the authenticated user.
        data: Validated partial update payload.

    Returns:
        Updated ``PerfilRead``.

    Raises:
        NotFoundException: If the user does not exist.
    """
    usuario: Usuario | None = uow.repos.usuarios.get(usuario_id)
    if usuario is None:
        raise NotFoundException(detail=f"Usuario con id={usuario_id} no encontrado")

    # Apply only the fields that were explicitly provided (non-None)
    if data.nombre is not None:
        usuario.nombre = data.nombre
    if data.apellido is not None:
        usuario.apellido = data.apellido
    if data.telefono is not None:
        usuario.telefono = data.telefono

    usuario.updated_at = datetime.utcnow()

    uow.session.add(usuario)
    uow.session.flush()
    uow.session.refresh(usuario)

    return PerfilRead.model_validate(usuario)
