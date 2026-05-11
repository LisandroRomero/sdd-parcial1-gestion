from __future__ import annotations

from backend.categorias.model import Categoria
from backend.categorias.schemas import CategoriaCreate, CategoriaTree, CategoriaUpdate
from backend.core.exceptions import ConflictException, NotFoundException
from backend.core.uow import UnitOfWork


def crear(uow: UnitOfWork, data: CategoriaCreate) -> Categoria:
    """Create a new category.

    Validates that no other active category with the same nombre exists at
    the same level (same parent_id) before persisting.

    Args:
        uow: The per-request UnitOfWork with the ``categorias`` repository registered.
        data: Validated creation payload.

    Returns:
        The newly created Categoria instance.

    Raises:
        ConflictException: If a category with the same nombre already exists at
            the same level (CATEGORIA_NOMBRE_DUPLICADO).
    """
    repo = uow.repos.categorias

    if repo.exists_name_at_level(data.nombre, data.parent_id):
        raise ConflictException(
            detail="CATEGORIA_NOMBRE_DUPLICADO: Ya existe una categoría con ese nombre en este nivel"
        )

    categoria = Categoria(
        nombre=data.nombre,
        descripcion=data.descripcion,
        parent_id=data.parent_id,
    )
    return repo.add(categoria)


def listar_arbol(uow: UnitOfWork) -> list[CategoriaTree]:
    """Return the full category tree as nested CategoriaTree nodes.

    Uses a recursive CTE to fetch all active categories in a single query,
    then builds the nested structure in Python with a dict-index (O(n)).

    Args:
        uow: The per-request UnitOfWork with the ``categorias`` repository registered.

    Returns:
        A list of root-level CategoriaTree nodes, each with nested ``hijos``.
    """
    repo = uow.repos.categorias
    flat_rows = repo.get_tree()

    # Build dict-index: id → CategoriaTree node
    nodes: dict[int, CategoriaTree] = {}
    for row in flat_rows:
        nodes[row["id"]] = CategoriaTree(
            id=row["id"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            parent_id=row["parent_id"],
            hijos=[],
        )

    # Wire children to parents; collect root nodes
    roots: list[CategoriaTree] = []
    for row in flat_rows:
        node = nodes[row["id"]]
        if row["parent_id"] is None:
            roots.append(node)
        else:
            parent = nodes.get(row["parent_id"])
            if parent is not None:
                parent.hijos.append(node)

    return roots


def actualizar(uow: UnitOfWork, id: int, data: CategoriaUpdate) -> Categoria:
    """Update an existing category.

    Validates:
    - The category exists and is active.
    - If parent_id is being changed to a non-None value, that parent_id != id
      (direct self-reference) and that setting this parent_id would not create
      a cycle in the hierarchy.
    - The new nombre (if changed) does not duplicate another category at the same level.

    Args:
        uow: The per-request UnitOfWork with the ``categorias`` repository registered.
        id: Primary key of the category to update.
        data: Validated update payload (partial — only provided fields are updated).

    Returns:
        The updated Categoria instance.

    Raises:
        NotFoundException: If the category does not exist or is soft-deleted.
        ConflictException: On self-reference, cycle detection, or duplicate nombre.
    """
    repo = uow.repos.categorias

    categoria = repo.get_by_id_active(id)
    if categoria is None:
        raise NotFoundException(detail="CATEGORIA_NOT_FOUND: Categoría no encontrada")

    # Determine the effective parent_id after the update
    new_parent_id = data.parent_id if data.parent_id is not None else categoria.parent_id
    # Allow explicitly clearing parent_id to None
    if "parent_id" in data.model_fields_set:
        new_parent_id = data.parent_id

    # Validate no direct self-reference
    if new_parent_id is not None and new_parent_id == id:
        raise ConflictException(
            detail="CATEGORIA_CICLO_DETECTADO: Una categoría no puede ser su propio padre"
        )

    # Validate no ancestor cycle
    if new_parent_id is not None and new_parent_id != categoria.parent_id:
        if repo.has_ancestor_cycle(target_id=id, new_parent_id=new_parent_id):
            raise ConflictException(
                detail="CATEGORIA_CICLO_DETECTADO: El cambio de padre crearía un ciclo jerárquico"
            )

    # Validate nombre uniqueness at the target level
    target_nombre = data.nombre if data.nombre is not None else categoria.nombre
    check_parent_id = new_parent_id
    if repo.exists_name_at_level(target_nombre, check_parent_id, exclude_id=id):
        raise ConflictException(
            detail="CATEGORIA_NOMBRE_DUPLICADO: Ya existe una categoría con ese nombre en este nivel"
        )

    # Apply updates
    if data.nombre is not None:
        categoria.nombre = data.nombre
    if data.descripcion is not None:
        categoria.descripcion = data.descripcion
    if "parent_id" in data.model_fields_set:
        categoria.parent_id = data.parent_id

    return repo.update(categoria)


def eliminar(uow: UnitOfWork, id: int) -> None:
    """Soft-delete a category.

    Validates:
    - The category exists and is active.
    - No active products are linked to it via ProductoCategoria (RN-CA03).
    - No active direct subcategories exist.

    Args:
        uow: The per-request UnitOfWork with the ``categorias`` repository registered.
        id: Primary key of the category to delete.

    Raises:
        NotFoundException: If the category does not exist or is already soft-deleted.
        ConflictException: If there are active products or subcategories blocking deletion.
    """
    repo = uow.repos.categorias

    categoria = repo.get_by_id_active(id)
    if categoria is None:
        raise NotFoundException(detail="CATEGORIA_NOT_FOUND: Categoría no encontrada")

    active_products = repo.count_active_products(id)
    if active_products > 0:
        raise ConflictException(
            detail="CATEGORIA_CON_PRODUCTOS_ACTIVOS: No se puede eliminar una categoría con productos activos"
        )

    active_hijos = repo.count_active_hijos(id)
    if active_hijos > 0:
        raise ConflictException(
            detail="CATEGORIA_CON_SUBCATEGORIAS_ACTIVAS: No se puede eliminar una categoría con subcategorías activas"
        )

    repo.delete(categoria)
