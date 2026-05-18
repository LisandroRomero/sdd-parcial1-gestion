## ADDED Requirements

### Requirement: Menú de acciones con transiciones múltiples desde tabla

El menú desplegable de acciones en la tabla SHALL mostrar "Avanzar estado" como opción cuando `getAdminNextStates()` retorne un array no vacío. Al hacer clic, SHALL mostrar un selector inline con las opciones disponibles en lugar de asumir un único estado destino.

#### Scenario: Menú muestra Avanzar estado para PENDIENTE
- **WHEN** el admin abre el menú de acciones de un pedido en PENDIENTE
- **THEN** "Avanzar estado" aparece como opción, y al hacer clic se despliega un selector con CONFIRMADO y CANCELADO

#### Scenario: Menú oculta Avanzar estado para ENTREGADO
- **WHEN** el admin abre el menú de acciones de un pedido en ENTREGADO
- **THEN** la opción "Avanzar estado" no se muestra (`getAdminNextStates("ENTREGADO")` es `[]`)
