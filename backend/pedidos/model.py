from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import ARRAY, Column, DateTime, Integer, func
from datetime import datetime
from decimal import Decimal
from typing import Optional


class EstadoPedido(SQLModel, table=True):
    codigo: str = Field(max_length=20, primary_key=True)
    descripcion: Optional[str] = Field(default=None)
    es_terminal: bool = Field(default=False)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )

    pedidos: list["Pedido"] = Relationship(back_populates="estado")
    historiales_desde: list["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_desde_rel",
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_desde"},
    )
    historiales_hasta: list["HistorialEstadoPedido"] = Relationship(
        back_populates="estado_hasta_rel",
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_hasta"},
    )


class Pedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    forma_pago_codigo: Optional[str] = Field(default=None, max_length=20, foreign_key="formapago.codigo")
    direccion_id: int = Field(foreign_key="direccionentrega.id")
    estado_actual: str = Field(max_length=20, foreign_key="estadopedido.codigo")
    total: Decimal = Field(max_digits=10, decimal_places=2, default=0)
    costo_envio: Decimal = Field(max_digits=10, decimal_places=2, default=0)
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

    usuario: "Usuario" = Relationship(back_populates="pedidos")
    forma_pago: "FormaPago" = Relationship(back_populates="pedidos")
    direccion: "DireccionEntrega" = Relationship(back_populates="pedidos")
    estado: "EstadoPedido" = Relationship(back_populates="pedidos")
    detalles: list["DetallePedido"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    historial_estados: list["HistorialEstadoPedido"] = Relationship(
        back_populates="pedido",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    pagos: list["Pago"] = Relationship(back_populates="pedido")

    @property
    def cantidad_items(self) -> int:
        return len(self.detalles) if self.detalles else 0


class DetallePedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    producto_id: int = Field(foreign_key="producto.id")
    nombre_snapshot: str = Field(max_length=200)
    precio_snapshot: Decimal = Field(max_digits=10, decimal_places=2)
    cantidad: int = Field(default=1)
    personalizacion: Optional[list[int]] = Field(
        default=None, sa_column=Column(ARRAY(Integer))
    )
    subtotal: Decimal = Field(max_digits=10, decimal_places=2, default=0)

    pedido: "Pedido" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_pedido")


class HistorialEstadoPedido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id")
    estado_desde: Optional[str] = Field(
        default=None, max_length=20, foreign_key="estadopedido.codigo"
    )
    estado_hasta: str = Field(max_length=20, foreign_key="estadopedido.codigo")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    motivo: Optional[str] = Field(default=None, max_length=255)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )

    pedido: "Pedido" = Relationship(back_populates="historial_estados")
    estado_desde_rel: Optional["EstadoPedido"] = Relationship(
        back_populates="historiales_desde",
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_desde"},
    )
    estado_hasta_rel: "EstadoPedido" = Relationship(
        back_populates="historiales_hasta",
        sa_relationship_kwargs={"foreign_keys": "HistorialEstadoPedido.estado_hasta"},
    )
    usuario: Optional["Usuario"] = Relationship(back_populates="historial_estados_pedido")
