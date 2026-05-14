## Context

El change `admin-settings-and-configuration` (7.5) se implementó y archivó, pero quedaron dos bugs:

1. **Network Error en `/admin/configuracion`**: `run_server.py` levanta el backend en puerto 8000, pero `frontend/.env` define `VITE_API_BASE_URL=http://localhost:8001/api/v1`. Toda request del frontend al backend falla por conexión rechazada.

2. **Toggle "Mostrar eliminados" sin efecto**: El toggle en `AdminProductosPage` envía `include_deleted=true` correctamente, pero:
   - `ProductoRead` no incluye `deleted_at` en sus campos → Pydantic no serializa el valor → el frontend nunca puede detectar qué productos están eliminados
   - El repository siempre filtra `disponible=True` incluso cuando `include_deleted=True` → productos eliminados con `disponible=false` quedan excluidos

## Goals / Non-Goals

**Goals:**
- Corregir el puerto del backend para que coincida con la URL del frontend
- Que `ProductoRead` serialice `deleted_at` para que el frontend pueda mostrar el badge "Eliminado"
- Que el filtro `disponible` no se aplique automáticamente cuando se incluyen eliminados

**Non-Goals:**
- No se modifican specs existentes (los requirements ya están correctos en `admin-soft-delete-visibility` y `admin-payment-settings`)
- No se toca el frontend (los componentes ya están implementados correctamente)
- No se agregan nuevas funcionalidades

## Decisions

| Decisión | Opciones | Elegido | Razón |
|----------|----------|---------|-------|
| Puerto backend | 8000 (actual) vs **8001** | 8001 | El frontend ya apunta a 8001, el `.env.example` referencia 8000 como default pero el proyecto usa 8001 |
| Cómo exponer `deleted_at` | Nuevo schema separado vs **agregar campo a `ProductoRead`** | Agregar campo | Ya hay un schema `ProductoRead` existente, agregar un campo opcional es el cambio mínimo. Los clientes actuales no se rompen porque es `Optional` con default `None` |
| Filtro disponible con `include_deleted` | Ignorar `include_deleted` vs **no filtrar disponible por defecto** | No filtrar disponible | Cuando un admin pide "mostrar eliminados", quiere ver TODOS los productos sin filtros. Si quiere filtrar por disponible, puede explicitarlo |

## Risks / Trade-offs

- **[Riesgo Bajo]** Agregar `deleted_at` a `ProductoRead` expone información de soft-delete a cualquier cliente HTTP. Mitigación: el endpoint ya requiere autenticación y el campo solo es útil para admin/stock. Los clientes públicos ya tienen su propio schema (público) que no incluye este campo.
- **[Riesgo Muy Bajo]** Cambiar el puerto en `run_server.py` puede requerir reiniciar el servidor si está corriendo en 8000. Mitigación: es un cambio de 1 línea, se reinicia y listo.
