## Why

El flujo de compra está bloqueado: existe un catálogo público (Epic 2.5) y stores de estado cliente (Epic 0.5), pero no hay ningún mecanismo para que el usuario agregue productos a un carrito, los personalice ni calcule el total antes de confirmar un pedido. Sin este componente no se puede iniciar la Epic 4 (checkout + pagos). Cubre US-029 a US-034.

## What Changes

- **Nuevo Zustand store `useCartStore`** — el store de carrito definido en `client-state` (Epic 0.5) necesita ser completado con soporte explícito a `ingredientesExcluidos` y la acción `toggleIngrediente`. El store actual en `cart.store.ts` existe pero usa `precioUnitario` en vez de `precio_base` y la interfaz `AddProductInput` difiere del modelo de dominio frontend planificado.
- **Nueva entidad de dominio `CartItem`** — type de dominio frontend que modela un ítem del carrito con los campos necesarios para el checkout.
- **Nueva feature `features/carrito/`** — lógica de UI encapsulada para agregar al carrito, personalizar ingredientes, y ver el resumen del carrito (drawer/panel lateral).
- **Nuevos componentes UI de carrito** — `CartDrawer`, `CartItemCard`, `CartSummary`, `IngredientToggle`, `AddToCartButton`.
- **Integración con catálogo** — el botón "Agregar al carrito" se conecta con `ProductCard` (Epic 2.5) para iniciar el flujo de personalización.
- **Persistencia en localStorage** — via Zustand `persist` middleware (`food-store-cart`, versión 1). Ya implementado en el store actual.

## Capabilities

### New Capabilities

- `shopping-cart`: Feature frontend de carrito de compras — store con acciones completas, entidad CartItem tipada, componentes UI (drawer, item cards, resumen, toggle de ingredientes), persistencia localStorage, y cálculo de totales. Puro estado cliente, sin llamadas backend propias.

### Modified Capabilities

- `client-state`: La interfaz `CartItem` y `AddProductInput` actuales en `cart.store.ts` requieren alineación con el modelo de dominio planificado (campo `precio_base` vs `precioUnitario`, acción `toggleIngrediente`). Se ajusta el contrato del store sin romper la lógica central.

## Impact

- **`frontend/src/shared/lib/stores/cart.store.ts`** — ajustar campos de `CartItem` y agregar acción `toggleIngrediente`. Actualizar `CartState` y `AddProductInput`.
- **`frontend/src/shared/lib/stores/index.ts`** — re-exportar tipos actualizados.
- **`frontend/src/entities/carrito/`** — crear tipos de dominio (`CartItem`, `CartSummary`).
- **`frontend/src/entities/producto/`** — crear tipos de dominio del producto para el frontend (`ProductoRead`, `ProductoDetalleRead`, `ProductoIngredienteRead`).
- **`frontend/src/features/carrito/`** — crear feature completa con hooks, componentes, y lógica de UI.
- **`frontend/src/shared/components/`** — posibles componentes base compartidos (`Badge`, `QuantityControl`).
- Sin cambios en backend — el carrito es 100% estado cliente.
- Sin nuevas dependencias externas — usa Zustand ya instalado.
