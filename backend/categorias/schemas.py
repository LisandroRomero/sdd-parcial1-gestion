from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None


class CategoriaRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
