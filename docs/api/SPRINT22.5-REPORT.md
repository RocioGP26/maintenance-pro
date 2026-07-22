# Sprint 22.5 · Documentación y cierre

**Estado:** Finalizado ✅

**Fecha:** 2026-07-22

## Resultado

Sprint 22 queda cerrado con material para integradores, ejemplos ejecutables,
colección de pruebas, auditoría de integraciones y pruebas de aislamiento entre
empresas.

## Incluye

- [x] Guía para integradores (`integrator-guide.md`)
- [x] Ejemplos curl/Python y receptor de webhooks (`examples.md`)
- [x] Colección Postman Sprint 22 (`collections/roustix-sprint22.postman_collection.json`)
- [x] Auditoría admin `/api/v1/admin/integration-audit`
- [x] Pruebas de aislamiento entre empresas (`tests/test_api_tenant_isolation.py`)

## Suite Sprint 22 (resumen)

| Sub-sprint | Entrega |
|---|---|
| 22.0 | Diseño y contrato |
| 22.1 | Credenciales de integración |
| 22.2 | API pública Maintenance |
| 22.3 | Webhooks (outbox, HMAC, reintentos) |
| 22.4 | Seguridad y observabilidad |
| 22.5 | Documentación y cierre |

## Verificación sugerida

```powershell
python -m unittest tests.test_public_maintenance_api tests.test_integration_credentials tests.test_webhooks tests.test_webhook_security tests.test_api_tenant_isolation
```

## Cierre de programa

La API pública Maintenance y los webhooks quedan listos para integraciones
externas bajo contrato `/api/v1`, con aislamiento tenant, scopes, entitlements
y material de onboarding para terceros.
