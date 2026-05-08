from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.auth.schemas import UserResponse
from backend.core.dependencies import get_uow, require_role
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario
from backend.usuarios.schemas import AssignRolesRequest
from backend.usuarios.service import assign_roles

router = APIRouter()


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
