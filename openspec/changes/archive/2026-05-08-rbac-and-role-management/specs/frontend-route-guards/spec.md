## ADDED Requirements

### Requirement: El frontend redirige usuarios no autenticados al login

El sistema SHALL proveer un componente `ProtectedRoute` que intercepte la navegación a cualquier ruta privada y redirija al login si el usuario no está autenticado.

#### Scenario: Usuario no autenticado accede a ruta privada

- **WHEN** un usuario no autenticado intenta navegar a una ruta que requiere autenticación (ej. `/pedidos`, `/perfil`, `/admin`)
- **THEN** el sistema redirige al usuario a `/login` sin mostrar el contenido de la ruta solicitada

#### Scenario: Usuario autenticado accede a ruta privada

- **WHEN** un usuario autenticado navega a una ruta privada que no requiere rol específico
- **THEN** el sistema renderiza el contenido de la ruta normalmente

#### Scenario: Rutas públicas accesibles sin autenticación

- **WHEN** cualquier usuario (autenticado o no) navega a `/`, `/login`, `/registro` o `/catalogo`
- **THEN** el sistema renderiza el contenido sin verificar autenticación

### Requirement: El frontend restringe rutas por rol

El sistema SHALL proveer un componente `RoleGuard` que verifique que el usuario autenticado posee el rol requerido para una ruta, retornando una pantalla 403 o redirigiendo si el rol es insuficiente.

#### Scenario: Usuario con rol correcto accede a ruta restringida

- **WHEN** un usuario con rol ADMIN navega a una ruta que requiere ADMIN (ej. `/admin/usuarios`)
- **THEN** el sistema renderiza el contenido de la ruta

#### Scenario: Usuario sin rol requerido ve pantalla de acceso denegado

- **WHEN** un usuario autenticado con rol CLIENT intenta navegar a una ruta que requiere ADMIN o STOCK
- **THEN** el sistema muestra una pantalla 403 o redirige a una ruta segura

### Requirement: El authStore expone hasRole para verificación de roles

El sistema SHALL proveer un método `hasRole(role: string): boolean` en el `authStore` que verifique si el usuario autenticado posee un rol dado.

#### Scenario: hasRole retorna true para rol que el usuario posee

- **WHEN** `hasRole("ADMIN")` es llamado y el usuario autenticado tiene `roles: ["ADMIN", "CLIENT"]`
- **THEN** retorna `true`

#### Scenario: hasRole retorna false para rol que el usuario no posee

- **WHEN** `hasRole("STOCK")` es llamado y el usuario autenticado tiene `roles: ["CLIENT"]`
- **THEN** retorna `false`

#### Scenario: hasRole retorna false si no hay usuario autenticado

- **WHEN** `hasRole("ADMIN")` es llamado y `user` es `null`
- **THEN** retorna `false`
