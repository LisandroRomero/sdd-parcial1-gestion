## 1. Entities — Pedidos

- [x] 1.1 Crear `frontend/src/entities/pedidos/types.ts` con `PedidoCreate`, `PedidoRead`, `DetallePedidoCreate`
- [x] 1.2 Crear `frontend/src/entities/pedidos/api.ts` con función `createPedido(data: PedidoCreate): Promise<PedidoRead>` usando Axios POST a `/api/v1/pedidos`
- [x] 1.3 Crear `frontend/src/entities/pedidos/index.ts` barrel export

## 2. Features — Checkout Hooks

- [x] 2.1 Crear `frontend/src/features/checkout/hooks/useCheckout.ts` con `useMutation` para `POST /pedidos`, manejando `onSuccess` (limpiar carrito con `clearCart()`) y `onError`
- [x] 2.2 Agregar `getItemsForCheckout(): DetallePedidoCreate[]` al Zustand store `cart.store.ts`

## 3. Features — Checkout Components

- [x] 3.1 Crear `frontend/src/features/checkout/CheckoutSummary.tsx` — componente que muestra resumen del carrito (items, cantidades, subtotales, total) consumiendo `useCartStore`
- [x] 3.2 Crear `frontend/src/features/checkout/AddressSelector.tsx` — componente que lista direcciones usando `useDirecciones()` y permite seleccionar una, mostrando estado vacío si no hay direcciones
- [x] 3.3 Crear `frontend/src/features/checkout/OrderConfirmation.tsx` — pantalla de éxito con ícono, número de pedido, resumen breve y botón "Volver al catálogo"

## 4. Page — Checkout Page + Routing

- [x] 4.1 Crear `frontend/src/pages/checkout/CheckoutPage.tsx` con layout de 2 columnas y 3 estados (idle → checkout form, pending → spinner, success → confirmación)
- [x] 4.2 Crear `frontend/src/pages/checkout/index.ts` barrel export
- [x] 4.3 Agregar ruta `/checkout` en `frontend/src/app/router.tsx` como ruta hija protegida (rol CLIENTE, `ProtectedRoute`)

## 5. Integración y Edge Cases

- [x] 5.1 Manejar carrito vacío en checkout: mostrar mensaje con CTA a catálogo, deshabilitar botón confirmar
- [x] 5.2 Manejar usuario sin direcciones: mostrar mensaje con CTA a `/perfil`, deshabilitar botón confirmar
- [x] 5.3 Manejar error POST /pedidos: mostrar error específico según código (stock, dirección, producto no disponible) con opción de reintentar cuando corresponda
- [x] 5.4 Actualizar `frontend/src/features/carrito/components/CartSummary.tsx` para que "Confirmar pedido" navegue a `/checkout` en lugar de mostrar placeholder
