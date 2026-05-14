## Why

Los usuarios necesitan un flujo de checkout donde puedan revisar su carrito, seleccionar dirección de entrega y confirmar el pedido, recibiendo un número de seguimiento como confirmación.

## What Changes

- Crear página `/checkout` (ruta protegida, solo rol Cliente)
- Componente resumen del carrito (items, cantidades, subtotal por item, total general)
- Selector de dirección de entrega desde direcciones guardadas del usuario
- Botón "Confirmar pedido" → `POST /api/v1/pedidos`
- Pantalla de confirmación con número de pedido y resumen
- Limpiar carrito (Zustand store) después de crear pedido exitosamente

## Capabilities

### New Capabilities
- `frontend-checkout-page`: Página de checkout con resumen del carrito, selector de dirección y confirmación de pedido

### Modified Capabilities
- `shopping-cart`: El carrito debe poder ser leído desde la página de checkout y limpiado después de una compra exitosa
- `frontend-address-management`: Las direcciones guardadas deben poder ser seleccionadas desde el checkout (no solo desde gestión de perfil)
- `order-creation`: El frontend necesita una interfaz (entity + api) para consumir el endpoint `POST /pedidos`

## Impact

- **Frontend only**: nueva feature `checkout` en `pages/checkout/`, entities `pedidos/`, y routing en `/checkout`
- Depende de POST /pedidos backend (ya implementado en Epic 5.1)
- Depende de direcciones de entrega (ya implementado en Epic 3.1)
- Depende del carrito Zustand store (ya implementado en Epic 4.1)
