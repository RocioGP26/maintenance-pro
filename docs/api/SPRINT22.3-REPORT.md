# Sprint 22.3 · Webhooks

**Estado:** Finalizado ✅

**Fecha:** 2026-07-22

## Resultado

Roustix emite eventos de Maintenance y Asset Health mediante outbox
transaccional, con entrega firmada HMAC-SHA256, validación SSRF, reintentos y
administración tenant-safe.

## Eventos iniciales

| Evento | Origen |
|---|---|
| `incident.created` | incidencia confirmada |
| `incident.status_changed` | cambio efectivo de estado |
| `work_order.created` | OT numerada |
| `work_order.assigned` | técnico asignado o reasignado |
| `work_order.status_changed` | transición de estado |
| `work_order.completed` | trabajo técnico terminado |
| `work_order.closed` | cierre definitivo |
| `meter.reading_created` | lectura confirmada |
| `meter.reading_flagged` | lectura fuera de rango / anomalía |
| `asset_health.band_changed` | cambio persistido de banda |

## Entregables

- [x] tablas `webhook_endpoints`, `integration_events`, `webhook_deliveries`
- [x] migración `rz6o2q48v71g`
- [x] outbox en la misma transacción de negocio
- [x] firma `HMAC_SHA256(secret, timestamp + "." + body)` y headers Roustix
- [x] reintentos (inmediato → 1m → 5m → 15m → 1h) y leases
- [x] SSRF (HTTPS en live; HTTP/localhost solo en `test`)
- [x] admin REST `/api/v1/admin/webhooks` y entregas / retry
- [x] worker CLI `flask webhooks deliver`
- [x] pruebas de contrato HMAC, outbox y SSRF

## Operación

```powershell
flask webhooks deliver --limit 50
```

## Próximo paso

**Sprint 22.5 · Documentación y cierre** — completado. Programa Sprint 22 cerrado.
