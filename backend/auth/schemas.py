from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Schema for user registration request body."""

    nombre: str
    apellido: str
    email: EmailStr
    password: str

    @field_validator("nombre", "apellido")
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Debe tener al menos 2 caracteres")
        if len(v) > 80:
            raise ValueError("Debe tener máximo 80 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class LoginRequest(BaseModel):
    """Schema for user login request body."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class TokenResponse(BaseModel):
    """Schema for the token pair returned after a successful login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Schema for the refresh token request body."""

    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("refresh_token no puede estar vacío")
        return v


class UserResponse(BaseModel):
    """Schema for user data returned after registration."""

    id: int
    nombre: str | None = None
    apellido: str | None = None
    email: str
    roles: list[str] = []
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_codes(cls, v: object) -> list[str]:
        if v and hasattr(v[0], "rol_codigo"):
            return [ur.rol_codigo for ur in v]
        return list(v) if v else []
