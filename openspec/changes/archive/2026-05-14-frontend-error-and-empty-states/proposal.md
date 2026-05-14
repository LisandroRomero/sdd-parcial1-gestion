## Why

Hoy el frontend maneja estados de carga/vacio/error de forma dispareja entre pantallas, lo que genera UX inconsistente y dificulta aplicar patrones correctos con TanStack Query. Necesitamos un set compartido de estados y reglas de mapeo para que el comportamiento sea uniforme en toda la app.

## What Changes

- Se incorporan componentes compartidos para estados: loading, empty, error (inline), offline y no-permission.
- Se definen reglas de mapeo de errores (por tipo/status) y patrones recomendados para estados de TanStack Query en pantallas.
- Se reemplazan manejos ad-hoc en paginas clave (catalogo, detalle de producto, carrito, checkout, pedidos, perfil y paneles admin) por los componentes/reglas compartidas.

## Capabilities

### New Capabilities

- `frontend-ui-states`: Estandares de UX y componentes compartidos para estados de loading/empty/error/offline/no-permission en todas las superficies del frontend (incluye reglas de mapeo con TanStack Query).

### Modified Capabilities

<!-- None -->

## Impact

- Frontend: `frontend/src/shared/ui` (componentes base), paginas y features que consumen TanStack Query.
- Consistencia: unifica mensajes, CTAs y comportamiento de reintento.
- Dependencias: posible reutilizacion de helper existente `getErrorMessage` (si esta presente) y de guards/roles para no-permission.
