# Guía para integradores · API pública y Webhooks v1

**Audiencia:** equipos ERP, BI, iPaaS y desarrollo externo.  
**Base:** `https://<host>/api/v1` · autenticación `Authorization: Bearer <credential>`

## 1. Identidad

| Tipo | Formato | Uso |
|---|---|---|
| API key de prueba | `rtx_test_<prefix>.<secret>` | Sandbox / QA |
| API key live | `rtx_live_<prefix>.<secret>` | Producción |
| JWT de usuario | token de `/api/v1/auth/login` | Apps interactivas |

El secreto de la API key **solo se muestra una vez** al crear o rotar. Guárdalo
en un vault; Roustix solo conserva hash `scrypt` y prefijo.

Scopes habituales:

```text
maintenance.assets:read
maintenance.incidents:read
maintenance.incidents:write
maintenance.work_orders:read
maintenance.meters:read
maintenance.meters:write
```

## 2. Contrato de respuesta

Éxito:

```json
{
  "data": { },
  "meta": {
    "request_id": "req_…",
    "api_version": "v1",
    "pagination": { "page": 1, "page_size": 50, "total": 12 }
  }
}
```

Error:

```json
{
  "error": {
    "code": "SCOPE_REQUIRED",
    "message": "La credencial no permite esta operación.",
    "details": {},
    "request_id": "req_…"
  }
}
```

Headers de respuesta: `X-Request-Id`, `X-Roustix-Api-Version`.

## 3. Recursos Maintenance

| Método | Ruta | Scope |
|---|---|---|
| GET | `/me` | cualquiera válida |
| GET | `/maintenance/assets` | `maintenance.assets:read` |
| GET | `/maintenance/assets/{id}` | `maintenance.assets:read` |
| GET | `/maintenance/work-orders` | `maintenance.work_orders:read` |
| GET | `/maintenance/work-orders/{id}` | `maintenance.work_orders:read` |
| GET/POST | `/maintenance/incidents` | read / write |
| GET | `/maintenance/incidents/{id}` | `maintenance.incidents:read` |
| GET | `/maintenance/assets/{id}/meters` | `maintenance.meters:read` |
| GET/POST | `/maintenance/meters/{id}/readings` | read / write |

Filtros incrementales: `updated_since` (ISO-8601 UTC).  
Escrituras: header obligatorio `Idempotency-Key` (8–120 caracteres ASCII).

## 4. Webhooks

1. Un administrador registra la URL HTTPS y selecciona eventos.
2. Copia el secreto `whsec_…` (única visualización).
3. Verifica cada entrega:

```text
HMAC_SHA256(secret, "{timestamp}." + raw_body)
```

Headers: `X-Roustix-Event-Id`, `X-Roustix-Timestamp`, `X-Roustix-Signature: v1=<hex>`.  
Rechaza timestamps con más de 5 minutos de diferencia y deduplica por event id.

Catálogo: ver [webhooks.md](webhooks.md).

Worker operativo:

```powershell
flask webhooks deliver --limit 50
flask webhooks prune
```

## 5. Límites y planes

Los cupos (RPM, credenciales, endpoints, retención) salen de entitlements del
plan activo. Consulta admin `/api/v1/admin/webhook-stats` (sesión admin).

## 6. Aislamiento tenant

- El tenant se deriva de la credencial, nunca del body.
- Recursos de otra empresa responden `404` / `RESOURCE_NOT_FOUND`.
- Eventos y entregas llevan siempre `empresa_id` del emisor.

## 7. Material de apoyo

| Recurso | Ruta |
|---|---|
| Ejemplos curl/Python | [examples.md](examples.md) |
| OpenAPI | [openapi.v1.yaml](openapi.v1.yaml) |
| Colecciones | [collections/README.md](collections/README.md) |
| Contrato REST | [api-contract.md](api-contract.md) |
| Webhooks | [webhooks.md](webhooks.md) |
| Permisos | [permissions-plans.md](permissions-plans.md) |
