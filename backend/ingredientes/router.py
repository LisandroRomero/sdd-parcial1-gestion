from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.ingredientes import service as ingrediente_service
from backend.ingredientes.repository import IngredienteRepository
from backend.ingredientes.schemas import IngredienteCreate, IngredientePaginado, IngredienteRead, IngredienteUpdate
from backend.core.database import engine
from backend.core.dependencies import get_current_user, require_role
from backend.core.exceptions import AppException
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers IngredienteRepository
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork with IngredienteRepository registered."""
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("ingredientes", lambda s: IngredienteRepository(s))
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


@router.get(
    "/",
    response_model=IngredientePaginado,
    status_code=status.HTTP_200_OK,
    summary="List ingredientes",
)
def listar_ingredientes(
    es_alergeno: Optional[bool] = None,
    page: int = 1,
    size: int = 20,
    uow: UnitOfWork = Depends(_get_uow),
) -> IngredientePaginado:
    """Return a paginated list of active ingredientes (public endpoint).

    Optionally filter by ``es_alergeno``. Returns an empty items list when
    no ingredientes exist.
    """
    return ingrediente_service.listar(uow, es_alergeno=es_alergeno, page=page, size=size)


@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ingrediente",
)
def crear_ingrediente(
    body: IngredienteCreate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> IngredienteRead:
    """Create a new ingrediente.

    Requires ADMIN or STOCK role. Returns the created ingrediente.
    HTTP 409 if an ingrediente with the same nombre already exists.
    """
    ingrediente = ingrediente_service.crear(uow, body)
    uow.commit()
    return IngredienteRead.model_validate(ingrediente)


@router.put(
    "/{id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Update an ingrediente",
)
def actualizar_ingrediente(
    id: int,
    body: IngredienteUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> IngredienteRead:
    """Update an ingrediente's nombre or es_alergeno flag.

    Requires ADMIN or STOCK role.
    HTTP 404 if the ingrediente does not exist or is deleted.
    HTTP 409 if the new nombre is already in use.
    """
    ingrediente = ingrediente_service.actualizar(uow, id, body)
    uow.commit()
    return IngredienteRead.model_validate(ingrediente)


@router.delete(
    "/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete an ingrediente",
)
def eliminar_ingrediente(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> Response:
    """Soft-delete an ingrediente.

    Requires ADMIN or STOCK role. Returns 204 No Content on success.
    HTTP 404 if not found or already deleted.
    """
    ingrediente_service.eliminar(uow, id)
    uow.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
