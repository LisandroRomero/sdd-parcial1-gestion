## ADDED Requirements

### Requirement: Modal de creación siempre renderizado en el árbol de React
El sistema SHALL asegurar que el modal de creación/edición de direcciones (`DireccionFormModal`) esté siempre presente en el árbol de React, independientemente del estado de carga, error o datos vacíos del componente `DireccionesList`.

#### Scenario: Modal se abre desde empty state
- **WHEN** el usuario no tiene direcciones guardadas y hace clic en "Agregar dirección"
- **THEN** el modal de creación de dirección se muestra correctamente

#### Scenario: Modal se abre desde listado con direcciones
- **WHEN** el usuario tiene direcciones guardadas y hace clic en "Agregar dirección"
- **THEN** el modal de creación de dirección se muestra correctamente

#### Scenario: Modal de edición se abre desde cualquier estado
- **WHEN** el usuario hace clic en "Editar" sobre una dirección existente
- **THEN** el modal de edición de dirección se muestra correctamente

### Requirement: Confirmación de eliminación siempre renderizada en el árbol de React
El sistema SHALL asegurar que el diálogo de confirmación de eliminación (`DeleteConfirmDialog`) esté siempre presente en el árbol de React, independientemente del estado de los datos.

#### Scenario: Confirmación de eliminación desde listado con direcciones
- **WHEN** el usuario hace clic en "Eliminar" sobre una dirección
- **THEN** el diálogo de confirmación se muestra correctamente
