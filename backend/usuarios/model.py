from sqlmodel import SQLModel, Field, Relationship, PrimaryKeyConstraint
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=254, unique=True, index=True)
    password_hash: str = Field(max_length=60)
    nombre: Optional[str] = Field(default=None, max_length=100)
    apellido: Optional[str] = Field(default=None, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    activo: bool = Field(default=True)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )
    deleted_at: Optional[datetime] = Field(default=None)

    roles: list["UsuarioRol"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"},
    )
    roles_asignados: list["UsuarioRol"] = Relationship(
        back_populates="asignado_por",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.asignado_por_id"},
    )
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="usuario")
    direcciones: list["DireccionEntrega"] = Relationship(back_populates="usuario")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")


class Rol(SQLModel, table=True):
    codigo: str = Field(max_length=20, primary_key=True)
    descripcion: Optional[str] = Field(default=None)

    usuarios: list["UsuarioRol"] = Relationship(back_populates="rol")


class UsuarioRol(SQLModel, table=True):
    usuario_id: int = Field(foreign_key="usuario.id")
    rol_codigo: str = Field(max_length=20, foreign_key="rol.codigo")
    asignado_por_id: Optional[int] = Field(default=None, foreign_key="usuario.id")

    __table_args__ = (PrimaryKeyConstraint("usuario_id", "rol_codigo"),)

    usuario: "Usuario" = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.usuario_id"},
    )
    rol: "Rol" = Relationship(back_populates="usuarios")
    asignado_por: Optional["Usuario"] = Relationship(
        back_populates="roles_asignados",
        sa_relationship_kwargs={"foreign_keys": "UsuarioRol.asignado_por_id"},
    )
