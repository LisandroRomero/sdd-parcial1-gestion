from __future__ import annotations

from decimal import Decimal

import pytest

from sqlmodel import Session

from backend.pedidos.model import EstadoPedido, Pedido, HistorialEstadoPedido
from backend.direcciones.model import DireccionEntrega
from backend.pagos.model import FormaPago
from backend.tests.conftest import auth_headers


@pytest.fixture
def test_data(session: Session, client_user) -> dict:
    estados = ["PENDIENTE", "CONFIRMADO", "EN_PREP", "EN_CAMINO", "ENTREGADO", "CANCELADO"]
    for e in estados:
        existing = session.get(EstadoPedido, e)
        if existing is None:
            session.add(EstadoPedido(codigo=e, es_terminal=(e in ("ENTREGADO", "CANCELADO"))))

    fp = FormaPago(codigo="EFECTIVO", descripcion="Efectivo")
    session.add(fp)
    session.flush()

    direccion = DireccionEntrega(
        usuario_id=client_user.id,
        alias="Casa",
        calle="Av. Siempre Viva",
        numero="123",
        ciudad="Springfield",
        provincia="BS AS",
        codigo_postal="1000",
    )
    session.add(direccion)
    session.flush()

    pedido = Pedido(
        usuario_id=client_user.id,
        forma_pago_codigo="EFECTIVO",
        direccion_id=direccion.id,
        estado_actual="CONFIRMADO",
        total=Decimal("100.00"),
        costo_envio=Decimal("10.00"),
    )
    session.add(pedido)
    session.flush()

    h1 = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=None,
        estado_hasta="PENDIENTE",
    )
    session.add(h1)
    session.flush()

    h2 = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde="PENDIENTE",
        estado_hasta="CONFIRMADO",
        usuario_id=client_user.id,
    )
    session.add(h2)
    session.flush()

    h3 = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde="CONFIRMADO",
        estado_hasta="CANCELADO",
        usuario_id=client_user.id,
        motivo="El cliente canceló",
    )
    session.add(h3)
    session.commit()

    return {"pedido_id": pedido.id, "direccion_id": direccion.id}


def test_historial_cliente_propio(client, session: Session, client_token: str, test_data: dict):
    pedido_id = test_data["pedido_id"]
    res = client.get(f"/api/v1/pedidos/{pedido_id}/historial", headers=auth_headers(client_token))
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_historial_cliente_ajeno_devuelve_403(client, session: Session, roles, test_data: dict):
    from backend.usuarios.model import Usuario, UsuarioRol
    from backend.core.security import create_access_token, hash_password

    other_user = Usuario(email="other@test.local", password_hash=hash_password("Password1234!"), activo=True)
    session.add(other_user)
    session.flush()
    session.add(UsuarioRol(usuario_id=other_user.id, rol_codigo="CLIENT"))
    session.commit()
    session.refresh(other_user)

    other_token = create_access_token(str(other_user.id), data={"role": "CLIENT"})

    res = client.get(f"/api/v1/pedidos/{test_data['pedido_id']}/historial", headers=auth_headers(other_token))
    assert res.status_code == 403
    assert "PEDIDO_NO_AUTORIZADO" in res.text


def test_historial_admin_ve_cualquiera(client, admin_token: str, test_data: dict):
    res = client.get(f"/api/v1/pedidos/{test_data['pedido_id']}/historial", headers=auth_headers(admin_token))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3


def test_historial_gestor_pedidos_ve_cualquiera(client, session: Session, roles, test_data: dict):
    from backend.usuarios.model import Usuario, UsuarioRol
    from backend.core.security import create_access_token, hash_password

    gestor = Usuario(email="gestor@test.local", password_hash=hash_password("Password1234!"), activo=True)
    session.add(gestor)
    session.flush()
    session.add(UsuarioRol(usuario_id=gestor.id, rol_codigo="PEDIDOS"))
    session.commit()
    session.refresh(gestor)

    gestor_token = create_access_token(str(gestor.id), data={"role": "PEDIDOS"})

    res = client.get(f"/api/v1/pedidos/{test_data['pedido_id']}/historial", headers=auth_headers(gestor_token))
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3


def test_historial_pedido_inexistente_devuelve_404(client, client_token: str):
    res = client.get("/api/v1/pedidos/99999/historial", headers=auth_headers(client_token))
    assert res.status_code == 404


def test_historial_integridad_datos(client, client_token: str, test_data: dict):
    pedido_id = test_data["pedido_id"]
    res = client.get(f"/api/v1/pedidos/{pedido_id}/historial", headers=auth_headers(client_token))
    assert res.status_code == 200
    data = res.json()

    timestamps = [d["created_at"] for d in data]
    assert timestamps == sorted(timestamps)

    assert data[0]["estado_desde"] is None
    assert data[0]["estado_hasta"] == "PENDIENTE"

    assert data[2]["motivo"] == "El cliente canceló"
    assert data[2]["usuario_id"] is not None

    for entry in data:
        assert entry["id"] is not None
        assert entry["pedido_id"] == pedido_id
        assert entry["estado_hasta"] is not None
        assert entry["created_at"] is not None
