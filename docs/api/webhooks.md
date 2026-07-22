# Contrato de Webhooks v1

## Catálogo inicial

| Evento | Cuándo se genera |
|---|---|
| `incident.created` | incidencia confirmada |
| `incident.status_changed` | cambio efectivo de estado |
| `work_order.created` | OT confirmada |
| `work_order.assigned` | técnico asignado o reasignado |
| `work_order.status_changed` | transición válida de estado |
| `work_order.completed` | trabajo técnico terminado |
| `work_order.closed` | cierre definitivo supervisado |
| `meter.reading_created` | lectura confirmada |
| `meter.reading_flagged` | lectura fuera de rango o secuencia |
| `asset_health.band_changed` | cambio persistido de banda de salud |

No se emite un evento si la transacción de negocio hace rollback. Los cambios
sin efecto no crean eventos duplicados.

## Envelope

```json
{
  "id": "evt_01K…",
  "type": "work_order.completed",
  "api_version": "v1",
  "occurred_at": "2026-07-21T20:15:30Z",
  "tenant": {"slug": "empresa-xyz"},
  "data": {
    "object": {
      "work_order_id": 128,
      "asset_id": 15,
      "status": "completed"
    }
  }
}
```

Los timestamps siempre son UTC. El payload contiene referencias necesarias,
no expedientes completos ni secretos. El receptor consulta la API si requiere
el estado más reciente.

## Headers

```http
Content-Type: application/json
User-Agent: Roustix-Webhooks/1.0
X-Roustix-Event-Id: evt_01K…
X-Roustix-Timestamp: 1784664930
X-Roustix-Signature: v1=<hex_hmac_sha256>
```

La firma se calcula sobre:

```text
HMAC_SHA256(secret, timestamp + "." + raw_body)
```

El receptor compara en tiempo constante, rechaza timestamps con más de cinco
minutos de diferencia y deduplica por `X-Roustix-Event-Id`.

## Entrega y reintentos

| Resultado | Tratamiento |
|---|---|
| `200–299` | entregado |
| `408`, `425`, `429` | reintentar; respetar `Retry-After` acotado |
| `500–599` o error de red | reintentar |
| otros `400–499` | fallo terminal de esa entrega |

Máximo cinco intentos: inmediato, 1 minuto, 5 minutos, 15 minutos y 1 hora.
Cada intento tiene timeout de 5 segundos. La entrega no garantiza orden global;
`occurred_at` y `id` permiten ordenar y deduplicar.

## Administración

El administrador puede:

- registrar URL HTTPS y seleccionar eventos;
- enviar un evento de prueba claramente identificado;
- rotar el secreto;
- pausar o eliminar el endpoint;
- consultar estado, HTTP, latencia e intentos;
- reintentar manualmente si el entitlement lo permite.

El secreto solo se muestra al crear o rotar. Los historiales no exponen headers
sensibles ni cuerpos de respuesta completos.

## Estados

Endpoint: `active`, `paused`, `disabled`.

Entrega: `pending`, `processing`, `delivered`, `retry_scheduled`, `failed`.

Una tarea `processing` abandonada vuelve a `pending` mediante lease con
expiración. Los endpoints con fallos consecutivos se desactivan automáticamente
tras el umbral configurado y quedan auditados.
