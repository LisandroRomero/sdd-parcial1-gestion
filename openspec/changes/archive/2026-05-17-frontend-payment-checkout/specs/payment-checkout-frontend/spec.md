## ADDED Requirements

### Requirement: Visualizar formas de pago activas en checkout
El sistema SHALL obtener y mostrar las formas de pago activas desde un endpoint público en el checkout. El usuario SHALL poder seleccionar una forma de pago antes de confirmar el pedido.

#### Scenario: Checkout carga formas de pago activas
- **WHEN** el usuario accede al checkout y las formas de pago activas se cargan exitosamente desde `GET /api/v1/pagos/formas-pago`
- **THEN** se muestran como opciones seleccionables (radio buttons) en el formulario de checkout

#### Scenario: El admin deshabilita una forma de pago
- **WHEN** el admin deshabilita una forma de pago en el backend
- **THEN** esa forma de pago deja de aparecer en las opciones del checkout

#### Scenario: Error al cargar formas de pago
- **WHEN** ocurre un error al cargar las formas de pago desde el endpoint
- **THEN** se muestran opciones por defecto con solo "EFECTIVO" como forma de pago seleccionable

### Requirement: Crear pedido con forma de pago seleccionada
El sistema SHALL crear el pedido usando la forma de pago que el usuario seleccionó. SHALL almacenar `forma_pago_codigo` correctamente en el pedido.

#### Scenario: Usuario selecciona EFECTIVO y confirma
- **WHEN** el usuario selecciona "EFECTIVO" como forma de pago y confirma el pedido
- **THEN** el pedido se crea con `forma_pago_codigo="EFECTIVO"` y se redirige a la pantalla de confirmación sin ejecutar pago

#### Scenario: Usuario selecciona MERCADOPAGO y confirma
- **WHEN** el usuario selecciona "MERCADOPAGO" como forma de pago y confirma el pedido
- **THEN** el pedido se crea con `forma_pago_codigo="MERCADOPAGO"` y se muestra el formulario de tokenización de tarjeta

### Requirement: Tokenizar tarjeta con SDK de MercadoPago
Si el usuario selecciona MERCADOPAGO, el sistema SHALL mostrar el formulario de tokenización de tarjeta provisto por `@mercadopago/sdk-react` después de crear el pedido. El formulario SHALL utilizar `VITE_MP_PUBLIC_KEY` para inicializar el SDK.

#### Scenario: Usuario ingresa datos de tarjeta válidos
- **WHEN** el usuario ingresa datos de tarjeta válidos en el formulario de tokenización
- **THEN** el SDK genera un `card_token` exitosamente y se procede a ejecutar el pago contra el backend

#### Scenario: Usuario ingresa datos inválidos
- **WHEN** el usuario ingresa datos de tarjeta inválidos en el formulario de tokenización
- **THEN** el SDK muestra un error de validación y el usuario puede corregir los datos

#### Scenario: Usuario cancela el pago
- **WHEN** el usuario hace clic en "Cancelar" durante el flujo de tokenización
- **THEN** puede volver al checkout sin crear un pago y sin perder el pedido creado

### Requirement: Ejecutar pago contra backend
El sistema SHALL llamar a `POST /api/v1/pagos/crear` con `pedido_id`, `card_token`, `payment_method_id` y `monto` para ejecutar el pago. SHALL actualizar el paymentStore según el resultado.

#### Scenario: Pago aprobado
- **WHEN** el backend responde con `estado="aprobado"` en `POST /api/v1/pagos/crear`
- **THEN** `paymentStore.setApproved(paymentId)` se ejecuta y se muestra una pantalla de éxito con el ID del pago

#### Scenario: Pago rechazado
- **WHEN** el backend responde con `estado="rechazado"` en `POST /api/v1/pagos/crear`
- **THEN** `paymentStore.setRejected(error)` se ejecuta, se muestra el mensaje de error al usuario y se permite reintentar con una nueva tarjeta

#### Scenario: Error de red al llamar al backend
- **WHEN** ocurre un error de red al llamar a `POST /api/v1/pagos/crear`
- **THEN** se muestra un mensaje de error con una opción de reintentar el pago

### Requirement: Mostrar resultado del pago en OrderConfirmation
El sistema SHALL mostrar el resultado del pago (aprobado/rechazado/pendiente) en la pantalla de confirmación post-checkout cuando el método de pago es MERCADOPAGO.

#### Scenario: Pago aprobado
- **WHEN** el pago fue aprobado exitosamente
- **THEN** se muestra un badge verde con el texto "Pago aprobado", el ID de pago correspondiente y un botón "Ver detalle del pedido"

#### Scenario: Pago rechazado
- **WHEN** el pago fue rechazado por el procesador
- **THEN** se muestra un badge rojo con el texto "Pago rechazado" y un botón "Reintentar pago" que permite al usuario volver al flujo de pago

#### Scenario: Pago pendiente
- **WHEN** el pago queda en estado pendiente (por ejemplo, pago offline o en revisión)
- **THEN** se muestra un badge amarillo con el texto "Pago en proceso" y un mensaje indicando que se notificará al usuario cuando se confirme
