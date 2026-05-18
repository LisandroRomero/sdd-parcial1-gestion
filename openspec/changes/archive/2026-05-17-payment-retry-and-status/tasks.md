## 1. Fix external_reference generation

- [x] 1.1 Modify `crear_pago()` in service.py to count existing pagos for the pedido and generate `external_reference = f"{pedido_id}-{count + 1}"`
- [x] 1.2 Add validation at top of `crear_pago()`: if pedido has any existing payment with `mp_status == "approved"`, raise ConflictException (PAGO_YA_APROBADO) to prevent retry after success

## 2. GET /api/v1/pagos/{pedido_id} endpoint

- [x] 2.1 Create `consultar_pagos(uow, pedido_id, current_user) -> list[Pago]` in service.py — loads pedido, checks ownership (404 if not found or not owned), delegates to `get_by_pedido()`, returns ordered list
- [x] 2.2 Add `GET /{pedido_id}` endpoint in router.py with `response_model=list[PagoRead]`, auth CLIENT/ADMIN, calls service.consultar_pagos()

## 3. Tests

- [x] 3.1 Test GET /api/v1/pagos/{pedido_id}: pedido propio con pagos → 200 + lista
- [x] 3.2 Test GET /api/v1/pagos/{pedido_id}: pedido ajeno → 404
- [x] 3.3 Test GET /api/v1/pagos/{pedido_id}: pedido sin pagos → 200 + lista vacía
- [x] 3.4 Test POST /api/v1/pagos/crear: retry after rejected payment → 201 + nuevo Pago con external_reference único
- [x] 3.5 Test POST /api/v1/pagos/crear: retry blocked because pedido has approved payment → 409
- [x] 3.6 Test external_reference is unique per attempt (multiple attempts produce different values)
