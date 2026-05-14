## Why

El cliente necesita una interfaz gráfica para gestionar su perfil y direcciones de entrega. Actualmente los endpoints backend existen (cambios 3.1 y 3.2 archivados), pero no hay UI que los consumo. Sin esta página, el cliente no puede ver/editar sus datos personales ni administrar sus direcciones de envío.

## What Changes

- Crear página `/perfil` con dos secciones: datos del perfil y gestión de direcciones
- Formulario de perfil: ver y editar nombre, apellido y teléfono
- Gestión de direcciones: listar, crear, editar, eliminar y marcar dirección principal
- Agregar enlace "Mi Perfil" en la navegación para usuarios autenticados
- Hooks y mutaciones de TanStack Query para consumir APIs de perfil y direcciones
- Manejo de estados: carga, error, vacío, éxito con toast notifications

## Capabilities

### New Capabilities
- `frontend-profile-page`: Página de perfil del cliente autenticado con visualización y edición de datos personales (nombre, apellido, teléfono), consumiendo `GET/PUT /api/v1/usuarios/me/perfil`
- `frontend-address-management`: Gestión completa de direcciones de entrega desde el frontend con ABM y marcado de principal, consumiendo los endpoints `/api/v1/usuarios/me/direcciones/*`

### Modified Capabilities
- *(Ninguna — los specs backend ya están definidos y archivados)*

## Impact

- **Frontend**: nuevas páginas, componentes, hooks de TanStack Query, integración con APIs existentes
- **Enrutamiento**: nueva ruta protegida `/perfil` en el router de React
- **Navegación**: nuevo link "Mi Perfil" en el header para usuarios autenticados
- **No afecta backend**: los endpoints ya existen y están probados
