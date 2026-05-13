from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import math


class IngredienteCreate(BaseModel):
    nombre: str
    es_alergeno: bool = False


class IngredienteUpdate(BaseModel):
    nombre: Optional[str] = None
    es_alergeno: Optional[bool] = None


class IngredienteRead(BaseModel):
    id: int
    nombre: str
    es_alergeno: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IngredientePaginado(BaseModel):
    """Paginated response for ingredientes."""

    items: list[IngredienteRead]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(
        cls,
        items: list[IngredienteRead],
        total: int,
        page: int,
        size: int,
    ) -> "IngredientePaginado":
        pages = math.ceil(total / size) if size > 0 else 0
        return cls(items=items, total=total, page=page, size=size, pages=pages)


class ProductoIngredienteCreate(BaseModel):
    ingrediente_id: int
    cantidad: Optional[float] = None
    unidad: Optional[str] = None


class ProductoIngredienteRead(BaseModel):
    ingrediente_id: int
    nombre: str
    es_alergeno: bool
    cantidad: Optional[float]
    unidad: Optional[str]
    es_removible: bool

    model_config = ConfigDict(from_attributes=True)


class ProductoIngredienteListResponse(BaseModel):
    items: list[ProductoIngredienteRead]
    total: int
