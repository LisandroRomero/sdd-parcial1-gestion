from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from decimal import Decimal
from typing import Optional


class FormaPago(SQLModel, table=True):
    codigo: str = Field(max_length=20, primary_key=True)
    descripcion: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )

    pedidos: list["Pedido"] = Relationship(back_populates="forma_pago")


class Pago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    mp_payment_id: Optional[int] = Field(default=None, unique=True)
    mp_status: Optional[str] = Field(default=None, max_length=30)
    external_reference: Optional[str] = Field(default=None, unique=True, max_length=255)
    idempotency_key: Optional[str] = Field(default=None, unique=True, max_length=255)
    monto: Decimal = Field(max_digits=10, decimal_places=2)
    moneda: str = Field(default="ARS", max_length=3)
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

    pedido: "Pedido" = Relationship(back_populates="pagos")
