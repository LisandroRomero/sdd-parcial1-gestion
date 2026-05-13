from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ProductoCreate(BaseModel):
    codigo_sku: str
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal = Field(gt=0)
    stock_cantidad: int = 0
    disponible: bool = True
    imagen_url: Optional[str] = None
    categoria_ids: list[int] = []

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
    precio_base: Optional[Decimal] = Field(default=None, gt=0)
    stock_cantidad: Optional[int] = None
    disponible: Optional[bool] = None
    imagen_url: Optional[str] = None
    categoria_ids: Optional[list[int]] = None

    @field_validator("stock_cantidad")
    @classmethod
    def stock_no_negativo(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("stock_cantidad must be >= 0")
        return v


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


class StockUpdate(BaseModel):
    stock_cantidad: int

    @field_validator("stock_cantidad")
    @classmethod
    def stock_no_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("stock_cantidad must be >= 0")
        return v


class DisponibilidadUpdate(BaseModel):
    disponible: bool


class ProductoPaginado(BaseModel):
    items: list[ProductoRead]
    total: int
    page: int
    size: int
    pages: int


class ProductoCategoriaCreate(BaseModel):
    producto_id: int
    categoria_id: int
    es_principal: bool = False


class ProductoCategoriaRead(BaseModel):
    producto_id: int
    categoria_id: int
    es_principal: bool

    model_config = ConfigDict(from_attributes=True)
