## Context

El frontend actual tiene estructura FSD con routing protegido, layout con navbar, y stores Zustand configurados. Los backends de perfil (3.2) y direcciones (3.1) ya están implementados y archivados con las siguientes APIs:

- `GET /api/v1/usuarios/me/perfil` → `PerfilRead` (nombre, apellido, email, teléfono, roles, direcciones activas)
- `PUT /api/v1/usuarios/me/perfil` → actualiza nombre, apellido, teléfono
- `GET /api/v1/usuarios/me/direcciones` → lista de `DireccionEntregaRead`
- `POST /api/v1/usuarios/me/direcciones` → crear dirección
- `PUT /api/v1/usuarios/me/direcciones/{id}` → actualizar dirección
- `PATCH /api/v1/usuarios/me/direcciones/{id}/principal` → marcar como principal
- `DELETE /api/v1/usuarios/me/direcciones/{id}` → soft delete

El frontend usa TanStack Query para datos del servidor y Zustand para estado del cliente (sesión, carrito, UI). El interceptor Axios ya maneja JWT automáticamente.

## Goals / Non-Goals

**Goals:**
- Crear página `/perfil` protegida (requiere autenticación, rol CLIENT o superior)
- Sección "Mis Datos": formulario precargado para ver/editar nombre, apellido y teléfono
- Sección "Mis Direcciones": listado de direcciones con ABM completo + marcado de principal
- Validación visual de formularios (TanStack Form)
- Manejo de estados: loading (skeleton), error (toast + mensaje), empty (mensaje + CTA), success (toast)
- Integración en la navbar con link "Mi Perfil" visible solo para autenticados

**Non-Goals:**
- No se modifican endpoints backend (ya existen)
- No se maneja cambio de email ni contraseña (no están en los specs)
- No se implementa paginación de direcciones (el volumen esperado es bajo)
- No se implementa soft delete con confirmación en frontend (se hace toast nomás)

## Decisions

### 1. Página única con tabs / secciones verticales vs. páginas separadas
**Decisión:** Una sola página `/perfil` con dos secciones verticales (Mis Datos arriba, Mis Direcciones abajo).
**Razón:** El volumen de contenido justifica una página única. El perfil es compacto (3-4 campos) y las direcciones son un listado. Dos páginas separadas agregaría complejidad de navegación innecesaria.
**Alternativa:** Dos rutas `/perfil` y `/direcciones` — descartado porque agrega fricción al usuario.

### 2. TanStack Query hooks separados por dominio
**Decisión:** Dos hooks personalizados: `usePerfil()` y `useDirecciones()`.
**Razón:** Separa concerns. El perfil se consulta una vez y rara vez cambia. Las direcciones pueden mutar frecuentemente. Invalidación independiente.
**Estructura:**
- `features/perfil/hooks/usePerfil.ts` — `useQuery` para GET + `useMutation` para PUT
- `features/direcciones/hooks/useDirecciones.ts` — `useQuery` para GET + `useMutation` para POST/PUT/PATCH/DELETE

### 3. Formulario de perfil con TanStack Form
**Decisión:** Usar TanStack Form (ya es dependencia del proyecto) para el formulario de edición de perfil.
**Razón:** Consistencia con el stack definido en la spec. Validación declarativa y tipada.
**Validaciones:**
- `nombre`: requerido, min 2 chars, max 80
- `apellido`: requerido, min 2 chars, max 80
- `telefono`: opcional, si se ingresa validar formato

### 4. Direcciones con modal/drawer para crear/editar
**Decisión:** Modal para crear/editar dirección inline en la misma página. Tarjeta por dirección con acciones (editar, eliminar, marcar principal).
**Razón:** Mejor UX que un formulario en línea — no desplaza el contenido. Sigue el patrón de modales ya existente en el proyecto.
**Campos del formulario:** alias, calle, número, piso (opcional), depto (opcional), ciudad, provincia, código postal.

### 5. Invalidación optimista con TanStack Query
**Decisión:** Usar `onMutate` para actualización optimista del caché en operaciones frecuentes (marcar principal, eliminar). `onSettled` para invalidar y refetch como respaldo.
**Razón:** Marcar dirección como principal debe sentirse instantáneo. Si la API falla, el rollback restaura el estado anterior.

### 6. Ruta protegida con rol CLIENT+
**Decisión:** La ruta `/perfil` usa `<ProtectedRoute />` + `<RoleGuard roles={['CLIENT', 'ADMIN']} />`.
**Razón:** Solo CLIENT puede ver su perfil (US-061). ADMIN también. STOCK y PEDIDOS no tienen perfil de cliente.

## Risks / Trade-offs

- **[Riesgo] Mutaciones concurrentes en direcciones** → Las operaciones de marcar principal y editar son atómicas en backend (UoW). El frontend optimista puede mostrar estado inconsistente por milisegundos hasta el refetch. Aceptable.
- **[Riesgo] Perfil editado por otro usuario** → No aplica, cada usuario solo ve su propio perfil (ownership por JWT).
- **[Trade-off] Una sola página con scroll** → Si el usuario tiene muchas direcciones, la página se alarga. Alternativa con tabs se consideró pero el volumen esperado (2-5 direcciones por usuario) no lo justifica.
