from sqlmodel import SQLModel, Field, Relationship, PrimaryKeyConstraint
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional


class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True)
    es_alergeno: bool = Field(default=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"nullable": True},
    )

    productos: list["ProductoIngrediente"] = Relationship(back_populates="ingrediente")


class ProductoIngrediente(SQLModel, table=True):
    producto_id: int = Field(foreign_key="producto.id")
    ingrediente_id: int = Field(foreign_key="ingrediente.id")
    es_removible: bool = Field(default=False)

    __table_args__ = (PrimaryKeyConstraint("producto_id", "ingrediente_id"),)

    producto: "Producto" = Relationship(back_populates="ingredientes")
    ingrediente: "Ingrediente" = Relationship(back_populates="productos")
