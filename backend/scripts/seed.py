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
from backend.categorias.model import Categoria
from backend.ingredientes.model import Ingrediente, ProductoIngrediente
from backend.productos.model import Producto, ProductoCategoria

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
        {"codigo": "EN_PREP", "descripcion": "En preparación", "es_terminal": False},
        {"codigo": "EN_CAMINO", "descripcion": "Enviado al cliente", "es_terminal": False},
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


def seed_categorias(session: Session) -> None:
    parents_data = [
        {"nombre": "Hamburguesas", "descripcion": "Hamburguesas artesanales"},
        {"nombre": "Bebidas", "descripcion": "Bebidas frías"},
        {"nombre": "Papas & Acompañamientos", "descripcion": "Papas fritas y acompañamientos"},
        {"nombre": "Postres", "descripcion": "Postres caseros"},
    ]
    children_data = [
        {"nombre": "Clásicas", "descripcion": "Hamburguesas tradicionales", "parent_nombre": "Hamburguesas"},
        {"nombre": "Especiales", "descripcion": "Hamburguesas con ingredientes premium", "parent_nombre": "Hamburguesas"},
        {"nombre": "Gaseosas", "descripcion": "Gaseosas lineales", "parent_nombre": "Bebidas"},
        {"nombre": "Aguas", "descripcion": "Aguas minerales", "parent_nombre": "Bebidas"},
    ]

    for c in parents_data:
        existing = session.exec(select(Categoria).where(Categoria.nombre == c["nombre"])).first()
        if not existing:
            session.add(Categoria(nombre=c["nombre"], descripcion=c["descripcion"], parent_id=None))
    session.flush()

    for c in children_data:
        existing = session.exec(select(Categoria).where(Categoria.nombre == c["nombre"])).first()
        if not existing:
            parent = session.exec(select(Categoria).where(Categoria.nombre == c["parent_nombre"])).first()
            session.add(Categoria(nombre=c["nombre"], descripcion=c["descripcion"], parent_id=parent.id))
    session.commit()


def seed_ingredientes(session: Session) -> None:
    ingredientes = [
        {"nombre": "Medallón de carne", "es_alergeno": False},
        {"nombre": "Queso cheddar", "es_alergeno": True},
        {"nombre": "Queso muzzarella", "es_alergeno": True},
        {"nombre": "Lechuga", "es_alergeno": False},
        {"nombre": "Tomate", "es_alergeno": False},
        {"nombre": "Cebolla", "es_alergeno": False},
        {"nombre": "Pan de hamburguesa", "es_alergeno": True},
        {"nombre": "Panceta", "es_alergeno": False},
        {"nombre": "Huevo", "es_alergeno": True},
        {"nombre": "Mayonesa", "es_alergeno": True},
        {"nombre": "Ketchup", "es_alergeno": False},
        {"nombre": "Mostaza", "es_alergeno": False},
        {"nombre": "Pepinillos", "es_alergeno": False},
        {"nombre": "Jamón", "es_alergeno": False},
        {"nombre": "Papas fritas", "es_alergeno": False},
        {"nombre": "Salsa barbacoa", "es_alergeno": False},
        {"nombre": "Salsa cheddar", "es_alergeno": True},
        {"nombre": "Dulce de leche", "es_alergeno": True},
        {"nombre": "Vainilla", "es_alergeno": False},
    ]
    for i in ingredientes:
        existing = session.exec(select(Ingrediente).where(Ingrediente.nombre == i["nombre"])).first()
        if not existing:
            session.add(Ingrediente(**i))
    session.commit()


def seed_productos(session: Session) -> None:
    productos_data = [
        {
            "codigo_sku": "HMB-CLS-001",
            "nombre": "Hamburguesa Clásica",
            "descripcion": "Medallón de carne 150g con lechuga, tomate y cheddar",
            "precio_base": 4500.00,
            "stock_cantidad": 50,
            "disponible": True,
            "categoria_nombre": "Clásicas",
            "ingredientes": [
                {"nombre": "Medallón de carne", "es_removible": False},
                {"nombre": "Pan de hamburguesa", "es_removible": False},
                {"nombre": "Lechuga", "es_removible": True},
                {"nombre": "Tomate", "es_removible": True},
                {"nombre": "Queso cheddar", "es_removible": False},
                {"nombre": "Ketchup", "es_removible": True},
            ],
        },
        {
            "codigo_sku": "HMB-CLS-002",
            "nombre": "Hamburguesa Completa",
            "descripcion": "Medallón de carne 150g con jamón, huevo, lechuga, tomate y mayonesa",
            "precio_base": 5500.00,
            "stock_cantidad": 40,
            "disponible": True,
            "categoria_nombre": "Clásicas",
            "ingredientes": [
                {"nombre": "Medallón de carne", "es_removible": False},
                {"nombre": "Pan de hamburguesa", "es_removible": False},
                {"nombre": "Lechuga", "es_removible": True},
                {"nombre": "Tomate", "es_removible": True},
                {"nombre": "Jamón", "es_removible": False},
                {"nombre": "Huevo", "es_removible": False},
                {"nombre": "Mayonesa", "es_removible": False},
                {"nombre": "Queso muzzarella", "es_removible": False},
            ],
        },
        {
            "codigo_sku": "HMB-ESP-001",
            "nombre": "Hamburguesa BBQ",
            "descripcion": "Medallón de carne 150g con panceta, cheddar, cebolla crispy y salsa barbacoa",
            "precio_base": 6000.00,
            "stock_cantidad": 35,
            "disponible": True,
            "categoria_nombre": "Especiales",
            "ingredientes": [
                {"nombre": "Medallón de carne", "es_removible": False},
                {"nombre": "Pan de hamburguesa", "es_removible": False},
                {"nombre": "Queso cheddar", "es_removible": False},
                {"nombre": "Panceta", "es_removible": False},
                {"nombre": "Cebolla", "es_removible": True},
                {"nombre": "Salsa barbacoa", "es_removible": False},
            ],
        },
        {
            "codigo_sku": "HMB-ESP-002",
            "nombre": "Hamburguesa Cheddar Supreme",
            "descripcion": "Medallón de carne 150g bañado en salsa cheddar con panceta y cebolla caramelizada",
            "precio_base": 6500.00,
            "stock_cantidad": 30,
            "disponible": True,
            "categoria_nombre": "Especiales",
            "ingredientes": [
                {"nombre": "Medallón de carne", "es_removible": False},
                {"nombre": "Pan de hamburguesa", "es_removible": False},
                {"nombre": "Salsa cheddar", "es_removible": False},
                {"nombre": "Panceta", "es_removible": False},
                {"nombre": "Cebolla", "es_removible": True},
            ],
        },
        {
            "codigo_sku": "PAP-001",
            "nombre": "Papas Fritas",
            "descripcion": "Porción de papas fritas crujientes",
            "precio_base": 2000.00,
            "stock_cantidad": 100,
            "disponible": True,
            "categoria_nombre": "Papas & Acompañamientos",
            "ingredientes": [
                {"nombre": "Papas fritas", "es_removible": False},
            ],
        },
        {
            "codigo_sku": "PAP-002",
            "nombre": "Papas con Cheddar y Panceta",
            "descripcion": "Papas fritas cubiertas con salsa cheddar y panceta crocante",
            "precio_base": 3200.00,
            "stock_cantidad": 60,
            "disponible": True,
            "categoria_nombre": "Papas & Acompañamientos",
            "ingredientes": [
                {"nombre": "Papas fritas", "es_removible": False},
                {"nombre": "Salsa cheddar", "es_removible": False},
                {"nombre": "Panceta", "es_removible": False},
            ],
        },
        {
            "codigo_sku": "BEB-GAS-001",
            "nombre": "Coca-Cola 500ml",
            "descripcion": "Gaseosa Coca-Cola sabor original 500ml",
            "precio_base": 1500.00,
            "stock_cantidad": 200,
            "disponible": True,
            "categoria_nombre": "Gaseosas",
            "ingredientes": [],
        },
        {
            "codigo_sku": "BEB-GAS-002",
            "nombre": "Sprite 500ml",
            "descripcion": "Gaseosa Sprite sabor lima-limón 500ml",
            "precio_base": 1500.00,
            "stock_cantidad": 200,
            "disponible": True,
            "categoria_nombre": "Gaseosas",
            "ingredientes": [],
        },
        {
            "codigo_sku": "BEB-AGU-001",
            "nombre": "Agua Mineral 500ml",
            "descripcion": "Agua mineral sin gas 500ml",
            "precio_base": 1000.00,
            "stock_cantidad": 200,
            "disponible": True,
            "categoria_nombre": "Aguas",
            "ingredientes": [],
        },
        {
            "codigo_sku": "POS-001",
            "nombre": "Flan con Dulce de Leche",
            "descripcion": "Flan casero con dulce de leche",
            "precio_base": 2500.00,
            "stock_cantidad": 30,
            "disponible": True,
            "categoria_nombre": "Postres",
            "ingredientes": [
                {"nombre": "Dulce de leche", "es_removible": False},
                {"nombre": "Vainilla", "es_removible": False},
            ],
        },
    ]

    for p in productos_data:
        existing = session.exec(select(Producto).where(Producto.codigo_sku == p["codigo_sku"])).first()
        if existing:
            continue
        producto = Producto(
            codigo_sku=p["codigo_sku"],
            nombre=p["nombre"],
            descripcion=p["descripcion"],
            precio_base=p["precio_base"],
            stock_cantidad=p["stock_cantidad"],
            disponible=p["disponible"],
        )
        session.add(producto)
        session.flush()

        categoria = session.exec(select(Categoria).where(Categoria.nombre == p["categoria_nombre"])).first()
        if categoria:
            session.add(ProductoCategoria(producto_id=producto.id, categoria_id=categoria.id, es_principal=True))

        for ing in p["ingredientes"]:
            ingrediente = session.exec(select(Ingrediente).where(Ingrediente.nombre == ing["nombre"])).first()
            if ingrediente:
                session.add(ProductoIngrediente(
                    producto_id=producto.id,
                    ingrediente_id=ingrediente.id,
                    es_removible=ing["es_removible"],
                ))

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
        seed_categorias(session)
        print("[Seed] Categories created")
        seed_ingredientes(session)
        print("[Seed] Ingredients created")
        seed_productos(session)
        print("[Seed] Products created")
    print("[Seed] Seed complete!")


if __name__ == "__main__":
    main()
