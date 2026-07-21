# Contrato API pública v1

## Envelope

Recurso individual:

```json
{"data":{"asset_id":15,"asset_code":"PC-CAL-014"},"meta":{"request_id":"req_…","api_version":"v1"}}
```

Colección:

```json
{
  "data": [],
  "meta": {
    "request_id": "req_…",
    "api_version": "v1",
    "pagination": {"page": 1, "page_size": 50, "total": 0}
  }
}
```

Error:

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "La credencial no permite esta operación.",
    "details": {},
    "request_id": "req_…"
  }
}
```

## Recursos aprobados

| Método | Ruta | Scope mínimo | Fase |
|---|---|---|---|
| GET | `/api/v1/me` | autenticado | existente |
| GET | `/api/v1/maintenance/assets` | `maintenance.assets:read` | existente/convergencia |
| GET | `/api/v1/maintenance/assets/{asset_id}` | `maintenance.assets:read` | existente/convergencia |
| GET | `/api/v1/maintenance/incidents` | `maintenance.incidents:read` | 22.2 |
| GET | `/api/v1/maintenance/incidents/{incident_id}` | `maintenance.incidents:read` | 22.2 |
| POST | `/api/v1/maintenance/incidents` | `maintenance.incidents:write` | 22.2 |
| GET | `/api/v1/maintenance/work-orders` | `maintenance.work_orders:read` | existente/convergencia |
| GET | `/api/v1/maintenance/work-orders/{work_order_id}` | `maintenance.work_orders:read` | 22.2 |
| GET | `/api/v1/maintenance/assets/{asset_id}/meters` | `maintenance.meters:read` | 22.2 |
| GET | `/api/v1/maintenance/meters/{meter_id}/readings` | `maintenance.meters:read` | 22.2 |
| POST | `/api/v1/maintenance/meters/{meter_id}/readings` | `maintenance.meters:write` | 22.2 |
| CRUD | `/api/v1/admin/integration-credentials` | sesión admin | 22.1 |
| CRUD | `/api/v1/admin/webhooks` | sesión admin | 22.3 |
| GET | `/api/v1/admin/webhook-deliveries` | sesión admin | 22.3 |
| POST | `/api/v1/admin/webhook-deliveries/{id}/retry` | sesión admin | 22.3 |

No se habilitan escrituras maestras de activos ni cierre remoto de OT en el MVP.
Se añadirán después de definir concurrencia, auditoría e idempotencia específicas.

## Filtros y paginación

- `page` inicia en 1; `page_size` por defecto 50 y máximo 200.
- `updated_since` usa ISO 8601 UTC y permite sincronización incremental.
- filtros de estado, prioridad, activo y fecha se combinan con AND.
- orden predeterminado estable: fecha descendente e ID descendente.
- parámetros desconocidos producen `400 INVALID_PARAMETER`.

## Escrituras e idempotencia

`POST` de incidencias y lecturas acepta `Idempotency-Key` de 8–120 caracteres.
La clave se aísla por empresa, credencial y operación. Repetir la misma clave y
el mismo cuerpo devuelve la respuesta original; cambiar el cuerpo devuelve
`409 IDEMPOTENCY_CONFLICT`.

## Códigos adicionales

| Código | HTTP |
|---|---:|
| `INVALID_API_KEY` | 401 |
| `API_KEY_EXPIRED` | 401 |
| `API_KEY_REVOKED` | 401 |
| `SCOPE_REQUIRED` | 403 |
| `ENTITLEMENT_REQUIRED` | 403 |
| `IDEMPOTENCY_CONFLICT` | 409 |
| `RATE_LIMIT_EXCEEDED` | 429 |

Los recursos ajenos al tenant siempre responden `404 RESOURCE_NOT_FOUND`.
