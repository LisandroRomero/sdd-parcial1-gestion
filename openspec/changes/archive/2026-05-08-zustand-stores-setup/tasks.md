## 1. Instalación y estructura

- [x] 1.1 Instalar `zustand` v4 como dependencia del frontend
- [x] 1.2 Crear directorio `shared/lib/stores/` con barrel export (`index.ts`)

## 2. authStore — Sesión de usuario

- [x] 2.1 Definir tipos `AuthState` y acciones (user, token, isAuthenticated, login, logout, updateUser)
- [x] 2.2 Implementar `authStore` con Zustand `create` — estado en memoria, sin persistencia
- [x] 2.3 Exportar hook `useAuthStore` y store object desde barrel

## 3. cartStore — Carrito de compras

- [x] 3.1 Definir tipo `CartItem` (id, productoId, nombre, precioUnitario, cantidad, imagenUrl?, ingredientesExcluidos?)
- [x] 3.2 Implementar `cartStore` con persist middleware en localStorage (versión 1)
- [x] 3.3 Implementar `addItem` con lógica de merge (mismo producto + personalización = incrementar)
- [x] 3.4 Implementar `removeItem`, `updateQuantity` (auto-eliminar si cantidad <= 0)
- [x] 3.5 Implementar `updateCustomization` para ingredientes excluidos
- [x] 3.6 Implementar `clearCart`, getters `totalItems`, `totalPrice`, `isCartEmpty`
- [x] 3.7 Exportar hook y store object desde barrel

## 4. paymentStore — Estado de pagos

- [x] 4.1 Definir tipo `PaymentStatus` (idle | processing | approved | rejected | pending)
- [x] 4.2 Definir interfaz `PaymentState` (preferenceId, status, paymentId, error)
- [x] 4.3 Implementar `paymentStore` con todas las acciones (setPreferenceId, setApproved, setRejected, setProcessing, resetState)
- [x] 4.4 Exportar hook y store object desde barrel

## 5. uiStore — Estado de interfaz de usuario

- [x] 5.1 Definir interfaz `UIState` (sidebarOpen, theme, activeModal, toast)
- [x] 5.2 Implementar `uiStore` con persist middleware y `partialize` para persistir solo sidebarOpen y theme
- [x] 5.3 Implementar acciones de sidebar (toggleSidebar, setSidebar)
- [x] 5.4 Implementar acciones de tema (setTheme)
- [x] 5.5 Implementar acciones de modal (openModal, closeModal)
- [x] 5.6 Implementar acciones de toast (showToast, hideToast)
- [x] 5.7 Exportar hook y store object desde barrel

## 6. Verificación

- [x] 6.1 Verificar que el build de TypeScript compile sin errores (`tsc -b`)
- [x] 6.2 Verificar que `npm run dev` arranque sin errores
- [x] 6.3 Verificar barrel exports importables desde `@/shared/lib/stores`
