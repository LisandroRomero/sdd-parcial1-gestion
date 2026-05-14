## Context

El CRUD de productos, categorías e ingredientes está completamente implementado en el backend (changes 2.1–2.4). Los endpoints ya existen y funcionan. El frontend tiene solo las llamadas de **lectura pública** (`fetchProductos`, `fetchProductoDetalle`, `fetchCategorias`).

El único problema backend es que `POST/PUT/DELETE /productos` tienen `require_role("ADMIN")` en lugar de `require_role("ADMIN", "STOCK")` — esto bloquea a gestores de stock de crear/editar/eliminar productos, contradiciendo US-015/US-020/US-022.

## Goals / Non-Goals

**Goals:**
- Corregir RBAC en endpoints de mutación de productos (agregar STOCK)
- Crear 3 páginas admin (productos, categorías, ingredientes) con tabla + CRUD completo
- Reutilizar los endpoints y schemas existentes — sin nuevos endpoints de backend

**Non-Goals:**
- Asociación de ingredientes a productos desde el panel (complejidad alta, scope de 2.4)
- Imágenes de productos (no hay storage configurado)
- Filtros avanzados en las páginas admin (no requerido en US-015/020/021/022)
- Dashboard de métricas (7.1)

## Decisions

### D1: Reutilizar endpoints existentes — sin admin-specific endpoints

**Decisión:** Las páginas admin usan los mismos endpoints públicos y de gestión existentes (`POST /productos/`, `PUT /productos/{id}`, etc.). No se crean endpoints bajo `/admin/` para catálogo.

**Razón:** El backend ya implementa RBAC correctamente (ADMIN y STOCK). Los datos que el admin necesita son los mismos. Duplicar endpoints solo agrega mantenimiento.

**Consecuencia:** El API client admin llama a los mismos paths que el frontend público, pero con autenticación.

### D2: Mostrar todos los productos en panel admin (incluyendo eliminados)

**Decisión:** El panel de productos admin lista todos los productos incluyendo soft-deleted. Para esto se agrega un endpoint o se aprovecha que el listado público filtra por `disponible`. Dado que el backend actual solo expone productos no eliminados, la tabla admin mostrará solo los activos — la reapertura de eliminados no es scope de este change.

**Alternativa descartada:** Crear endpoint especial `GET /admin/productos` que incluya soft-deleted — requiere más backend work, fuera de scope.

### D3: UI — tabla simple con modales de creación/edición

**Decisión:** Cada página admin usa una tabla con columnas relevantes + botones de Editar/Eliminar por fila + botón "Nuevo" en el encabezado que abre un modal de formulario.

**Alternativa descartada:** Página de detalle dedicada para crear/editar — overhead de routing innecesario para formularios simples.

### D4: Formularios con validación básica en frontend

**Decisión:** Validación mínima en el formulario (campos obligatorios) — el backend es la fuente de verdad para validaciones de negocio (precio > 0, nombre único, etc.). Los errores de backend se muestran en el modal.

### D5: Reutilizar tipos existentes cuando sea posible

**Decisión:** Reutilizar `CategoriaRead`, `ProductoRead`, `ProductoDetalleRead` de `entities/producto/types.ts`. Agregar solo los tipos faltantes para mutaciones.

## Risks / Trade-offs

- **[Soft-deleted no visibles]** El panel admin no puede mostrar productos eliminados con la API actual → aceptado para este scope; reabrir productos podría ser una mejora posterior.
- **[Sin imágenes]** ProductoCreate incluye `imagen_url` opcional pero no hay UI de upload → el campo se omite del formulario o acepta texto.
- **[Ciclos en categorías]** La validación de ciclos jerárquicos está en el backend — errores se muestran como mensajes en el modal.
