from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.auth.schemas import UserResponse
from backend.core.dependencies import get_current_user, get_uow, require_role
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario
from backend.usuarios.schemas import AssignRolesRequest, PerfilRead, PerfilUpdate
from backend.usuarios.service import assign_roles, get_perfil, update_perfil

router = APIRouter()


@router.get(
    "/me/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_200_OK,
    summary="Get the full profile of the authenticated user",
)
def get_my_perfil(
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> PerfilRead:
    """Return the authenticated user's full profile.

    Includes ``nombre``, ``apellido``, ``telefono``, ``roles`` (as string
    codes), ``activo``, timestamps, and the list of active delivery addresses.

    Accessible to any authenticated user (no role restriction).
    """
    return get_perfil(uow, current_user.id)


@router.put(
    "/me/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_200_OK,
    summary="Update the authenticated user's own profile",
)
def update_my_perfil(
    body: PerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> PerfilRead:
    """Partially update the authenticated user's own profile.

    Only ``nombre``, ``apellido``, and ``telefono`` may be changed.
    ``email``, ``password``, and ``roles`` are intentionally excluded
    from this endpoint.

    Accessible to any authenticated user (no role restriction).
    """
    perfil = update_perfil(uow, current_user.id, body)
    uow.commit()
    return perfil


@router.put(
    "/{id}/roles",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace all roles for a user (ADMIN only)",
)
def assign_user_roles(
    id: int,
    body: AssignRolesRequest,
    current_user: Usuario = Depends(require_role("ADMIN")),
    uow: UnitOfWork = Depends(get_uow),
) -> UserResponse:
    """Replace the full set of roles for a user.

    Accepts a list of role codes and atomically replaces all existing
    role assignments. Enforces RN-RB04 (cannot remove last ADMIN).

    Requires: ADMIN role.
    """
    usuario = assign_roles(uow, id, body, current_user)
    uow.commit()
    return UserResponse.model_validate(usuario)
