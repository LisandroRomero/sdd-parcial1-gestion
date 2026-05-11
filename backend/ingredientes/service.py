from __future__ import annotations

from datetime import datetime, timezone

from backend.ingredientes.model import Ingrediente
from backend.ingredientes.schemas import IngredienteCreate, IngredientePaginado, IngredienteRead, IngredienteUpdate
from backend.core.exceptions import ConflictException, NotFoundException
from backend.core.uow import UnitOfWork


def listar(
    uow: UnitOfWork,
    *,
    es_alergeno: bool | None,
    page: int,
    size: int,
) -> IngredientePaginado:
    """Return a paginated list of active ingredientes.

    Optionally filtered by ``es_alergeno``.

    Args:
        uow: The per-request UnitOfWork with the ``ingredientes`` repository registered.
        es_alergeno: If provided, filter by allergen flag.
        page: 1-based page number.
        size: Number of records per page.

    Returns:
        IngredientePaginado with items, total, page, size, and pages.
    """
    repo = uow.repos.ingredientes
    skip = (page - 1) * size
    items, total = repo.list_active(es_alergeno=es_alergeno, skip=skip, limit=size)
    read_items = [IngredienteRead.model_validate(i) for i in items]
    return IngredientePaginado.build(items=read_items, total=total, page=page, size=size)


def crear(uow: UnitOfWork, data: IngredienteCreate) -> Ingrediente:
    """Create a new ingrediente.

    Validates that no other active ingrediente with the same nombre exists before persisting.

    Args:
        uow: The per-request UnitOfWork with the ``ingredientes`` repository registered.
        data: Validated creation payload.

    Returns:
        The newly created Ingrediente instance.

    Raises:
        ConflictException: If an ingrediente with the same nombre already exists
            (INGREDIENTE_NOMBRE_DUPLICADO).
    """
    repo = uow.repos.ingredientes

    if repo.exists_by_nombre(data.nombre):
        raise ConflictException(
            detail="INGREDIENTE_NOMBRE_DUPLICADO: Ya existe un ingrediente con ese nombre"
        )

    ingrediente = Ingrediente(
        nombre=data.nombre,
        es_alergeno=data.es_alergeno,
    )
    return repo.add(ingrediente)


def actualizar(uow: UnitOfWork, id: int, data: IngredienteUpdate) -> Ingrediente:
    """Update an existing ingrediente.

    Validates:
    - The ingrediente exists and is active.
    - If nombre is being changed, the new nombre is not already in use by another active ingrediente.

    Args:
        uow: The per-request UnitOfWork with the ``ingredientes`` repository registered.
        id: Primary key of the ingrediente to update.
        data: Validated update payload (partial — only provided fields are updated).

    Returns:
        The updated Ingrediente instance.

    Raises:
        NotFoundException: If the ingrediente does not exist or is soft-deleted.
        ConflictException: If the new nombre is already in use by another ingrediente.
    """
    repo = uow.repos.ingredientes

    ingrediente = repo.get_by_id_active(id)
    if ingrediente is None:
        raise NotFoundException(detail="INGREDIENTE_NOT_FOUND: Ingrediente no encontrado")

    if data.nombre is not None and data.nombre != ingrediente.nombre:
        if repo.exists_by_nombre(data.nombre, exclude_id=id):
            raise ConflictException(
                detail="INGREDIENTE_NOMBRE_DUPLICADO: Ya existe un ingrediente con ese nombre"
            )
        ingrediente.nombre = data.nombre

    if data.es_alergeno is not None:
        ingrediente.es_alergeno = data.es_alergeno

    return repo.update(ingrediente)


def eliminar(uow: UnitOfWork, id: int) -> None:
    """Soft-delete an ingrediente.

    Args:
        uow: The per-request UnitOfWork with the ``ingredientes`` repository registered.
        id: Primary key of the ingrediente to delete.

    Raises:
        NotFoundException: If the ingrediente does not exist or is already soft-deleted.
    """
    repo = uow.repos.ingredientes

    ingrediente = repo.get_by_id_active(id)
    if ingrediente is None:
        raise NotFoundException(detail="INGREDIENTE_NOT_FOUND: Ingrediente no encontrado")

    ingrediente.deleted_at = datetime.now(tz=timezone.utc)
    repo.update(ingrediente)
