from __future__ import annotations

import hashlib
import hmac
import json
import logging
import uuid

from backend.core.config import get_settings
from backend.core.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from backend.core.uow import UnitOfWork
from backend.pagos.mp_client import consultar_pago_mp, get_mp_client
from backend.pagos.model import FormaPago, Pago
from backend.pagos.schemas import CrearPagoRequest
from backend.usuarios.model import Usuario

logger = logging.getLogger(__name__)


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

    # ── 6. Retry check + external_reference ──────────────────────────
    existing_pagos = uow.repos.pagos.get_by_pedido(pedido.id)
    for pago in existing_pagos:
        if pago.mp_status == "approved":
            raise ConflictException("PAGO_YA_APROBADO: El pedido ya tiene un pago aprobado")
    attempt = len(existing_pagos) + 1
    external_reference = f"{pedido.id}-{attempt}"

    # ── 7. Generate idempotency key ─────────────────────────────────
    idempotency_key = str(uuid.uuid4())

    # ── 8. Build MP payload ─────────────────────────────────────────
    settings = get_settings()
    mp_client = get_mp_client()

    payment_data: dict = {
        "transaction_amount": float(request.monto),
        "token": request.card_token,
        "description": f"Pedido FoodStore #{pedido.id}",
        "payment_method_id": request.payment_method_id,
        "installments": 1,
        "payer": {"email": current_user.email},
        "external_reference": external_reference,
    }

    # Only include notification_url if configured
    if settings.mercadopago_notification_url:
        payment_data["notification_url"] = settings.mercadopago_notification_url

    # ── 9. Call MercadoPago API ─────────────────────────────────────
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

    # ── 10. Parse MP response ───────────────────────────────────────
    mp_response = result.get("response", {})
    mp_payment_id = mp_response.get("id")
    mp_status = mp_response.get("status", "rejected")

    # ── 11. Create Pago record ──────────────────────────────────────
    pago = Pago(
        pedido_id=pedido.id,
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
        external_reference=external_reference if mp_payment_id else None,
        idempotency_key=idempotency_key,
        monto=request.monto,
        moneda="ARS",
    )
    uow.repos.pagos.add(pago)

    return pago


def consultar_pagos(
    uow: UnitOfWork,
    pedido_id: int,
    current_user: Usuario,
) -> list[Pago]:
    """Return all payment attempts for an order, ordered newest-first.

    Flow:
    1. Load pedido by ID
    2. If not found → NotFoundException
    3. Ownership check: if not ADMIN and pedido doesn't belong to user → 404
    4. Delegate to repository get_by_pedido()
    5. Return ordered list
    """
    pedido = uow.repos.pedidos.get(pedido_id)
    if pedido is None:
        raise NotFoundException("PAGO_PEDIDO_NOT_FOUND")

    user_roles = {ur.rol_codigo for ur in current_user.roles}
    is_admin = "ADMIN" in user_roles

    if not is_admin and pedido.usuario_id != current_user.id:
        raise NotFoundException("PAGO_PEDIDO_NOT_FOUND")

    return uow.repos.pagos.get_by_pedido(pedido_id)


# ── Webhook Processing ─────────────────────────────────────────────


def validar_firma_webhook(raw_body: bytes, x_signature: str) -> bool:
    """Validate ``X-Signature`` HMAC-SHA256 from MercadoPago webhook.

    The ``X-Signature`` header may be in either of these formats:

    * ``ts=<timestamp>,v1=<hex_digest>`` — newer MP format (preferred).
    * ``<hex_digest>`` — raw hex digest (fallback).

    In both cases the digest is HMAC-SHA256 of the raw request body
    computed with ``MERCADOPAGO_WEBHOOK_SECRET``. Comparison uses
    constant-time ``hmac.compare_digest``.

    Args:
        raw_body: The raw request body bytes.
        x_signature: The raw ``X-Signature`` header value.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    settings = get_settings()
    secret = settings.mercadopago_webhook_secret
    if not secret:
        logger.warning("MERCADOPAGO_WEBHOOK_SECRET is not configured — rejecting webhook")
        return False

    # Try to parse the newer format: ts=...,v1=<hex>
    v1 = x_signature
    if "," in x_signature:
        for pair in x_signature.split(","):
            pair = pair.strip()
            if pair.startswith("v1="):
                v1 = pair[3:]
                break

    if not v1:
        logger.warning("X-Signature header is empty or unparseable")
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


def procesar_webhook(
    uow: UnitOfWork,
    raw_body: bytes,
    x_signature: str,
) -> None:
    """Process an incoming MercadoPago IPN webhook notification.

    Flow:
    1. Validate ``X-Signature`` — reject with ``ValidationException``
       (HTTP 422) if invalid.
    2. Parse the JSON body and extract the ``mp_payment_id`` from
       ``data.id``.
    3. Look up the ``Pago`` record by ``mp_payment_id``.
    4. If no matching ``Pago`` → log and return gracefully.
    5. Consult the current payment status from MP API.
    6. **Idempotency**: if ``Pago.mp_status`` already matches the
       notified status → skip without side effects.
    7. Update ``Pago.mp_status``.
    8. If ``status == "approved"`` → attempt to advance the order from
       ``PENDIENTE`` to ``CONFIRMADO`` via ``avanzar_estado()``,
       recording a system-originated transition (``usuario_id=NULL``).
    9. On any non-recoverable error → log and return gracefully
       (the endpoint always returns 200 to MP for non-signature
       failures).

    Args:
        uow: The UnitOfWork with ``pagos`` and ``pedidos`` repos
             registered.
        raw_body: Raw request body bytes.
        x_signature: The ``X-Signature`` header value.

    Raises:
        ValidationException: If the ``X-Signature`` is invalid.
    """
    # ── 1. Signature validation ─────────────────────────────────────
    if not validar_firma_webhook(raw_body, x_signature):
        raise ValidationException(
            "PAGO_WEBHOOK_FIRMA_INVALIDA: X-Signature no válida"
        )

    # ── 2. Parse payload ────────────────────────────────────────────
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        logger.warning("Webhook payload is not valid JSON: %s", exc)
        return

    # ── 3. Extract mp_payment_id ────────────────────────────────────
    notification_type = payload.get("type") or payload.get("topic")
    if notification_type != "payment":
        logger.info("Ignoring non-payment webhook notification: %s", notification_type)
        return

    data = payload.get("data", {})
    raw_id = data.get("id")
    if raw_id is None:
        logger.warning("Webhook payload missing data.id")
        return

    try:
        mp_payment_id = int(raw_id)
    except (ValueError, TypeError):
        logger.warning("Webhook data.id is not an integer: %s", raw_id)
        return

    # ── 4. Look up Pago ─────────────────────────────────────────────
    pago = uow.repos.pagos.get_by_mp_payment_id(mp_payment_id)
    if pago is None:
        logger.info("Ignoring webhook for unknown mp_payment_id=%s", mp_payment_id)
        return

    # ── 5. Consult MP API ───────────────────────────────────────────
    mp_response = consultar_pago_mp(mp_payment_id)
    if not mp_response:
        logger.warning("Empty response from MP API for payment %s — skipping", mp_payment_id)
        return

    mp_status = mp_response.get("status")

    # ── 6. Idempotency ──────────────────────────────────────────────
    if pago.mp_status == mp_status:
        logger.info(
            "Idempotent skip for pago_id=%s mp_payment_id=%s (status=%s)",
            pago.id, mp_payment_id, mp_status,
        )
        return

    # ── 7. Update Pago.mp_status ────────────────────────────────────
    old_status = pago.mp_status
    pago.mp_status = mp_status
    uow.repos.pagos.update(pago)

    # ── 8. If approved → advance order ──────────────────────────────
    if mp_status == "approved":
        try:
            from backend.pedidos.service import avanzar_estado

            avanzar_estado(
                uow=uow,
                pedido_id=pago.pedido_id,
                nuevo_estado="CONFIRMADO",
                # System-originated transition → usuario_id=NULL
                usuario_actual=None,
            )
            logger.info(
                "Pedido %s avanzó a CONFIRMADO (pago_id=%s, mp_payment_id=%s)",
                pago.pedido_id, pago.id, mp_payment_id,
            )
        except (NotFoundException, ConflictException, ValidationException) as exc:
            # Pedido not found, state no longer PENDIENTE, etc.
            # Log and continue — MP doesn't need to retry.
            logger.info(
                "Order transition skipped for pago_id=%s: %s",
                pago.id, exc,
            )

    logger.info(
        "Webhook processed: pago_id=%s mp_payment_id=%s status=%s->%s",
        pago.id, mp_payment_id, old_status, mp_status,
    )
