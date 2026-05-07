from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# ── Health ──────────────────────────────────────────────────────────


@router.get("/health", response_model=dict[str, str])
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Feature routers (stubs) ────────────────────────────────────────
# Uncomment each line once the corresponding router module is implemented.
#
# from backend.auth.router import router as auth_router
# from backend.usuarios.router import router as usuarios_router
# from backend.productos.router import router as productos_router
# from backend.categorias.router import router as categorias_router
# from backend.ingredientes.router import router as ingredientes_router
# from backend.pedidos.router import router as pedidos_router
# from backend.pagos.router import router as pagos_router
# from backend.direcciones.router import router as direcciones_router
#
# sub_routers = [
#     (auth_router, "/auth", "auth"),
#     (usuarios_router, "/usuarios", "usuarios"),
#     (productos_router, "/productos", "productos"),
#     (categorias_router, "/categorias", "categorias"),
#     (ingredientes_router, "/ingredientes", "ingredientes"),
#     (pedidos_router, "/pedidos", "pedidos"),
#     (pagos_router, "/pagos", "pagos"),
#     (direcciones_router, "/direcciones", "direcciones"),
# ]
# for sub_router, prefix, tag in sub_routers:
#     router.include_router(sub_router, prefix=prefix, tags=[tag])
