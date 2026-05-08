## Why

El frontend carece de un sistema de estado del cliente. Actualmente no hay stores para manejar autenticación, carrito de compras, pagos ni estado de UI. Sin esta base, cualquier feature de frontend (login, carrito, checkout, panel) requiere resolver estado ad-hoc, duplicando lógica y generando inconsistencias. Este cambio instala y configura Zustand como gestor de estado del cliente, creando los 4 stores base que el resto del sistema va a consumir.

## What Changes

- Instalar `zustand` v4 como dependencia del frontend
- Crear `shared/lib/stores/` como directorio contenedor de stores
- Implementar `authStore`: estado de autenticación (token, usuario, `isAuthenticated`)
- Implementar `cartStore`: carrito de compras (items, cantidades, totales, personalización)
- Implementar `paymentStore`: estado de pagos (preferenceId, status, resultado)
- Implementar `uiStore`: estado de UI (sidebar, modales, preferencias)
- Agregar persistencia selectiva con `persist` middleware en `cartStore` y `uiStore`
- Agregar barrel export `stores/index.ts` para importaciones limpias

## Capabilities

### New Capabilities
- `client-state`: Gestión de estado del cliente con Zustand, incluyendo stores tipados, persistencia selectiva y suscripciones granulares

### Modified Capabilities
- *(none — no existing specs are changing)*

## Impact

- **Frontend**: `frontend/package.json` (nueva dependencia), `frontend/src/shared/lib/stores/` (4 stores nuevos + barrel)
- **Dependencias**: `zustand` v4 agregada a `dependencies`
- **No breaking**: los stores son nuevos, no reemplazan nada existente. Cero impacto en backend.
