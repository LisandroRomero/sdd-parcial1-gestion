from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional


class DireccionEntrega(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    alias: str = Field(max_length=50)
    linea1: str = Field(max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=20)
    es_principal: bool = Field(default=False)
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

    usuario: "Usuario" = Relationship(back_populates="direcciones")
    pedidos: list["Pedido"] = Relationship(back_populates="direccion")
