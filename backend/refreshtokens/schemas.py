from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class RefreshTokenCreate(BaseModel):
    token_hash: str
    usuario_id: int
    expires_at: datetime


class RefreshTokenRead(BaseModel):
    id: int
    usuario_id: int
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
