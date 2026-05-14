## ADDED Requirements

### Requirement: Desktop layout SHALL provide a persistent sidebar navigation
El frontend SHALL renderizar un layout con un `aside` persistente en viewport desktop, conteniendo la navegacion primaria del usuario (incluyendo secciones publicas y privadas segun corresponda).

#### Scenario: Desktop renders sidebar with primary navigation
- **WHEN** el usuario navega el sitio en un viewport que cumple el breakpoint de desktop
- **THEN** el layout SHALL renderizar un `aside` visible con items de navegacion
- **THEN** el contenido principal SHALL renderizarse en `main` junto a la sidebar

### Requirement: Mobile layout SHALL provide the sidebar as a drawer
En viewport mobile/tablet, la navegacion de sidebar SHALL presentarse como un drawer off-canvas que puede abrirse/cerrarse mediante un trigger en la top navbar.

#### Scenario: Mobile uses drawer instead of persistent sidebar
- **WHEN** el usuario navega el sitio en un viewport mobile/tablet
- **THEN** el layout SHALL NOT renderizar un `aside` persistente visible
- **THEN** la navegacion SHALL estar disponible en un drawer que puede abrirse desde la top navbar

### Requirement: Navigation items SHALL reflect the active route
Los items de navegacion SHALL indicar el estado activo basado en la ruta actual (incluyendo rutas anidadas) para que el usuario tenga contexto de ubicacion.

#### Scenario: Active item matches current route
- **WHEN** la ruta actual coincide con el `to` de un item (o un descendiente cuando corresponda)
- **THEN** el item correspondiente SHALL renderizarse con un estilo de estado activo

### Requirement: Sidebar SHALL support collapsible mode on desktop
La sidebar en desktop SHALL permitir alternar entre expandida y colapsada (ej. icons-only) para optimizar espacio.

#### Scenario: User collapses and expands sidebar
- **WHEN** el usuario activa el control de colapso en desktop
- **THEN** la sidebar SHALL cambiar entre estado expandido y colapsado sin perder navegacion

### Requirement: Drawer SHALL be accessible and keyboard operable
El drawer de navegacion SHALL cumplir requerimientos basicos de accesibilidad: etiquetado ARIA, cierre por `Escape`, bloqueo de interaccion con el fondo, y manejo correcto de foco.

#### Scenario: Drawer uses dialog semantics
- **WHEN** el drawer esta abierto
- **THEN** el contenedor del drawer SHALL tener `role="dialog"` y `aria-modal="true"`
- **THEN** el drawer SHALL exponer un titulo accesible via `aria-labelledby` (o equivalente)

#### Scenario: Escape closes drawer and returns focus to trigger
- **WHEN** el drawer esta abierto y el usuario presiona `Escape`
- **THEN** el drawer SHALL cerrarse
- **THEN** el foco SHALL volver al elemento trigger que lo abrio

#### Scenario: Tab key is trapped within the drawer while open
- **WHEN** el drawer esta abierto y el usuario navega con `Tab`
- **THEN** el foco SHALL permanecer dentro de los elementos focusables del drawer
