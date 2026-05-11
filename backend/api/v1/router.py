from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# ── Health ──────────────────────────────────────────────────────────


@router.get("/health", response_model=dict[str, str])
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Feature routers ─────────────────────────────────────────────────
#
# Import each router as it is implemented.
#

from backend.auth.router import router as auth_router
from backend.categorias.router import router as categorias_router
from backend.ingredientes.router import router as ingredientes_router
from backend.usuarios.router import router as usuarios_router

sub_routers = [
    (auth_router, "/auth", "auth"),
    (usuarios_router, "/usuarios", "usuarios"),
    (categorias_router, "/categorias", "categorias"),
    (ingredientes_router, "/ingredientes", "ingredientes"),
]
for sub_router, prefix, tag in sub_routers:
    router.include_router(sub_router, prefix=prefix, tags=[tag])
