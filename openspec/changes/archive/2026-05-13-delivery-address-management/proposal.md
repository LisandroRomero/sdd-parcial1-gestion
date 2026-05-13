## Why

Los usuarios clientes necesitan gestionar sus propias direcciones de entrega para poder asociarlas a sus pedidos. Actualmente el módulo `backend/direcciones/` tiene el modelo `DireccionEntrega` y los schemas básicos definidos, pero carece de repositorio, servicio, router y lógica de negocio. Sin esta funcionalidad los pedidos no pueden tener una dirección de entrega válida asignada, bloqueando el flujo completo de compra (Epic 3 en adelante).

## What Changes

- Agregar `deleted_at` al modelo `DireccionEntrega` para habilitar soft delete (el modelo actual no lo tiene)
- Extender el modelo con campos faltantes según spec: `calle`, `numero`, `piso`, `departamento`, `provincia` (el modelo actual usa `linea1`/`linea2` en su lugar)
- Implementar `DireccionEntregaRepository` con queries específicos de ownership y principal
- Implementar `DireccionEntregaService` con lógica de negocio: ownership check, regla de principal única
- Implementar `DireccionEntregaRouter` con 5 endpoints bajo `/api/v1/usuarios/me/direcciones`
- Registrar el repositorio en el `get_uow()` de `core/dependencies.py`
- Crear migración Alembic para los cambios de schema

Endpoints nuevos:
- `POST /api/v1/usuarios/me/direcciones` — crear dirección (roles: CLIENT, ADMIN)
- `GET /api/v1/usuarios/me/direcciones` — listar direcciones activas del usuario autenticado
- `PUT /api/v1/usuarios/me/direcciones/{id}` — actualizar dirección propia
- `DELETE /api/v1/usuarios/me/direcciones/{id}` — soft delete dirección propia
- `PATCH /api/v1/usuarios/me/direcciones/{id}/principal` — marcar como principal

## Capabilities

### New Capabilities

- `delivery-address-management`: CRUD completo de direcciones de entrega con ownership por usuario, marcado de principal y soft delete

### Modified Capabilities

- `database-models`: El modelo `DireccionEntrega` cambia su estructura de campos (agrega `deleted_at`, reemplaza `linea1`/`linea2` por campos granulares según spec v5.0: `calle`, `numero`, `piso`, `departamento`, `provincia`)

## Impact

- `backend/direcciones/model.py` — modificación de campos + agregar `deleted_at`
- `backend/direcciones/schemas.py` — actualizar schemas para campos nuevos
- `backend/direcciones/repository.py` — implementar desde cero
- `backend/direcciones/service.py` — implementar desde cero
- `backend/direcciones/router.py` — implementar desde cero
- `backend/core/dependencies.py` — registrar `DireccionEntregaRepository` en `_register_repos`
- `backend/main.py` — incluir el router de direcciones
- `alembic/versions/` — nueva migración para cambios en tabla `direccionentrega`
- Historias de usuario afectadas: US-024, US-025, US-026, US-027, US-028
