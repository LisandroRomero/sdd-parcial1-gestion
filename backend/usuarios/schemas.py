from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, model_validator
from datetime import datetime
from typing import Optional


class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if v is not None and len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UsuarioRead(BaseModel):
    id: int
    email: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RolCreate(BaseModel):
    codigo: str
    descripcion: Optional[str] = None


class RolRead(BaseModel):
    codigo: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UsuarioRolCreate(BaseModel):
    usuario_id: int
    rol_codigo: str


class UsuarioRolRead(BaseModel):
    usuario_id: int
    rol_codigo: str
    asignado_por_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


_VALID_ROLES = {"ADMIN", "STOCK", "PEDIDOS", "CLIENT"}


class AssignRolesRequest(BaseModel):
    """Schema for replacing a user's full set of roles."""

    roles: list[str]

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("La lista de roles no puede estar vacía")
        invalid = set(v) - _VALID_ROLES
        if invalid:
            raise ValueError(
                f"Roles inválidos: {', '.join(sorted(invalid))}. "
                f"Los valores válidos son: {', '.join(sorted(_VALID_ROLES))}"
            )
        return v
