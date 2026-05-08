## ADDED Requirements

### Requirement: authStore — Sesión de usuario

La aplicación SHALL mantener un store de autenticación (`authStore`) que refleje el estado de sesión del cliente en memoria.

El store SHALL exponer:
- `user`: `User | null` — datos del usuario autenticado o null
- `token`: `string | null` — JWT access token o null
- `isAuthenticated`: `boolean` — getter derivado de token !== null
- `login(user, token)`: acción que setea user y token
- `logout()`: acción que limpia user y token a null
- `updateUser(user)`: acción que actualiza solo user (ej: después de editar perfil)

El store NO SHALL persistir en localStorage. La sesión vive exclusivamente en memoria.

#### Scenario: Login exitoso
- **WHEN** `login(userData, accessToken)` es llamado
- **THEN** `user` SHALL contener `userData`
- **THEN** `token` SHALL contener `accessToken`
- **THEN** `isAuthenticated` SHALL ser true

#### Scenario: Logout
- **WHEN** `logout()` es llamado
- **THEN** `user` SHALL ser null
- **THEN** `token` SHALL ser null
- **THEN** `isAuthenticated` SHALL ser false

#### Scenario: Actualización de perfil
- **WHEN** `updateUser(updatedData)` es llamado
- **THEN** `user` SHALL contener los datos actualizados
- **THEN** `token` SHALL permanecer sin cambios

### Requirement: cartStore — Carrito de compras

La aplicación SHALL mantener un store de carrito de compras (`cartStore`) con persistencia en localStorage.

El store SHALL exponer:
- `items`: `CartItem[]` — ítems en el carrito
- `totalItems`: `number` — getter con suma de cantidades
- `totalPrice`: `number` — getter con suma de (item.precioUnitario * item.cantidad)
- `addItem(product, cantidad, personalizacion?)`: agrega un producto al carrito. Si ya existe (mismo producto + misma personalización), incrementa cantidad. Si no, agrega nuevo ítem.
- `removeItem(itemId)`: elimina un ítem del carrito por ID
- `updateQuantity(itemId, cantidad)`: actualiza la cantidad de un ítem. Si cantidad <= 0, elimina el ítem.
- `updateCustomization(itemId, ingredientesExcluidos)`: actualiza los ingredientes excluidos de un ítem personalizado
- `clearCart()`: vacía el carrito completamente
- `isCartEmpty`: `boolean` — getter derivado de items.length === 0

Cada CartItem SHALL contener: id, productoId, nombre, precioUnitario, cantidad, imagenUrl (opcional), ingredientesExcluidos (opcional).

El store SHALL usar persist middleware con localStorage como storage. Versión de persistencia: 1.

#### Scenario: Agregar ítem nuevo al carrito
- **WHEN** `addItem(product, 2)` es llamado con un producto que NO está en items
- **THEN** un nuevo CartItem SHALL ser agregado con cantidad = 2

#### Scenario: Agregar ítem existente al carrito
- **WHEN** `addItem(product, 1)` es llamado con un producto que YA existe en items (mismo productoId y sin personalización)
- **THEN** la cantidad del ítem existente SHALL incrementarse en 1

#### Scenario: Agregar ítem con personalización distinta
- **WHEN** `addItem(product, 1, { ingredientesExcluidos: [1] })` es llamado
- **WHEN** existe el mismo producto pero con personalización diferente (ingredientesExcluidos: [2])
- **THEN** se SHALL agregar un nuevo CartItem (son personalizaciones distintas)

#### Scenario: Remover ítem del carrito
- **WHEN** `removeItem(itemId)` es llamado con un ID existente
- **THEN** el ítem SHALL ser eliminado de items

#### Scenario: Actualizar cantidad a valor positivo
- **WHEN** `updateQuantity(itemId, 5)` es llamado
- **THEN** el ítem correspondiente SHALL tener cantidad = 5

#### Scenario: Actualizar cantidad a cero o negativo
- **WHEN** `updateQuantity(itemId, 0)` es llamado
- **THEN** el ítem SHALL ser eliminado de items

#### Scenario: Calcular total de ítems
- **WHEN** el carrito tiene 2 ítems con cantidades 3 y 1
- **THEN** `totalItems` SHALL ser 4

#### Scenario: Calcular precio total
- **WHEN** el carrito tiene un ítem con precio 100 y cantidad 2, y otro con precio 50 y cantidad 1
- **THEN** `totalPrice` SHALL ser 250

#### Scenario: Carrito vacío
- **WHEN** `clearCart()` es llamado
- **THEN** `items` SHALL ser un array vacío
- **THEN** `totalItems` SHALL ser 0
- **THEN** `totalPrice` SHALL ser 0

#### Scenario: Persistencia post-refresh
- **WHEN** un usuario agrega productos al carrito
- **WHEN** la página es recargada
- **THEN** items SHALL mantener los mismos productos y cantidades

### Requirement: paymentStore — Estado de pagos

La aplicación SHALL mantener un store de pagos (`paymentStore`) para gestionar el estado de la transacción en curso.

El store SHALL exponer:
- `preferenceId`: `string | null` — ID de preferencia de MercadoPago
- `status`: `'idle' | 'processing' | 'approved' | 'rejected' | 'pending'` — estado del pago
- `paymentId`: `number | null` — ID del pago devuelto por MP (post-aprobación)
- `error`: `string | null` — mensaje de error si el pago falla
- `setPreferenceId(id)`: setea preferenceId y pasa status a pending
- `setApproved(paymentId)`: marca el pago como aprobado
- `setRejected(error?)`: marca el pago como rechazado con mensaje opcional
- `setProcessing()`: marca el pago como en proceso
- `resetState()`: vuelve a valores iniciales (para nuevo pago o cancelación)

El store NO SHALL persistir en localStorage. Es estado transitorio.

#### Scenario: Iniciar flujo de pago
- **WHEN** `setPreferenceId('pref_123')` es llamado
- **THEN** `preferenceId` SHALL ser pref_123
- **THEN** `status` SHALL ser pending

#### Scenario: Pago aprobado
- **WHEN** `setApproved(98765)` es llamado
- **THEN** `status` SHALL ser approved
- **THEN** `paymentId` SHALL ser 98765

#### Scenario: Pago rechazado
- **WHEN** `setRejected('Tarjeta sin fondos')` es llamado
- **THEN** `status` SHALL ser rejected
- **THEN** `error` SHALL contener el mensaje

#### Scenario: Resetear estado
- **WHEN** `resetState()` es llamado
- **THEN** `preferenceId` SHALL ser null
- **THEN** `status` SHALL ser idle
- **THEN** `paymentId` SHALL ser null
- **THEN** `error` SHALL ser null

### Requirement: uiStore — Estado de interfaz de usuario

La aplicación SHALL mantener un store de UI (`uiStore`) con persistencia en localStorage para preferencias de interfaz.

El store SHALL exponer:
- `sidebarOpen`: `boolean` — estado del sidebar (default: true)
- `theme`: `'light' | 'dark'` — tema visual (default: light)
- `activeModal`: `string | null` — ID del modal activo o null
- `toast`: `{ message: string; type: 'success' | 'error' | 'info' } | null` — notificación activa
- `toggleSidebar()`: alterna sidebarOpen
- `setSidebar(open)`: setea sidebarOpen explícitamente
- `setTheme(theme)`: cambia el tema
- `openModal(modalId)`: setea activeModal
- `closeModal()`: limpia activeModal a null
- `showToast(message, type)`: muestra una notificación
- `hideToast()`: limpia la notificación a null

El store SHALL usar persist middleware con localStorage como storage, pero SOLO para sidebarOpen y theme. activeModal y toast no se persisten (son transitorios). Usar `partialize` para filtrar. Versión de persistencia: 1.

#### Scenario: Toggle sidebar
- **WHEN** sidebarOpen es true
- **WHEN** toggleSidebar() es llamado
- **THEN** sidebarOpen SHALL ser false

#### Scenario: Cambiar tema
- **WHEN** setTheme('dark') es llamado
- **THEN** theme SHALL ser 'dark'

#### Scenario: Abrir modal
- **WHEN** openModal('confirm-dialog') es llamado
- **THEN** activeModal SHALL ser 'confirm-dialog'

#### Scenario: Cerrar modal
- **WHEN** closeModal() es llamado
- **THEN** activeModal SHALL ser null

#### Scenario: Mostrar toast
- **WHEN** showToast('Pedido creado', 'success') es llamado
- **THEN** toast SHALL contener el mensaje y type success

#### Scenario: Ocultar toast
- **WHEN** hideToast() es llamado
- **THEN** toast SHALL ser null

#### Scenario: Persistencia selectiva de preferencias
- **WHEN** usuario cambia tema a dark y cierra sidebar
- **WHEN** la página es recargada
- **THEN** theme SHALL mantener el valor persistido
- **THEN** sidebarOpen SHALL mantener el valor persistido
- **THEN** activeModal SHALL ser null (no persistido)
- **THEN** toast SHALL ser null (no persistido)
