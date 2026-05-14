## MODIFIED Requirements

### Requirement: Listado de direcciones del usuario

El sistema SHALL mostrar en la página `/perfil` una sección "Mis Direcciones" que liste todas las direcciones activas del usuario obtenidas desde `GET /api/v1/usuarios/me/direcciones`, mostrando alias, calle, número, ciudad, provincia y un badge si es la dirección principal.

El hook `useDirecciones` SHALL ser exportable y reutilizable desde otras páginas/features (incluyendo checkout) para obtener el listado de direcciones del usuario.

#### Scenario: Listado con direcciones existentes

- **WHEN** el usuario tiene una o más direcciones activas
- **THEN** el sistema muestra cada dirección como una tarjeta con alias, dirección completa, indicador de principal, y botones de acción (editar, eliminar, marcar principal)

#### Scenario: Sin direcciones registradas

- **WHEN** el usuario no tiene ninguna dirección activa
- **THEN** el sistema muestra un estado vacío con mensaje "No tenés direcciones guardadas" y un botón "Agregar dirección"

#### Scenario: Indicador visual de dirección principal

- **WHEN** una dirección tiene `es_principal=true`
- **THEN** el sistema muestra un badge "Principal" destacado en esa tarjeta y deshabilita el botón "Marcar como principal" para esa dirección

### Requirement: Hook reutilizable useDirecciones

El frontend SHALL exportar el hook `useDirecciones` desde `frontend/src/features/direcciones/hooks/useDirecciones.ts` para que pueda ser importado por otras features (incluyendo checkout). El hook SHALL retornar `{ direcciones, isLoading, isError, refetch }`.

#### Scenario: Checkout consume useDirecciones

- **WHEN** la página de checkout importa y llama `useDirecciones()`
- **THEN** recibe el listado de direcciones del usuario con sus estados de carga y error
