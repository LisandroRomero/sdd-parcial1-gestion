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
    producto_id: int
    ingrediente_id: int
    es_removible: bool = False


class ProductoIngredienteRead(BaseModel):
    producto_id: int
    ingrediente_id: int
    es_removible: bool

    model_config = ConfigDict(from_attributes=True)
