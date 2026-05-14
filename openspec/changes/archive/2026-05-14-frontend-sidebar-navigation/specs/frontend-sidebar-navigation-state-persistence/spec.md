## ADDED Requirements

### Requirement: Sidebar collapsed state MAY be persisted locally
Si el sistema implementa modo colapsado, el estado colapsada/expandida MAY persistirse localmente para restaurar la preferencia del usuario al recargar.

#### Scenario: Persist collapsed state when user toggles collapse
- **WHEN** el usuario alterna el colapso de la sidebar en desktop
- **THEN** el sistema MAY persistir la preferencia en almacenamiento local (ej. `localStorage`)

#### Scenario: Restore collapsed state on reload
- **WHEN** el usuario recarga la aplicacion
- **THEN** si existe una preferencia persistida, la sidebar MAY inicializarse en ese estado

### Requirement: Persistence key SHALL be stable
La key usada para persistir el estado SHALL ser estable para evitar perder preferencia entre deploys.

#### Scenario: Same key is used across sessions
- **WHEN** el sistema guarda el estado en almacenamiento local
- **THEN** SHALL usar una key constante (ej. `ui.sidebar.collapsed`) de forma consistente
