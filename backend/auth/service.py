from __future__ import annotations

from backend.auth.schemas import RegisterRequest
from backend.core.exceptions import ConflictException
from backend.core.security import hash_password
from backend.core.uow import UnitOfWork
from backend.usuarios.model import Usuario, UsuarioRol


def register(uow: UnitOfWork, body: RegisterRequest) -> Usuario:
    """Register a new user with CLIENT role.

    Validates email uniqueness, hashes the password, creates the user
    and assigns the CLIENT role — all within the same transaction.
    Does NOT commit; the caller (router / UoW context) is responsible
    for that.

    Args:
        uow: The per-request UnitOfWork with registered repositories.
        body: Validated registration data.

    Returns:
        The newly created Usuario instance (with relationships loaded).

    Raises:
        ConflictException: If the email is already registered.
    """
    # 1. Check email uniqueness
    existing = uow.repos.usuarios.get_by_email(body.email)
    if existing is not None:
        raise ConflictException(detail="El email ya está registrado")

    # 2. Hash password
    password_hash = hash_password(body.password)

    # 3. Create user
    usuario = Usuario(
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        password_hash=password_hash,
    )
    uow.repos.usuarios.add(usuario)

    # 4. Assign CLIENT role
    usuario_rol = UsuarioRol(
        usuario_id=usuario.id,
        rol_codigo="CLIENT",
    )
    uow.repos.usuarios.session.add(usuario_rol)
    uow.repos.usuarios.session.flush()
    uow.repos.usuarios.session.refresh(usuario)

    return usuario
