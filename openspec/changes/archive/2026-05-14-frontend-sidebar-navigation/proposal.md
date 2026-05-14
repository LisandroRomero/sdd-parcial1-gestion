## Why

Hoy la navegacion principal es basicamente un top navbar. En pantallas grandes eso desperdicia espacio, escala mal cuando crece la cantidad de secciones, y hace que el usuario pierda contexto sobre donde esta parado.

Agregar una sidebar persistente mejora la UX en desktop (descubribilidad, menor friccion para navegar entre modulos) sin degradar mobile, donde debe seguir siendo accesible via drawer.

## What Changes

- Incorporar un layout de navegacion con **sidebar en desktop** y **top navbar** complementaria.
- En mobile/tablet, la sidebar se presenta como **drawer** (off-canvas) con apertura/cierre y manejo correcto de foco.
- La lista de items de navegacion soporta:
  - estado activo (ruta actual)
  - agrupacion/separadores
  - render condicional segun autenticacion y rol
- (Opcional) Persistir preferencia de usuario para sidebar colapsada/expandida.

## Capabilities

### New Capabilities

- `frontend-sidebar-navigation`: Navegacion principal con sidebar (desktop) y drawer/collapsible (responsive), integrada al router y alineada a FSD.
- `frontend-sidebar-navigation-access-control`: Items de navegacion visibles/ocultos segun autenticacion y roles, consistente con los guards existentes.
- `frontend-sidebar-navigation-state-persistence`: Persistencia opcional de estado (colapsada/expandida) y restauracion al recargar.

### Modified Capabilities

<!-- (none) -->

## Impact

- Frontend (React + Router + Tailwind): cambios en el layout de la app y componentes de navegacion.
- Router: integracion para resaltar item activo y mantener experiencia consistente con rutas protegidas.
- Accesibilidad: ARIA, navegacion por teclado, focus trap al usar drawer.
- Estado de UI: puede requerir store para abrir/cerrar/persistir colapso (sin duplicar estado de servidor).
