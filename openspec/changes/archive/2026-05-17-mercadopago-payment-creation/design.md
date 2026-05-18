## Context

El módulo `backend/pagos/` tiene el modelo de datos completo (`Pago`, `FormaPago`) con migraciones aplicadas y seed data cargado, pero carece de toda lógica de negocio:

- `repository.py`, `service.py`, `router.py` están **vacíos** (0 líneas)
- `schemas.py` tiene un `PagoCreate` mínimo que no contempla `card_token` ni `payment_method_id`
- El SDK `mercadopago` está en `requirements.txt` pero **no se importa en ningún lado**
- Las variables `MERCADOPAGO_ACCESS_TOKEN` y `MERCADOPAGO_WEBHOOK_SECRET` están configuradas en `config.py`; faltan `MP_PUBLIC_KEY` y `MP_NOTIFICATION_URL`
- El router de pagos **no está registrado** en `backend/api/v1/router.py`
- El UoW en `core/uow.py` está completo y listo para registrar `PagoRepository`

Este change implementa exclusivamente el endpoint de creación de pago (`POST /api/v1/pagos/crear`). El procesamiento del webhook (6.2), reintentos (6.3) y frontend (6.4) son cambios separados.

## Goals / Non-Goals

**Goals:**
- Implementar `PagoRepository` heredando de `BaseRepository[Pago]`
- Implementar `PagoService.crear_pago()` con lógica de integración a MercadoPago vía SDK
- Crear endpoint `POST /api/v1/pagos/crear` con autenticación CLIENT
- Actualizar schemas Pydantic para soportar la creación de pago
- Registrar el router de pagos en la API v1
- Agregar variables de configuración faltantes (`MP_PUBLIC_KEY`, `MP_NOTIFICATION_URL`)
- Inicializar el SDK de MercadoPago como dependencia de FastAPI
- Garantizar idempotencia mediante `idempotency_key` UUID
- Registrar el pago en BD atómicamente vía UoW

**Non-Goals:**
- ❌ Procesar webhooks IPN de MercadoPago (change 6.2)
- ❌ Consultar estado de pago por pedido (change 6.3)
- ❌ Reintentos de pago o múltiples pagos por pedido (change 6.3)
- ❌ Integración frontend con SDK de MercadoPago (change 6.4)
- ❌ Notificaciones al usuario por cambio de estado de pago
- ❌ Testing con mocks (change 8.2)

## Decisions

### 1. SDK de MercadoPago como lazy singleton vía `@lru_cache`

**Decisión:** Crear una función `get_mp_client() -> mercadopago.SDK` con `@lru_cache` en un nuevo archivo `backend/pagos/mp_client.py`.

**Alternativa considerada:** Inicializar el SDK directamente en `PagoService.__init__()`.

**Razón:** El SDK de MP es thread-safe y no mantiene estado mutable. Un singleton lazy evita inicializarlo si no se usa (ej: en tests que mockean el SDK) y sigue el patrón existente de `get_settings()` en `config.py`.

### 2. Validación del pedido en el Service, no en el Router

**Decisión:** El `PagoService.crear_pago()` recibe `usuario_id` y valida:
- El pedido existe y pertenece al usuario autenticado
- El pedido está en estado `PENDIENTE`
- La forma de pago está activa (`FormaPago.activo = true`)

**Alternativa considerada:** Validar pertenencia en el router y dejar solo la lógica MP en el service.

**Razón:** Consistencia con el patrón del proyecto donde el Service centraliza toda la lógica de negocio. El router solo parsea HTTP y delega. Además, validar existencia y estado del pedido requiere acceso a BD, que es responsabilidad del Service vía UoW.

### 3. Idempotency key generada y gestionada por el backend

**Decisión:** El backend genera un UUID v4 como `idempotency_key` en cada llamada a `POST /api/v1/pagos/crear`. Se envía a MercadoPago en el header `X-Idempotency-Key`. La tabla `Pago` tiene `UNIQUE(idempotency_key)` para evitar duplicados en BD.

**Alternativa considerada:** El frontend envía el idempotency key.

**Razón:** La idempotency key debe ser generada y controlada por el backend para evitar que el cliente (que puede tener bugs o ser malicioso) reutilice keys o cause estados inconsistentes. El `UNIQUE` en BD es la red de seguridad final.

### 4. `PagoRepository` como clase separada (no inline en UoW)

**Decisión:** `PagoRepository` hereda de `BaseRepository[Pago]` y se registra en el `UnitOfWork` mediante `uow.repos.register("pagos", PagoRepository)`.

**Alternativa considerada:** Usar el genérico `BaseRepository` directamente desde el service.

**Razón:** El proyecto usa repositorios específicos por módulo (ya existen `UsuarioRepository`, `PedidoRepository`, etc.). `PagoRepository` necesitará métodos adicionales como `get_by_idempotency_key()` en changes futuros (6.2, 6.3). Tener la clase desde el inicio facilita la extensión sin refactor.

### 5. `MP_PUBLIC_KEY` y `MP_NOTIFICATION_URL` en `config.py`

**Decisión:** Agregar ambas variables a `Settings` en `core/config.py`:
- `mp_public_key: str = Field(default="", alias="MP_PUBLIC_KEY")`
- `mp_notification_url: str = Field(default="", alias="MP_NOTIFICATION_URL")`

**Razón:** `MP_PUBLIC_KEY` se necesita ahora porque forma parte del `PagoCreateRequest` que el frontend utiliza con el SDK de MP (seguidamente la incluirá en una futura respuesta del backend). `MP_NOTIFICATION_URL` se necesita para configurar el webhook en MercadoPago al crear el pago. Ambas deben ser configurables por entorno.

## Risks / Trade-offs

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Timeout en llamada a API de MP | El usuario ve un error 5xx aunque el pago pudo haberse creado en MP | Configurar timeout en SDK de MP (ej: 10s). Implementar consulta de estado posterior como reintento (change 6.3) |
| `idempotency_key` único violado por reintento del frontend | Dos registros Pago con misma key | `UNIQUE(idempotency_key)` en BD + validación en service antes de llamar a MP |
| SDK de MP cambia su API | Compilación en runtime, no en tiempo de compilación | La versión `>=2.3.0` está fijada en requirements. Las breaking changes de MP SDK son poco frecuentes y documentadas |
| Token de tarjeta expirado | MP rechaza el pago | El error se devuelve al frontend para que el usuario pueda reintentar (6.3) |
| Pedido cancelado entre que el frontend muestra el botón y el usuario paga | Pago exitoso pero pedido no válido | Validar estado `PENDIENTE` del pedido *dentro* de la transacción UoW (con bloqueo optimista si es necesario) |
