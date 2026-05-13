from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.pedidos.model import Pedido
    from backend.usuarios.model import Usuario


class DireccionEntrega(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    alias: str = Field(max_length=50)
    calle: str = Field(max_length=100)
    numero: str = Field(max_length=20)
    piso: Optional[str] = Field(default=None, max_length=10)
    departamento: Optional[str] = Field(default=None, max_length=10)
    ciudad: str = Field(max_length=100)
    provincia: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=10)
    es_principal: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    usuario: "Usuario" = Relationship(back_populates="direcciones")
    pedidos: list["Pedido"] = Relationship(back_populates="direccion")
