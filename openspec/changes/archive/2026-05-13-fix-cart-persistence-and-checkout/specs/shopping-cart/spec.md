## MODIFIED Requirements (delta from existing `openspec/specs/shopping-cart/spec.md`)

### Changed: getItemsForCheckout output

The `getItemsForCheckout` return type SHALL be updated from `{ producto_id: number, cantidad: number }` to `{ producto_id: number, cantidad: number, personalizacion: number[] }`.

Replace the existing Scenario "getItemsForCheckout mapea CartItems a DetallePedidoCreate" with:

#### Scenario: getItemsForCheckout mapea CartItems a DetallePedidoCreate con personalizacion

- **GIVEN** `items = [{ productoId: 1, cantidad: 2, ingredientesExcluidos: [3] }, { productoId: 5, cantidad: 1, ingredientesExcluidos: [] }]`
- **WHEN** `getItemsForCheckout()` es llamado
- **THEN** retorna `[{ producto_id: 1, cantidad: 2, personalizacion: [3] }, { producto_id: 5, cantidad: 1, personalizacion: [] }]`

Update `getItemsForCheckout` en el Requisito "useCartStore &mdash; Estado del carrito":

Elstore SHALL exponer `getItemsForCheckout(): DetallePedidoCreate[]` que devuelve los items listos para enviar a `POST /pedidos`, mapeando cada `CartItem` a `{ producto_id: number, cantidad: number, personalizacion: number[] }`.

### Added: Custom merge function for persist middleware

Add to the persist middleware configuration in "useCartStore &mdash; Estado del carrito":

El persist middleware SHALL incluir una función `merge` personalizada que:
1. Toma el estado persistido y el estado inicial
2. Extrae `items` del estado persistido (o `[]` si no hay)
3. Recalcula `totalItems`, `totalPrice` e `isCartEmpty` a partir de `items`
4. Retorna el estado completo con los valores recalculados

### Added: Migrate function for version bumps

Add to the persist middleware configuration in "useCartStore &mdash; Estado del carrito":

El persist middleware SHALL incluir una función `migrate` que maneje la transición de versión 1 a versión 2:
- Si `oldVersion < 2`, extraer SOLO `items` del estado persistido previo (descartar `totalItems`, `totalPrice`, `isCartEmpty`, `precio_unitario` y cualquier campo legacy)
- Retornar `{ items }` para que la función `merge` recalcule los valores derivados

### Changed: totalItems, totalPrice, isCartEmpty as computed selectors

Modify the store definition to clarify these are NOT stored/persisted state:

`totalItems` (suma de cantidades), `totalPrice` (suma de `precio_base * cantidad`) e `isCartEmpty` (`items.length === 0`) SHALL ser valores computados (getters/selectors), NO estado almacenado. Se computan desde `items` en cada acceso.

El `partialize` SHALL persistir SOLO `items`.

#### Scenario: Derived state is correct after persist hydration

Replace the existing Scenario "Persistencia sobrevive a recarga de página" with:

- **GIVEN** el carrito tiene items
- **WHEN** la página es recargada
- **THEN** `items` SHALL contener los mismos items
- **THEN** `totalItems` y `totalPrice` SHALL recalcularse correctamente desde los items persistidos (via custom `merge`)
- **THEN** la función `migrate` SHALL ejecutarse si hay cambio de versión
