"""Seed data: roles, order states, payment methods, and admin user."""
from datetime import datetime, timezone

from sqlmodel import Session, select

from backend.core.database import engine
from backend.usuarios.model import Usuario, Rol, UsuarioRol
# Import ALL model modules to resolve SQLModel relationships
import backend.refreshtokens.model  # noqa: F401
import backend.direcciones.model  # noqa: F401
import backend.categorias.model  # noqa: F401
import backend.productos.model  # noqa: F401
import backend.ingredientes.model  # noqa: F401
from backend.pedidos.model import EstadoPedido
from backend.pagos.model import FormaPago

import bcrypt


def seed_roles(session: Session) -> None:
    roles = [
        {"codigo": "ADMIN", "descripcion": "Administrador general"},
        {"codigo": "STOCK", "descripcion": "Gestor de Stock"},
        {"codigo": "PEDIDOS", "descripcion": "Gestor de Pedidos"},
        {"codigo": "CLIENT", "descripcion": "Cliente"},
    ]
    for r in roles:
        existing = session.exec(select(Rol).where(Rol.codigo == r["codigo"])).first()
        if not existing:
            session.add(Rol(**r))
    session.commit()


def seed_estados_pedido(session: Session) -> None:
    estados = [
        {"codigo": "PENDIENTE", "descripcion": "Pedido pendiente", "es_terminal": False},
        {"codigo": "CONFIRMADO", "descripcion": "Pedido confirmado", "es_terminal": False},
        {"codigo": "PREPARACION", "descripcion": "En preparación", "es_terminal": False},
        {"codigo": "ENVIADO", "descripcion": "Enviado al cliente", "es_terminal": False},
        {"codigo": "ENTREGADO", "descripcion": "Entregado", "es_terminal": True},
        {"codigo": "CANCELADO", "descripcion": "Cancelado", "es_terminal": True},
    ]
    for e in estados:
        existing = session.exec(select(EstadoPedido).where(EstadoPedido.codigo == e["codigo"])).first()
        if not existing:
            session.add(EstadoPedido(**e))
    session.commit()


def seed_formas_pago(session: Session) -> None:
    formas = [
        {"codigo": "MERCADOPAGO", "descripcion": "Mercado Pago"},
        {"codigo": "EFECTIVO", "descripcion": "Efectivo"},
        {"codigo": "TRANSFERENCIA", "descripcion": "Transferencia Bancaria"},
    ]
    for f in formas:
        existing = session.exec(select(FormaPago).where(FormaPago.codigo == f["codigo"])).first()
        if not existing:
            session.add(FormaPago(**f))
    session.commit()


def seed_admin(session: Session) -> None:
    existing = session.exec(select(Usuario).where(Usuario.email == "admin@foodstore.com")).first()
    if existing:
        return  # ya existe
    admin = Usuario(
        email="admin@foodstore.com",
        password_hash=bcrypt.hashpw("Admin1234!".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8"),
        nombre="Admin",
        apellido="FoodStore",
        activo=True,
    )
    session.add(admin)
    session.flush()  # para obtener el id

    # Asignar rol ADMIN
    session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
    session.commit()


def main():
    print("[Seed] Seeding database...")
    with Session(engine) as session:
        seed_roles(session)
        print("[Seed] Roles created")
        seed_estados_pedido(session)
        print("[Seed] Order states created")
        seed_formas_pago(session)
        print("[Seed] Payment methods created")
        seed_admin(session)
        print("[Seed] Admin user created")
    print("[Seed] Seed complete!")


if __name__ == "__main__":
    main()
