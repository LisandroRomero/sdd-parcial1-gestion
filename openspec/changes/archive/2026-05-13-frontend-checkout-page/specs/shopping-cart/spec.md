## MODIFIED Requirements

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
- `getItemsForCheckout(): DetallePedidoCreate[]` — devuelve los items listos para enviar a `POST /pedidos`, mapeando cada `CartItem` a `{ producto_id: number, cantidad: number }`

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

#### Scenario: getItemsForCheckout mapea CartItems a DetallePedidoCreate

- **GIVEN** `items = [{ productoId: 1, cantidad: 2 }, { productoId: 3, cantidad: 1 }]`
- **WHEN** `getItemsForCheckout()` es llamado
- **THEN** retorna `[{ producto_id: 1, cantidad: 2 }, { producto_id: 3, cantidad: 1 }]`

---

### Requirement: Feature carrito — CartSummary

El frontend SHALL implementar `CartSummary` en `frontend/src/features/carrito/components/CartSummary.tsx`.

El componente SHALL mostrar:
- Cantidad total de ítems (`totalItems`)
- Precio total (`totalPrice`) formateado como moneda ARS (ej: `$1.500,00`)
- Botón "Vaciar carrito" que llama a `clearCart()`
- Botón "Confirmar pedido" (habilitado solo si `!isCartEmpty`) que navega a `/checkout`

#### Scenario: Precio total formateado en ARS

- **GIVEN** `totalPrice = 1500`
- **THEN** SHALL mostrarse como `$1.500,00` o similar con separador de miles

#### Scenario: Confirmar pedido navega a checkout

- **WHEN** el usuario hace clic en "Confirmar pedido" con `!isCartEmpty`
- **THEN** el sistema navega a la ruta `/checkout`
