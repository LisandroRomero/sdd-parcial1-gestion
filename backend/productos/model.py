from sqlmodel import SQLModel, Field, Relationship, PrimaryKeyConstraint
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from decimal import Decimal
from typing import Optional


class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_sku: str = Field(max_length=50, unique=True)
    nombre: str = Field(max_length=200)
    descripcion: Optional[str] = Field(default=None)
    precio_base: Decimal = Field(max_digits=10, decimal_places=2)
    stock_cantidad: int = Field(default=0)
    disponible: bool = Field(default=True)
    imagen_url: Optional[str] = Field(default=None, max_length=500)
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

    categorias: list["ProductoCategoria"] = Relationship(back_populates="producto")
    ingredientes: list["ProductoIngrediente"] = Relationship(back_populates="producto")
    detalles_pedido: list["DetallePedido"] = Relationship(back_populates="producto")


class ProductoCategoria(SQLModel, table=True):
    producto_id: int = Field(foreign_key="producto.id")
    categoria_id: int = Field(foreign_key="categoria.id")
    es_principal: bool = Field(default=False)

    __table_args__ = (PrimaryKeyConstraint("producto_id", "categoria_id"),)

    producto: "Producto" = Relationship(back_populates="categorias")
    categoria: "Categoria" = Relationship(back_populates="productos")
