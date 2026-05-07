from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class DireccionEntregaCreate(BaseModel):
    usuario_id: int
    alias: str
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    codigo_postal: str
    es_principal: bool = False


class DireccionEntregaUpdate(BaseModel):
    alias: Optional[str] = None
    linea1: Optional[str] = None
    linea2: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    es_principal: Optional[bool] = None


class DireccionEntregaRead(BaseModel):
    id: int
    usuario_id: int
    alias: str
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    codigo_postal: str
    es_principal: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
