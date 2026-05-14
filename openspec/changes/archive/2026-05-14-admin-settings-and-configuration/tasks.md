## 1. Backend — Migración Alembic: FormaPago.activo

- [x] 1.1 Crear nueva migración Alembic en `backend/alembic/versions/` que agrega la columna `activo BOOLEAN NOT NULL DEFAULT TRUE` a la tabla `formapago`. La migración debe incluir `upgrade()` con `op.add_column('formapago', sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'))` y `downgrade()` con `op.drop_column('formapago', 'activo')`.

## 2. Backend — Modelo y schemas

- [x] 2.1 En `backend/pagos/model.py`, agregar `activo: bool = Field(default=True)` al modelo `FormaPago`.
- [x] 2.2 En `backend/admin/schemas.py`, agregar:
  - `FormaPagoRead(codigo: str, descripcion: Optional[str], activo: bool, created_at: Optional[datetime])` con `from_attributes=True`
  - `FormaPagoUpdate(activo: bool)`

## 3. Backend — Admin service para formas de pago

- [x] 3.1 En `backend/admin/service.py`, agregar dos funciones:
  - `list_formas_pago(uow) -> list[FormaPagoRead]`: consulta todas las formas de pago ordenadas por código
  - `toggle_forma_pago(uow, codigo: str, body: FormaPagoUpdate) -> FormaPagoRead`: busca por código (NotFoundException si no existe), actualiza `activo = body.activo`

## 4. Backend — Admin router: endpoints de configuración

- [x] 4.1 En `backend/admin/router.py`, agregar al UoW local el import de `FormaPago` y los 2 nuevos endpoints bajo el prefijo `/configuracion`:
  - `GET /configuracion/formas-de-pago` → `response_model=list[FormaPagoRead]` — guard ADMIN — llama `list_formas_pago`
  - `PATCH /configuracion/formas-de-pago/{codigo}` → `response_model=FormaPagoRead` — guard ADMIN — llama `toggle_forma_pago`

## 5. Backend — include_deleted en ingredientes

- [x] 5.1 En `backend/ingredientes/repository.py`, modificar `listar(es_alergeno?, page, size)` para aceptar `include_deleted: bool = False`. Cuando `include_deleted=False`, mantener el filtro `Ingrediente.deleted_at.is_(None)`. Cuando `True`, omitir ese filtro.
- [x] 5.2 En `backend/ingredientes/service.py`, pasar `include_deleted` desde `listar()` al repository.
- [x] 5.3 En `backend/ingredientes/router.py`, agregar `include_deleted: bool = Query(default=False)` al endpoint `GET /` junto con `current_user: Optional[Usuario] = Depends(get_current_user_optional)` (o directamente `Depends(require_role("ADMIN", "STOCK"))`). Pasar `include_deleted` al service solo si el usuario tiene rol ADMIN o STOCK; sino forzar `False`.
  - Si `get_current_user_optional` no existe, agregar una nueva dependencia en `backend/core/dependencies.py` que retorna `Optional[Usuario]` sin lanzar excepción.

## 6. Backend — include_deleted en productos

- [x] 6.1 En `backend/productos/repository.py`, función `listar` (que construye la query pública): agregar param `include_deleted: bool = False`. Cuando `False` mantener `Producto.deleted_at.is_(None)`. Cuando `True` omitirlo.
- [x] 6.2 En `backend/productos/service.py`, función `listar_publico`: pasar `include_deleted` al repository.
- [x] 6.3 En `backend/productos/router.py`, endpoint `GET /`: agregar param `include_deleted: bool = Query(default=False)` y dependencia opcional de usuario. Pasar al service solo si ADMIN/STOCK; sino forzar `False`.

## 7. Frontend — API client y hooks para configuración

- [x] 7.1 Crear `frontend/src/features/admin/api/adminConfiguracionApi.ts`:
  - `listarFormasPago()` → `GET /admin/configuracion/formas-de-pago` → `FormaPagoRead[]`
  - `toggleFormaPago(codigo: string, activo: boolean)` → `PATCH /admin/configuracion/formas-de-pago/{codigo}` → `FormaPagoRead`
- [x] 7.2 Agregar tipos en `frontend/src/entities/admin/types.ts`:
  - `FormaPagoRead { codigo: string, descripcion: string | null, activo: boolean, created_at?: string | null }`
  - `FormaPagoUpdate { activo: boolean }`
- [x] 7.3 Crear hooks en `frontend/src/features/admin/hooks/`:
  - `useListarFormasPago.ts` — useQuery, queryKey `['formas-pago']`
  - `useToggleFormaPago.ts` — useMutation + invalidate `['formas-pago']`

## 8. Frontend — AdminConfiguracionPage

- [x] 8.1 Crear `frontend/src/pages/admin/AdminConfiguracionPage.tsx`:
  - Sección "Formas de pago": usa `useListarFormasPago` para cargar las formas
  - Una card por forma de pago con: nombre (`codigo`), descripción, badge "Activo"/"Inactivo", botón toggle que llama `useToggleFormaPago`
  - Estado de carga (skeleton) y error básico
  - Títulos y layout consistentes con el resto del panel admin

## 9. Frontend — Toggle "Mostrar eliminados" en páginas admin de catálogo

- [x] 9.1 En `frontend/src/features/admin/api/adminProductosApi.ts`, agregar función `listarProductosAdmin(params: { include_deleted?: boolean })` que llama `GET /productos/` con el param.
- [x] 9.2 En `frontend/src/features/admin/api/adminIngredientesApi.ts`, modificar `listarIngredientesAdmin` para aceptar `include_deleted?: boolean` y pasarlo como query param.
- [x] 9.3 En `frontend/src/pages/admin/AdminProductosPage.tsx`, agregar un `<label><input type="checkbox" /> Mostrar eliminados</label>` que controla un estado local `includeDeleted: boolean`. Cuando cambia, recargar el listado con `include_deleted=true/false`. Mostrar badge "Eliminado" en las filas donde `deleted_at` no es nulo (agregar `deleted_at?: string | null` al tipo `ProductoRead`).
- [x] 9.4 En `frontend/src/pages/admin/AdminIngredientesPage.tsx`, ídem — toggle "Mostrar eliminados" con badge en filas eliminadas.

## 10. Frontend — Routing y nav

- [x] 10.1 En `frontend/src/app/router.tsx`, agregar lazy import y ruta `{ path: 'configuracion', element: <AdminConfiguracionPage /> }` dentro del grupo `AdminRoute`.
- [x] 10.2 En `frontend/src/app/routes/layout.tsx`, agregar `<NavLink to="/admin/configuracion">Configuración</NavLink>` en la sección admin (junto a los links existentes de Usuarios, Productos, etc.).
