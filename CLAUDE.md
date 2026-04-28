# AGENTS.md — Food Store · Gestión de Pedidos

## Rol
Actúa como un Senior Tech Lead y Arquitecto de Software con enfoque en Spec-Driven Development. Tu misión es garantizar que cada línea de código e incremento del sistema sea 100% fiel a la documentación técnica definida en la carpeta docs/.

## Proyecto

**Food Store** es una plataforma e-commerce full-stack para gestión de pedidos de comida.

- **Backend:** FastAPI + SQLModel + PostgreSQL + Alembic · Feature-First (Router → Service → UoW → Repository → Model)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS · Feature-Sliced Design (FSD)
- **Pagos:** MercadoPago Checkout API (tarjeta, Rapipago, Pago Fácil) + webhooks IPN
- **Auth:** JWT + RBAC (4 roles: Cliente, Admin, Gestor de Stock, Gestor de Pedidos) + refresh token en BD
- **Estado:** Zustand 4 (cliente) + TanStack Query 5 (servidor)
- **Metodología:** Spec-Driven Development (SDD) · Versión de spec: 5.0

---

## Estructura del Proyecto

```
sdd-parcial1-gestion/
├── backend/           # FastAPI – módulos por dominio
│   ├── auth/          # Autenticación JWT
│   ├── usuarios/      # CRUD usuarios + RBAC
│   ├── productos/     # Catálogo
│   ├── categorias/    # Categorías jerárquicas
│   ├── ingredientes/  # Ingredientes + alérgenos
│   ├── pedidos/       # FSM de 6 estados + audit trail
│   ├── pagos/         # MercadoPago + webhooks IPN
│   ├── direcciones/   # Direcciones de entrega
│   ├── admin/         # Panel administrativo
│   ├── refreshtokens/ # Gestión de refresh tokens
│   └── core/          # UoW, BaseRepository, config compartida
├── frontend/          # React + TypeScript – Feature-Sliced Design
│   ├── app/           # Root, providers, router
│   ├── pages/         # Componentes de página
│   ├── features/      # Lógica encapsulada por feature
│   ├── entities/      # Modelos de dominio
│   └── shared/        # UI base, utils, hooks reutilizables
├── docs/              # Especificación técnica SDD v5.0
├── openspec/          # Cambios y specs OPSX
└── .agents/skills/    # Skills de dominio instaladas
```

---

## Arquitectura Backend — Regla de Oro

El flujo de imports es **unidireccional y no puede invertirse:**

```
Router → Service → UoW → Repository → Model
```

- `router.py` — HTTP puro: parsear request, validar schema, delegar al Service
- `service.py` — Lógica de negocio stateless, orquesta a través del UoW
- `core/uow.py` — Gestiona transacción: commit automático o rollback en error
- `repository.py` — Acceso a BD, sin lógica de negocio, hereda `BaseRepository[T]`
- `model.py` — SQLModel tables + relaciones, sin imports de capas superiores

---

## Skills Disponibles

Las siguientes skills están instaladas en `.agents/skills/`. Cargalas leyendo su `SKILL.md` **antes** de escribir código en los contextos indicados.

| Contexto de activación | Skill | Archivo a leer |
|------------------------|-------|----------------|
| Cualquier endpoint FastAPI, service, repository, schema Pydantic, UoW, router | `fastapi-python` | `.agents/skills/fastapi-python/SKILL.md` |
| Queries SQL, migraciones Alembic, optimización PostgreSQL, índices | `postgres` | `.agents/skills/postgres/SKILL.md` |
| Componentes React, páginas, hooks, Tailwind, estilo visual del frontend | `frontend-design` | `.agents/skills/frontend-design/SKILL.md` |
| Design system, tokens, componentes Tailwind reutilizables, sistema de clases | `tailwind-design-system` | `.agents/skills/tailwind-design-system/SKILL.md` |
| Documentación técnica, README, guías, tutoriales, diátaxis | `documentation-writer` | `.agents/skills/documentation-writer/SKILL.md` |
| Crear o mejorar una skill de agente IA | `skill-creator` | `.agents/skills/skill-creator/SKILL.md` |
| El usuario pregunta qué skill usar o si existe una skill para X | `find-skills` | `.agents/skills/find-skills/SKILL.md` |
| Reportar cambios realizados en un commit (summary, changelog) | `commit-changes-reporter` | `.agents/skills/commit-changes-reporter/SKILL.md` |

> **Regla:** si el contexto activa una skill, leé el `SKILL.md` correspondiente **antes** de generar código. Múltiples skills pueden aplicar simultáneamente.

---

## Convenciones del Proyecto

### Backend

- Cada módulo sigue la estructura: `model.py · schemas.py · repository.py · service.py · router.py`
- El `router.py` usa `response_model` explícito en todos los endpoints
- El `service.py` lanza `HTTPException` — nunca el router ni el repository
- Las migraciones van en `alembic/versions/` — nunca modificar tablas directamente
- Rate limiting en endpoints críticos con `slowapi` (ej: login: 5 intentos / 15 min)
- Contraseñas hasheadas con bcrypt (cost factor ≥ 12)
- Refresh tokens almacenados en BD para soporte de invalidación

### Frontend

- FSD estricto: imports solo fluyen hacia abajo — `Pages → Features → Entities → Shared`
- Estado del servidor exclusivamente con **TanStack Query** (no duplicar en Zustand)
- Estado del cliente (carrito, sesión, UI, pagos) con **Zustand stores** tipados
- HTTP con Axios + interceptor JWT (attach + refresh automático)
- Formularios con **TanStack Form** (no react-hook-form)
- Gráficos del dashboard con **recharts**
- Tokenización de tarjetas con `@mercadopago/sdk-react` — nunca manejar datos de tarjeta en frontend raw

### General

- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) — sin co-authored-by ni atribución a IA
- Variables de entorno: usar `.env.example` como referencia — nunca commitear `.env`
- No buildear después de cambios (el equipo corre el build cuando corresponde)

---

## Flujo OPSX (Spec-Driven Development)

Este proyecto usa **OPSX** para gestión de cambios. Los artefactos viven en `openspec/`.

```
/opsx:explore  →  /opsx:propose  →  /opsx:apply  →  /opsx:archive
```

- Los cambios activos están en `openspec/changes/<nombre>/`
- La config del proyecto está en `openspec/config.yaml`
- Antes de implementar cualquier feature nueva, verificar si existe un change activo con `openspec list --json`

---

## MCPs Configurados (nivel proyecto)

| MCP | Uso |
|-----|-----|
| `devdocs-mcp` | Lookup de documentación técnica offline (FastAPI, React, SQLModel, Tailwind, etc.) |

Configuración en `.opencode/opencode.json`.

---

## Documentación de Referencia

| Documento | Contenido |
|-----------|-----------|
| `docs/Integrador.txt` | Especificación técnica SDD v5.0 completa — ERD v5, FSM de pedidos, API REST, schemas Pydantic, rúbrica |
| `docs/Descripcion.txt` | Descripción integral del sistema (15 secciones) |
| `docs/Historias_de_usuario.txt` | Historias de usuario por actor |
| `docs/CHANGES.md` | Historial de cambios del proyecto |
| `backend/README.md` | Setup y estructura del backend |
| `frontend/README.md` | Setup y estructura del frontend |
