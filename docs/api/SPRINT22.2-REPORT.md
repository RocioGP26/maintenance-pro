# Sprint 22.2 · API pública Maintenance

**Estado:** Finalizado ✅

**Fecha:** 2026-07-22

## Resultado

La API pública v1 de Maintenance queda disponible para integraciones tenant-safe:
activos, OT, incidencias, medidores y lecturas, con contrato uniforme, scopes e
idempotencia.

## Entregables

- [x] API pública de activos, OT, incidencias, medidores y lecturas
- [x] Envelopes y errores normalizados (`data` / `meta` / `error.code`)
- [x] `X-Request-Id`, paginación y filtros incrementales (`updated_since`, etc.)
- [x] Rate limit por identidad (credencial, usuario o IP)
- [x] Creación idempotente de incidencias y lecturas
- [x] Notificaciones por área
- [x] Integración con automatizaciones y Asset Health
- [x] Migración `qy5n1p37u60f` (timestamps incrementales + registros idempotentes)
- [x] OpenAPI y colecciones Postman/Insomnia
- [x] Pruebas de contrato (`tests.test_public_maintenance_api`,
  `tests.test_integration_credentials`)

## Endpoints

| Método | Ruta |
|---|---|
| GET | `/api/v1/maintenance/assets` |
| GET | `/api/v1/maintenance/assets/{id}` |
| GET | `/api/v1/maintenance/work-orders` |
| GET | `/api/v1/maintenance/work-orders/{id}` |
| GET/POST | `/api/v1/maintenance/incidents` |
| GET | `/api/v1/maintenance/incidents/{id}` |
| GET | `/api/v1/maintenance/assets/{id}/meters` |
| GET/POST | `/api/v1/maintenance/meters/{id}/readings` |

## Próximo paso

**Sprint 22.5 · Documentación y cierre** — completado. Programa Sprint 22 cerrado.
