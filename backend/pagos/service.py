from __future__ import annotations

import uuid

from backend.core.config import get_settings
from backend.core.exceptions import (
    NotFoundException,
    ValidationException,
)
from backend.core.uow import UnitOfWork
from backend.pagos.mp_client import get_mp_client
from backend.pagos.model import FormaPago, Pago
from backend.pagos.schemas import CrearPagoRequest
from backend.usuarios.model import Usuario


def crear_pago(
    uow: UnitOfWork,
    request: CrearPagoRequest,
    current_user: Usuario,
) -> Pago:
    """Create a payment in MercadoPago and register it in the database.

    Flow:
    1. Validate pedido exists, belongs to user, and is in PENDIENTE state.
    2. Validate monto matches pedido total.
    3. Verify forma_pago is active.
    4. Generate idempotency_key UUID.
    5. Call MercadoPago API via SDK.
    6. Register Pago in database atomically via UoW.
    7. Return the created Pago.
    """
    # ── 1. Load pedido ──────────────────────────────────────────────
    pedido = uow.repos.pedidos.get(request.pedido_id)
    if pedido is None:
        raise NotFoundException("PAGO_PEDIDO_NOT_FOUND")

    # ── 2. Ownership check ──────────────────────────────────────────
    user_roles = {ur.rol_codigo for ur in current_user.roles}
    is_admin = "ADMIN" in user_roles

    if not is_admin and pedido.usuario_id != current_user.id:
        # Don't reveal existence — same 404 as "not found"
        raise NotFoundException("PAGO_PEDIDO_NOT_FOUND")

    # ── 3. State validation ─────────────────────────────────────────
    if pedido.estado_actual != "PENDIENTE":
        raise ValidationException(
            "PAGO_PEDIDO_NO_PENDIENTE: "
            "El pedido debe estar en estado PENDIENTE para realizar el pago"
        )

    # ── 4. Amount validation ────────────────────────────────────────
    if request.monto != pedido.total:
        raise ValidationException(
            "PAGO_MONTO_INCORRECTO: "
            f"El monto enviado ({request.monto}) no coincide con el total del pedido ({pedido.total})"
        )

    # ── 5. Verify forma_pago is active ──────────────────────────────
    forma_pago = uow.session.get(FormaPago, pedido.forma_pago_codigo)
    if forma_pago is None or not forma_pago.activo:
        raise ValidationException(
            "PAGO_FORMA_PAGO_INACTIVA: "
            "La forma de pago seleccionada no está disponible actualmente"
        )

    # ── 6. Generate idempotency key ─────────────────────────────────
    idempotency_key = str(uuid.uuid4())

    # ── 7. Build MP payload ─────────────────────────────────────────
    settings = get_settings()
    mp_client = get_mp_client()

    payment_data: dict = {
        "transaction_amount": float(request.monto),
        "token": request.card_token,
        "description": f"Pedido FoodStore #{pedido.id}",
        "payment_method_id": request.payment_method_id,
        "installments": 1,
        "payer": {"email": current_user.email},
        "external_reference": str(pedido.id),
    }

    # Only include notification_url if configured
    if settings.mercadopago_notification_url:
        payment_data["notification_url"] = settings.mercadopago_notification_url

    # ── 8. Call MercadoPago API ─────────────────────────────────────
    try:
        from mercadopago.config import RequestOptions

        request_options = RequestOptions()
        request_options.custom_headers = {
            "X-Idempotency-Key": idempotency_key,
        }
        result = mp_client.payment().create(payment_data, request_options)
    except Exception as exc:
        # SDK or network error — raise as validation error so the
        # frontend can ask the user to retry.
        raise ValidationException(
            f"PAGO_MP_ERROR: Error al comunicarse con MercadoPago: {exc}"
        )

    # ── 9. Parse MP response ────────────────────────────────────────
    mp_response = result.get("response", {})
    mp_payment_id = mp_response.get("id")
    mp_status = mp_response.get("status", "rejected")

    # ── 10. Create Pago record ──────────────────────────────────────
    pago = Pago(
        pedido_id=pedido.id,
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
        external_reference=str(pedido.id) if mp_payment_id else None,
        idempotency_key=idempotency_key,
        monto=request.monto,
        moneda="ARS",
    )
    uow.repos.pagos.add(pago)

    return pago
