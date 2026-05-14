## Context

El carrito de compras (Zustand store), la gestión de direcciones (entity + features) y el endpoint `POST /api/v1/pedidos` ya están implementados. Falta la página de checkout que conecte estos tres componentes en un flujo cohesivo para que el usuario pueda finalizar su compra.

Actualmente el `CartSummary` tiene un botón "Confirmar pedido" que está habilitado pero sin ruta definida — navegará a `/checkout`.

## Goals / Non-Goals

**Goals:**
- Proveer una página `/checkout` protegida (solo rol CLIENTE, ruta hija de `/`)
- Mostrar resumen completo del carrito (items, cantidades, subtotales, total)
- Permitir seleccionar dirección de entrega entre las direcciones guardadas del usuario
- Enviar `POST /api/v1/pedidos` con los datos del carrito y la dirección seleccionada
- Mostrar pantalla de confirmación con número de pedido tras creación exitosa
- Limpiar el carrito (Zustand store) después de un pedido exitoso

**Non-Goals:**
- No se implementa pago en esta iteración (es Epic separado 6.x)
- No se implementa edición de direcciones desde checkout (solo selección)
- No se implementa modificación de cantidades desde checkout (solo vista)

## Decisions

1. **Layout de 2 columnas**: Columna izquierda con resumen del carrito; columna derecha con selector de dirección + botón confirmar. En mobile se apilan verticalmente.
2. **useMutation de TanStack Query** para `POST /pedidos`: manejamos estados `isPending`, `isError`, `isSuccess` para controlar las pantallas (checkout → loading → confirmación/error).
3. **State-driven rendering**: 3 estados visuales manejados por la mutation:
   - `idle`: formulario checkout (resumen + selector dirección)
   - `pending`: spinner de carga
   - `success`: pantalla de confirmación con número de pedido
4. **useDirecciones() hook existente**: se reutiliza el hook de la feature `direcciones` para obtener las direcciones del usuario. Si no hay direcciones, se muestra mensaje con CTA a la página de perfil.
5. **Carrito se limpia en `onSuccess`** de la mutation via `useCartStore().clearCart()`, antes de navegar a la pantalla de confirmación.
6. **Ruta `/checkout`** como hija de `/` (ruta protegida con `ProtectedRoute` y rol CLIENTE).

## Risks / Trade-offs

- **Riesgo: Carrito vacío al llegar a checkout** → Mostrar estado vacío con CTA a catálogo. No permitir confirmar si `isCartEmpty`.
- **Riesgo: Error POST /pedidos (stock, dirección inválida, etc.)** → Mostrar mensaje de error específico según el error code devuelto por el backend y permitir reintentar sin perder la selección.
- **Riesgo: Usuario sin direcciones guardadas** → Mostrar mensaje "No tenés direcciones guardadas" con botón "Ir a mi perfil" para agregar una. Deshabilitar confirmar.
- **Riesgo: Refrescar la pantalla de confirmación** → El carrito ya fue limpiado, y la confirmación muestra datos de la respuesta (número de pedido). Si se refresca, se ve el estado vacío. Aceptable por ahora, en iteración futura se puede persistir el último pedido.
