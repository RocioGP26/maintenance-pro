# Sprint 22.4 · Seguridad y observabilidad

**Estado:** Finalizado ✅

**Fecha:** 2026-07-22

## Resultado

La superficie pública y los webhooks quedan gobernados por entitlements de plan,
con firma HMAC verificable, límites de solicitudes, registro de entregas,
reintentos, desactivación automática auditada y aislamiento estricto por tenant.

## Incluye

| Capacidad | Implementación |
|---|---|
| Firma HMAC | `sign_payload` / `verify_signature` (ventana 5 min, compare digest) |
| Límites de solicitudes | `public_api.requests_per_minute` por plan → Flask-Limiter dinámico |
| Registro de entregas | historial tenant-safe + `response_excerpt` + `/webhook-stats` |
| Reintentos | cola con backoff; reintento manual gated por entitlement |
| Desactivación automática | umbral `webhooks.auto_disable_after` + auditoría |
| Datos por tenant | outbox/entregas filtrados por `empresa_id`; payload sin secretos |

## Matriz comercial (entitlements)

Claves estables (`webhooks.enabled`, `public_api.credentials_max`, …) resueltas
desde el plan activo (Trial / Start / Grow / Scale / Enterprise) sin
`if plan == enterprise` en las rutas.

## Entregables

- [x] `app/integrations/entitlements.py`
- [x] límites de endpoints y credenciales
- [x] rate limit dinámico de API pública
- [x] stats admin `/api/v1/admin/webhook-stats`
- [x] migración `sa7p3r59w82h` (`response_excerpt`)
- [x] CLI `flask webhooks prune`
- [x] pruebas HMAC, límites e aislamiento tenant

## Próximo paso

**Sprint 22.5 · Documentación y cierre** — completado. Programa Sprint 22 cerrado.
