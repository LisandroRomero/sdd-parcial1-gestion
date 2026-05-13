## 1. Tipos de dominio (entities/)

- [x] 1.1 Crear `frontend/src/entities/producto/types.ts` con `ProductoIngredienteRead`, `ProductoRead`, `ProductoDetalleRead`
- [x] 1.2 Crear `frontend/src/entities/producto/index.ts` con re-exports
- [x] 1.3 Crear `frontend/src/entities/carrito/types.ts` con re-export de `CartItem` desde el store y `CartSummary` type
- [x] 1.4 Crear `frontend/src/entities/carrito/index.ts` con re-exports

## 2. Actualizar useCartStore

- [x] 2.1 Cambiar campo `precioUnitario` → `precio_base` en `CartItem` e `AddProductInput` en `cart.store.ts`
- [x] 2.2 Incrementar `version` de `1` a `2` en la config de `persist` para invalidar localStorage anterior
- [x] 2.3 Agregar acción `toggleIngrediente(itemId: string, ingredienteId: number)` al store
- [x] 2.4 Actualizar `CartState` interface para incluir `toggleIngrediente`
- [x] 2.5 Actualizar `shared/lib/stores/index.ts` para re-exportar tipos actualizados (`CartItem`, `AddProductInput`, `CartState`)

## 3. Componentes base compartidos

- [x] 3.1 Crear `frontend/src/shared/components/QuantityControl.tsx` — control +/- con input numérico, props: `value`, `onChange`, `min?`, `max?`
- [x] 3.2 Exportar `QuantityControl` desde `frontend/src/shared/components/index.ts`

## 4. Feature carrito — estructura y hook

- [x] 4.1 Crear directorio `frontend/src/features/carrito/components/`
- [x] 4.2 Crear `frontend/src/features/carrito/hooks/useCart.ts` — wrapper con helpers: `getItemCount(productoId)`, `isInCart(productoId)` usando `useCartStore`
- [x] 4.3 Crear `frontend/src/features/carrito/index.ts` con re-exports públicos de la feature

## 5. Componente AddToCartButton

- [x] 5.1 Crear `frontend/src/features/carrito/components/AddToCartButton.tsx` — botón que recibe `producto: ProductoDetalleRead`
- [x] 5.2 Implementar lógica de flujo directo (sin ingredientes removibles) — llama a `addItem` inmediatamente
- [x] 5.3 Implementar modal de personalización de ingredientes (cuando hay ingredientes con `es_removible = true`) — lista de checkboxes con `IngredientToggle`
- [x] 5.4 Crear `frontend/src/features/carrito/components/IngredientToggle.tsx` — checkbox para cada ingrediente removible
- [x] 5.5 Integrar feedback visual al agregar — usar `useUIStore().showToast('Producto agregado', 'success')`
- [x] 5.6 Estado disabled cuando `producto.disponible === false` con texto "No disponible"

## 6. Componente CartItemCard

- [x] 6.1 Crear `frontend/src/features/carrito/components/CartItemCard.tsx` — card que muestra un ítem del carrito
- [x] 6.2 Mostrar nombre, precio unitario, subtotal (`precio_base * cantidad`)
- [x] 6.3 Integrar `QuantityControl` para cambiar cantidad (llama a `updateQuantity`)
- [x] 6.4 Botón eliminar que llama a `removeItem(item.id)`
- [x] 6.5 Mostrar lista de ingredientes excluidos si `item.ingredientesExcluidos.length > 0` (solo IDs en esta iteración — mejora futura mostrar nombres)

## 7. Componente CartSummary

- [x] 7.1 Crear `frontend/src/features/carrito/components/CartSummary.tsx` — resumen con totales
- [x] 7.2 Mostrar `totalItems` y `totalPrice` formateado como ARS (`Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })`)
- [x] 7.3 Botón "Vaciar carrito" — llama a `clearCart()` con confirmación visual
- [x] 7.4 Botón "Confirmar pedido" — deshabilitado si `isCartEmpty`, ruta al checkout a definir en Epic 5

## 8. Componente CartDrawer

- [x] 8.1 Crear `frontend/src/features/carrito/components/CartDrawer.tsx` — panel lateral deslizante desde la derecha
- [x] 8.2 Controlar visibilidad con `useUIStore().activeModal === 'cart-drawer'`
- [x] 8.3 Implementar overlay con click-outside para cerrar (`closeModal()`)
- [x] 8.4 Implementar listener de tecla `Escape` para cerrar el drawer
- [x] 8.5 Renderizar lista de `CartItemCard` para cada item en `useCartStore().items`
- [x] 8.6 Renderizar `CartSummary` al fondo del drawer
- [x] 8.7 Mostrar estado vacío con mensaje "Tu carrito está vacío" y CTA al catálogo cuando `isCartEmpty`
- [x] 8.8 Agregar atributos de accessibility: `role="dialog"`, `aria-modal="true"`, `aria-label="Carrito de compras"`

## 9. Integración en Layout

- [x] 9.1 Importar y renderizar `CartDrawer` en `frontend/src/app/routes/layout.tsx` (fuera del `<main>`, en el root)
- [x] 9.2 Agregar badge de cantidad al header (ícono de carrito con `useCartStore().totalItems`) que abre el drawer con `openModal('cart-drawer')`
- [x] 9.3 Crear `frontend/src/features/carrito/components/CartBadge.tsx` — ícono con contador de items para el header

## 10. Verificación

- [x] 10.1 Verificar que `useCartStore` persiste items en localStorage tras recarga (inspección manual con DevTools)
- [x] 10.2 Verificar que al agregar el mismo producto sin personalización se incrementa la cantidad (no se crea item duplicado)
- [x] 10.3 Verificar que al agregar el mismo producto con distinta personalización se crean dos items separados
- [x] 10.4 Verificar que `toggleIngrediente` alterna correctamente la presencia del ingrediente
- [x] 10.5 Verificar que el CartDrawer se abre/cierra con el ícono del header, con Escape y con click en overlay
- [x] 10.6 Verificar que el total se recalcula correctamente al cambiar cantidades
