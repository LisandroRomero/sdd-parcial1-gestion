from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)
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

    parent: Optional["Categoria"] = Relationship(
        back_populates="hijos",
        sa_relationship_kwargs={"remote_side": "Categoria.id"},
    )
    hijos: list["Categoria"] = Relationship(back_populates="parent")
    productos: list["ProductoCategoria"] = Relationship(back_populates="categoria")
