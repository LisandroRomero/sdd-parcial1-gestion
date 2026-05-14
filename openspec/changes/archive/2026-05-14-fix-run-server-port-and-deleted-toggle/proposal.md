## Why

Se detectaron dos bugs en funcionalidades del change `admin-settings-and-configuration` (7.5) ya archivado. El primero impide cargar la página de configuración admin por un mismatch de puerto entre frontend y backend. El segundo impide que el toggle "Mostrar eliminados" en el panel admin de productos tenga efecto visual, porque el schema `ProductoRead` no serializa `deleted_at` y además el filtro `disponible=True` se aplica incluso cuando se piden eliminados. Se corrigen ambos para cumplir con las specs existentes.

## What Changes

1. **Bugfix `run_server.py`**: Cambiar `port=8000` → `port=8001` para que coincida con `VITE_API_BASE_URL=http://localhost:8001/api/v1` del frontend.
2. **Bugfix schema `ProductoRead`**: Agregar `deleted_at: Optional[datetime] = None` al schema Pydantic para que se serialice y el frontend pueda mostrar el badge "Eliminado".
3. **Bugfix repository `productos`**: No aplicar el filtro `disponible=True` cuando `include_deleted=True`, para que los productos eliminados (que pueden tener `disponible=false`) aparezcan en el listado.

## Capabilities

### New Capabilities
<!-- No se introducen nuevas capabilities. Es un bugfix sobre capabilities existentes. -->

### Modified Capabilities
<!-- No cambian requirements existentes. Se corrige implementación para cumplir con lo ya especificado. -->

## Impact

- `run_server.py`: cambio de 1 línea (port 8000 → 8001)
- `backend/productos/schemas.py`: agregar 1 campo a `ProductoRead`
- `backend/productos/repository.py`: modificar condición del filtro `disponible`
- Sin impacto en BD, migraciones, o frontend.
