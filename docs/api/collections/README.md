# Colecciones API · Roustix v1

Colecciones oficiales alineadas a [`openapi.v1.yaml`](../openapi.v1.yaml) y a la
[guía para integradores](../integrator-guide.md).

## Archivos

| Archivo | Uso |
|---------|-----|
| `roustix-sprint22.postman_collection.json` | **Sprint 22.5** · Maintenance + Webhooks admin + auditoría |
| `roustix-maintenance-v1.postman_collection.json` | Maintenance pública (API key) |
| `roustix-maintenance-v1.insomnia.json` | Insomnia · Maintenance |
| `roustix-api-v1.postman_collection.json` | Postman · Collection MAG general |
| `roustix-sandbox.postman_environment.json` | Postman · entorno Sandbox |
| `roustix-api-v1.insomnia.json` | Insomnia · Export v4 |

## Importación rápida (Sprint 22)

1. Import → `roustix-sprint22.postman_collection.json`
2. Import → `roustix-sandbox.postman_environment.json` (opcional)
3. Define `roustix_api_key` con una key `rtx_test_…`
4. Carpeta **Public · Maintenance**: requests con Bearer
5. Carpeta **Admin · Webhooks**: requiere sesión de administrador (cookie)

## Variables

| Variable | Valor por defecto |
|----------|-------------------|
| `base_url` | `http://127.0.0.1:5000/api/v1` |
| `roustix_api_key` | `rtx_test_REPLACE_ME` |
| `asset_id` / `work_order_id` / `meter_id` | IDs de prueba |

## Pruebas automatizadas relacionadas

```powershell
python -m unittest tests.test_public_maintenance_api tests.test_integration_credentials tests.test_webhooks tests.test_webhook_security tests.test_api_tenant_isolation
```

→ [MSD-03 OpenAPI](../../msd/chapters/03-openapi.md) · [MSD-08 Colecciones](../../msd/chapters/08-colecciones.md)
