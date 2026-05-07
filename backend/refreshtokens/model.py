from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional


class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token_hash: str = Field(max_length=64, unique=True, index=True)
    usuario_id: int = Field(foreign_key="usuario.id")
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))
    revoked_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )

    usuario: "Usuario" = Relationship(back_populates="refresh_tokens")
