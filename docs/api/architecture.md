# Arquitectura · API pública y Webhooks

## Vista lógica

```text
Integrador
   │ Authorization: Bearer <JWT|rtx_key>
   ▼
API Gateway Flask · /api/v1
   ├─ Request ID y rate limit
   ├─ Autenticación
   ├─ Resolución inmutable de tenant
   ├─ Scope + módulo + entitlement
   ├─ Servicio de dominio
   └─ Auditoría
          │
          ├─ Respuesta REST
          └─ Evento Outbox ─► Dispatcher ─► Firma HMAC ─► Endpoint cliente
                                      └────► Historial / reintentos
```

## Separación de responsabilidades

| Componente previsto | Responsabilidad |
|---|---|
| `app/public_api/` | rutas, serialización, filtros, errores y OpenAPI |
| `app/integrations/credentials.py` | emisión, hash, rotación y revocación de keys |
| `app/integrations/authorization.py` | scopes, módulos y derechos técnicos |
| `app/integrations/webhooks.py` | endpoints, suscripciones, firma y validación URL |
| `app/integrations/outbox.py` | eventos persistidos dentro de la transacción de negocio |
| worker/CLI | reserva entregas, envía, reintenta y recupera trabajos vencidos |

Las rutas no duplican lógica de mantenimiento: llaman servicios de dominio
existentes. La capa pública traduce nombres internos al contrato MAG.

## Modelo conceptual

### `integration_credentials`

`id`, `empresa_id`, `name`, `key_prefix`, `secret_hash`, `scopes_json`,
`environment`, `expires_at`, `last_used_at`, `revoked_at`, `created_by_id`,
`created_at`.

### `webhook_endpoints`

`id`, `empresa_id`, `name`, `url`, `secret_ciphertext`, `events_json`,
`environment`, `active`, `failure_count`, `disabled_at`, auditoría temporal.

### `integration_events`

`id` UUID, `empresa_id`, `event_type`, `api_version`, `resource_type`,
`resource_id`, `occurred_at`, `payload_json`, `created_at`.

### `webhook_deliveries`

`id`, `empresa_id`, `event_id`, `endpoint_id`, `attempt`, `status`,
`next_attempt_at`, `http_status`, `duration_ms`, `error_code`, timestamps.

Restricciones únicas evitan duplicar `(event_id, endpoint_id, attempt)` y las
consultas siempre incluyen `empresa_id`.

## Outbox transaccional

El evento se guarda en la misma transacción que el cambio de negocio. El worker
solo toma eventos confirmados y crea una entrega por endpoint suscrito. Esto
evita avisar sobre una OT que luego hizo rollback y evita perder el evento entre
el `commit` y una llamada HTTP.

La garantía es **at-least-once**: puede repetirse una entrega, nunca se promete
exactly-once. El receptor deduplica mediante `X-Roustix-Event-Id`.

## Seguridad de red

- HTTPS obligatorio fuera de sandbox.
- Prohibidos localhost, loopback, link-local, metadatos cloud y redes privadas.
- Resolución DNS validada al registrar y antes de entregar.
- Sin redirecciones automáticas.
- Timeout total de 5 segundos y tamaño de respuesta limitado.
- Secretos cifrados o hasheados según necesidad de recuperación.

## Observabilidad

Cada solicitud obtiene `X-Request-Id`. Se registran actor técnico, tenant,
scope, ruta, estado y duración, nunca credenciales ni payloads sensibles. Las
métricas mínimas son solicitudes, latencia, 4xx/5xx, rate limits, backlog de
outbox, éxito de entregas y antigüedad del evento más viejo.
