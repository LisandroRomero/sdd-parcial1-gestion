from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class PagoCreate(BaseModel):
    pedido_id: int
    monto: Decimal


class PagoRead(BaseModel):
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
