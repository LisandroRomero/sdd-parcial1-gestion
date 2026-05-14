## 1. Navigation Model

- [x] 1.1 Definir modelo tipado de items de navegacion (label, to, requiereAuth, roles opcionales, icon opcional)
- [x] 1.2 Crear una unica fuente de verdad de items (con secciones publicas/privadas/admin)
- [x] 1.3 Implementar helper de filtrado por `isAuthenticated` y `user.roles`

## 2. Desktop Sidebar

- [x] 2.1 Reestructurar `Layout` para incluir `aside` (sidebar) + `main` (contenido)
- [x] 2.2 Renderizar items de navegacion en sidebar con estado activo segun ruta
- [x] 2.3 Implementar toggle de colapso/expansion en desktop

## 3. Mobile Drawer

- [x] 3.1 Agregar trigger en top navbar para abrir/cerrar drawer
- [x] 3.2 Implementar drawer off-canvas con overlay y bloqueo de scroll del body
- [x] 3.3 Implementar cierre por click en overlay y por tecla `Escape`
- [x] 3.4 Implementar focus trap dentro del drawer y devolver foco al trigger al cerrar
- [x] 3.5 Aplicar atributos ARIA (`role="dialog"`, `aria-modal`, titulo accesible)

## 4. Access Control In Navigation

- [x] 4.1 Ocultar items privados cuando `isAuthenticated` sea false
- [x] 4.2 Ocultar items admin cuando el usuario no tenga rol `ADMIN`
- [x] 4.3 Asegurar que items ocultos NO rendericen links interactivos

## 5. Optional Persistence

- [x] 5.1 Persistir el estado colapsada/expandida en `localStorage` con key estable (ej. `ui.sidebar.collapsed`)
- [x] 5.2 Restaurar el estado persistido al iniciar la app

## 6. UX Polish

- [x] 6.1 Ajustar header para convivir con sidebar (branding + acciones globales + trigger)
- [x] 6.2 Validar navegacion por teclado en sidebar y drawer (Tab/Shift+Tab/Enter)
- [x] 6.3 Revisar responsive en breakpoints principales (mobile, tablet, desktop)
