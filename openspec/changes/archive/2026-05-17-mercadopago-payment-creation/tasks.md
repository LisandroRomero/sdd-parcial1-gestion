## 1. Configuración

- [x] 1.1 Agregar `MP_PUBLIC_KEY` y `MP_NOTIFICATION_URL` a `backend/core/config.py` como campos opcionales en `Settings`
- [x] 1.2 Actualizar `backend/.env.example` con `MP_PUBLIC_KEY` y `MP_NOTIFICATION_URL` documentados

## 2. Schemas Pydantic

- [x] 2.1 Actualizar `backend/pagos/schemas.py`: reemplazar `PagoCreate` con `CrearPagoRequest` que incluya `pedido_id: int`, `card_token: str`, `payment_method_id: str`, `monto: Decimal`
- [x] 2.2 Agregar `PagoResponse` a `backend/pagos/schemas.py` con campos: `id`, `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference`, `monto`, `moneda`, `created_at` (usando `model_config = ConfigDict(from_attributes=True)`)
- [x] 2.3 Actualizar `PagoRead` existente si es necesario para alinearlo con el modelo actual

## 3. Cliente SDK de MercadoPago

- [x] 3.1 Crear `backend/pagos/mp_client.py` con función `get_mp_client() -> mercadopago.SDK` usando `@lru_cache` y `settings.mercadopago_access_token`
- [x] 3.2 Manejar caso donde `MERCADOPAGO_ACCESS_TOKEN` está vacío o es inválido

## 4. Repositorio

- [x] 4.1 Implementar `backend/pagos/repository.py` con clase `PagoRepository(BaseRepository[Pago])`
- [x] 4.2 Agregar método `get_by_pedido(self, pedido_id: int) -> list[Pago]` ordenado por created_at DESC
- [x] 4.3 Agregar método `get_by_idempotency_key(self, key: str) -> Pago | None` para verificar duplicados
- [x] 4.4 Agregar método `get_by_mp_payment_id(self, mp_payment_id: int) -> Pago | None`

## 5. Service — Lógica de negocio

- [x] 5.1 Implementar `backend/pagos/service.py` con función `crear_pago()`
- [x] 5.2 Implementar función `crear_pago(uow, request, current_user) -> Pago` que:
  - [x] 5.2.1 Obtiene el pedido vía UoW y valida que exista (404 si no)
  - [x] 5.2.2 Valida que el pedido pertenezca al usuario (404 si no, para CLIENT; ADMIN puede pagar cualquier pedido)
  - [x] 5.2.3 Valida que el pedido esté en estado `PENDIENTE` (422 si no)
  - [x] 5.2.4 Valida que `request.monto` coincida con `pedido.total` (422 si difiere)
  - [x] 5.2.5 Verifica que la forma de pago (MercadoPago) esté activa (422 si no)
  - [x] 5.2.6 Genera UUID v4 como `idempotency_key`
  - [x] 5.2.7 Obtiene SDK de MP via `get_mp_client()`
  - [x] 5.2.8 Construye payload para MP: `token`, `payment_method_id`, `installments: 1`, `transaction_amount`, `external_reference`, `description`, `notification_url`
  - [x] 5.2.9 Llama a `mp_client.payment().create(payload, RequestOptions)` con idempotency key
  - [x] 5.2.10 Crea `Pago` en BD con: `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference`, `idempotency_key`, `monto`, `moneda` vía `uow.repos.pagos.add()`
  - [x] 5.2.11 Captura errores de MP/SDK y eleva ValidationException
  - [x] 5.2.12 Retorna el `Pago` creado

## 6. Router — Endpoint REST

- [x] 6.1 Implementar `backend/pagos/router.py` con `APIRouter()` y UoW factory local
- [x] 6.2 Crear endpoint `POST /crear` que:
  - [x] 6.2.1 Requiere autenticación: `usuario = Depends(get_current_user)`
  - [x] 6.2.2 Requiere rol CLIENT o ADMIN: `Depends(require_role("CLIENT", "ADMIN"))`
  - [x] 6.2.3 Recibe `CrearPagoRequest` validado por Pydantic
  - [x] 6.2.4 Usa UoW via `Depends(_get_uow)`
  - [x] 6.2.5 Llama `pago_service.crear_pago(uow, body, current_user)`
  - [x] 6.2.6 Retorna HTTP 201 con `PagoResponse`

## 7. Registro en API

- [x] 7.1 Importar `pagos_router` en `backend/api/v1/router.py`
- [x] 7.2 Agregar `(pagos_router, "/pagos", "pagos")` a la lista `sub_routers`
- [x] 7.3 Registrar `PagoRepository` en el `UnitOfWork` dentro de `core/dependencies.py` (registro lazy en `uow.repos.register("pagos", PagoRepository)`)
