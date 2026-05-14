from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class DireccionSnapshot(BaseModel):
    id: int
    calle: str
    numero: str
    piso: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: str
    provincia: str
    codigo_postal: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


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
    """Compact schema for order listings — no details, history, or payment data."""

    id: int
    usuario_id: int
    estado_actual: str
    total: Decimal
    costo_envio: Decimal
    created_at: Optional[datetime] = None
    cantidad_items: int = 0

    model_config = ConfigDict(from_attributes=True)


class PagoResumen(BaseModel):
    """Minimal payment summary embedded in PedidoDetail."""

    id: int
    estado_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    monto: Decimal

    model_config = ConfigDict(from_attributes=True)


class PedidoDetail(PedidoRead):
    """Full order detail — extends PedidoRead with items, history, and payment."""

    detalles: list[DetallePedidoRead] = []
    historial_estados: list["HistorialEstadoRead"] = []
    pago: Optional[PagoResumen] = None
    direccion: Optional[DireccionSnapshot] = None


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
    """Paginated order list response with page/size format."""

    items: list[PedidoRead]
    total: int
    page: int
    size: int
    pages: int
