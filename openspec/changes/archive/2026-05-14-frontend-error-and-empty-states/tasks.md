## 1. Shared UI States (foundation)

- [x] 1.1 Auditar componentes existentes en `frontend/src/shared/ui` (ErrorMessage, EmptyState, loading/skeletons) y definir cuales se reutilizan vs se crean
- [x] 1.2 Estandarizar `ErrorMessage` para uso inline (props `message`, `onRetry?`, variante compacta si aplica)
- [x] 1.3 Estandarizar `EmptyState` con API consistente y soporte de CTA default por pantalla
- [x] 1.4 Crear `OfflineMessage` (inline) en `frontend/src/shared/ui` para comunicar estado sin conexion
- [x] 1.5 Crear `NoPermissionMessage` (inline) en `frontend/src/shared/ui` con CTAs para 401 (iniciar sesion) y 403 (volver/navegar)
- [x] 1.6 Crear/estandarizar un loading compartido (skeleton/placeholder) reutilizable para pantallas principales
- [x] 1.7 Exportar los componentes de estados desde un barrel (`frontend/src/shared/ui/index.ts`) para imports consistentes

## 2. Shared Mapping & Hooks

- [x] 2.1 Reutilizar `getErrorMessage` y documentar regla: toda UI de error deriva el texto desde este helper
- [x] 2.2 Implementar `useOffline()` en `frontend/src/shared/lib/hooks/useOffline.ts` basado en `navigator.onLine` + eventos `online/offline`
- [x] 2.3 Definir helper liviano para detectar 401/403 desde `AxiosError` (sin duplicar mapeo) y mapear a `NoPermissionMessage`
- [x] 2.4 Definir patrones de TanStack Query (query principal vs refetch con data previa) y una guia de aplicacion por pantalla

## 3. Integrations: Public Catalog & Product

- [x] 3.1 Catalogo: integrar loading/empty/error inline segun reglas de TanStack Query (sin romper grid actual)
- [x] 3.2 Detalle de producto: integrar loading/empty/error inline y CTA de reintento
- [x] 3.3 Catalogo/Detalle: si `useOffline()` esta activo, mostrar `OfflineMessage` (y deshabilitar reintentos si corresponde)

## 4. Integrations: Cart & Checkout

- [x] 4.1 Carrito: integrar empty state con CTA por defecto (ir al catalogo) y loading/error inline donde aplique
- [x] 4.2 Checkout page: reemplazar mensaje de error ad-hoc por `ErrorMessage` inline usando `getErrorMessage` + retry cuando aplique
- [x] 4.3 Checkout: manejar offline con `OfflineMessage` en acciones criticas (confirmar pago / crear preferencia)
- [x] 4.4 Checkout: mapear 401/403 a `NoPermissionMessage` (sin full-page)

## 5. Integrations: Orders

- [x] 5.1 Pedidos lista: reemplazar mensajes de error ad-hoc por `ErrorMessage` inline usando `getErrorMessage`
- [x] 5.2 Pedidos lista: empty state con CTA default segun rol (cliente -> ir a catalogo; staff/admin -> limpiar filtros o ver todos)
- [x] 5.3 Pedido detalle: mapear loading/error/not-found y asegurar que errores no borren data existente en refetch
- [x] 5.4 Pedido detalle: mutations (cancelar/avanzar) muestran error inline cercano al CTA y permiten reintento cuando tenga sentido
- [x] 5.5 Pedidos: offline state visible (y evitar reintentos enganiosos)

## 6. Integrations: Profile & Addresses

- [x] 6.1 Perfil page: usar `getErrorMessage(error)` en lugar de `error.message` para error inline
- [x] 6.2 Perfil page: al no haber perfil (`!perfil`), asegurar empty state con CTA (reintentar/recargar) definido
- [x] 6.3 Direcciones: validar consistencia (loading, error, empty) con nuevos componentes estandarizados
- [x] 6.4 Direcciones: mutations (crear/editar/eliminar/marcar principal) muestran errores consistentes (toast o inline) usando `getErrorMessage`

## 7. Integrations: Admin Panels

- [x] 7.1 Admin usuarios: integrar loading/error/empty inline en tabla/lista principal y `NoPermissionMessage` para 401/403
- [x] 7.2 Admin productos: integrar loading/error/empty inline y consolidar mensajes (sin duplicar strings)
- [x] 7.3 Admin categorias: integrar loading/error/empty inline y offline state
- [x] 7.4 Admin ingredientes: integrar loading/error/empty inline y offline state
- [x] 7.5 Admin configuracion pagos: integrar loading/error/empty inline y no-permission

## 8. Cleanup & Docs

- [x] 8.1 Reemplazar manejos ad-hoc restantes (mensajes sueltos, estados inconsistentes) por shared UI states
- [x] 8.2 Revisar exports/imports para mantener FSD (Pages -> Features -> Entities -> Shared)
- [x] 8.3 Documentar la guia de estados (loading/empty/error/offline/no-permission) y ejemplos con TanStack Query en docs del frontend si aplica
- [x] 8.4 Verificar que todas las pantallas clave cumplen: error inline + retry, empty con CTA, offline/no-permission mapeados
