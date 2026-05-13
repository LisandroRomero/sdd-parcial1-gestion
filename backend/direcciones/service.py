from __future__ import annotations

from datetime import datetime

from backend.core.exceptions import ForbiddenException, NotFoundException
from backend.core.uow import UnitOfWork
from backend.direcciones.model import DireccionEntrega
from backend.direcciones.schemas import DireccionEntregaCreate, DireccionEntregaUpdate


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------


def _get_direccion_owned(
    uow: UnitOfWork,
    direccion_id: int,
    usuario_id: int,
) -> DireccionEntrega:
    """Fetch an active address and verify ownership.

    Args:
        uow: Active Unit of Work with ``direcciones`` repository registered.
        direccion_id: PK of the address to retrieve.
        usuario_id: ID of the requesting user (from JWT token).

    Returns:
        The ``DireccionEntrega`` instance.

    Raises:
        NotFoundException: If the address does not exist or is soft-deleted.
        ForbiddenException: If the address belongs to a different user.
    """
    repo = uow.repos.direcciones
    direccion = repo.get_active(direccion_id)
    if direccion is None:
        raise NotFoundException(detail="Dirección no encontrada")
    if direccion.usuario_id != usuario_id:
        raise ForbiddenException(detail="No tenés permiso para acceder a esta dirección")
    return direccion


# ------------------------------------------------------------------
# Public service functions
# ------------------------------------------------------------------


def crear(
    uow: UnitOfWork,
    body: DireccionEntregaCreate,
    usuario_id: int,
) -> DireccionEntrega:
    """Create a new delivery address for the authenticated user.

    Args:
        uow: Active Unit of Work.
        body: Validated address creation payload (no ``usuario_id`` in body).
        usuario_id: ID of the owning user (from JWT token).

    Returns:
        The persisted ``DireccionEntrega`` instance.
    """
    direccion = DireccionEntrega(
        usuario_id=usuario_id,
        alias=body.alias,
        calle=body.calle,
        numero=body.numero,
        piso=body.piso,
        departamento=body.departamento,
        ciudad=body.ciudad,
        provincia=body.provincia,
        codigo_postal=body.codigo_postal,
        es_principal=body.es_principal,
    )
    return uow.repos.direcciones.add(direccion)


def listar(
    uow: UnitOfWork,
    usuario_id: int,
) -> list[DireccionEntrega]:
    """Return all active addresses for the authenticated user.

    Args:
        uow: Active Unit of Work.
        usuario_id: ID of the requesting user (from JWT token).

    Returns:
        List of active ``DireccionEntrega`` instances.
    """
    return uow.repos.direcciones.list_by_usuario(usuario_id)


def actualizar(
    uow: UnitOfWork,
    direccion_id: int,
    body: DireccionEntregaUpdate,
    usuario_id: int,
) -> DireccionEntrega:
    """Partially update an existing delivery address.

    Only fields explicitly set in ``body`` are applied (patch semantics).
    Verifies ownership before applying any changes.

    Args:
        uow: Active Unit of Work.
        direccion_id: PK of the address to update.
        body: Partial update payload.
        usuario_id: ID of the requesting user (from JWT token).

    Returns:
        The updated ``DireccionEntrega`` instance.

    Raises:
        NotFoundException: If the address does not exist or is soft-deleted.
        ForbiddenException: If the address belongs to a different user.
    """
    direccion = _get_direccion_owned(uow, direccion_id, usuario_id)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(direccion, field, value)

    direccion.updated_at = datetime.utcnow()
    return uow.repos.direcciones.update(direccion)


def eliminar(
    uow: UnitOfWork,
    direccion_id: int,
    usuario_id: int,
) -> None:
    """Soft-delete a delivery address.

    ``BaseRepository.delete()`` sets ``deleted_at`` automatically when the
    model has that column.

    Args:
        uow: Active Unit of Work.
        direccion_id: PK of the address to delete.
        usuario_id: ID of the requesting user (from JWT token).

    Raises:
        NotFoundException: If the address does not exist or is already soft-deleted.
        ForbiddenException: If the address belongs to a different user.
    """
    direccion = _get_direccion_owned(uow, direccion_id, usuario_id)
    uow.repos.direcciones.delete(direccion)


def marcar_principal(
    uow: UnitOfWork,
    direccion_id: int,
    usuario_id: int,
) -> DireccionEntrega:
    """Mark a delivery address as the user's primary address.

    Atomically clears ``es_principal`` on all other addresses of the user,
    then sets ``es_principal=True`` on the target address. Both operations
    share the same UoW session, guaranteeing the one-principal invariant.

    Args:
        uow: Active Unit of Work.
        direccion_id: PK of the address to mark as primary.
        usuario_id: ID of the requesting user (from JWT token).

    Returns:
        The updated ``DireccionEntrega`` with ``es_principal=True``.

    Raises:
        NotFoundException: If the address does not exist or is soft-deleted.
        ForbiddenException: If the address belongs to a different user.
    """
    repo = uow.repos.direcciones
    direccion = _get_direccion_owned(uow, direccion_id, usuario_id)

    # Clear principal on all other addresses of this user (bulk UPDATE).
    repo.unset_principal(usuario_id)

    # Set the target address as principal.
    direccion.es_principal = True
    direccion.updated_at = datetime.utcnow()
    return repo.update(direccion)
