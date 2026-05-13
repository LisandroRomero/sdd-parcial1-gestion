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
from backend.direcciones.router import router as direcciones_router
from backend.ingredientes.router import router as ingredientes_router
from backend.pedidos.router import router as pedidos_router
from backend.productos.router import router as productos_router
from backend.usuarios.router import router as usuarios_router

sub_routers = [
    (auth_router, "/auth", "auth"),
    (usuarios_router, "/usuarios", "usuarios"),
    (categorias_router, "/categorias", "categorias"),
    (ingredientes_router, "/ingredientes", "ingredientes"),
    (productos_router, "/productos", "productos"),
    (direcciones_router, "/usuarios/me/direcciones", "direcciones"),
    (pedidos_router, "/pedidos", "pedidos"),
]
for sub_router, prefix, tag in sub_routers:
    router.include_router(sub_router, prefix=prefix, tags=[tag])
