from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.core.database import engine
from backend.core.dependencies import get_current_user
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.direcciones import service as direccion_service
from backend.direcciones.repository import DireccionEntregaRepository
from backend.direcciones.schemas import DireccionEntregaCreate, DireccionEntregaRead, DireccionEntregaUpdate
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers DireccionEntregaRepository
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork with DireccionEntregaRepository registered.

    Mirrors the pattern established in ``backend/categorias/router.py``.
    Each module owns its UoW factory to keep modules self-contained and
    to avoid importing all repositories into ``core/dependencies.py``.
    """
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("direcciones", lambda s: DireccionEntregaRepository(s))
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


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------


@router.post(
    "/",
    response_model=DireccionEntregaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a delivery address for the authenticated user",
)
def crear_direccion(
    body: DireccionEntregaCreate,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionEntregaRead:
    """Create a new delivery address for the currently authenticated user.

    The ``usuario_id`` is taken from the JWT token — it is NOT part of the
    request body. Returns 201 with the created address.
    """
    direccion = direccion_service.crear(uow, body, current_user.id)
    uow.commit()
    return DireccionEntregaRead.model_validate(direccion)


@router.get(
    "/",
    response_model=list[DireccionEntregaRead],
    status_code=status.HTTP_200_OK,
    summary="List all active delivery addresses for the authenticated user",
)
def listar_direcciones(
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> list[DireccionEntregaRead]:
    """Return all active (non-deleted) delivery addresses of the current user."""
    direcciones = direccion_service.listar(uow, current_user.id)
    return [DireccionEntregaRead.model_validate(d) for d in direcciones]


@router.put(
    "/{id}",
    response_model=DireccionEntregaRead,
    status_code=status.HTTP_200_OK,
    summary="Update a delivery address",
)
def actualizar_direccion(
    id: int,
    body: DireccionEntregaUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionEntregaRead:
    """Update an existing delivery address.

    Only fields present in the request body are updated (patch semantics).
    Returns 404 if not found, 403 if the address belongs to another user.
    """
    direccion = direccion_service.actualizar(uow, id, body, current_user.id)
    uow.commit()
    return DireccionEntregaRead.model_validate(direccion)


@router.delete(
    "/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a delivery address",
)
def eliminar_direccion(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> Response:
    """Soft-delete a delivery address by setting ``deleted_at``.

    The address is no longer returned in ``GET /`` after deletion.
    Returns 204 No Content on success. Returns 404 if not found,
    403 if the address belongs to another user.
    """
    direccion_service.eliminar(uow, id, current_user.id)
    uow.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{id}/principal",
    response_model=DireccionEntregaRead,
    status_code=status.HTTP_200_OK,
    summary="Mark a delivery address as the user's primary address",
)
def marcar_principal_direccion(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    current_user: Usuario = Depends(get_current_user),
) -> DireccionEntregaRead:
    """Mark the specified address as the user's primary delivery address.

    Atomically clears ``es_principal`` on all other addresses of the same user,
    then sets it to ``True`` on the target. Guarantees one-principal invariant.
    Returns 404 if not found, 403 if the address belongs to another user.
    """
    direccion = direccion_service.marcar_principal(uow, id, current_user.id)
    uow.commit()
    return DireccionEntregaRead.model_validate(direccion)
