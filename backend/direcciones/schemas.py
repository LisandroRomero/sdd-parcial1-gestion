from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DireccionEntregaCreate(BaseModel):
    """Schema for creating a delivery address.

    Note: ``usuario_id`` is intentionally absent — it comes from the JWT token,
    not from the request body.
    """

    alias: str
    calle: str
    numero: str
    piso: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: str
    provincia: str
    codigo_postal: str
    es_principal: bool = False


class DireccionEntregaUpdate(BaseModel):
    """Schema for partial update (PATCH semantics) of a delivery address.

    All fields are optional — only provided fields are applied.
    """

    alias: Optional[str] = None
    calle: Optional[str] = None
    numero: Optional[str] = None
    piso: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: Optional[bool] = None


class DireccionEntregaRead(BaseModel):
    """Full output schema for a delivery address."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    alias: str
    calle: str
    numero: str
    piso: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: str
    provincia: str
    codigo_postal: str
    es_principal: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
