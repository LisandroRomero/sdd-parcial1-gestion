## ADDED Requirements

### Requirement: Cart store SHALL recalculate derived state after hydration

The cart store SHALL ensure that `totalItems`, `totalPrice`, and `isCartEmpty` are correct immediately after Zustand persist hydration completes.

#### Scenario: Derived state is correct after page reload

- **GIVEN** the cart has 2 items with `cantidad = 3` and `cantidad = 1` and `precio_base = 100` each
- **WHEN** the page reloads and persist hydration completes
- **THEN** `totalItems` SHALL be `4`
- **THEN** `totalPrice` SHALL be `400`
- **THEN** `isCartEmpty` SHALL be `false`

#### Scenario: Cart is empty after reload when no items persisted

- **GIVEN** localStorage has no persisted cart items
- **WHEN** the page reloads and persist hydration completes
- **THEN** `items` SHALL be `[]`
- **THEN** `isCartEmpty` SHALL be `true`
- **THEN** `totalItems` SHALL be `0`
- **THEN** `totalPrice` SHALL be `0`

### Requirement: Cart store SHALL have a custom merge function

The cart store persist middleware SHALL include a custom `merge` function that computes derived state from the persisted `items` array before returning state to subscribers.

#### Scenario: Merge recalculates derived state

- **GIVEN** persisted state has `items = [{ cantidad: 2, precio_base: 500 }]`
- **WHEN** the persist middleware calls `merge(persisted, initial)`
- **THEN** the returned state SHALL have `totalItems = 2`
- **THEN** the returned state SHALL have `totalPrice = 1000`
- **THEN** the returned state SHALL have `isCartEmpty = false`

### Requirement: isCartEmpty SHALL be a computed value

`isCartEmpty` SHALL NOT be stored in persisted state. It SHALL be computed as `items.length === 0` on every access.

### Requirement: Cart persist SHALL have migrate function for version bumps

The persist middleware SHALL include a `migrate` function that handles transitioning from version 1 to version 2. The migration SHALL extract only `items` from the old persisted state.

#### Scenario: Migrate from version 1 to version 2

- **GIVEN** localStorage has persisted cart state with `version: 1`
- **WHEN** the store initializes
- **THEN** the `migrate` function SHALL extract `items` from the old state
- **THEN** all derived state SHALL be recomputed from `items`
- **THEN** the persisted version SHALL be updated to `2`
