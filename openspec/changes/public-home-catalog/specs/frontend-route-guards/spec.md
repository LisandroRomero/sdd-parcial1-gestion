## MODIFIED Requirements

### Requirement: El frontend redirige usuarios no autenticados al login

El sistema SHALL proveer un componente `ProtectedRoute` que intercepte la navegacion a cualquier ruta privada y redirija al login si el usuario no esta autenticado. El componente DEBE estar integrado en `router.tsx` envolviendo todas las rutas que requieren autenticacion.

#### Scenario: Usuario no autenticado accede a ruta privada

- **WHEN** un usuario no autenticado intenta navegar a una ruta que requiere autenticacion (ej. `/pedidos`, `/perfil`, `/checkout`, `/admin`)
- **THEN** el sistema redirige al usuario a `/login` sin mostrar el contenido de la ruta solicitada

#### Scenario: Usuario autenticado accede a ruta privada

- **WHEN** un usuario autenticado navega a una ruta privada que no requiere rol especifico
- **THEN** el sistema renderiza el contenido de la ruta normalmente

#### Scenario: Rutas publicas accesibles sin autenticacion

- **WHEN** cualquier usuario (autenticado o no) navega a `/login` o `/register`
- **THEN** el sistema renderiza el contenido sin verificar autenticacion (el guard `PublicOnlyRoute` se aplica separadamente)

#### Scenario: ProtectedRoute integrado en el router protege rutas privadas bajo la raiz

- **WHEN** el router esta configurado con un branch protegido (envuelto por `ProtectedRoute`) en `path: "/"` sin `index`, que define children como `perfil`, `pedidos`, `checkout`, `admin/*`
- **THEN** cualquier acceso a esas rutas sin autenticacion resulta en redirect a `/login`
