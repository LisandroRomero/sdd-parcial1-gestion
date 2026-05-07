from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ProductoCreate(BaseModel):
    codigo_sku: str
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    stock_cantidad: int = 0
    disponible: bool = True
    imagen_url: Optional[str] = None

    @field_validator("stock_cantidad")
    @classmethod
    def stock_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("stock_cantidad must be >= 0")
        return v


class ProductoUpdate(BaseModel):
    codigo_sku: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[Decimal] = None
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    imagen_url: Optional[str] = None


class ProductoRead(BaseModel):
    id: int
    codigo_sku: str
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    stock_cantidad: int
    disponible: bool
    imagen_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductoCategoriaCreate(BaseModel):
    producto_id: int
    categoria_id: int
    es_principal: bool = False


class ProductoCategoriaRead(BaseModel):
    producto_id: int
    categoria_id: int
    es_principal: bool

    model_config = ConfigDict(from_attributes=True)
