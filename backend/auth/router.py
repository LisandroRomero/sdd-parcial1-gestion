from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from backend.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from backend.auth.service import login as login_user
from backend.auth.service import register
from backend.core.dependencies import get_uow
from backend.core.rate_limit import limiter
from backend.core.uow import UnitOfWork

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT tokens",
)
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    body: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> TokenResponse:
    """Authenticate a user with email and password.

    Verifies credentials, generates a JWT access token (30 min) and a
    refresh token (7 days), persists the hashed refresh token in the
    database, and returns the token pair.

    Rate limited to 5 requests per IP per 15-minute window.
    """
    result = login_user(uow, body)
    uow.commit()
    return result


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
