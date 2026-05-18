from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sqlmodel import Session

from backend.pagos.model import FormaPago, Pago
from backend.pedidos.model import EstadoPedido, Pedido
from backend.direcciones.model import DireccionEntrega
from backend.tests.conftest import auth_headers


@pytest.fixture
def payment_test_data(session: Session, client_user) -> dict:
    ep = session.get(EstadoPedido, "PENDIENTE")
    if ep is None:
        session.add(EstadoPedido(codigo="PENDIENTE", es_terminal=False))
        session.flush()

    fp = FormaPago(codigo="MP", descripcion="MercadoPago", activo=True)
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
        forma_pago_codigo="MP",
        direccion_id=direccion.id,
        estado_actual="PENDIENTE",
        total=Decimal("150.00"),
        costo_envio=Decimal("10.00"),
    )
    session.add(pedido)
    session.flush()
    session.commit()

    return {"pedido_id": pedido.id, "direccion_id": direccion.id}


@pytest.fixture(autouse=True)
def mock_mp_client():
    with patch("backend.pagos.service.get_mp_client") as mock_get:
        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_sdk.payment.return_value = mock_payment
        mock_payment.create.return_value = {
            "response": {
                "id": 12345678,
                "status": "approved",
                "status_detail": "accredited",
            }
        }
        mock_get.return_value = mock_sdk
        yield


REQUEST_BODY = {
    "pedido_id": 0,
    "card_token": "tok_test_12345",
    "payment_method_id": "visa",
    "monto": "150.00",
}


def _build_body(pedido_id: int, **overrides) -> dict:
    body = dict(REQUEST_BODY)
    body["pedido_id"] = pedido_id
    body.update(overrides)
    return body


# ── Happy path ─────────────────────────────────────────────────────


def test_crear_pago_exitoso_201(client, client_token: str, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 201
    data = res.json()
    assert isinstance(data["id"], int)
    assert data["mp_payment_id"] == 12345678
    assert data["mp_status"] == "approved"
    assert data["monto"] == "150.00"
    assert data["moneda"] == "ARS"
    assert data["pedido_id"] == payment_test_data["pedido_id"]


def test_crear_pago_admin_exitoso_201(client, admin_token: str, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(admin_token))
    assert res.status_code == 201
    data = res.json()
    assert data["mp_payment_id"] == 12345678
    assert isinstance(data["id"], int)


# ── Pedido errors ─────────────────────────────────────────────────


def test_crear_pago_pedido_inexistente_404(client, client_token: str):
    body = _build_body(99999)
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 404
    assert "PAGO_PEDIDO_NOT_FOUND" in res.text


def test_crear_pago_pedido_otro_usuario_404(client, session: Session, roles, client_token: str, payment_test_data: dict):
    from backend.usuarios.model import Usuario, UsuarioRol
    from backend.core.security import create_access_token, hash_password

    other = Usuario(email="other@test.local", password_hash=hash_password("Password1234!"), activo=True)
    session.add(other)
    session.flush()
    session.add(UsuarioRol(usuario_id=other.id, rol_codigo="CLIENT"))
    session.commit()
    session.refresh(other)
    other_token = create_access_token(str(other.id), data={"role": "CLIENT"})

    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(other_token))
    assert res.status_code == 404
    assert "PAGO_PEDIDO_NOT_FOUND" in res.text


def test_crear_pago_pedido_no_pendiente_422(client, session: Session, client_token: str, payment_test_data: dict):
    pedido = session.get(Pedido, payment_test_data["pedido_id"])
    pedido.estado_actual = "CONFIRMADO"
    session.commit()

    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 422
    assert "PAGO_PEDIDO_NO_PENDIENTE" in res.text


# ── Amount error ──────────────────────────────────────────────────


def test_crear_pago_monto_incorrecto_422(client, client_token: str, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"], monto="99.00")
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 422
    assert "PAGO_MONTO_INCORRECTO" in res.text


# ── FormaPago error ───────────────────────────────────────────────


def test_crear_pago_forma_pago_inactiva_422(client, session: Session, client_token: str, payment_test_data: dict):
    fp = session.get(FormaPago, "MP")
    fp.activo = False
    session.commit()

    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 422
    assert "PAGO_FORMA_PAGO_INACTIVA" in res.text


# ── MP SDK error ──────────────────────────────────────────────────


def test_crear_pago_mp_error_422(client, client_token: str, payment_test_data: dict):
    with patch("backend.pagos.service.get_mp_client") as mock_get:
        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_sdk.payment.return_value = mock_payment
        mock_payment.create.side_effect = RuntimeError("MP connection timeout")
        mock_get.return_value = mock_sdk

        body = _build_body(payment_test_data["pedido_id"])
        res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
        assert res.status_code == 422
        assert "PAGO_MP_ERROR" in res.text


# ── Auth / Authorization errors ───────────────────────────────────


def test_crear_pago_sin_token_401(client, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body)
    assert res.status_code == 401


def test_crear_pago_rol_stock_403(client, stock_token: str, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(stock_token))
    assert res.status_code == 403


# ── Notification URL ──────────────────────────────────────────────


def test_crear_pago_con_notification_url(client, client_token: str, payment_test_data: dict):
    with (
        patch("backend.pagos.service.get_settings") as mock_get_settings,
        patch("backend.pagos.service.get_mp_client") as mock_get_mp,
    ):
        mock_settings = MagicMock()
        mock_settings.mercadopago_notification_url = "https://hooks.example.com/mp"
        mock_settings.mercadopago_access_token = "test-token"
        mock_get_settings.return_value = mock_settings

        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_sdk.payment.return_value = mock_payment
        mock_payment.create.return_value = {
            "response": {"id": 99999, "status": "approved"}
        }
        mock_get_mp.return_value = mock_sdk

        body = _build_body(payment_test_data["pedido_id"])
        res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
        assert res.status_code == 201

        call_kwargs = mock_payment.create.call_args
        assert call_kwargs is not None
        payment_data = call_kwargs[0][0]
        assert payment_data["notification_url"] == "https://hooks.example.com/mp"


# ── Idempotency key ───────────────────────────────────────────────


def test_crear_pago_idempotency_key_en_payload(client, client_token: str, payment_test_data: dict):
    with patch("backend.pagos.service.get_mp_client") as mock_get:
        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_sdk.payment.return_value = mock_payment
        mock_payment.create.return_value = {
            "response": {"id": 88888, "status": "approved"}
        }
        mock_get.return_value = mock_sdk

        body = _build_body(payment_test_data["pedido_id"])
        res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
        assert res.status_code == 201

        call_kwargs = mock_payment.create.call_args
        assert call_kwargs is not None
        request_options = call_kwargs[0][1]
        headers = request_options.custom_headers
        assert "X-Idempotency-Key" in headers
        assert len(headers["X-Idempotency-Key"]) > 0


# ── DB persistence ────────────────────────────────────────────────


def test_crear_pago_persiste_en_db(client, session: Session, client_token: str, payment_test_data: dict):
    body = _build_body(payment_test_data["pedido_id"])
    res = client.post("/api/v1/pagos/crear", json=body, headers=auth_headers(client_token))
    assert res.status_code == 201
    pago_id = res.json()["id"]

    pago = session.get(Pago, pago_id)
    assert pago is not None
    assert pago.pedido_id == payment_test_data["pedido_id"]
    assert pago.mp_payment_id == 12345678
    assert pago.monto == Decimal("150.00")
    assert pago.moneda == "ARS"
    assert pago.idempotency_key is not None
