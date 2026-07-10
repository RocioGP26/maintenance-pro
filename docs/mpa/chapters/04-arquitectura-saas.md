# MPA-04-SAAS · Arquitectura SaaS

**Código:** MPA-04-SAAS · Sprint 6.4

> Cómo Maintix opera como **software como servicio** multi-tenant: **tenants** (empresas cliente), usuarios, planes, facturación y aislamiento.

**Terminología:** *tenant* = concepto arquitectónico · *empresa* = implementación (`empresa_id`). Contrato API → [MAG-03 · Multi-tenant](/mag/chapters/03-multi-tenant.md).

---

## 1 · Modelo SaaS

| Principio | Implementación |
|-----------|----------------|
| Una instancia de app | Un despliegue sirve N empresas |
| Aislamiento lógico | `empresa_id` + middleware tenancy |
| Activación por módulo | JSON en empresa, no despliegues separados |
| Planes con límites | Trial → Básico → Profesional → Enterprise |
| Onboarding self-service | Wizard de registro + plantilla sectorial |

---

## 2 · Multi-tenant

### Contexto de request

```
Request
  → JWT Bearer (API) o sesión Flask-Login (web)
  → middleware: g.empresa_id, g.user
  → verificar empresa no suspendida
  → verificar módulo requerido por endpoint
  → handler
```

**Archivos clave:** `app/tenancy/middleware.py`, `context.py`, `jwt_auth.py`

### Rutas públicas (sin tenant)

- Landing, login, onboarding, health
- Catálogos documentales (`/docs/`, `/mpa/`, `/mcm/`…)
- Platform superadmin (`/platform/`)

---

## 3 · Empresas

Entidad central `Empresa`:

| Campo | Uso |
|-------|-----|
| `razon_social`, `nit`, `pais` | Identidad legal |
| `sector` | Plantilla al registrarse |
| `slug` | Identificador URL |
| `modulos_activos_json` | Módulos habilitados |
| `suspendida` | Bloqueo por impago o administración |
| `moneda`, `zona_horaria`, jornada | Configuración operativa |

**Sedes:** soporte multi-sede dentro de un tenant (`Sede`).

---

## 4 · Usuarios

- Un usuario pertenece a **una empresa** (`User.empresa_id`)
- Autenticación web: sesión Flask-Login
- API: JWT con claims de tenant (`tenancy_api`)
- **Impersonación:** superadmin plataforma puede operar como empresa (auditoría registrada)

---

## 5 · Roles

Ver MPA-03-MOD. En SaaS, los roles controlan:

- Quién configura la empresa
- Quién opera OT vs ventas
- Quién invita usuarios al equipo

Los roles de **plataforma** (`/platform/`) son distintos: gestionan tenants, planes y facturación global.

---

## 6 · Planes

`PlanTipo` en `app/models.py`:

| Plan | Perfil comercial (MCM-06) |
|------|---------------------------|
| `trial` | Prueba 14 días |
| `basico` | Start — un módulo, equipo pequeño |
| `profesional` | Grow — módulos combinados |
| `enterprise` | Scale — límites ampliados, soporte |

Límites por plan (`CatalogoPlan`): activos, usuarios, `storage_mb`.

**Suscripción:** `PlanSuscripcion` por empresa con plan activo.

---

## 7 · Facturación

- Gestión desde `/platform/` (superadmin)
- Servicios: `subscription_service`, `platform_billing`
- Suspensión de tenant por estado de pago (`empresa_puede_operar`)

*Nota:* la integración con pasarela de pago es evolución planificada; hoy el ciclo es administrado en plataforma.

---

## 8 · Configuración

Niveles de configuración:

| Nivel | Ejemplos |
|-------|----------|
| **Plataforma** | Catálogo sectores, planes, feature flags |
| **Empresa** | Logo, moneda, módulos, jornada laboral |
| **Sector** | Tipos de activo, campos custom, dashboard JSON |
| **Usuario** | Perfil, preferencias |

---

## 9 · Aislamiento

| Capa | Mecanismo |
|------|-----------|
| Datos | `empresa_id` en queries |
| Archivos | Rutas con contexto tenant (logos, adjuntos) |
| Módulos | Middleware bloquea endpoints |
| Operación | Flag `suspendida` + bloqueo en middleware |
| Auditoría | `platform_audit` para acciones sensibles |

**Nunca** confiar solo en ocultar enlaces en UI — el backend debe rechazar acceso cross-tenant.

---

## 10 · Backups

- Servicio: `app/backup_service.py`
- SQLite y PostgreSQL (Neon en producción)
- CLI: `flask backup-db`
- Retención configurable (`prune_old_backups`)

Los backups son **de plataforma** (toda la base), con aislamiento lógico por tenant en restore selectivo (operación manual hoy).

---

## Siguiente

→ [MPA-05-ROAD · Roadmap de módulos](05-roadmap-modulos.md)
