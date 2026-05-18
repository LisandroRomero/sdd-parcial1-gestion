## ADDED Requirements

### Requirement: Mapa de transiciones admin centralizado en constants.ts

El sistema SHALL exportar desde `frontend/src/entities/pedidos/constants.ts` un mapa `ADMIN_TRANSITIONS: Record<string, string[]>` con las transiciones de estado válidas para roles ADMIN y PEDIDOS. Este mapa SHALL ser la única fuente de verdad para las transiciones visibles en el frontend admin.

El mapa SHALL contener:
- `PENDIENTE` → `["CONFIRMADO", "CANCELADO"]`
- `CONFIRMADO` → `["EN_PREP", "CANCELADO"]`
- `EN_PREP` → `["EN_CAMINO", "CANCELADO"]`
- `EN_CAMINO` → `["ENTREGADO"]`
- `ENTREGADO` → `[]`
- `CANCELADO` → `[]`

#### Scenario: Admin consulta transiciones desde constants
- **WHEN** un componente importa `ADMIN_TRANSITIONS` desde `constants.ts` con un estado `"PENDIENTE"`
- **THEN** obtiene `["CONFIRMADO", "CANCELADO"]`

#### Scenario: Estado terminal retorna array vacío
- **WHEN** se consulta `ADMIN_TRANSITIONS["ENTREGADO"]`
- **THEN** retorna `[]`

### Requirement: Función getAdminNextStates

El sistema SHALL exportar una función `getAdminNextStates(currentState: string): string[]` desde `constants.ts` que retorne los estados destino válidos para ADMIN según `ADMIN_TRANSITIONS`. Reemplaza a `getNextState` (que retornaba `string | null`).

#### Scenario: getAdminNextStates con PENDIENTE
- **WHEN** se llama a `getAdminNextStates("PENDIENTE")`
- **THEN** retorna `["CONFIRMADO", "CANCELADO"]`

#### Scenario: getAdminNextStates con estado terminal
- **WHEN** se llama a `getAdminNextStates("ENTREGADO")`
- **THEN** retorna `[]`

### Requirement: Eliminar FSM duplicada del detalle

El sistema SHALL eliminar la constante `ADMIN_TRANSITIONS` definida localmente en `AdminPedidoDetailPage.tsx` e importarla desde `frontend/src/entities/pedidos/constants.ts`.

#### Scenario: AdminPedidoDetailPage importa transiciones centralizadas
- **WHEN** `AdminPedidoDetailPage.tsx` renderiza el selector de estados
- **THEN** usa `getAdminNextStates(pedido.estado_actual)` importado desde `constants.ts`
