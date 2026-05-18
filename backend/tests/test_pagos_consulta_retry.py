from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from sqlmodel import Session

from backend.pagos.model import FormaPago, Pago
from backend.pedidos.model import EstadoPedido, Pedido
from backend.direcciones.model import DireccionEntrega
from backend.tests.conftest import auth_headers


# ── Helpers ────────────────────────────────────────────────────────

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


def _crear_pedido_base(session: Session, usuario_id: int) -> dict:
    ep = session.get(EstadoPedido, "PENDIENTE")
    if ep is None:
        session.add(EstadoPedido(codigo="PENDIENTE", es_terminal=False))
        session.flush()

    fp = session.get(FormaPago, "MP")
    if fp is None:
        session.add(FormaPago(codigo="MP", descripcion="MercadoPago", activo=True))
        session.flush()

    direccion = DireccionEntrega(
        usuario_id=usuario_id,
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
        usuario_id=usuario_id,
        forma_pago_codigo="MP",
        direccion_id=direccion.id,
        estado_actual="PENDIENTE",
        total=Decimal("150.00"),
        costo_envio=Decimal("10.00"),
    )
    session.add(pedido)
    session.flush()

    return {"pedido_id": pedido.id, "direccion_id": direccion.id}


def _crear_pago(
    session: Session,
    pedido_id: int,
    mp_status: str,
    external_reference: str,
    mp_payment_id: int,
    monto: Decimal | None = None,
    created_at: datetime | None = None,
) -> Pago:
    pago = Pago(
        pedido_id=pedido_id,
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
        external_reference=external_reference,
        monto=monto or Decimal("150.00"),
        moneda="ARS",
    )
    if created_at is not None:
        pago.created_at = created_at
    session.add(pago)
    session.flush()
    return pago


# ════════════════════════════════════════════════════════════════════
# 3.x  GET /api/v1/pagos/{pedido_id}
# ════════════════════════════════════════════════════════════════════


def test_consulta_pagos_pedido_propio_con_pagos_200(
    client, session: Session, client_user, client_token: str,
):
    """3.1 Pedido propio con pagos → 200 + lista ordenada DESC."""
    base = _crear_pedido_base(session, client_user.id)
    pedido_id = base["pedido_id"]

    old_pago = _crear_pago(
        session, pedido_id,
        mp_status="rejected", external_reference=f"{pedido_id}-1",
        mp_payment_id=10000001,
        created_at=datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
    )
    new_pago = _crear_pago(
        session, pedido_id,
        mp_status="pending", external_reference=f"{pedido_id}-2",
        mp_payment_id=10000002,
        created_at=datetime(2025, 6, 1, 10, 5, 0, tzinfo=timezone.utc),
    )
    session.commit()

    res = client.get(f"/api/v1/pagos/{pedido_id}", headers=auth_headers(client_token))
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == new_pago.id
    assert data[1]["id"] == old_pago.id
    assert data[0]["mp_status"] == "pending"
    assert data[1]["mp_status"] == "rejected"


def test_consulta_pagos_pedido_ajeno_404(
    client, session: Session, roles, client_token: str,
):
    """3.2 Pedido ajeno → 404 PAGO_PEDIDO_NOT_FOUND."""
    from backend.usuarios.model import Usuario, UsuarioRol
    from backend.core.security import hash_password

    other = Usuario(
        email="other@test.local",
        password_hash=hash_password("Password1234!"),
        activo=True,
    )
    session.add(other)
    session.flush()
    session.add(UsuarioRol(usuario_id=other.id, rol_codigo="CLIENT"))
    session.flush()

    base = _crear_pedido_base(session, other.id)
    pedido_id = base["pedido_id"]
    session.commit()

    res = client.get(f"/api/v1/pagos/{pedido_id}", headers=auth_headers(client_token))
    assert res.status_code == 404
    assert "PAGO_PEDIDO_NOT_FOUND" in res.text


def test_consulta_pagos_pedido_sin_pagos_200(
    client, session: Session, client_user, client_token: str,
):
    """3.3 Pedido sin pagos → 200 + lista vacía."""
    base = _crear_pedido_base(session, client_user.id)
    pedido_id = base["pedido_id"]
    session.commit()

    res = client.get(f"/api/v1/pagos/{pedido_id}", headers=auth_headers(client_token))
    assert res.status_code == 200
    assert res.json() == []


# ════════════════════════════════════════════════════════════════════
# 3.x  POST /api/v1/pagos/crear — Retry logic
# ════════════════════════════════════════════════════════════════════


def test_crear_pago_retry_despues_de_rechazado_201(
    client, session: Session, client_user, client_token: str,
):
    """3.4 Retry after rejected payment → 201 + external_reference único."""
    base = _crear_pedido_base(session, client_user.id)
    pedido_id = base["pedido_id"]

    old_pago = _crear_pago(
        session, pedido_id,
        mp_status="rejected", external_reference=f"{pedido_id}-1",
        mp_payment_id=10000001,
    )
    session.commit()

    with patch("backend.pagos.service.get_mp_client") as mock_get:
        mock_sdk = MagicMock()
        mock_payment = MagicMock()
        mock_sdk.payment.return_value = mock_payment
        mock_payment.create.return_value = {
            "response": {
                "id": 20000001,
                "status": "rejected",
                "status_detail": "rejected",
            }
        }
        mock_get.return_value = mock_sdk

        body = _build_body(pedido_id)
        res = client.post(
            "/api/v1/pagos/crear", json=body, headers=auth_headers(client_token),
        )
        assert res.status_code == 201
        data = res.json()
        assert data["external_reference"] == f"{pedido_id}-2"
        assert data["pedido_id"] == pedido_id
        assert data["mp_status"] == "rejected"
        assert data["id"] != old_pago.id


def test_crear_pago_retry_bloqueado_por_aprobado_409(
    client, session: Session, client_user, client_token: str,
):
    """3.5 Retry blocked because pedido has approved payment → 409."""
    base = _crear_pedido_base(session, client_user.id)
    pedido_id = base["pedido_id"]

    _crear_pago(
        session, pedido_id,
        mp_status="approved", external_reference=f"{pedido_id}-1",
        mp_payment_id=10000001,
    )
    session.commit()

    body = _build_body(pedido_id)
    res = client.post(
        "/api/v1/pagos/crear", json=body, headers=auth_headers(client_token),
    )
    assert res.status_code == 409
    assert "PAGO_YA_APROBADO" in res.text


def test_crear_pago_external_reference_unico_por_intento(
    client, session: Session, client_user, client_token: str,
):
    """3.6 Cada intento genera external_reference único."""
    base = _crear_pedido_base(session, client_user.id)
    pedido_id = base["pedido_id"]
    session.commit()

    counter: dict[str, int] = {"count": 0}

    def mp_side_effect(*args, **kwargs):
        counter["count"] += 1
        return {
            "response": {
                "id": 90000000 + counter["count"],
                "status": "rejected",
                "status_detail": "rejected",
            }
        }

    references: list[str] = []
    for i in range(3):
        with patch("backend.pagos.service.get_mp_client") as mock_get:
            mock_sdk = MagicMock()
            mock_payment = MagicMock()
            mock_sdk.payment.return_value = mock_payment
            mock_payment.create.side_effect = mp_side_effect
            mock_get.return_value = mock_sdk

            body = _build_body(pedido_id)
            res = client.post(
                "/api/v1/pagos/crear", json=body, headers=auth_headers(client_token),
            )
            assert res.status_code == 201
            data = res.json()
            ref = data["external_reference"]
            references.append(ref)
            assert ref == f"{pedido_id}-{i + 1}"

    assert len(set(references)) == 3
