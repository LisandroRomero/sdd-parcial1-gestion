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

### Requirement: Crear nueva dirección

El sistema SHALL proveer un formulario modal para crear una nueva dirección mediante `POST /api/v1/usuarios/me/direcciones`, con los campos: alias (opcional), calle, número, piso (opcional), departamento (opcional), ciudad, provincia, código postal.

#### Scenario: Creación exitosa

- **WHEN** el usuario completa el formulario con campos válidos y confirma
- **THEN** el sistema envía `POST`, muestra toast de "Dirección agregada", cierra el modal y agrega la nueva dirección al listado

#### Scenario: Validación de campos requeridos

- **WHEN** el usuario intenta crear sin completar calle, número, ciudad, provincia o código postal
- **THEN** el sistema muestra errores de validación por campo y no envía la petición

#### Scenario: Creación como primera dirección (es_principal automático)

- **WHEN** el usuario no tiene direcciones y crea la primera
- **THEN** el sistema la crea con `es_principal=True` automáticamente (comportamiento del backend)

### Requirement: Editar dirección existente

El sistema SHALL permitir editar una dirección existente mediante un modal precargado que envía `PUT /api/v1/usuarios/me/direcciones/{id}`.

#### Scenario: Edición exitosa

- **WHEN** el usuario modifica campos de una dirección y confirma
- **THEN** el sistema envía `PUT`, muestra toast de "Dirección actualizada", y actualiza los datos en el listado

#### Scenario: Intentar editar dirección de otro usuario

- **WHEN** ocurre un escenario de forbidden (no debería pasar por diseño)
- **THEN** el sistema muestra toast de error "No tenés permisos para modificar esta dirección"

### Requirement: Eliminar dirección (soft delete)

El sistema SHALL permitir eliminar una dirección mediante `DELETE /api/v1/usuarios/me/direcciones/{id}` con confirmación previa del usuario.

#### Scenario: Eliminación exitosa

- **WHEN** el usuario confirma la eliminación en el diálogo de confirmación
- **THEN** el sistema envía `DELETE`, muestra toast de "Dirección eliminada" y remueve la dirección del listado

#### Scenario: Cancelar eliminación

- **WHEN** el usuario abre el diálogo de confirmación y luego cancela
- **THEN** el sistema no envía ninguna petición y el listado permanece sin cambios

### Requirement: Marcar dirección como principal

El sistema SHALL permitir al usuario marcar una dirección como principal mediante `PATCH /api/v1/usuarios/me/direcciones/{id}/principal`, actualizando el indicador visual de forma optimista.

#### Scenario: Marcar principal exitosamente

- **WHEN** el usuario hace clic en "Marcar como principal" en una dirección no principal
- **THEN** el sistema envía `PATCH`, actualiza el badge "Principal" a la dirección seleccionada y lo remueve de la anterior, con toast de confirmación

#### Scenario: Marcar principal con error

- **WHEN** la petición `PATCH` falla
- **THEN** el sistema revierte el cambio visual (rollback optimista) y muestra toast de error

### Requirement: Estados de carga y error en sección de direcciones

El sistema SHALL manejar estados de carga (skeleton) y error en la sección de direcciones, manteniendo independencia de la sección de perfil.

#### Scenario: Skeleton durante carga de direcciones

- **WHEN** la petición de listado de direcciones está en curso
- **THEN** el sistema muestra skeletons de tarjetas de dirección

#### Scenario: Error al cargar direcciones

- **WHEN** la petición `GET /api/v1/usuarios/me/direcciones` falla
- **THEN** el sistema muestra mensaje de error en la sección de direcciones con botón de reintentar, sin afectar la sección de perfil

### Requirement: Modal de creación/edición siempre renderizado en el árbol de React

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

### Requirement: Hook reutilizable useDirecciones

El frontend SHALL exportar el hook `useDirecciones` desde `frontend/src/features/direcciones/hooks/useDirecciones.ts` para que pueda ser importado por otras features (incluyendo checkout). El hook SHALL retornar `{ direcciones, isLoading, isError, refetch }`.

#### Scenario: Checkout consume useDirecciones

- **WHEN** la página de checkout importa y llama `useDirecciones()`
- **THEN** recibe el listado de direcciones del usuario con sus estados de carga y error
