## ADDED Requirements

### Requirement: Shared UI states are standardized across the frontend
El frontend MUST estandarizar el manejo de estados de UI para todas las superficies (publicas, autenticadas y admin) usando componentes compartidos.

#### Scenario: Screen renders a standardized loading state
- **WHEN** una pantalla tiene una query principal en estado `isLoading`/`isPending` y aun no existe `data`
- **THEN** la pantalla MUST mostrar un estado de loading consistente (skeleton o placeholder compartido) sin contenido final

#### Scenario: Screen renders a standardized empty state
- **WHEN** una pantalla recibe `data` exitosamente y el resultado funcional esta vacio (por ejemplo lista vacia)
- **THEN** la pantalla MUST mostrar un `EmptyState` con titulo, descripcion y un CTA por defecto relevante a la pantalla

### Requirement: Errors are shown inline with consistent messaging
Los errores MUST mostrarse inline (no como pantalla completa) y MUST usar un mapeo consistente de mensajes.

#### Scenario: Inline error uses shared error message mapping
- **WHEN** una query o mutation falla con `error: unknown`
- **THEN** el mensaje mostrado MUST derivarse de `getErrorMessage(error)` (o equivalente exportado desde `@/shared/api`)

#### Scenario: Inline error offers retry when possible
- **WHEN** una query falla y existe una accion de reintento disponible (`refetch`)
- **THEN** el componente de error MUST exponer un CTA de reintento que dispare `refetch`

### Requirement: Offline state is detected and communicated
El frontend MUST detectar estado offline del navegador y comunicarlo como un estado explicito.

#### Scenario: Offline is detected via browser connectivity
- **WHEN** `navigator.onLine` es `false` o el browser dispara el evento `offline`
- **THEN** el frontend MUST considerar el estado offline activo hasta recibir el evento `online`

#### Scenario: Offline state prevents misleading retries
- **WHEN** el estado offline esta activo y una pantalla intenta mostrar error con reintento
- **THEN** la UI MUST indicar que no hay conexion y MUST evitar presentar reintentos que no puedan ejecutarse (o MUST deshabilitarlos)

### Requirement: No-permission state is mapped and shown inline
El frontend MUST manejar estados de no-permission tanto por autenticacion como por autorizacion.

#### Scenario: Unauthorized API response maps to no-permission message
- **WHEN** una request falla con HTTP 401
- **THEN** la UI MUST mostrar un estado inline de no-permission con CTA para iniciar sesion

#### Scenario: Forbidden API response maps to no-permission message
- **WHEN** una request falla con HTTP 403
- **THEN** la UI MUST mostrar un estado inline de no-permission con CTA para volver o navegar a un lugar seguro

### Requirement: Shared components live under shared UI module
Los componentes de estados MUST existir en un modulo compartido del frontend para ser consumidos por paginas, features y entities.

#### Scenario: Components are located under shared UI path
- **WHEN** se implementan componentes de estados (error/empty/offline/loading)
- **THEN** sus fuentes MUST ubicarse bajo `frontend/src/shared/ui` (o subcarpetas) y MUST exportarse de forma consistente para su consumo

### Requirement: TanStack Query state mapping rules are applied
El frontend MUST aplicar reglas consistentes para mapear estados de TanStack Query a estados de UI.

#### Scenario: Error does not wipe existing data
- **WHEN** una query tiene `data` previa y luego ocurre un error en un refetch
- **THEN** la pantalla MUST conservar la UI basada en `data` y MUST mostrar el error inline de forma no bloqueante

#### Scenario: Fetching does not replace the main content
- **WHEN** una query esta en `isFetching` pero ya existe `data`
- **THEN** la pantalla MUST mantener el contenido principal visible y MAY mostrar un indicador sutil de refresco
