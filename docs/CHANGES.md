# CHANGES — Roadmap visible (Food Store v5.0)

> Objetivo: tener **a la vista** qué changes existen, en qué orden se implementan y de qué dependen.
>
> Fuente de verdad de ejecución: `openspec/` (OPSX). Este archivo es un **mapa/plan** para humanos.

**Última actualización:** 2026-05-17

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
| 0.1 | setup-backend-infrastructure | ✅ Hecho (archivado 2026-05-06) | `openspec/changes/archive/2026-05-06-setup-backend-infrastructure/` |
| 0.2 | setup-frontend-infrastructure | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-setup-frontend-infrastructure/` |
| 0.3 | database-schema-and-seed | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-database-schema-and-seed/` |
| 0.4 | base-patterns-backend | ✅ Hecho (archivado 2026-05-07) | `openspec/changes/archive/2026-05-07-base-patterns-backend/` |
| 0.5 | zustand-stores-setup | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-zustand-stores-setup/` |
| 1.1 | user-registration | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-user-registration/` |
| 1.2 | user-login-with-jwt | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-user-login-with-jwt/` |
| 1.3 | token-refresh-and-rotation | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-token-refresh-and-rotation/` |
| 1.4 | logout | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-logout/` |
| 1.5 | rbac-and-role-management | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-rbac-and-role-management/` |
| 1.6 | frontend-auth-interceptors | ✅ Hecho (archivado 2026-05-08) | `openspec/changes/archive/2026-05-08-frontend-auth-interceptors/` |
| 2.1 | category-management-hierarchical | ✅ Hecho (archivado 2026-05-11) | `openspec/changes/archive/2026-05-11-category-management-hierarchical/` |
| 2.2 | ingredient-management | ✅ Hecho (archivado 2026-05-11) | `openspec/changes/archive/2026-05-11-ingredient-management/` |
| 2.3 | product-crud-and-stock | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-product-crud-and-stock/` |
| 2.4 | product-ingredient-association | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-product-ingredient-association/` |
| 2.5 | public-product-catalog | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-public-product-catalog/` |
| 3.1 | delivery-address-management | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-delivery-address-management/` |
| 3.2 | user-profile-view-and-edit | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-user-profile-view-and-edit/` |
| 4.1 | shopping-cart-frontend | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-shopping-cart-frontend/` |
| 5.1 | order-creation-with-uow | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-order-creation-with-uow/` |
| 1.7 | frontend-auth-pages | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-frontend-auth-pages/` |
| 2.6 | frontend-product-catalog-page | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-frontend-product-catalog-page/` |
| 3.3 | frontend-profile-and-addresses | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-frontend-profile-and-addresses/` |
| — | fix-direcciones-empty-state-modal | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-fix-direcciones-empty-state-modal/` |
| 4.2 | frontend-checkout-page | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-frontend-checkout-page/` |
| 5.2 | order-fsm-and-state-transition | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-order-fsm-and-state-transition/` |
| 5.3 | order-cancellation | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-order-cancellation/` |
| — | fix-cart-persistence-and-checkout | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-fix-cart-persistence-and-checkout/` |
| — | fix-lazy-routing-suspense | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-fix-lazy-routing-suspense/` |
| 5.4 | order-history-audit-trail | ✅ Hecho (archivado 2026-05-13) | `openspec/changes/archive/2026-05-13-order-history-audit-trail/` |
| 5.5 | order-list-and-detail | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-order-list-and-detail/` |
| 5.6 | frontend-order-history | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-frontend-order-history/` |
| 7.2 | admin-user-management | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-admin-user-management/` |
| 7.3 | admin-product-management | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-admin-product-management/` |
| 7.4 | admin-order-management | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-admin-order-management/` |
| 7.5 | admin-settings-and-configuration | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-admin-settings-and-configuration/` |
| — | fix-run-server-port-and-deleted-toggle | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-fix-run-server-port-and-deleted-toggle/` |
| 8.1 | error-handling-standardized | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-error-handling-standardized/` |
| 8.3 | frontend-error-and-empty-states | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-frontend-error-and-empty-states/` |
| — | frontend-sidebar-navigation | ✅ Hecho (archivado 2026-05-14) | `openspec/changes/archive/2026-05-14-frontend-sidebar-navigation/` |

| — | admin-pedidos-management | ✅ Hecho (archivado 2026-05-17) | `openspec/changes/archive/2026-05-17-admin-pedidos-management/` |
| — | admin-pedidos-fix-acciones | ✅ Hecho (archivado 2026-05-17) | `openspec/changes/archive/2026-05-17-admin-pedidos-fix-acciones/` |
| 6.1 | mercadopago-payment-creation | ✅ Hecho (archivado 2026-05-17) | `openspec/changes/archive/2026-05-17-mercadopago-payment-creation/` |
| 6.2 | mercadopago-webhook-processing | ✅ Hecho (archivado 2026-05-17) | `openspec/changes/archive/2026-05-17-mercadopago-webhook-processing/` |

> Este change deja listo el **esqueleto monorepo** (`/backend`, `/frontend`), `.gitignore`, `.env.example` y READMEs. **No** instala dependencias ni configura FastAPI/Vite.

---

## Sprint 0 — Infraestructura (NO negociable)

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|

---

## Epic 01 — Autenticación y autorización

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|

---

## Epic 02 — Catálogo de productos

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|

---

## Epic 03 — Direcciones y perfil de cliente

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
---

## Epic 04 — Carrito (frontend)

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|

---

## Epic 05 — Órdenes y máquina de estados

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|

---

## Epic 06 — Pagos (MercadoPago)

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 6.3 | payment-retry-and-status | US-048 | 1:N pagos por pedido + GET /pagos/{pedido_id} + reintentos | 6.1, 6.2 |
| 6.4 | frontend-payment-checkout | US-045, US-048 | Checkout FE con SDK MP + tokenización tarjeta en browser (RN-AU09) + polling estado + UI approved/rejected/pending | 6.1, 4.2, 0.5 |

---

## Epic 07 — Admin panel

| ID | Change | Historias | Funcionalidad | Depende de |
|---:|---|---|---|---|
| 7.1 | admin-dashboard-metrics | US-052, US-053 | KPIs + gráficos (recharts) | 5.5, 6.3, 1.5 |


---

## Epic 08 — Calidad y robustez (transversal)

| ID | Change | Historias | Funcionalidad | Depende de | Razón |
|---:|---|---|---|---|---|
| 8.2 | testing-and-fixtures | Bonus | Pytest: auth/pagos/pedidos/producto + fixtures + mocks MP | Todos | Opcional recomendado |
| 8.4 | frontend-home-and-navigation | — | Landing page con CTA al catálogo, navbar con links a Catálogo/Mis Pedidos/Perfil, footer | 1.7, 2.6 | Sin nav el usuario no puede moverse por la app |

---

## Orden de implementación recomendado (macro)

1) **Fundación (Sprint 0):** 0.1 → 0.2 → 0.3 → 0.4 → 0.5
2) **Auth (Sprint 1):** 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → **1.7** (login/register pages)
3) **Catálogo (Sprint 2-3):** 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → **2.6** (catalog page)
4) **Cliente (Sprint 3):** 3.1 → 3.2 → **3.3** (profile page) → 4.1 → **4.2** (checkout page)
5) **Órdenes (Sprint 4-5):** 5.1 → 5.2 → 5.3 → 5.4 → 5.5 → **5.6** (order history page)
6) **Pagos (Sprint 5-6):** 6.1 → 6.2 → 6.3 → 6.4
7) **Admin (Sprint 7):** 7.1 → 7.2 → 7.3 → 7.4 → 7.5
8) **Calidad (transversal):** **8.3** (error states) + **8.4** (home + nav) → 8.1 → 8.2

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

