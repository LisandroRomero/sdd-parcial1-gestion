## Context

El componente `DireccionesList.tsx` usa early returns para manejar los estados de carga, error y vacío. Los modales `<DireccionFormModal>` y `<DeleteConfirmDialog>` están renderizados únicamente en el bloque "normal" (cuando hay direcciones). Esto provoca que, al estar en empty state y hacer clic en "Agregar dirección", el estado `isCreating = true` se setea pero el modal nunca se monta porque el componente re-evalúa el early return.

## Goals / Non-Goals

**Goals:**
- Que `<DireccionFormModal>` y `<DeleteConfirmDialog>` estén siempre en el árbol de React, independientemente del estado de los datos.
- Mantener el mismo comportamiento visual: skeletons en loading, error message en error, empty state con botón cuando no hay direcciones, grilla de cards cuando hay datos.

**Non-Goals:**
- No se cambia la lógica de negocio, ni los hooks, ni la API.
- No se modifica el estilo ni los componentes hijos.

## Decisions

- **Patrón de content variable:** Se asigna el contenido condicional a una variable (`content`) usando un ternario o IIFE, y se renderiza dentro de un `<></>` junto con los modales. Alternativa considerada: Fragment con modales al inicio y un bloque condicional después. Se prefiere la variable de contenido porque es más legible y evita duplicar los modales en cada branch.

- **No extraer a un subcomponente:** Se evaluó extraer el grid de direcciones a un subcomponente, pero el cambio es mínimo y no justifica una nueva abstracción.

## Risks / Trade-offs

- [Riesgo mínimo] Al estar los modales siempre montados, cualquier efecto secundario en su montaje se ejecutará siempre. Se verifica que `DireccionFormModal` y `DeleteConfirmDialog` no tienen efectos secundarios en `useEffect` que dependan de datos — solo renderizan según `isOpen`.
