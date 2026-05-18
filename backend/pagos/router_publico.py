from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from backend.core.database import get_session
from backend.pagos.model import FormaPago

formas_pago_router = APIRouter()


class FormaPagoRead(BaseModel):
    codigo: str
    descripcion: str | None = None
    activo: bool = True

    model_config = ConfigDict(from_attributes=True)


@formas_pago_router.get(
    "/",
    response_model=list[FormaPagoRead],
    summary="List all active payment methods",
)
def listar_formas_pago(
    session: Session = Depends(get_session),
) -> list[FormaPagoRead]:
    """Return all active payment methods (FormaPago)."""
    formas = session.query(FormaPago).filter(FormaPago.activo == True).all()
    return [FormaPagoRead.model_validate(f) for f in formas]
