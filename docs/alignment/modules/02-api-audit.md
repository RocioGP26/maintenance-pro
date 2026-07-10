# Fase 1.4 · API MAG vs implementación · Mantenimiento

**Sprint 14.4** · **Estado:** 🟡 Alineado parcial  
**MAG:** [MAG-04 Recursos](/mag/chapters/04-recursos.md) · [OpenAPI v1](/api/v1/openapi.json)

---

## Mapa de rutas

| MAG v1 | Legacy | Método | Estado |
|--------|--------|--------|--------|
| `/api/v1/auth/login` | `/api/auth/login` | POST | ✅ |
| `/api/v1/me` | `/api/me` | GET | ✅ |
| `/api/v1/maintenance/assets` | `/api/activos` | GET | ✅ |
| `/api/v1/maintenance/assets/{id}` | `/api/activos/{id}` | GET | ✅ |
| `/api/v1/maintenance/work-orders` | — | GET | 🟡 Lectura |
| `/api/v1/admin/summary` | `/api/admin/resumen` | GET | ✅ |
| `/api/v1/maintenance/assets` | — | POST | 📋 |
| `/api/v1/maintenance/assets/{id}` | — | PATCH/PUT/DELETE | 📋 |
| `/api/v1/maintenance/work-orders` | — | POST | 📋 |
| `/api/v1/auth/refresh` | — | POST | 📋 MAG v2 |

**OpenAPI:** `/api/v1/openapi.json` · `/api/v1/openapi.yaml`

---

## Alineación aplicada (2026-07-10)

### Alias `/api/v1`

Rutas v1 registradas en `app/tenancy/api_routes.py` — legacy conservado con cabeceras:

- `Deprecation: true`
- `Link: </api/v1/...>; rel="successor-version"`

### Formato MAG v1

| Recurso | Legacy | v1 |
|---------|--------|-----|
| Activos | `{ total, items[] }` español | `{ data[], meta.pagination }` inglés |
| Asset fields | `id`, `codigo`, `nombre` | `asset_id`, `asset_code`, `name` |
| Status | `operativo`, `mantenimiento`, `falla` | `operational`, `maintenance`, `failure` |
| Login | `token` | + `expires_in`, `modules` |
| `/me` | básico | + `modules` (`maintenance`, `inventory`) |

### Módulos MAG

`app/modules.py` → `modulos_mag_de()` mapea `mantenimiento` → `maintenance`, `inventario` → `inventory`.

### Guard de tenant

Endpoints maintenance verifican módulo `mantenimiento` activo antes de responder.

---

## Rutas web (fuera de MAG)

| Ruta | Tipo | Notas |
|------|------|-------|
| `/activos/api/sugerir-codigo` | Sesión web | No es API pública MAG |
| `/activos/api/campos` | Sesión web | Campos personalizados |
| `/ordenes/api/historial-proveedor/{id}` | Sesión web | OT interna |

---

## Gaps pendientes

| ID | Gap | Prioridad |
|----|-----|-----------|
| A1 | POST/PATCH/DELETE assets v1 | P2 |
| A2 | CRUD work-orders v1 | P2 |
| A3 | Envelope errores MAG-06 estructurado | P2 |
| A4 | Webhooks `work_order.*` | 📋 |
| A5 | Paginación legacy `/api/activos` | 📋 |
| A6 | OpenAPI enum `failure` vs `inactive` | Doc |

---

## Verificación manual

```bash
# Login v1
curl -s -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"...","password":"...","empresa_slug":"..."}'

# Activos MAG
curl -s http://127.0.0.1:5000/api/v1/maintenance/assets \
  -H "Authorization: Bearer TOKEN"

# OT MAG
curl -s http://127.0.0.1:5000/api/v1/maintenance/work-orders \
  -H "Authorization: Bearer TOKEN"
```

---

→ [Auditoría Fase 1](02-maintenance-audit.md) · [Permisos](02-permissions-matrix.md)
