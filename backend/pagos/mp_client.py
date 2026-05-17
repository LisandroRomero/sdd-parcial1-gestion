from __future__ import annotations

from functools import lru_cache

import mercadopago

from backend.core.config import get_settings


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
