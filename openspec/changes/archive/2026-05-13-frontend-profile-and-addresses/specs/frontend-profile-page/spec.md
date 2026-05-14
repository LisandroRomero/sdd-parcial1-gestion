## ADDED Requirements

### Requirement: Página de perfil con datos del cliente autenticado

El sistema SHALL proveer una página `/perfil` protegida (requiere autenticación con rol CLIENT o ADMIN) que muestre los datos personales del usuario autenticado obtenidos desde `GET /api/v1/usuarios/me/perfil`, incluyendo nombre, apellido, email y teléfono.

#### Scenario: Visualizar perfil con datos cargados exitosamente

- **WHEN** el usuario autenticado navega a `/perfil`
- **THEN** el sistema muestra un skeleton loader mientras carga, y luego renderiza el formulario con los datos precargados: nombre, apellido, email (solo lectura), teléfono, y fecha de registro

#### Scenario: Error al cargar perfil

- **WHEN** la petición `GET /api/v1/usuarios/me/perfil` falla (error de red o 500)
- **THEN** el sistema muestra un mensaje de error con opción de reintentar

#### Scenario: Usuario no autenticado intenta acceder

- **WHEN** un usuario no autenticado navega a `/perfil`
- **THEN** el sistema redirige a `/login`

### Requirement: Edición de datos personales del perfil

El sistema SHALL permitir al usuario autenticado editar su nombre, apellido y teléfono mediante un formulario que envía `PUT /api/v1/usuarios/me/perfil`. El email NO es editable desde esta pantalla y se muestra como campo de solo lectura.

#### Scenario: Edición exitosa con todos los campos

- **WHEN** el usuario completa nombre, apellido y teléfono válidos y presiona "Guardar cambios"
- **THEN** el sistema envía `PUT /api/v1/usuarios/me/perfil`, muestra un toast de "Datos actualizados correctamente", y actualiza los datos mostrados en el formulario

#### Scenario: Edición parcial (solo un campo)

- **WHEN** el usuario modifica solo el teléfono y presiona "Guardar cambios"
- **THEN** el sistema actualiza solo el teléfono y el resto de los campos permanecen sin cambios

#### Scenario: Validación de nombre vacío

- **WHEN** el usuario intenta guardar con nombre vacío
- **THEN** el sistema muestra error de validación "El nombre es obligatorio" y no envía la petición

#### Scenario: Validación de apellido vacío

- **WHEN** el usuario intenta guardar con apellido vacío
- **THEN** el sistema muestra error de validación "El apellido es obligatorio" y no envía la petición

#### Scenario: Error en actualización

- **WHEN** la petición `PUT /api/v1/usuarios/me/perfil` falla
- **THEN** el sistema muestra un toast de error con el mensaje del servidor

### Requirement: Estado de carga y skeleton en perfil

El sistema SHALL mostrar un estado de carga visual (skeleton) mientras se obtienen los datos del perfil, y un estado vacío coherente si el usuario no tiene datos (caso borde).

#### Scenario: Skeleton durante carga

- **WHEN** la petición de perfil está en curso
- **THEN** el sistema muestra placeholders animados (skeleton) simulando la estructura del formulario
