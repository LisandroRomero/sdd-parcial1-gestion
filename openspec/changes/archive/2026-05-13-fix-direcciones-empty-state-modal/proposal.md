## Why

El botón "Agregar dirección" en el estado vacío (sin direcciones guardadas) no abre el modal de creación porque los early returns del componente `DireccionesList.tsx` impiden que `<DireccionFormModal>` se monte en el árbol de React. Al hacer clic, se setea `isCreating = true`, pero el componente re-evalúa el early return del empty state y el modal nunca se renderiza.

## What Changes

- Refactor del componente `DireccionesList.tsx` para mover `<DireccionFormModal>` y `<DeleteConfirmDialog>` fuera de los early returns, asegurando que siempre estén montados en el árbol de React.
- Uso del patrón de asignar contenido condicional a una variable y renderizarlo junto a los modales en un `<></>` (Fragment).
- No hay cambios de API, schemas, lógica de negocio ni backend.

## Capabilities

### New Capabilities

- `fix-direcciones-empty-state-modal`: Corrección del bug en el frontend que impide abrir el modal de creación de direcciones cuando el usuario no tiene direcciones guardadas.

### Modified Capabilities

- `delivery-address-management`: No cambian requerimientos. Solo se modifica la implementación del componente React que consume la API existente.

## Impact

- **Código afectado:** `frontend/src/features/direcciones/components/DireccionesList.tsx`
- **Sin cambios en backend, schemas, API ni base de datos.**
- **Sin impacto en otras features.**
