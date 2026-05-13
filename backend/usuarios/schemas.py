from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

from backend.direcciones.schemas import DireccionEntregaRead


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


class PerfilRead(BaseModel):
    """Full profile schema for the authenticated user, including roles and active addresses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: str
    telefono: Optional[str] = None
    roles: list[str] = []
    activo: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    direcciones: list[DireccionEntregaRead] = []

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_codes(cls, v: object) -> list[str]:
        if v and hasattr(next(iter(v), None), "rol_codigo"):
            return [ur.rol_codigo for ur in v]
        return list(v) if v else []

    @field_validator("direcciones", mode="before")
    @classmethod
    def filter_active_direcciones(cls, v: object) -> list:
        if v is None:
            return []
        return [d for d in v if getattr(d, "deleted_at", None) is None]


class PerfilUpdate(BaseModel):
    """Schema for updating the authenticated user's own profile.

    Only ``nombre``, ``apellido``, and ``telefono`` are editable.
    Email, password, and roles are intentionally excluded.
    """

    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None

    @field_validator("nombre", "apellido")
    @classmethod
    def reject_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v == "":
            raise ValueError("Este campo no puede ser una cadena vacía")
        return v
