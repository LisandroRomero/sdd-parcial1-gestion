from __future__ import annotations

import logging
from functools import lru_cache

import mercadopago

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_mp_client() -> mercadopago.SDK:
    """Return a cached MercadoPago SDK client.

    The SDK is thread-safe and stateless, so a single instance is safe
    to share across all requests. Uses ``@lru_cache`` for lazy
    initialisation — the client is created on first call and reused
    thereafter.

    Raises:
        RuntimeError: If ``MERCADOPAGO_ACCESS_TOKEN`` is not configured.
    """
    settings = get_settings()
    if not settings.mercadopago_access_token:
        raise RuntimeError(
            "MERCADOPAGO_ACCESS_TOKEN is not configured. "
            "Set it in your environment or .env file."
        )
    return mercadopago.SDK(settings.mercadopago_access_token)


def consultar_pago_mp(mp_payment_id: int) -> dict:
    """Consult MercadoPago API for the current status of a payment.

    Args:
        mp_payment_id: The MercadoPago payment ID to query.

    Returns:
        The ``"response"`` dict from the SDK result, or an empty dict
        if the payment is not found or a communication error occurs.
    """
    try:
        client = get_mp_client()
        result = client.payment().get(mp_payment_id)
        return result.get("response", {})
    except Exception as exc:
        logger.warning(
            "Error consulting MP payment %s: %s", mp_payment_id, exc
        )
        return {}
