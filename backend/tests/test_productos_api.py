from __future__ import annotations

from decimal import Decimal

from sqlmodel import Session, select

from backend.categorias.model import Categoria
from backend.productos.model import Producto, ProductoCategoria
from backend.tests.conftest import auth_headers


def test_post_productos_crea_producto_201_devuelve_id_y_created_at(client, session: Session, admin_token: str):
    body = {
        "codigo_sku": "SKU-001",
        "nombre": "Producto 1",
        "descripcion": "Desc",
        "precio_base": "12.50",
        "stock_cantidad": 10,
        "disponible": True,
        "imagen_url": None,
    }

    res = client.post("/api/v1/productos/", json=body, headers=auth_headers(admin_token))
    assert res.status_code == 201
    data = res.json()
    assert isinstance(data.get("id"), int)
    assert data.get("created_at") is not None
    assert data["codigo_sku"] == "SKU-001"

    producto = session.get(Producto, data["id"])
    assert producto is not None
    assert producto.precio_base == Decimal("12.50")


def test_post_productos_con_categoria_ids_crea_pivots(client, session: Session, admin_token: str):
    cat1 = Categoria(nombre="Cat 1")
    cat2 = Categoria(nombre="Cat 2")
    session.add(cat1)
    session.add(cat2)
    session.commit()
    session.refresh(cat1)
    session.refresh(cat2)

    body = {
        "codigo_sku": "SKU-002",
        "nombre": "Producto 2",
        "precio_base": "10.00",
        "stock_cantidad": 0,
        "disponible": True,
        "categoria_ids": [cat1.id, cat2.id],
    }
    res = client.post("/api/v1/productos/", json=body, headers=auth_headers(admin_token))
    assert res.status_code == 201
    producto_id = res.json()["id"]

    pivots = session.exec(
        select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
    ).all()
    assert sorted([p.categoria_id for p in pivots]) == sorted([cat1.id, cat2.id])
    assert all(p.es_principal is False for p in pivots)


def test_post_productos_sku_duplicado_retorna_409(client, admin_token: str):
    body = {
        "codigo_sku": "SKU-DUP",
        "nombre": "Producto",
        "precio_base": "10.00",
        "stock_cantidad": 1,
        "disponible": True,
    }
    res1 = client.post("/api/v1/productos/", json=body, headers=auth_headers(admin_token))
    assert res1.status_code == 201

    res2 = client.post("/api/v1/productos/", json=body, headers=auth_headers(admin_token))
    assert res2.status_code == 409


def test_put_productos_actualiza_y_retorna_200(client, admin_token: str):
    create = {
        "codigo_sku": "SKU-003",
        "nombre": "Producto 3",
        "precio_base": "10.00",
        "stock_cantidad": 1,
        "disponible": True,
    }
    created = client.post(
        "/api/v1/productos/", json=create, headers=auth_headers(admin_token)
    ).json()

    update = {"nombre": "Producto 3 (edit)", "precio_base": "11.00"}
    res = client.put(
        f"/api/v1/productos/{created['id']}",
        json=update,
        headers=auth_headers(admin_token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["nombre"] == "Producto 3 (edit)"
    assert data["precio_base"] == "11.00"


def test_put_productos_sync_categorias_reemplaza_pivots(client, session: Session, admin_token: str):
    cat1 = Categoria(nombre="Cat A")
    cat2 = Categoria(nombre="Cat B")
    cat3 = Categoria(nombre="Cat C")
    session.add(cat1)
    session.add(cat2)
    session.add(cat3)
    session.commit()
    for c in (cat1, cat2, cat3):
        session.refresh(c)

    created = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-004",
            "nombre": "Producto 4",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
            "categoria_ids": [cat1.id, cat2.id],
        },
        headers=auth_headers(admin_token),
    ).json()

    res = client.put(
        f"/api/v1/productos/{created['id']}",
        json={"categoria_ids": [cat3.id]},
        headers=auth_headers(admin_token),
    )
    assert res.status_code == 200

    pivots = session.exec(
        select(ProductoCategoria).where(ProductoCategoria.producto_id == created["id"])
    ).all()
    assert [p.categoria_id for p in pivots] == [cat3.id]


def test_patch_disponibilidad_retorna_200_y_toggles(client, admin_token: str):
    created = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-005",
            "nombre": "Producto 5",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
        },
        headers=auth_headers(admin_token),
    ).json()

    res = client.patch(
        f"/api/v1/productos/{created['id']}/disponibilidad",
        json={"disponible": False},
        headers=auth_headers(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["disponible"] is False


def test_patch_stock_retorna_200_y_actualiza(client, admin_token: str):
    created = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-006",
            "nombre": "Producto 6",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
        },
        headers=auth_headers(admin_token),
    ).json()

    res = client.patch(
        f"/api/v1/productos/{created['id']}/stock",
        json={"stock_cantidad": 50},
        headers=auth_headers(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["stock_cantidad"] == 50


def test_patch_stock_negativo_retorna_422(client, admin_token: str):
    created = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-007",
            "nombre": "Producto 7",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
        },
        headers=auth_headers(admin_token),
    ).json()

    res = client.patch(
        f"/api/v1/productos/{created['id']}/stock",
        json={"stock_cantidad": -1},
        headers=auth_headers(admin_token),
    )
    assert res.status_code == 422


def test_delete_productos_retorna_204_y_deleted_at_poblado(client, session: Session, admin_token: str):
    created = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-008",
            "nombre": "Producto 8",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
        },
        headers=auth_headers(admin_token),
    ).json()

    res = client.delete(
        f"/api/v1/productos/{created['id']}", headers=auth_headers(admin_token)
    )
    assert res.status_code == 204

    producto = session.get(Producto, created["id"])
    assert producto is not None
    assert producto.deleted_at is not None


def test_endpoints_protegidos_rechazan_client_con_403(client, client_token: str):
    headers = auth_headers(client_token)

    res_create = client.post(
        "/api/v1/productos/",
        json={
            "codigo_sku": "SKU-009",
            "nombre": "Producto 9",
            "precio_base": "10.00",
            "stock_cantidad": 1,
            "disponible": True,
        },
        headers=headers,
    )
    assert res_create.status_code == 403

    # Other endpoints also protected: use non-existing id to avoid setup.
    assert client.put("/api/v1/productos/1", json={}, headers=headers).status_code == 403
    assert client.delete("/api/v1/productos/1", headers=headers).status_code == 403
    assert (
        client.patch(
            "/api/v1/productos/1/disponibilidad", json={"disponible": True}, headers=headers
        ).status_code
        == 403
    )
    assert (
        client.patch("/api/v1/productos/1/stock", json={"stock_cantidad": 1}, headers=headers).status_code
        == 403
    )
