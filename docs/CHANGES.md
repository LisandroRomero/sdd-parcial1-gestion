# CHANGES — Roadmap visible (Food Store v5.0)

> Objetivo: tener **a la vista** qué changes existen, en qué orden se implementan y de qué dependen.
>
> Fuente de verdad de ejecución: `openspec/` (OPSX). Este archivo es un **mapa/plan** para humanos.

**Última actualización:** 2026-05-08

---

## Cómo usar este roadmap con OPSX

Para trabajar un change, el flujo recomendado es:

```bash
/opsx:propose <change-name>
/opsx:apply <change-name>
/opsx:archive <change-name>
```

Notas:
- **No implementes sin artefactos** (`proposal.md` + `design.md` aprobados).
- **Un change = un commit** (o varios commits atómicos), pero nunca mezcles changes.
- El orden importa por dependencias (ver tablas).

---

## Ya realizado (archivado en OPSX)

| ID | Change | Estado | Evidencia |
|---:|---|---|---|
| 0.0 | scaffolding-monorepo-setup | ✅ Hecho (archivado 2026-04-24) | `openspec/changes/archive/2026-04-24-scaffolding-monorepo-setup/` |
| 0.2 | setup-frontend-infrastructure | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-setup-frontend-infrastructure/` |
| 0.3 | database-schema-and-seed | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-database-schema-and-seed/` |
| 0.4 | base-patterns-backend | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-base-patterns-backend/` |
| 0.5 | zustand-stores-setup | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-zustand-stores-setup/` |

> Este change deja listo el **esqueleto monorepo** (`/backend`, `/frontend`), `.gitignore`, `.env.example` y READMEs. **No** instala dependencias ni configura FastAPI/Vite.

---

## Sprint 0 — Infraestructura (NO negociable)

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 0.1 | setup-backend-infrastructure | US-000, US-000a | FastAPI, SQLModel, Alembic, config.py, core/, main.py | 0.0 | Construye sobre el scaffold |

---

## Epic 01 — Autenticación y autorización

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 1.1 | user-registration | US-001, US-063 | POST /auth/register + rol CLIENT automático + bcrypt | 0.4 | Patrones + UoW |
| 1.2 | user-login-with-jwt | US-002, US-006, US-073 | POST /auth/login: JWT access (30m) + refresh (7d) + rate limiting 5/15m | 1.1 | Necesita usuarios |
| 1.3 | token-refresh-and-rotation | US-003 | POST /auth/refresh: rotación + detección replay | 1.2 | Necesita refresh tokens |
| 1.4 | logout | US-004 | POST /auth/logout: revocar refresh token | 1.3 | Necesita rotación |
| 1.5 | rbac-and-role-management | US-005, US-006, US-075, US-076 | CRUD roles + asignación (ADMIN) + require_role + guards FE | 1.2 | Roles dentro del JWT |
| 1.6 | frontend-auth-interceptors | US-066, US-067 | Axios interceptors: attach JWT, refresh automático, manejo global de errores | 1.5, 0.5 | Auth store + RBAC |

---

## Epic 02 — Catálogo de productos

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 2.1 | category-management-hierarchical | US-007, US-008, US-009, US-010 | Categorías jerárquicas (CTE recursiva) + validación de ciclos | 0.4, 1.5 | UoW + RBAC (STOCK/ADMIN) |
| 2.2 | ingredient-management | US-011, US-012, US-013, US-014 | CRUD ingredientes + flag alérgeno | 0.4, 1.5 | UoW + RBAC |
| 2.3 | product-crud-and-stock | US-015, US-020, US-021, US-022 | CRUD productos + PATCH stock + soft delete + snapshot precio | 2.1, 2.2, 0.4, 1.5 | Prereqs catálogo |
| 2.4 | product-ingredient-association | US-017 | M2M producto-ingrediente + flag es_removible | 2.2, 2.3 | Personalización |
| 2.5 | public-product-catalog | US-018, US-019, US-023 | GET /productos (paginado/filtros/búsqueda) + detalle + filtro alérgenos | 2.3, 2.4 | Catálogo público |

---

## Epic 03 — Direcciones y perfil de cliente

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 3.1 | delivery-address-management | US-024, US-025, US-026, US-027, US-028 | CRUD DireccionEntrega por usuario + principal + soft delete + ownership | 1.5 | RBAC + pertenencia |
| 3.2 | user-profile-view-and-edit | US-061, US-062 | GET/PUT /perfil: ver/editar nombre/email/teléfono | 1.5, 3.1 | Perfil + direcciones |

---

## Epic 04 — Carrito (frontend)

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 4.1 | shopping-cart-frontend | US-029..US-034 | cartStore: add/remove/update, personalización (exclude ingredientes), persist, totales | 0.5, 2.5 |

---

## Epic 05 — Órdenes y máquina de estados

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 5.1 | order-creation-with-uow | US-035..US-038 | POST /pedidos atómico: snapshots, validar stock, transacción all-or-nothing | 0.4, 2.3, 3.1, 1.5 |
| 5.2 | order-fsm-and-state-transitions | US-039..US-042 | FSM (6 estados) + PATCH /pedidos/{id}/estado + RN-01/02/03 | 5.1, 0.4 |
| 5.3 | order-cancellation | US-043 | Cancelación + restaurar stock atómico + regla ADMIN en EN_PREP | 5.2 |
| 5.4 | order-history-audit-trail | US-044 | HistorialEstadoPedido append-only + timeline | 5.1, 5.2 |
| 5.5 | order-list-and-detail | US-049..US-051 | GET /pedidos listado/filtros + detalle completo + pertenencia CLIENT | 5.4, 1.5 |

---

## Epic 06 — Pagos (MercadoPago)

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 6.1 | mercadopago-payment-creation | US-045, US-046 | POST /pagos/crear + idempotency_key + registrar Pago | 5.1, 0.4, 1.5 |
| 6.2 | mercadopago-webhook-processing | US-046, US-047 | POST /pagos/webhook: firma + topic=payment + actualizar estado + avanzar pedido + stock atómico | 6.1, 5.2 |
| 6.3 | payment-retry-and-status | US-048 | 1:N pagos por pedido + GET /pagos/{pedido_id} + reintentos | 6.1, 6.2 |
| 6.4 | frontend-payment-checkout | US-045, US-048 | Checkout FE con SDK MP + polling estado + UI approved/rejected/pending | 6.1, 0.5, 4.1 |

---

## Epic 07 — Admin panel

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 7.1 | admin-dashboard-metrics | US-052, US-053 | KPIs + gráficos (recharts) | 5.5, 6.3, 1.5 |
| 7.2 | admin-user-management | US-054..US-060 | CRUD usuarios + roles + desactivar + soft delete | 1.5, 0.4 |
| 7.3 | admin-product-management | US-015, US-020..US-022 (panel) | CRUD productos/stock/categorías/ingredientes desde panel | 2.1, 2.2, 2.3, 2.4, 1.5 |
| 7.4 | admin-order-management | US-041..US-043 | Ver pedidos + avanzar estados + historial + cancelar + filtros | 5.5, 5.3, 5.4, 1.5 |
| 7.5 | admin-settings-and-configuration | US-064 | Formas de pago habilitadas + parámetros sistema + ver soft-deleted | 1.5 |

---

## Epic 08 — Calidad y robustez (transversal)

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 8.1 | error-handling-standardized | US-068, US-074 | RFC 7807 + validación inputs + sanitización XSS/SQLi | 0.4, 0.2 | Implementar temprano |
| 8.2 | testing-and-fixtures | Bonus | Pytest: auth/pagos/pedidos/producto + fixtures + mocks MP | Todos | Opcional recomendado |

---

## Orden de implementación recomendado (macro)

1) **Fundación (Sprint 0):** 0.1 → 0.2 → 0.3 → 0.4 → 0.5
2) **Auth (Sprint 1):** 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6
3) **Catálogo (Sprint 2-3):** 2.1 → 2.2 → 2.3 → 2.4 → 2.5
4) **Cliente (Sprint 3):** 3.1 → 3.2 → 4.1
5) **Órdenes (Sprint 4-5):** 5.1 → 5.2 → 5.3 → 5.4 → 5.5
6) **Pagos (Sprint 5-6):** 6.1 → 6.2 → 6.3 → 6.4
7) **Admin (Sprint 7):** 7.1 → 7.2 → 7.3 → 7.4 → 7.5

Transversal en paralelo: **8.1** temprano; **8.2** cuando el sistema ya tenga endpoints reales para testear.

---

## Decisiones arquitectónicas clave (recordatorio)

1. **Sprint 0 es NO negociable.** Sin `0.4` no hay servicios consistentes; sin `0.3` no hay base para validar lógica.
2. **Unit of Work es el eje.** Si `0.4` está mal, caen órdenes/pagos.
3. **Snapshots y soft delete desde el inicio.** Evita refactors caros.
4. **Carrito es frontend-only** y depende de catálogo público.
5. **Pagos es lo más complejo:** el webhook debe ser atómico con actualizaciones críticas.
6. **Admin al final:** depende de casi todo.
7. **Las specs son código.** Se versionan en git, se revisan en PRs, evolucionan con el proyecto.

