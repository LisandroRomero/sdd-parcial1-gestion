## Why

Los productos del catálogo necesitan exponer qué ingredientes los componen (con cantidad y unidad), permitir gestión de esas asociaciones a través de la API y alertar a clientes sobre alérgenos presentes. Sin esta asociación, la plataforma no puede cumplir con la rúbrica SDD v5.0 que requiere trazabilidad de ingredientes por producto.

## What Changes

- Se agregan tres endpoints REST bajo `/api/v1/productos/{id}/ingredientes`:
  - `POST` — asociar un ingrediente a un producto (con `cantidad` y `unidad` opcionales)
  - `GET` — listar los ingredientes de un producto, incluyendo flag `es_alergeno`
  - `DELETE /{ingrediente_id}` — remover la asociación de un ingrediente de un producto
- Se extienden los schemas Pydantic de `backend/ingredientes/schemas.py` con `ProductoIngredienteCreate`, `ProductoIngredienteRead` y `ProductoIngredienteListResponse`
- Se agrega `ProductoIngredienteRepository` en `backend/ingredientes/repository.py` (siguiendo el patrón del módulo ya existente)
- Se agrega `ProductoIngredienteService` en `backend/ingredientes/service.py` (o método en el service existente)
- Se registran los nuevos endpoints en `backend/productos/router.py` bajo el prefijo `/{id}/ingredientes`
- Se genera una migración Alembic para agregar la columna `cantidad` (Float, nullable) y `unidad` (String(20), nullable) a la tabla `producto_ingredientes`, que actualmente solo tiene `producto_id`, `ingrediente_id` y `es_removible`

## Capabilities

### New Capabilities

- `product-ingredient-association`: Endpoints y lógica de negocio para asociar, listar y remover ingredientes de un producto, incluyendo validaciones de existencia/actividad y detección de alérgenos.

### Modified Capabilities

- `ingredient-management`: La spec existente cubre CRUD de ingredientes. Ahora se extiende con el requisito de que los ingredientes eliminados (soft delete) NO puedan ser asociados a productos nuevos (validación en el service de asociación). No cambia el comportamiento de los endpoints de ingredientes en sí, solo se documenta la regla de dependencia cruzada.

## Impact

- **backend/ingredientes/model.py** — `ProductoIngrediente` ya existe con `es_removible`; se deben agregar `cantidad` (Optional[float]) y `unidad` (Optional[str]) al modelo
- **backend/ingredientes/schemas.py** — nuevos schemas `ProductoIngredienteCreate`, `ProductoIngredienteRead`, `ProductoIngredienteListResponse`
- **backend/ingredientes/repository.py** — nuevos métodos: `agregar`, `listar_por_producto`, `remover`, `existe`
- **backend/ingredientes/service.py** — nueva lógica de negocio: validar producto activo, validar ingrediente activo, evitar duplicados (409), remover (404 si no existe)
- **backend/productos/router.py** — tres nuevos endpoints bajo `/{id}/ingredientes` que usan ambos repositorios (ProductoRepository + IngredienteRepository) via UoW
- **alembic/versions/** — nueva migración que agrega `cantidad` y `unidad` a `producto_ingredientes`
- **Sin impacto en frontend en este cambio** — la asociación es funcionalidad backend pura
