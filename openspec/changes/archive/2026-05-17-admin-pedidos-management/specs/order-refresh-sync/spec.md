## ADDED Requirements

### Requirement: Invalidación cruzada de queries al cambiar estado

Cuando un ADMIN o PEDIDOS cambia el estado de un pedido mediante `PATCH /{id}/estado` o `DELETE /{id}`, el sistema SHALL invalidar las queries de TanStack Query con keys `['pedido', pedidoId]` y `['pedidos']` para que cualquier vista activa (incluyendo la del usuario dueño del pedido) refetchee los datos actualizados.

#### Scenario: Admin cambia estado y cliente ve el cambio al refocusear

- **WHEN** un ADMIN cambia un pedido de CONFIRMADO a EN_PREP
- **THEN** el sistema invalida `['pedido', pedidoId]` y `['pedidos']` globalmente
- **AND** cuando el usuario CLIENT (dueño del pedido) refocusesa la ventana o la query alcanza su staleTime, la vista muestra el nuevo estado

### Requirement: Polling ligero en queries de pedidos

Las queries de listado de pedidos (`['pedidos', params]`) SHALL tener un `refetchInterval` de 30 segundos para detectar cambios realizados por otros usuarios sin necesidad de recarga manual.

#### Scenario: Pedidos se actualizan automáticamente cada 30s

- **WHEN** un usuario CLIENT está en la página de "Mis Pedidos" y un ADMIN cambia el estado de uno de sus pedidos
- **THEN** dentro de los siguientes 30 segundos, la lista del CLIENT se actualiza mostrando el nuevo estado

### Requirement: Sin efecto visual de recarga abrupta

El polling SHALL ser silencioso: `refetchInterval` con `refetchIntervalInBackground: false` para no consumir recursos cuando la pestaña no está activa. No SHALL mostrar indicadores de carga durante el refetch en segundo plano.

#### Scenario: Polling sin indicador de carga

- **WHEN** el refetchInterval se ejecuta en segundo plano
- **THEN** la UI no muestra skeletons ni spinners; los datos nuevos aparecen silenciosamente
