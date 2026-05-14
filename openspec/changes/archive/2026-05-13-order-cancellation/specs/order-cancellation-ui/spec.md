## ADDED Requirements

### Requirement: Botón contextual de cancelación según estado y rol

El frontend SHALL mostrar un botón "Cancelar pedido" contextualmente visible según el `estado_actual` del pedido y el `rol` del usuario autenticado. El botón SHALL estar visible únicamente cuando se cumplan las reglas de visibilidad definidas.

#### Scenario: CLIENTE ve botón cancelar en PENDIENTE
- **WHEN** un usuario con rol `CLIENTE` visualiza un pedido propio con `estado_actual = "PENDIENTE"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: CLIENTE no ve botón cancelar en CONFIRMADO
- **WHEN** un usuario con rol `CLIENTE` visualiza un pedido propio con `estado_actual = "CONFIRMADO"`
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible

#### Scenario: ADMIN ve botón cancelar en EN_PREP
- **WHEN** un usuario con rol `ADMIN` visualiza un pedido con `estado_actual = "EN_PREP"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: GESTOR_PEDIDOS ve botón cancelar en CONFIRMADO
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` visualiza un pedido con `estado_actual = "CONFIRMADO"`
- **THEN** el botón "Cancelar pedido" SHALL ser visible

#### Scenario: GESTOR_PEDIDOS no ve botón cancelar en EN_PREP
- **WHEN** un usuario con rol `GESTOR_PEDIDOS` visualiza un pedido con `estado_actual = "EN_PREP"`
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible

#### Scenario: GESTOR_STOCK no ve botón cancelar en ningún estado
- **WHEN** un usuario con rol `GESTOR_STOCK` visualiza cualquier pedido
- **THEN** el botón "Cancelar pedido" NO SHALL ser visible en ningún estado

---

### Requirement: Modal de confirmación con selección de motivo

Al hacer clic en "Cancelar pedido", el frontend SHALL mostrar un modal de confirmación que contenga:
- Título "¿Estás seguro de cancelar el pedido?"
- Selector de motivos predefinidos ("El cliente canceló", "Producto no disponible", "Error en el pedido", "Problema de stock", "Otro")
- Área de texto para motivo personalizado (máximo 255 caracteres) visible cuando se selecciona "Otro" o como campo adicional opcional
- Botón "Sí, cancelar pedido" (destructive style, rojo)
- Botón "No, mantener pedido" (secondary style)
- Indicación visual de que la acción es irreversible

#### Scenario: Modal se abre al hacer clic en cancelar
- **WHEN** el usuario hace clic en "Cancelar pedido"
- **THEN** el modal de confirmación SHALL abrirse con todos los elementos descritos
- **THEN** el botón "Sí, cancelar pedido" SHALL estar deshabilitado hasta que se ingrese un motivo

#### Scenario: Seleccionar motivo predefinido
- **WHEN** el usuario selecciona "El cliente canceló" del selector de motivos
- **THEN** el campo de motivo SHALL mostrar "El cliente canceló" como el valor a enviar

#### Scenario: Seleccionar "Otro" y escribir motivo personalizado
- **WHEN** el usuario selecciona "Otro" en el selector de motivos
- **THEN** el área de texto para motivo personalizado SHALL hacerse visible
- **AND** el usuario puede escribir hasta 255 caracteres

#### Scenario: Motivo excede 255 caracteres
- **WHEN** el usuario intenta escribir más de 255 caracteres en el área de texto
- **THEN** el frontend SHALL truncar o impedir la entrada adicional
- **THEN** SHALL mostrarse un contador de caracteres (ej: "245/255")

#### Scenario: Confirmar cancelación exitosamente
- **WHEN** el usuario hace clic en "Sí, cancelar pedido" con un motivo válido
- **AND** la mutación API responde exitosamente
- **THEN** el modal SHALL cerrarse
- **THEN** el pedido SHALL mostrar estado `CANCELADO` actualizado

#### Scenario: Cancelar desde el modal
- **WHEN** el usuario hace clic en "No, mantener pedido"
- **THEN** el modal SHALL cerrarse sin realizar ninguna acción

---

### Requirement: Hook useCancelarPedido con TanStack Query useMutation

El frontend SHALL implementar un hook `useCancelarPedido` que utilice `useMutation` de TanStack Query para enviar `DELETE /api/v1/pedidos/{id}?motivo={motivo}`. El hook SHALL invalidar y refetch las queries `["pedidos"]` y `["pedido", id]` al completar exitosamente.

#### Scenario: Mutación exitosa invalida queries
- **WHEN** `useCancelarPedido` se ejecuta exitosamente para un pedido con `id = 42`
- **THEN** la mutation SHALL invalidar las queries `["pedidos"]` y `["pedido", 42]`
- **THEN** TanStack Query SHALL refetch automáticamente ambas queries

#### Scenario: Hook retorna estado de carga
- **WHEN** la mutación está en curso (isPending === true)
- **THEN** el hook SHALL retornar `isPending = true`

#### Scenario: Hook retorna error en fallo
- **WHEN** la mutación falla con un error de API
- **THEN** el hook SHALL retornar el `error` correspondiente

---

### Requirement: Feedback visual durante cancelación

Mientras se procesa la cancelación, el frontend SHALL mostrar estado de carga en el modal deshabilitando el botón "Sí, cancelar pedido" y mostrando un spinner. Al completar exitosamente, SHALL mostrar un toast de éxito con mensaje "Pedido cancelado exitosamente". En caso de error, SHALL mostrar toast de error con el mensaje específico.

#### Scenario: Loading state mientras se procesa
- **WHEN** el usuario confirma la cancelación y la petición está en curso
- **THEN** el botón "Sí, cancelar pedido" SHALL deshabilitarse
- **THEN** el botón SHALL mostrar un spinner y el texto "Cancelando..."
- **THEN** el botón "No, mantener pedido" SHALL deshabilitarse también

#### Scenario: Toast de éxito al cancelar
- **WHEN** la cancelación se completa exitosamente
- **THEN** SHALL mostrarse un toast con ícono de check verde y mensaje "Pedido cancelado exitosamente"

#### Scenario: Toast de error por stock
- **WHEN** la cancelación falla con error `PEDIDO_STOCK_INSUFICIENTE`
- **THEN** SHALL mostrarse un toast con ícono de error rojo y el mensaje del error

#### Scenario: Toast de error por permiso
- **WHEN** la cancelación falla con error `PEDIDO_ROL_NO_AUTORIZADO`
- **THEN** SHALL mostrarse un toast con mensaje "No tenés permiso para cancelar este pedido"

#### Scenario: Toast de error genérico
- **WHEN** la cancelación falla con un error no específico
- **THEN** SHALL mostrarse un toast con mensaje "Error al cancelar el pedido. Intentá de nuevo."

---

### Requirement: Badge visual de estado CANCELADO

El frontend SHALL renderizar el estado `CANCELADO` con un badge visual diferenciado del resto de los estados. El badge SHALL usar color rojo/tono de alerta con ícono de cancelación y texto "Cancelado".

#### Scenario: Pedido cancelado muestra badge rojo
- **WHEN** un pedido tiene `estado_actual = "CANCELADO"`
- **THEN** SHALL mostrarse un badge con clase de color rojo (`bg-red-100`, `text-red-800`, `border-red-300`)
- **THEN** el badge SHALL incluir un ícono de "X" o cancelación
- **THEN** el badge SHALL mostrar el texto "Cancelado"

#### Scenario: Badge no afecta otros estados
- **WHEN** un pedido tiene estado distinto a `CANCELADO`
- **THEN** el badge de cancelado NO SHALL mostrarse
- **THEN** el estado SHALL renderizarse con su estilo habitual

---

### Requirement: Manejo de errores específicos en modal de cancelación

El modal de cancelación SHALL mostrar mensajes de error específicos según el tipo de error retornado por la API. Los errores SHALL mostrarse inline dentro del modal sin cerrarlo.

#### Scenario: Error de stock insuficiente en modal
- **WHEN** la cancelación falla con error `PEDIDO_STOCK_INSUFICIENTE`
- **THEN** el modal SHALL mostrar mensaje inline "No se pudo restaurar el stock. Contactá a soporte."
- **THEN** el modal NO SHALL cerrarse automáticamente
- **THEN** el botón "Sí, cancelar pedido" SHALL rehabilitarse para reintentar

#### Scenario: Error de permiso en modal
- **WHEN** la cancelación falla con error `PEDIDO_ROL_NO_AUTORIZADO`
- **THEN** el modal SHALL mostrar mensaje inline "No tenés permiso para cancelar este pedido"
- **THEN** el modal SHALL cerrarse al hacer clic en "Cerrar"

---

### Requirement: Cancelación con motivo estructurado

El frontend SHALL enviar un motivo estructurado al endpoint de cancelación combinando la razón predefinida seleccionada con el texto personalizado opcional. El formato SHALL ser `"[Razón predefinida]: [texto personalizado]"` o solo la razón predefinida si no hay texto personalizado.

#### Scenario: Motivo solo con razón predefinida
- **WHEN** el usuario selecciona "Producto no disponible" sin texto personalizado
- **THEN** el frontend SHALL enviar `motivo = "Producto no disponible"`

#### Scenario: Motivo con razón predefinida y texto personalizado
- **WHEN** el usuario selecciona "Otro" y escribe "El cliente pidió cambio de dirección"
- **THEN** el frontend SHALL enviar `motivo = "Otro: El cliente pidió cambio de dirección"`

#### Scenario: Motivo con texto personalizado adicional
- **WHEN** el usuario selecciona "El cliente canceló" y escribe "No le gusta el producto"
- **THEN** el frontend SHALL enviar `motivo = "El cliente canceló: No le gusta el producto"`
