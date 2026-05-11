from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None

    @field_validator("parent_id")
    @classmethod
    def parent_id_must_not_be_self(cls, v: Optional[int]) -> Optional[int]:
        # At schema-level we can't know the id yet — self-reference equality
        # (parent_id == id) is validated at service level where both are known.
        return v


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None

    @field_validator("parent_id")
    @classmethod
    def parent_id_must_not_be_self(cls, v: Optional[int]) -> Optional[int]:
        # Actual self-reference check (parent_id == categoria.id) is performed
        # at service level where both values are known.
        return v


class CategoriaRead(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CategoriaTree(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    hijos: list["CategoriaTree"] = []

    model_config = ConfigDict(from_attributes=True)


CategoriaTree.model_rebuild()
