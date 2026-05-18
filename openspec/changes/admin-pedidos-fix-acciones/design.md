## Context

El módulo admin de pedidos tiene lógica FSM duplicada:
- `frontend/src/entities/pedidos/constants.ts`: `FSM_TRANSITIONS` (Record<string,string>), lineal, no incluye PENDIENTE.
- `frontend/src/pages/admin/AdminPedidoDetailPage.tsx`: `ADMIN_TRANSITIONS` (Record<string,string[]>), completa con PENDIENTE y múltiples destinos.

Esto causa 3 bugs: (1) no hay acciones para PENDIENTE en la tabla, (2) inconsistencia entre tabla y detalle, (3) la tabla solo permite avance lineal.

## Goals / Non-Goals

**Goals:**
- Centralizar `ADMIN_TRANSITIONS` en `constants.ts` como fuente única de verdad.
- Refactor `AdminPedidosPage.tsx` para ofrecer selector de estado destino (múltiples opciones) en lugar de avance fijo.
- Refactor `AdminPedidoDetailPage.tsx` para que importe desde `constants.ts`.
- Sincronizar la FSM del frontend con la del backend (`TRANSICIONES_VALIDAS` en `service.py`), mostrando al ADMIN las transiciones que su rol puede ejecutar.

**Non-Goals:**
- No se modifica la validación del backend (ya es correcta).
- No se agregan nuevos roles ni nuevas transiciones.
- No se toca la lógica de cancelación ni el modal de motivo.

## Decisions

1. **Exportar `ADMIN_TRANSITIONS` desde `constants.ts`** como `Record<string, string[]>` en lugar del actual `Record<string, string>`. Cada estado origen mapea a un array de estados destino válidos para ADMIN.
2. **Renombrar `getNextState` a `getAdminNextStates`** que retorna `string[]` (el array de destinos) en lugar de `string | null`. Para estados terminales o sin transiciones retorna `[]`.
3. **En `AdminPedidosPage.tsx`**: cuando el usuario hace clic en "Avanzar estado", mostrar un mini-selector inline (como ya hace el detalle) en lugar de una única opción fija. Extraer la UI del selector a un componente compartido o mantener inline para mantener simplicidad.
4. **No crear componente compartido** por ahora — el patrón de inline row en la tabla y el select en el detalle son lo suficientemente diferentes como para que un componente compartido agregue abstracción innecesaria. Si aparece un tercer consumidor, se refactoriza.
5. **Mantener compatibilidad** con `AdminPedidosPage`: la mutación `advanceMutation` ya acepta `nuevoEstado` dinámico, solo falta pasar el estado seleccionado.

## Risks / Trade-offs

- **Riesgo: La tabla se vuelve más compleja visualmente** al agregar un selector inline por fila. → Mitigación: solo se muestra al hacer clic en "Avanzar estado" (accordion inline), no siempre visible.
- **Riesgo: ADMIN_TRANSITIONS en frontend puede desincronizarse del backend.** → Mitigación: documentar en el código que `ADMIN_TRANSITIONS` debe reflejar `TRANSICIONES_VALIDAS` del backend, filtrado por rol ADMIN y PEDIDOS. Agregar comentario con link a `backend/pedidos/service.py`.
