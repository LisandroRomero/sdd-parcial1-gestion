from __future__ import annotations

from fastapi import APIRouter, Depends, status

from backend.auth.schemas import RegisterRequest, UserResponse
from backend.auth.service import register
from backend.core.dependencies import get_uow
from backend.core.uow import UnitOfWork

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_endpoint(
    body: RegisterRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> UserResponse:
    """Create a new user account with CLIENT role.

    Validates the input data, checks email uniqueness, hashes the
    password, and persists the user together with the CLIENT role
    assignment in a single transaction.
    """
    usuario = register(uow, body)
    uow.commit()
    return UserResponse.model_validate(usuario)
