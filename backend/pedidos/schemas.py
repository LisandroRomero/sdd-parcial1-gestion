from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class DetallePedidoCreate(BaseModel):
    producto_id: int
    cantidad: int = 1
    personalizacion: Optional[list[int]] = None

    @field_validator("cantidad")
    @classmethod
    def cantidad_minima(cls, v: int) -> int:
        if v < 1:
            raise ValueError("cantidad must be >= 1")
        return v


class DetallePedidoRead(BaseModel):
    id: int
    pedido_id: int
    producto_id: int
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    personalizacion: Optional[list[int]] = None
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class PedidoCreate(BaseModel):
    direccion_id: int
    detalles: list[DetallePedidoCreate]


class PedidoUpdate(BaseModel):
    forma_pago_codigo: Optional[str] = None
    direccion_id: Optional[int] = None
    estado_actual: Optional[str] = None


class PedidoRead(BaseModel):
    id: int
    usuario_id: int
    forma_pago_codigo: Optional[str] = None
    direccion_id: int
    estado_actual: str
    total: Decimal
    costo_envio: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    detalles: list[DetallePedidoRead] = []

    model_config = ConfigDict(from_attributes=True)
