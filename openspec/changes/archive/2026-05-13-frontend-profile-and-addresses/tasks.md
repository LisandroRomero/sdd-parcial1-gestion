## 1. Routing y navegación

- [x] 1.1 Agregar ruta protegida `/perfil` en `app/router.tsx` dentro del Layout, con lazy loading de `PerfilPage`
- [x] 1.2 Agregar link "Mi Perfil" en la navbar del Layout para usuarios autenticados

## 2. Hooks de TanStack Query — Perfil

- [x] 2.1 Crear `features/perfil/hooks/usePerfil.ts` con `useQuery` para `GET /api/v1/usuarios/me/perfil` (queryKey: `['perfil']`)
- [x] 2.2 Agregar `useMutation` para `PUT /api/v1/usuarios/me/perfil` con invalidación de `['perfil']` en `onSuccess`

## 3. Página de Perfil — Sección "Mis Datos"

- [x] 3.1 Crear `pages/perfil/PerfilPage.tsx` como página principal con layout de dos secciones: "Mis Datos" y "Mis Direcciones"
- [x] 3.2 Crear `features/perfil/components/ProfileForm.tsx` con formulario (useState) (nombre, apellido, email readonly, teléfono) precargado con datos del perfil
- [x] 3.3 Implementar validación de formulario: nombre y apellido requeridos (min 2, max 80), teléfono opcional
- [x] 3.4 Manejar estados: skeleton loader mientras carga perfil, error con botón de reintentar

## 4. Hooks de TanStack Query — Direcciones

- [x] 4.1 Crear `features/direcciones/hooks/useDirecciones.ts` con `useQuery` para `GET /api/v1/usuarios/me/direcciones` (queryKey: `['direcciones']`)
- [x] 4.2 Agregar `useMutation` para crear dirección (`POST`), editar (`PUT`), eliminar (`DELETE`), y marcar principal (`PATCH`) con invalidación de `['direcciones']`
- [x] 4.3 Implementar actualización optimista para marcar principal: `onMutate` actualiza caché, `onError` revierte, `onSettled` invalida

## 5. Página de Perfil — Sección "Mis Direcciones"

- [x] 5.1 Crear `features/direcciones/components/DireccionesList.tsx` con listado de tarjetas de dirección
- [x] 5.2 Crear `features/direcciones/components/DireccionCard.tsx` con datos de dirección, badge "Principal", y botones Editar/Eliminar/Marcar principal
- [x] 5.3 Crear `features/direcciones/components/DireccionFormModal.tsx` con formulario para crear/editar dirección (alias, calle, número, piso, depto, ciudad, provincia, código postal)
- [x] 5.4 Crear `features/direcciones/components/DeleteConfirmDialog.tsx` con confirmación antes de eliminar
- [x] 5.5 Manejar estados: skeleton de tarjetas mientras carga, estado vacío con CTA "Agregar dirección", error con reintentar

## 6. Integración y polish

- [x] 6.1 Agregar barrel exports en `features/perfil/index.ts` y `features/direcciones/index.ts`
- [x] 6.2 Verificar que toda la navegación funciona: ruta protegida redirige a login si no autenticado
- [x] 6.3 Verificar que el layout responsive funciona en mobile con las dos secciones apiladas
