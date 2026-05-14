## 1. Backend — Schemas y modelos

- [x] 1.1 Agregar schema `DireccionSnapshot` a `backend/pedidos/schemas.py` con campos: `id`, `calle`, `numero`, `piso` (Optional), `departamento` (Optional), `ciudad`, `provincia`, `codigo_postal` (Optional), con `model_config = ConfigDict(from_attributes=True)`
- [x] 1.2 Agregar `@property cantidad_items(self) -> int` al modelo `Pedido` en `backend/pedidos/model.py` que retorne `len(self.detalles) if self.detalles else 0`
- [x] 1.3 Agregar `cantidad_items: int = 0` a `PedidoRead` en `backend/pedidos/schemas.py` (se leerá del property del modelo vía `from_attributes=True`)
- [x] 1.4 Agregar `direccion: Optional[DireccionSnapshot] = None` a `PedidoDetail` en `backend/pedidos/schemas.py`

## 2. Backend — Repository

- [x] 2.1 Agregar import de `selectinload` de `sqlalchemy.orm` y `Usuario` de `backend.usuarios.model` al top de `backend/pedidos/repository.py`
- [x] 2.2 Agregar `buscar: Optional[str] = None` como param a `list_pedidos` en `backend/pedidos/repository.py`
- [x] 2.3 Agregar `selectinload(Pedido.detalles)` a la query de `list_pedidos` para que `cantidad_items` esté disponible al serializar
- [x] 2.4 Agregar filtro de búsqueda en `list_pedidos`: cuando `buscar` es provisto, aplicar `cast(Pedido.id, String).ilike(f"%{buscar}%")` OR `JOIN Usuario` y `ilike` sobre `nombre`/`apellido` (usar `OR` dentro de un `and_`/`or_` de SQLAlchemy)

## 3. Backend — Router

- [x] 3.1 Agregar `buscar: Optional[str] = Query(default=None)` como query param al endpoint `GET /pedidos/` en `backend/pedidos/router.py`
- [x] 3.2 Pasar `buscar` al llamado de `uow.repos.pedidos.list_pedidos(...)` en el mismo endpoint

## 4. Frontend — Types

- [x] 4.1 Agregar `cantidad_items: number` a la interface `PedidoRead` en `frontend/src/entities/pedidos/types.ts`
- [x] 4.2 Agregar interface `DireccionSnapshot` con campos `id`, `calle`, `numero`, `piso?`, `departamento?`, `ciudad`, `provincia`, `codigo_postal?` a `types.ts`
- [x] 4.3 Agregar `direccion?: DireccionSnapshot | null` a la interface `PedidoDetail` en `types.ts`
- [x] 4.4 Agregar `buscar?: string` a la interface `ListarPedidosParams` en `types.ts`

## 5. Frontend — OrderCard

- [x] 5.1 Mostrar `cantidad_items` en `OrderCard.tsx` con formato "N ítems" / "1 ítem" (singular/plural), junto a la fecha y costo de envío existentes

## 6. Frontend — PedidoDetailPage

- [x] 6.1 Agregar sección "Dirección de entrega" en `PedidoDetailPage.tsx` con un `<Card>` que muestre `calle + numero`, `piso`/`departamento` (si existen), `ciudad + provincia`. Renderizar solo si `pedido.direccion` no es nulo.

## 7. Frontend — PedidoListPage

- [x] 7.1 Agregar `const user = useAuthStore((s) => s.user)` en `PedidoListPage.tsx` y usar `user?.roles.includes('CLIENT') ? 'Mis Pedidos' : 'Pedidos'` como título de la página `<h1>`
- [x] 7.2 Agregar `buscar?: string` al estado de filtros en `PedidoListPage.tsx` y pasarlo a `useListarPedidos` vía el spread de `filters`

## 8. Frontend — OrderFilters

- [x] 8.1 Agregar campo `buscar` al tipo de filtros en `OrderFilters.tsx` (prop `onFilterChange` ya existe — extender con `buscar`)
- [x] 8.2 Agregar un `<input>` de búsqueda en `OrderFilters.tsx` con placeholder "Buscar por N° de pedido..." que actualice `buscar` en el estado local del componente
- [x] 8.3 Incluir `buscar` en el objeto de filtros que se pasa a `onFilterChange` cuando el usuario escribe (con debounce o al perder el foco)
