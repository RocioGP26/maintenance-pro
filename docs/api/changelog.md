# Changelog · API pública y Webhooks

## [0.6.0] — 2026-07-22 · Sprint 22.5

### Added

- Guía para integradores y ejemplos curl/Python.
- Colección Postman Sprint 22 (Maintenance + Webhooks admin).
- Endpoint de auditoría `/api/v1/admin/integration-audit`.
- Pruebas de aislamiento entre empresas.

### Status

- ✅ Sprint 22.5 finalizado.
- ✅ Programa Sprint 22 (API pública y Webhooks) cerrado.

## [0.5.0] — 2026-07-22 · Sprint 22.4

### Added

- Matriz de entitlements por plan (API pública y webhooks).
- Rate limit dinámico `public_api.requests_per_minute`.
- Límites de credenciales y endpoints; retención y prune de entregas.
- Verificación HMAC con ventana temporal; excerpt de respuesta en entregas.
- Stats admin `/api/v1/admin/webhook-stats` y desactivación automática auditada.
- Migración `sa7p3r59w82h`.

### Status

- ✅ Sprint 22.4 finalizado.
- ✅ Sprint 22.5 finalizado · programa Sprint 22 cerrado.

## [0.4.0] — 2026-07-22 · Sprint 22.3

### Added

- Endpoints de webhook tenant-safe con secreto de única visualización.
- Outbox transaccional (`integration_events`) y entregas con leases.
- Firma HMAC-SHA256, headers de evento y validación SSRF.
- Reintentos escalonados y desactivación tras fallos consecutivos.
- Eventos de incidencias, OT, lecturas y Asset Health.
- Worker CLI `flask webhooks deliver` y admin REST de entregas.
- Migración `rz6o2q48v71g`.

### Status

- ✅ Sprint 22.3 finalizado.
- ✅ Sprint 22.4 finalizado.
- ✅ Sprint 22.5 finalizado · programa Sprint 22 cerrado.

## [0.3.0] — 2026-07-22 · Sprint 22.2

### Added

- Envelope canónico con `request_id`, versión y paginación.
- Errores estructurados y rate limit por credencial, usuario o IP.
- Filtros incrementales para activos, OT e incidencias.
- Lectura y creación idempotente de incidencias con notificaciones por área.
- Detalle de OT, medidores por activo y lecturas históricas.
- Registro idempotente de lecturas integrado con automatizaciones y Asset Health.
- Colecciones Postman e Insomnia específicas de Maintenance.
- Migración `qy5n1p37u60f`.

### Status

- ✅ Sprint 22.2 finalizado.
- ✅ Sprint 22.3 finalizado.
- ✅ Sprint 22.4 finalizado.
- ✅ Sprint 22.5 finalizado · programa Sprint 22 cerrado.

## [0.2.0] — 2026-07-22 · Sprint 22.1

### Added

- Modelo y migración `integration_credentials` tenant-safe.
- Emisión de API keys `rtx_test_` y `rtx_live_` con secreto visible una vez.
- Hash `scrypt`, scopes, expiración, último uso, rotación y revocación.
- Administración web y REST exclusiva para administradores del tenant.
- Autenticación Bearer unificada para JWT y API key en `/api/v1`.
- Autorización por scopes en activos y órdenes de trabajo.
- Auditoría y pruebas de aislamiento entre empresas.

### Status

- ✅ Sprint 22.1–22.5 finalizados · programa Sprint 22 cerrado.

## [0.1.0] — 2026-07-21 · Sprint 22.0

### Added

- Charter y arquitectura de integración pública.
- Contrato API v1 para Maintenance.
- API keys con scopes y ciclo de vida seguro.
- Catálogo inicial de eventos y envelope de webhooks.
- Firma HMAC con timestamp, reintentos, idempotencia y controles SSRF.
- Modelo de derechos técnicos desacoplado de planes comerciales.
- Roadmap de implementación 22.1–22.5.

### Status

- ✅ Diseño y contrato finalizados.
- 📋 Implementación inicia en Sprint 22.1.
