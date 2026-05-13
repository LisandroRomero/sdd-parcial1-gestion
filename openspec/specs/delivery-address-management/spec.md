### Requirement: Usuario puede crear una dirección de entrega
El sistema SHALL permitir a un usuario autenticado con rol CLIENT o ADMIN crear una nueva dirección de entrega asociada a su propio ID. La dirección requiere los campos: `alias`, `calle`, `numero`, `ciudad`, `provincia`, `codigo_postal`. Los campos `piso` y `departamento` son opcionales. El campo `es_principal` es opcional y por defecto `False`.

#### Scenario: Creación exitosa de dirección
- **WHEN** el usuario CLIENT envía POST `/api/v1/usuarios/me/direcciones` con campos requeridos válidos
- **THEN** el sistema crea la dirección con `usuario_id` del usuario autenticado y devuelve 201 con el objeto creado

#### Scenario: Creación con es_principal=True como primera dirección
- **WHEN** el usuario envía POST con `es_principal=True` y no tiene otras direcciones
- **THEN** el sistema crea la dirección con `es_principal=True` y devuelve 201

#### Scenario: Creación sin campos requeridos
- **WHEN** el usuario envía POST con campos requeridos faltantes (ej: sin `calle`)
- **THEN** el sistema devuelve 422 con detalle de validación

#### Scenario: Usuario no autenticado intenta crear dirección
- **WHEN** se envía POST sin token de autorización
- **THEN** el sistema devuelve 401

### Requirement: Usuario puede listar sus direcciones de entrega activas
El sistema SHALL devolver todas las direcciones de entrega del usuario autenticado que no tengan `deleted_at` (no eliminadas). Las direcciones eliminadas (soft delete) NO deben aparecer en el listado.

#### Scenario: Listado de direcciones activas
- **WHEN** el usuario autenticado envía GET `/api/v1/usuarios/me/direcciones`
- **THEN** el sistema devuelve 200 con lista de sus direcciones activas (excluye `deleted_at IS NOT NULL`)

#### Scenario: Listado cuando no hay direcciones
- **WHEN** el usuario autenticado no tiene ninguna dirección creada o todas fueron eliminadas
- **THEN** el sistema devuelve 200 con lista vacía `[]`

#### Scenario: Usuario no autenticado intenta listar
- **WHEN** se envía GET sin token de autorización
- **THEN** el sistema devuelve 401

### Requirement: Usuario puede actualizar una dirección propia
El sistema SHALL permitir al usuario autenticado actualizar campos de una dirección que le pertenece. Solo los campos incluidos en el body deben actualizarse (PATCH semántics aunque sea PUT). La dirección debe estar activa (no soft-deleted).

#### Scenario: Actualización exitosa de campos
- **WHEN** el usuario envía PUT `/api/v1/usuarios/me/direcciones/{id}` con campos válidos a actualizar
- **THEN** el sistema actualiza los campos y devuelve 200 con la dirección actualizada

#### Scenario: Intento de actualizar dirección de otro usuario
- **WHEN** el usuario autenticado envía PUT con un `{id}` que pertenece a otro usuario
- **THEN** el sistema devuelve 403

#### Scenario: Actualizar dirección inexistente o eliminada
- **WHEN** el usuario envía PUT con un `{id}` que no existe o fue soft-deleted
- **THEN** el sistema devuelve 404

### Requirement: Usuario puede eliminar (soft delete) una dirección propia
El sistema SHALL permitir al usuario autenticado eliminar una de sus direcciones estableciendo `deleted_at` a la fecha/hora actual. La dirección eliminada no debe aparecer en futuros listados.

#### Scenario: Soft delete exitoso
- **WHEN** el usuario envía DELETE `/api/v1/usuarios/me/direcciones/{id}` sobre una dirección propia activa
- **THEN** el sistema establece `deleted_at = now()` y devuelve 204 No Content

#### Scenario: Intento de eliminar dirección de otro usuario
- **WHEN** el usuario envía DELETE con `{id}` de dirección de otro usuario
- **THEN** el sistema devuelve 403

#### Scenario: Eliminar dirección ya eliminada o inexistente
- **WHEN** el usuario envía DELETE con `{id}` de dirección que no existe o ya fue eliminada
- **THEN** el sistema devuelve 404

### Requirement: Usuario puede marcar una dirección como principal
El sistema SHALL permitir al usuario autenticado designar una de sus direcciones activas como la principal. Al hacerlo, el sistema MUST establecer `es_principal=False` para todas las demás direcciones activas del mismo usuario de forma atómica, y luego `es_principal=True` para la dirección seleccionada.

#### Scenario: Marcar principal con éxito
- **WHEN** el usuario envía PATCH `/api/v1/usuarios/me/direcciones/{id}/principal` sobre una dirección activa propia
- **THEN** el sistema establece `es_principal=True` en la dirección target, `es_principal=False` en las demás del usuario, y devuelve 200 con la dirección actualizada

#### Scenario: Solo una dirección puede ser principal a la vez
- **WHEN** el usuario tiene 3 direcciones y marca la tercera como principal
- **THEN** las otras 2 deben quedar con `es_principal=False` y solo la tercera con `es_principal=True`

#### Scenario: Intento de marcar principal en dirección de otro usuario
- **WHEN** el usuario envía PATCH `/principal` con `{id}` de dirección ajena
- **THEN** el sistema devuelve 403

#### Scenario: Marcar principal en dirección inexistente o eliminada
- **WHEN** el usuario envía PATCH `/principal` con `{id}` inexistente o soft-deleted
- **THEN** el sistema devuelve 404

### Requirement: Ownership enforced en todas las operaciones
El sistema SHALL validar que el usuario autenticado es el dueño (`usuario_id` coincide) de la dirección antes de permitir cualquier operación de lectura individual, actualización, eliminación o marcado de principal. Esta validación MUST ocurrir en el service layer, no en el router.

#### Scenario: Validación de ownership en update
- **WHEN** cualquier operación de modificación es intentada sobre una dirección con `usuario_id != current_user.id`
- **THEN** el sistema devuelve 403 sin exponer información sobre la existencia del recurso (o 404 si el recurso directamente no existe)
