## ADDED Requirements

### Requirement: Checkout SHALL send direccion_id (not direccion_entrega_id)

The checkout page SHALL send `direccion_id` in the POST /api/v1/pedidos payload. The field `direccion_entrega_id` SHALL NOT be used.

#### Scenario: Direccion field is correct

- **WHEN** the user confirms the order with a selected address
- **THEN** the payload SHALL include `direccion_id` (not `direccion_entrega_id`)

### Requirement: Checkout SHALL include forma_pago_codigo

The checkout page SHALL include `forma_pago_codigo` in the POST /api/v1/pedidos payload.

#### Scenario: Forma de pago is included

- **WHEN** the user confirms the order
- **THEN** the payload SHALL include `forma_pago_codigo`

### Requirement: Forma de pago SHALL have a default value

When no payment method has been selected by the user, the checkout SHALL default to `forma_pago_codigo: "EFECTIVO"`.

#### Scenario: Default forma de pago used

- **GIVEN** the user has not selected a payment method
- **WHEN** the user confirms the order
- **THEN** the payload SHALL include `forma_pago_codigo: "EFECTIVO"`

### Requirement: Cart getItemsForCheckout SHALL use personalizacion field name

The `getItemsForCheckout` function SHALL output `personalizacion: number[]` (not `ingredientes_excluidos`) for each item's customization.

#### Scenario: getItemsForCheckout returns personalizacion

- **GIVEN** a CartItem with `ingredientesExcluidos = [2, 5]`
- **WHEN** `getItemsForCheckout()` is called
- **THEN** the returned item SHALL include `personalizacion: [2, 5]`
- **THEN** the returned item SHALL NOT include `ingredientes_excluidos`

### Requirement: getItemsForCheckout SHALL NOT include precio_unitario

The `getItemsForCheckout` return type SHALL NOT include `precio_unitario`. Each item SHALL only contain `producto_id`, `cantidad`, and `personalizacion`.

#### Scenario: precio_unitario is excluded

- **WHEN** `getItemsForCheckout()` is called
- **THEN** each returned item SHALL NOT have a `precio_unitario` field
