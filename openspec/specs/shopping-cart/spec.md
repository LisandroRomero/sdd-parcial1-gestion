### Requirement: Tipos de dominio frontend — CartItem

El frontend SHALL definir el tipo `CartItem` en `frontend/src/entities/carrito/types.ts` con los siguientes campos:
- `id: string` — identificador único del item en el carrito (generado localmente, no es el ID del producto)
- `productoId: number` — ID del producto en el backend
- `nombre: string` — nombre del producto
- `precio_base: number` — precio unitario del producto
- `cantidad: number` — cantidad seleccionada (siempre > 0)
- `imagenUrl?: string` — URL de la imagen del producto (opcional)
- `ingredientesExcluidos: number[]` — IDs de ingredientes removidos (default `[]`)

El campo `id` SHALL ser generado localmente con una función que combine timestamp y un string aleatorio para garantizar unicidad durante la sesión. Dos ítems del mismo producto con distintos `ingredientesExcluidos` SHALL tener `id` diferentes.

#### Scenario: Dos CartItems del mismo producto son distintos si tienen personalizaciones distintas

- **GIVEN** `itemA` tiene `productoId = 1` e `ingredientesExcluidos = [2]`
- **GIVEN** `itemB` tiene `productoId = 1` e `ingredientesExcluidos = [3]`
- **THEN** `itemA.id !== itemB.id`
- **THEN** ambos ítems pueden coexistir en el carrito simultáneamente

---

### Requirement: Tipos de dominio frontend — ProductoIngredienteRead

El frontend SHALL definir el tipo `ProductoIngredienteRead` en `frontend/src/entities/producto/types.ts` con los siguientes campos mínimos necesarios para la feature de carrito:
- `ingrediente_id: number`
- `nombre: string`
- `es_removible: boolean`
- `es_alergeno: boolean`

#### Scenario: Filtrado de ingredientes removibles

- **GIVEN** un `ProductoDetalleRead` con `ingredientes: ProductoIngredienteRead[]`
- **WHEN** el componente de personalización se renderiza
- **THEN** SOLO SHALL mostrarse los ingredientes donde `es_removible === true`

---

### Requirement: Tipos de dominio frontend — ProductoDetalleRead

El frontend SHALL definir el tipo `ProductoDetalleRead` en `frontend/src/entities/producto/types.ts` con los siguientes campos:
- `id: number`
- `nombre: string`
- `descripcion: string | null`
- `precio_base: number`
- `disponible: boolean`
- `imagen_url: string | null`
- `ingredientes: ProductoIngredienteRead[]`
- `tiene_alergenos: boolean`

---

### Requirement: useCartStore — Estado del carrito

El frontend SHALL mantener un Zustand store `useCartStore` exportado desde `frontend/src/shared/lib/stores/cart.store.ts`.

El store SHALL exponer el siguiente estado:
- `items: CartItem[]` — lista de ítems en el carrito
- `totalItems: number` — suma de cantidades de todos los ítems
- `totalPrice: number` — suma de `precio_base * cantidad` por item
- `isCartEmpty: boolean` — `true` si `items.length === 0`

El store SHALL exponer las siguientes acciones:
- `addItem(product, cantidad, personalizacion?)` — agrega un producto al carrito
- `removeItem(itemId)` — elimina un ítem por ID
- `updateQuantity(itemId, cantidad)` — actualiza cantidad; si `cantidad <= 0` elimina el ítem
- `toggleIngrediente(itemId, ingredienteId)` — alterna la presencia de `ingredienteId` en `item.ingredientesExcluidos`
- `clearCart()` — vacía el carrito completamente

El store SHALL usar Zustand `persist` middleware con:
- `name: 'food-store-cart'`
- `version: 2`
- `partialize`: persistir SOLO `items`; los valores derivados (`totalItems`, `totalPrice`, `isCartEmpty`) se recomputan al hidratarse

#### Scenario: Agregar un producto nuevo al carrito

- **WHEN** `addItem({ id: 1, nombre: 'Pizza', precio_base: 500 }, 2)` es llamado
- **AND** no existe ningún item con `productoId === 1` y `ingredientesExcluidos = []`
- **THEN** `items` SHALL tener 1 elemento con `productoId = 1`, `cantidad = 2`, `precio_base = 500`
- **THEN** `totalItems` SHALL ser `2`
- **THEN** `totalPrice` SHALL ser `1000`

#### Scenario: Agregar el mismo producto sin personalización incrementa cantidad

- **WHEN** `addItem({ id: 1, nombre: 'Pizza', precio_base: 500 }, 1)` es llamado
- **AND** ya existe un item con `productoId === 1` e `ingredientesExcluidos = []`
- **THEN** la cantidad del item existente SHALL incrementarse en `1`
- **THEN** NO se SHALL agregar un nuevo item

#### Scenario: Agregar el mismo producto con personalización distinta crea item nuevo

- **WHEN** existe un item con `productoId = 1` e `ingredientesExcluidos = [2]`
- **WHEN** se llama `addItem({ id: 1, ... }, 1, { ingredientesExcluidos: [3] })`
- **THEN** se SHALL agregar un nuevo item con `ingredientesExcluidos = [3]`
- **THEN** `items.length` SHALL ser `2`

#### Scenario: Remover un ítem del carrito

- **WHEN** `removeItem(itemId)` es llamado con un ID existente
- **THEN** el ítem SHALL ser eliminado de `items`
- **THEN** `totalItems` y `totalPrice` SHALL recalcularse correctamente

#### Scenario: Actualizar cantidad a valor positivo

- **WHEN** `updateQuantity(itemId, 5)` es llamado
- **THEN** el ítem correspondiente SHALL tener `cantidad = 5`
- **THEN** `totalPrice` SHALL recalcularse

#### Scenario: Actualizar cantidad a cero o negativo elimina el ítem

- **WHEN** `updateQuantity(itemId, 0)` es llamado
- **THEN** el ítem SHALL ser eliminado de `items`

#### Scenario: toggleIngrediente agrega ingrediente excluido

- **GIVEN** un item con `ingredientesExcluidos = []`
- **WHEN** `toggleIngrediente(itemId, 5)` es llamado
- **THEN** `item.ingredientesExcluidos` SHALL ser `[5]`

#### Scenario: toggleIngrediente quita ingrediente ya excluido

- **GIVEN** un item con `ingredientesExcluidos = [5]`
- **WHEN** `toggleIngrediente(itemId, 5)` es llamado
- **THEN** `item.ingredientesExcluidos` SHALL ser `[]`

#### Scenario: clearCart vacía el carrito

- **WHEN** `clearCart()` es llamado
- **THEN** `items` SHALL ser `[]`
- **THEN** `totalItems` SHALL ser `0`
- **THEN** `totalPrice` SHALL ser `0`
- **THEN** `isCartEmpty` SHALL ser `true`

#### Scenario: Persistencia sobrevive a recarga de página

- **GIVEN** el carrito tiene items
- **WHEN** la página es recargada
- **THEN** `items` SHALL contener los mismos items
- **THEN** `totalItems` y `totalPrice` SHALL recalcularse correctamente desde los items persistidos

---

### Requirement: Feature carrito — AddToCartButton

El frontend SHALL implementar un componente `AddToCartButton` en `frontend/src/features/carrito/components/AddToCartButton.tsx`.

El componente SHALL recibir `producto: ProductoDetalleRead` como prop.

El componente SHALL:
1. Mostrar un botón "Agregar al carrito" cuando el producto tiene `disponible = true`
2. Si el producto tiene ingredientes con `es_removible = true`, mostrar primero un modal/panel de personalización antes de confirmar
3. Al confirmar, llamar a `useCartStore().addItem()` con el producto y los ingredientes excluidos seleccionados
4. Mostrar feedback visual (toast de confirmación o animación) al agregar exitosamente

Si `producto.disponible === false`, el botón SHALL estar deshabilitado con texto "No disponible".

#### Scenario: Producto sin ingredientes removibles — agregar directo

- **GIVEN** un producto con `ingredientes` todos con `es_removible = false`
- **WHEN** el usuario hace click en "Agregar al carrito"
- **THEN** el item se agrega directamente al store sin mostrar modal de personalización

#### Scenario: Producto con ingredientes removibles — mostrar personalización

- **GIVEN** un producto con al menos un ingrediente con `es_removible = true`
- **WHEN** el usuario hace click en "Agregar al carrito"
- **THEN** se muestra el panel de personalización con los ingredientes removibles listados
- **THEN** el usuario puede marcar/desmarcar ingredientes a excluir
- **THEN** al confirmar, se llama `addItem` con los `ingredientesExcluidos` seleccionados

---

### Requirement: Feature carrito — CartDrawer

El frontend SHALL implementar un componente `CartDrawer` en `frontend/src/features/carrito/components/CartDrawer.tsx`.

El drawer SHALL:
- Deslizarse desde la derecha cuando `useUIStore().activeModal === 'cart-drawer'`
- Cerrarse al hacer click fuera del drawer (overlay) o al presionar `Escape`
- Mostrar `CartItemCard` por cada item en `useCartStore().items`
- Mostrar `CartSummary` al fondo con `totalItems` y `totalPrice`
- Mostrar estado vacío ("Tu carrito está vacío") cuando `isCartEmpty === true`

#### Scenario: Abrir el CartDrawer

- **WHEN** `useUIStore().openModal('cart-drawer')` es llamado
- **THEN** el drawer SHALL deslizarse desde la derecha
- **THEN** el overlay SHALL cubrir el contenido de fondo

#### Scenario: Cerrar el CartDrawer con Escape

- **WHEN** el drawer está abierto
- **WHEN** el usuario presiona la tecla `Escape`
- **THEN** el drawer SHALL cerrarse (llamar a `useUIStore().closeModal()`)

#### Scenario: Carrito vacío

- **WHEN** `useCartStore().isCartEmpty === true`
- **THEN** SHALL mostrarse un mensaje "Tu carrito está vacío" con un CTA para ir al catálogo

---

### Requirement: Feature carrito — CartItemCard

El frontend SHALL implementar `CartItemCard` en `frontend/src/features/carrito/components/CartItemCard.tsx`.

El componente SHALL recibir `item: CartItem` como prop y mostrar:
- Nombre del producto (`item.nombre`)
- Precio unitario (`item.precio_base`)
- Control de cantidad con botones `+` y `−`
- Subtotal (`item.precio_base * item.cantidad`)
- Botón de eliminar que llama a `removeItem(item.id)`
- Lista de ingredientes excluidos (si `item.ingredientesExcluidos.length > 0`)

Al cambiar la cantidad, SHALL llamar a `updateQuantity(item.id, nuevaCantidad)`.

#### Scenario: Disminuir cantidad a 0 elimina el ítem

- **WHEN** el usuario hace click en `−` con `item.cantidad === 1`
- **THEN** el ítem SHALL ser eliminado del carrito (cantidad llega a 0)

---

### Requirement: Feature carrito — CartSummary

El frontend SHALL implementar `CartSummary` en `frontend/src/features/carrito/components/CartSummary.tsx`.

El componente SHALL mostrar:
- Cantidad total de ítems (`totalItems`)
- Precio total (`totalPrice`) formateado como moneda ARS (ej: `$1.500,00`)
- Botón "Vaciar carrito" que llama a `clearCart()`
- Botón "Confirmar pedido" (habilitado solo si `!isCartEmpty`) que navega al checkout (ruta futura)

#### Scenario: Precio total formateado en ARS

- **GIVEN** `totalPrice = 1500`
- **THEN** SHALL mostrarse como `$1.500,00` o similar con separador de miles
