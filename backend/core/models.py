from __future__ import annotations

# Import all SQLModel table models so SQLAlchemy's mapper registry is fully
# populated before any query runs. Forward references in Relationship()
# declarations (e.g. "RefreshToken", "Pedido") require every referenced class
# to be imported at startup — otherwise the mapper raises InvalidRequestError.
import backend.admin.model  # noqa: F401
import backend.auth.model  # noqa: F401
import backend.categorias.model  # noqa: F401
import backend.direcciones.model  # noqa: F401
import backend.ingredientes.model  # noqa: F401
import backend.pagos.model  # noqa: F401
import backend.pedidos.model  # noqa: F401
import backend.productos.model  # noqa: F401
import backend.refreshtokens.model  # noqa: F401
import backend.usuarios.model  # noqa: F401
