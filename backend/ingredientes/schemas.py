from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


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


class ProductoIngredienteCreate(BaseModel):
    producto_id: int
    ingrediente_id: int
    es_removible: bool = False


class ProductoIngredienteRead(BaseModel):
    producto_id: int
    ingrediente_id: int
    es_removible: bool

    model_config = ConfigDict(from_attributes=True)
