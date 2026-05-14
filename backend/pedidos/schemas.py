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
    forma_pago_codigo: str
    detalles: list[DetallePedidoCreate]


class PedidoUpdate(BaseModel):
    forma_pago_codigo: Optional[str] = None
    direccion_id: Optional[int] = None
    # NOTA: estado_actual eliminado — las transiciones usan AvanzarEstadoRequest


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
    historial_estados: list["HistorialEstadoRead"] = []

    model_config = ConfigDict(from_attributes=True)


class AvanzarEstadoRequest(BaseModel):
    nuevo_estado: str
    motivo: Optional[str] = None

    @field_validator("motivo")
    @classmethod
    def motivo_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() == "":
            raise ValueError("motivo cannot be empty")
        return v


class HistorialEstadoRead(BaseModel):
    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hasta: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PedidoListRead(BaseModel):
    items: list[PedidoRead]
    total: int
    limit: int
    offset: int
