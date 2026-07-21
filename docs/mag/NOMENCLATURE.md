# Nomenclatura · MAG

**Código:** MAG · Roustix API Guide
**Suite docs:** 07 · Sprint 8

## Capítulos (01 – 10)

| Código | Archivo | Título |
|--------|---------|--------|
| **MAG-01-PHIL** | `01-filosofia-api.md` | Filosofía de la API |
| **MAG-02-AUTH** | `02-autenticacion-jwt.md` | Autenticación JWT |
| **MAG-03-TNT** | `03-multi-tenant.md` | Multi-tenant |
| **MAG-04-RES** | `04-recursos.md` | Recursos REST |
| **MAG-05-NAM** | `05-convenciones-nombres.md` | Convenciones de nombres |
| **MAG-06-ERR** | `06-manejo-errores.md` | Manejo de errores |
| **MAG-07-VER** | `07-versionado.md` | Versionado `/api/v1` |
| **MAG-08-HOOK** | `08-webhooks.md` | Webhooks |
| **MAG-09-EX** | `09-ejemplos.md` | Ejemplos y SDK |
| **MAG-10-LIM** | `10-limites-buenas-practicas.md` | Límites y buenas prácticas |

## Terminología

| Término | Significado |
|---------|-------------|
| **Tenant** | Concepto arquitectónico de aislamiento (MPA) |
| **Empresa** | Implementación en BD (`empresa_id`, tabla `empresas`) |
| Uso en docs | *Tenant (Empresa)* cuando ambos aplican |

## Política de idioma (MAG)

| Capa | Idioma |
|------|--------|
| URLs · HTTP methods · JSON keys (`data`, `meta`, `links`, `error`) | **Inglés** |
| Prosa documental · `error.message` | Español |
| Atributos de recurso | `snake_case` inglés (MAG-05) |

## Árbol API v1 (MAG-04)

Prefijo: `/api/v1` · namespaces: `maintenance`, `inventory`, `purchasing`, `sales`, `crm`, `admin`, `platform`

## Versionado API (MAG-07)

| Versión | Prefijo | Estado |
|---------|---------|--------|
| Legacy | `/api/*` | Temporal · `Deprecation` |
| v1 | `/api/v1/` | Contrato oficial |
| v2 | `/api/v2/` | Roadmap |

OpenAPI: `/api/v1/openapi.json` · docs: `/docs/api/v1`

## Claims JWT (MAG-02)

| Claim | Descripción |
|-------|-------------|
| `sub` | ID usuario |
| `empresa_id` | Tenant |
| `empresa_slug` | Slug público |
| `rol` | Rol principal |
| `plan` | Plan contratado |
| `modules` | Módulos activos |
| `iat` / `exp` | Emisión · expiración |

## Claims reservados (MAG-02)

`tenant_type` · `permissions` · `locale` · `timezone` · `features`

## Auth endpoints

| Ruta | Estado |
|------|--------|
| `POST /api/v1/auth/login` | Contrato v1 · legacy `/api/auth/login` activo |
| `POST /api/v1/auth/refresh` | 📋 MAG v2.0 |
| `POST /api/v1/auth/logout` | 📋 Planificado |

## Códigos de error (MAG-06)

Catálogo completo → [06-manejo-errores.md](chapters/06-manejo-errores.md)

| Categoría | Códigos |
|-----------|---------|
| Auth | `INVALID_TOKEN`, `TOKEN_EXPIRED`, `LOGIN_FAILED`, `USER_DISABLED`, `SESSION_EXPIRED` |
| Permisos | `PERMISSION_DENIED`, `MODULE_NOT_ENABLED`, `PLAN_NOT_ALLOWED`, `TENANT_SUSPENDED` |
| Recursos | `RESOURCE_NOT_FOUND`, `RESOURCE_ALREADY_EXISTS`, `RESOURCE_CONFLICT` |
| Validación | `VALIDATION_ERROR`, `INVALID_PARAMETER`, `INVALID_REQUEST` |
| Plataforma | `INTERNAL_ERROR`, `DATABASE_ERROR`, `SERVICE_UNAVAILABLE`, `RATE_LIMIT_EXCEEDED` |

## Eventos webhook (MAG-08)

Catálogo completo → [08-webhooks.md](chapters/08-webhooks.md)

| Módulo | Eventos |
|--------|---------|
| Maintenance | `asset.created`, `asset.updated`, `work_order.created`, `work_order.updated`, `work_order.closed` |
| Inventory | `product.created`, `product.updated`, `stock.updated`, `stock.low`, `movement.created` |
| Platform | `tenant.created`, `user.created`, `subscription.updated`, `plan.changed` |

Headers: `X-Roustix-Signature` · `X-Event-Id`

## Estado Sprint 8

| Capítulo | Estado |
|----------|--------|
| MAG-01 – MAG-10 | ✅ Entregado · **MAG v1.0 completo** |

## Relación

| Doc | Rol |
|-----|-----|
| MPA | Arquitectura interna · MPA-06 integraciones |
| MRL | Exportaciones PDF/Excel |
| SDK (08) | Clientes oficiales sobre MAG v1 |
| Developer (09) | Setup local · contribución |
