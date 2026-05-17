from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class CrearPagoRequest(BaseModel):
    """Request schema for POST /api/v1/pagos/crear."""

    pedido_id: int
    card_token: str
    payment_method_id: str
    monto: Decimal


class PagoResponse(BaseModel):
    """Response schema returned after creating a payment."""

    id: int
    pedido_id: int
    mp_payment_id: Optional[int] = None
    mp_status: Optional[str] = None
    external_reference: Optional[str] = None
    monto: Decimal
    moneda: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PagoRead(BaseModel):
    """Read schema for querying an existing payment."""

    id: int
    pedido_id: int
    mp_payment_id: Optional[int] = None
    mp_status: Optional[str] = None
    external_reference: Optional[str] = None
    monto: Decimal
    moneda: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
