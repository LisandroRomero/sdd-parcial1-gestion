from __future__ import annotations

from collections.abc import Generator
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

# Ensure Settings required env vars exist before importing the app.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("MERCADOPAGO_ACCESS_TOKEN", "test-mp-token")
os.environ.setdefault("MERCADOPAGO_WEBHOOK_SECRET", "test-webhook-secret")

from backend.core.security import create_access_token, hash_password
from backend.main import create_app
from backend.usuarios.model import Rol, Usuario, UsuarioRol


@pytest.fixture
def engine():
    # In-memory SQLite DB for isolated API tests.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        # Share the same in-memory DB across multiple Sessions/connections.
        poolclass=StaticPool,
    )

    # Create only the subset of tables we need.
    # Full metadata includes PostgreSQL-only types (e.g. ARRAY) that SQLite can't compile.
    wanted = {
        "rol",
        "usuario",
        "usuariorol",
        "categoria",
        "producto",
        "productocategoria",
        "estadopedido",
        "pedido",
        "historialestadopedido",
        "direccionentrega",
        "formapago",
        "pago",
    }
    tables = [t for name, t in SQLModel.metadata.tables.items() if name in wanted]
    SQLModel.metadata.create_all(engine, tables=tables)
    return engine


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(engine) -> Generator[TestClient, None, None]:
    # Patch module-level engine references used by feature routers.
    import backend.core.database as core_database
    import backend.core.dependencies as core_dependencies
    import backend.categorias.router as categorias_router
    import backend.ingredientes.router as ingredientes_router
    import backend.productos.router as productos_router
    import backend.pedidos.router as pedidos_router
    import backend.pagos.router as pagos_router

    core_database.engine = engine
    core_dependencies.engine = engine
    categorias_router.engine = engine
    ingredientes_router.engine = engine
    productos_router.engine = engine
    pedidos_router.engine = engine
    pagos_router.engine = engine

    app = create_app()

    def _override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    from backend.core.database import get_session

    app.dependency_overrides[get_session] = _override_get_session

    with TestClient(app) as c:
        yield c


@pytest.fixture
def roles(session: Session) -> None:
    for codigo in ["ADMIN", "STOCK", "PEDIDOS", "CLIENT"]:
        existing = session.get(Rol, codigo)
        if existing is None:
            session.add(Rol(codigo=codigo, descripcion=codigo))
    session.commit()


def _create_user_with_roles(session: Session, *, email: str, roles: list[str]) -> Usuario:
    user = Usuario(
        email=email,
        password_hash=hash_password("Password1234!"),
        activo=True,
    )
    session.add(user)
    session.flush()

    for role in roles:
        session.add(UsuarioRol(usuario_id=user.id, rol_codigo=role))
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_user(session: Session, roles: None) -> Usuario:
    return _create_user_with_roles(session, email="admin@test.local", roles=["ADMIN"])


@pytest.fixture
def stock_user(session: Session, roles: None) -> Usuario:
    return _create_user_with_roles(session, email="stock@test.local", roles=["STOCK"])


@pytest.fixture
def client_user(session: Session, roles: None) -> Usuario:
    return _create_user_with_roles(session, email="client@test.local", roles=["CLIENT"])


@pytest.fixture
def admin_token(admin_user: Usuario) -> str:
    return create_access_token(str(admin_user.id), data={"role": "ADMIN"})


@pytest.fixture
def stock_token(stock_user: Usuario) -> str:
    return create_access_token(str(stock_user.id), data={"role": "STOCK"})


@pytest.fixture
def client_token(client_user: Usuario) -> str:
    return create_access_token(str(client_user.id), data={"role": "CLIENT"})


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
