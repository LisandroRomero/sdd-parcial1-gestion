from __future__ import annotations

import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sqlmodel import Session

from backend.pagos.model import FormaPago, Pago
from backend.pedidos.model import EstadoPedido, Pedido
from backend.direcciones.model import DireccionEntrega
from backend.tests.conftest import auth_headers

WEBHOOK_SECRET = "test-webhook-secret"


# ── Helpers ────────────────────────────────────────────────────────


def _build_signature(body: bytes) -> str:
    """Compute a valid X-Signature for a given raw body."""
    return hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


def _build_headers(body: bytes) -> dict[str, str]:
    """Return headers with a valid X-Signature."""
    return {"X-Signature": _build_signature(body)}


def _make_payload(mp_payment_id: int) -> bytes:
    """Build a realistic MP IPN notification payload."""
    return json.dumps({
        "id": 987654321,
        "live_mode": False,
        "type": "payment",
        "date_created": "2025-01-15T10:00:00.000-03:00",
        "user_id": 123456,
        "api_version": "v1",
        "action": "payment.created",
        "data": {"id": str(mp_payment_id)},
    }).encode("utf-8")


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def webhook_test_data(session: Session, client_user) -> dict:
    """Set up a pedido (PENDIENTE) and a linked Pago record."""
    # Ensure EstadoPedido exists
    for codigo in ("PENDIENTE", "CONFIRMADO", "CANCELADO"):
        ep = session.get(EstadoPedido, codigo)
        if ep is None:
            session.add(EstadoPedido(codigo=codigo, es_terminal=(codigo == "CANCELADO")))
    session.flush()

    # FormaPago
    fp = session.get(FormaPago, "MP")
    if fp is None:
        session.add(FormaPago(codigo="MP", descripcion="MercadoPago", activo=True))
        session.flush()

    # Direccion
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

    # Pedido
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

    # Pago
    pago = Pago(
        pedido_id=pedido.id,
        mp_payment_id=12345678,
        mp_status="pending",
        monto=Decimal("150.00"),
        moneda="ARS",
    )
    session.add(pago)
    session.flush()
    session.commit()

    return {
        "pedido_id": pedido.id,
        "pago_id": pago.id,
        "mp_payment_id": 12345678,
        "direccion_id": direccion.id,
    }


# ── 5.1 Webhook con firma válida → 200 ────────────────────────────


def test_webhook_firma_valida_200(client, webhook_test_data: dict):
    """Verify that a webhook with a valid X-Signature returns 200."""
    payload = _make_payload(webhook_test_data["mp_payment_id"])

    with patch("backend.pagos.service.consultar_pago_mp") as mock_consulta:
        mock_consulta.return_value = {"status": "approved"}
        res = client.post(
            "/api/v1/pagos/webhook",
            content=payload,
            headers=_build_headers(payload),
        )

    assert res.status_code == 200


# ── 5.2 Webhook con firma inválida → 401 ──────────────────────────


def test_webhook_firma_invalida_401(client, webhook_test_data: dict):
    """Verify that a webhook with an invalid X-Signature returns 401."""
    payload = _make_payload(webhook_test_data["mp_payment_id"])

    res = client.post(
        "/api/v1/pagos/webhook",
        content=payload,
        headers={"X-Signature": "invalid-signature"},
    )

    assert res.status_code == 401


def test_webhook_sin_firma_401(client, webhook_test_data: dict):
    """Verify that a webhook without X-Signature returns 401."""
    payload = _make_payload(webhook_test_data["mp_payment_id"])

    res = client.post(
        "/api/v1/pagos/webhook",
        content=payload,
    )

    assert res.status_code == 401


# ── 5.3 Pago aprobado → avanza pedido a CONFIRMADO ────────────────


def test_webhook_pago_aprobado_avanza_pedido(client, session: Session, webhook_test_data: dict):
    """Verify that an approved payment advances the order to CONFIRMADO."""
    payload = _make_payload(webhook_test_data["mp_payment_id"])

    with patch("backend.pagos.service.consultar_pago_mp") as mock_consulta:
        mock_consulta.return_value = {"status": "approved"}
        res = client.post(
            "/api/v1/pagos/webhook",
            content=payload,
            headers=_build_headers(payload),
        )

    assert res.status_code == 200

    # Verify Pago.mp_status was updated
    pago = session.get(Pago, webhook_test_data["pago_id"])
    assert pago is not None
    assert pago.mp_status == "approved"

    # Verify Pedido advanced to CONFIRMADO
    pedido = session.get(Pedido, webhook_test_data["pedido_id"])
    assert pedido is not None
    assert pedido.estado_actual == "CONFIRMADO"


# ── 5.4 Pago rechazado → pedido queda PENDIENTE ───────────────────


def test_webhook_pago_rechazado_pedido_pendiente(client, session: Session, webhook_test_data: dict):
    """Verify that a rejected payment does NOT advance the order."""
    payload = _make_payload(webhook_test_data["mp_payment_id"])

    with patch("backend.pagos.service.consultar_pago_mp") as mock_consulta:
        mock_consulta.return_value = {"status": "rejected"}
        res = client.post(
            "/api/v1/pagos/webhook",
            content=payload,
            headers=_build_headers(payload),
        )

    assert res.status_code == 200

    # Verify Pago.mp_status was updated
    pago = session.get(Pago, webhook_test_data["pago_id"])
    assert pago is not None
    assert pago.mp_status == "rejected"

    # Verify Pedido is still PENDIENTE
    pedido = session.get(Pedido, webhook_test_data["pedido_id"])
    assert pedido is not None
    assert pedido.estado_actual == "PENDIENTE"


# ── 5.5 Idempotencia: mismo estado → skip sin efectos ─────────────


def test_webhook_idempotencia_mismo_estado(client, session: Session, webhook_test_data: dict):
    """Verify that a duplicate notification with same status is idempotent."""
    # Pre-set Pago to "approved" to simulate already processed
    pago = session.get(Pago, webhook_test_data["pago_id"])
    pago.mp_status = "approved"
    session.commit()

    payload = _make_payload(webhook_test_data["mp_payment_id"])

    with patch("backend.pagos.service.consultar_pago_mp") as mock_consulta:
        mock_consulta.return_value = {"status": "approved"}
        res = client.post(
            "/api/v1/pagos/webhook",
            content=payload,
            headers=_build_headers(payload),
        )

    assert res.status_code == 200

    # Pago still "approved"
    pago = session.get(Pago, webhook_test_data["pago_id"])
    assert pago.mp_status == "approved"

    # Pedido remains PENDIENTE (never called avanzar_estado)
    pedido = session.get(Pedido, webhook_test_data["pedido_id"])
    assert pedido.estado_actual == "PENDIENTE"


# ── 5.6 mp_payment_id no encontrado → 200 sin errores ─────────────


def test_webhook_mp_payment_id_no_encontrado_200(client, webhook_test_data: dict):
    """Verify unknown mp_payment_id returns 200 without errors."""
    unknown_id = 99999999  # Does not exist in DB
    payload = _make_payload(unknown_id)

    with patch("backend.pagos.service.consultar_pago_mp") as mock_consulta:
        mock_consulta.return_value = {"status": "approved"}
        res = client.post(
            "/api/v1/pagos/webhook",
            content=payload,
            headers=_build_headers(payload),
        )

    assert res.status_code == 200
