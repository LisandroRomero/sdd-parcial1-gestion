## Context

El proyecto tiene Zustand 4 instalado y un `cart.store.ts` ya creado en `frontend/src/shared/lib/stores/`. El store actual implementa la lógica central de carrito (add, remove, updateQuantity, clearCart, persist) pero usa nomenclatura inconsistente con el modelo de dominio planificado (`precioUnitario` en vez de `precio_base`, no tiene `toggleIngrediente`). El catálogo público (Epic 2.5) expone `ProductoDetalleRead` con campo `ingredientes: list[ProductoIngredienteRead]` donde cada ingrediente tiene `es_removible: bool`. La feature de carrito debe consumir esa información para la personalización.

La arquitectura es Feature-Sliced Design (FSD): `Pages → Features → Entities → Shared`. Los stores viven en `shared/lib/stores/` — esto es correcto porque son estado global cliente. Los componentes de UI del carrito van en `features/carrito/`. Los tipos de dominio van en `entities/`.

## Goals / Non-Goals

**Goals:**
- Completar el store `useCartStore` con interfaz de tipos alineada al modelo de dominio (`precio_base`, `toggleIngrediente`).
- Definir tipos de dominio frontend en `entities/`: `CartItem`, `ProductoRead`, `ProductoDetalleRead`, `ProductoIngredienteRead`.
- Implementar la feature `features/carrito/` con todos los componentes de UI.
- Persistencia automática en localStorage con Zustand `persist` (ya funcional, mantener).
- Cálculo reactivo de totales (`totalItems`, `totalPrice`).

**Non-Goals:**
- Llamadas HTTP propias del carrito — el carrito es 100% estado cliente.
- Sincronización del carrito con el backend antes del checkout — se sincroniza al confirmar el pedido (Epic 5).
- Autenticación — el carrito funciona para usuarios anónimos y autenticados por igual.
- Validación de stock en tiempo real — se valida al confirmar el pedido.

## Decisions

### D1: Store en `shared/lib/stores/`, no en `features/carrito/`

**Decision:** el store `useCartStore` permanece en `shared/lib/stores/cart.store.ts`.

**Rationale:** el carrito es estado global que múltiples features necesitan consumir: la feature de catálogo lo usa para mostrar cantidad en el `ProductCard`, la feature de pedidos lo consume al confirmar, el layout lo usa para mostrar el badge de items en el header. Un store en `features/carrito/` violaría el flujo FSD (features no pueden importar de otras features). `shared/` es el nivel correcto para estado global cross-cutting.

**Alternative considered:** store local en `features/carrito/store/`. Descartado — rompe FSD y dificulta el consumo desde otras features.

### D2: Ajustar `CartItem` para usar `precio_base` en vez de `precioUnitario`

**Decision:** cambiar el campo `precioUnitario: number` a `precio_base: number` en `CartItem` y actualizar `AddProductInput` en consecuencia.

**Rationale:** alinear la nomenclatura del frontend con el schema del backend (`ProductoRead.precio_base`) elimina la necesidad de mapping explícito al construir el carrito desde datos del catálogo. Reduce superficie de error. La función `recompute()` interna del store usa el campo correctamente.

**Migration:** el store ya tiene `version: 1` en persist. Al cambiar el nombre del campo se debe incrementar a `version: 2` para que Zustand invalide el estado persistido existente y no crashee con la estructura anterior.

### D3: `toggleIngrediente` como acción atómica en el store

**Decision:** agregar `toggleIngrediente(itemId: string, ingredienteId: number)` al store.

**Rationale:** la acción alterna la presencia de `ingredienteId` en `item.ingredientesExcluidos`. Encapsularla en el store mantiene la lógica pura (sin referencias al DOM/React) y facilita testing. Alternativa: manejar el toggle en el componente con `updateCustomization` existente — descartado porque requeriría que el componente conozca el estado actual del item para construir el nuevo array, acoplando lógica de negocio al componente.

### D4: Tipos de dominio frontend en `entities/`, no en `shared/`

**Decision:** crear `entities/producto/types.ts` y `entities/carrito/types.ts` con los tipos de dominio.

**Rationale:** en FSD los tipos de dominio viven en `entities/`. `shared/` se reserva para utilities, UI base y librerías. Esto permite que tanto `features/carrito/` como `features/catalogo/` (futuro) importen los tipos desde `entities/` sin violar el flujo de imports.

### D5: `CartDrawer` como panel lateral deslizante (no modal)

**Decision:** implementar el carrito como un drawer lateral (sliding panel desde la derecha), no como modal o página separada.

**Rationale:** es el patrón UX más común para carritos en e-commerce — permite ver los productos del catálogo mientras se revisa el carrito. Técnicamente se implementa con `position: fixed` + `translate-x` de Tailwind + transición CSS. No requiere bibliotecas adicionales. Se controla con `useUIStore.openModal('cart-drawer')` / `closeModal()`.

**Alternative considered:** página `/carrito` separada. Descartado — interrumpe el flujo de navegación del catálogo.

### D6: `AddToCartButton` como componente en `features/carrito/`

**Decision:** el botón que conecta un `ProductoDetalleRead` con el store vive en `features/carrito/components/AddToCartButton.tsx`.

**Rationale:** el botón contiene lógica de la feature (llama a `useCartStore().addItem`, maneja el modal de personalización). No pertenece a `entities/` (entidades no tienen lógica de acción) ni a `shared/` (es específico del dominio carrito). En FSD, `features/` es el lugar correcto para componentes con side effects o estado de feature.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Cambiar `precioUnitario` → `precio_base` rompe el localStorage persistido existente | Incrementar `version: 2` en `persist` para que Zustand descarte el estado anterior. Los carritos en vuelo se vacían. |
| El drawer CSS-only puede tener problemas de accessibility (focus trap, Escape) | Implementar `useEffect` para cerrar con Escape y `aria-modal` en el drawer. |
| Performance: `recompute()` corre en cada acción del store | Aceptable — el carrito no tendrá más de ~50 items. No es un cuello de botella. |
| Ingredientes excluidos guardados como `number[]` (IDs) — si el backend cambia IDs entre deploys | El carrito se vacía al cerrar sesión del checkout; los IDs son estables para el ciclo de vida del carrito. |

## Migration Plan

1. Actualizar `cart.store.ts` — cambiar `precioUnitario` → `precio_base`, agregar `toggleIngrediente`, incrementar `version` a 2.
2. Actualizar `shared/lib/stores/index.ts` — re-exportar tipos actualizados.
3. Crear `entities/producto/types.ts` — `ProductoRead`, `ProductoDetalleRead`, `ProductoIngredienteRead`.
4. Crear `entities/carrito/types.ts` — `CartItem` (re-export del tipo del store), `CartSummary`.
5. Crear `features/carrito/` — hooks, componentes, index.ts.
6. Integrar `CartDrawer` en `app/routes/layout.tsx`.

**Rollback:** todos los cambios están en el frontend. No hay migraciones de BD ni cambios de API. Revertir los archivos es suficiente. El incremento de versión en el store invalida localStorage, pero el carrito siempre puede re-llenarse.

## Open Questions

- ¿La pantalla de personalización de ingredientes se muestra en un modal inline dentro del drawer, o en un modal separado? Por simplicidad, se implementa como sección expandible dentro del `AddToCartButton` flow (modal separado antes de agregar al carrito).
- ¿El badge de cantidad en el header pertenece a `features/carrito/` o al `Layout`? El header puede consumir `useCartStore().totalItems` directamente — no necesita un componente específico de la feature.
