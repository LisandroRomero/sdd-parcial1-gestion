from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UsuarioAdminRead(BaseModel):
    """Full representation of a user as seen by an admin."""

    id: int
    nombre: Optional[str]
    apellido: Optional[str]
    email: str
    activo: bool
    roles: list[str]
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioAdminUpdate(BaseModel):
    """Partial update for a user's profile data and/or role list."""

    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    roles: Optional[list[str]] = None


class EstadoUsuarioUpdate(BaseModel):
    """Toggle a user's active state."""

    activo: bool


class UsuarioAdminListRead(BaseModel):
    """Paginated list of users for the admin panel."""

    items: list[UsuarioAdminRead]
    total: int
    page: int
    size: int
    pages: int


class FormaPagoRead(BaseModel):
    """Forma de pago as seen by an admin."""

    codigo: str
    descripcion: Optional[str] = None
    activo: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FormaPagoUpdate(BaseModel):
    """Toggle a payment method's active state."""

    activo: bool
