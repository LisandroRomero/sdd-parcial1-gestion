from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from backend.categorias import service as categoria_service
from backend.categorias.repository import CategoriaRepository
from backend.categorias.schemas import CategoriaCreate, CategoriaRead, CategoriaTree, CategoriaUpdate
from backend.core.database import engine
from backend.core.dependencies import get_current_user, require_role
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario

router = APIRouter()


# ------------------------------------------------------------------
# Local UoW factory — registers CategoriaRepository
# ------------------------------------------------------------------


def _get_uow() -> Generator[UnitOfWork, None, None]:
    """Per-request UnitOfWork with CategoriaRepository registered."""
    from backend.core.exceptions import AppException
    from fastapi import HTTPException

    def _session_factory() -> Session:
        return Session(engine)

    uow = UnitOfWork(_session_factory)
    uow.__enter__()
    uow.repos.register("categorias", lambda s: CategoriaRepository(s))
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
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def crear_categoria(
    body: CategoriaCreate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> CategoriaRead:
    """Create a new category (root or child).

    Requires ADMIN or STOCK role. Returns the created category.
    HTTP 409 if a category with the same nombre already exists at the same level.
    """
    categoria = categoria_service.crear(uow, body)
    uow.commit()
    return CategoriaRead.model_validate(categoria)


@router.get(
    "/",
    response_model=list[CategoriaTree],
    status_code=status.HTTP_200_OK,
    summary="List the full category tree",
)
def listar_categorias(
    uow: UnitOfWork = Depends(_get_uow),
) -> list[CategoriaTree]:
    """Return the complete category tree (public endpoint, no authentication required).

    Uses a recursive CTE for a single-query fetch. Returns an empty list
    when no categories exist.
    """
    return categoria_service.listar_arbol(uow)


@router.put(
    "/{id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Update a category",
)
def actualizar_categoria(
    id: int,
    body: CategoriaUpdate,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> CategoriaRead:
    """Update a category's nombre, descripcion, or parent_id.

    Requires ADMIN or STOCK role.
    HTTP 404 if the category does not exist or is deleted.
    HTTP 409 on cycle detection or duplicate nombre at target level.
    """
    categoria = categoria_service.actualizar(uow, id, body)
    uow.commit()
    return CategoriaRead.model_validate(categoria)


@router.delete(
    "/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a category",
)
def eliminar_categoria(
    id: int,
    uow: UnitOfWork = Depends(_get_uow),
    _: Usuario = Depends(require_role("ADMIN", "STOCK")),
) -> Response:
    """Soft-delete a category.

    Requires ADMIN or STOCK role. Returns 204 No Content on success.
    HTTP 404 if not found. HTTP 409 if the category has active products or
    active subcategories.
    """
    categoria_service.eliminar(uow, id)
    uow.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
