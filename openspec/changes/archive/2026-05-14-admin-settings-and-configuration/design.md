## Context

La tabla `formapago` existe en BD con registros TARJETA, RAPIPAGO, PAGO_FACIL (seeded). El modelo `FormaPago` solo tiene `codigo`, `descripcion`, `created_at` — no hay `activo`. Los listados de productos, categorías e ingredientes filtran soft-deleted vía `WHERE deleted_at IS NULL` en los services/repositories, sin opción de override. El módulo `backend/admin/` ya tiene router, service, schemas implementados (7.2).

## Goals / Non-Goals

**Goals:**
- Agregar `activo: bool` a `FormaPago` con migración Alembic
- Endpoints admin para leer y togglear formas de pago
- Param `include_deleted` en listados de catálogo (solo válido para ADMIN/STOCK)
- Página `/admin/configuracion` con gestión de formas de pago
- Toggle "Mostrar eliminados" en los 3 paneles admin de catálogo

**Non-Goals:**
- Tabla `Configuracion` key-value genérica (no hay modelo ni migración prevista)
- Horarios de atención, zonas de entrega (fuera de scope del parcial)
- Restaurar (undelete) entidades soft-deleted — solo visualización
- Validar en checkout si una forma de pago está activa (scope de Epic 6)

## Decisions

### D1: `activo` en FormaPago — sin CASCADE a pedidos existentes

**Decisión:** El campo `activo` solo afecta si la forma de pago aparece disponible para nuevos pedidos. Los pedidos históricos mantienen su referencia sin alteración.

**Trade-off:** Deshabilitar una forma de pago no cancela pedidos pendientes que la usan — aceptado para el scope del parcial.

### D2: `include_deleted` solo en listados — sin endpoint de restore

**Decisión:** Los listados de ADMIN/STOCK aceptan `include_deleted=true` para mostrar ítems eliminados con badge "Eliminado". No hay endpoint de restauración en este change.

**Razón:** La restauración (SET deleted_at = NULL) requiere validación de negocio (ej: stock al restaurar un producto) que está fuera de scope.

### D3: Reutilizar módulo `backend/admin/` para configuración

**Decisión:** Los endpoints de configuración van en `backend/admin/router.py` bajo el prefijo `/configuracion`. No se crea un módulo separado.

**Razón:** El módulo admin ya está registrado en `api/v1/router.py` con prefix `/admin`. Extenderlo es más simple que registrar otro módulo.

### D4: `include_deleted` — validación de rol en el service, no en el router

**Decisión:** El router pasa `include_deleted` al service. El service ignora el param si el usuario no tiene rol ADMIN o STOCK (lo fuerza a `False`).

**Razón:** Centraliza la lógica de autorización en el service, no en el router param.

## Risks / Trade-offs

- **[Migración Alembic]** Agregar columna `activo DEFAULT TRUE` es una operación no-bloqueante (no requiere lock de tabla en PostgreSQL para columnas con default). Riesgo bajo.
- **[include_deleted en listado público]** El endpoint público de productos NO debe aceptar `include_deleted`. El param solo aplica a endpoints que tienen guard de ADMIN/STOCK.
