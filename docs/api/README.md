# API · Referencia técnica Roustix

**Código:** MTX-API · Suite docs **07** (complemento MAG)

Referencia **machine-readable** — complementa [MAG](../mag/README.md) (guía conceptual para integradores).

## Contenido

| Sección | Descripción | Estado |
|---------|-------------|--------|
| [MAG v1.0](/mag/) | Guía completa API | ✅ Sprint 8 |
| [MSD v1.0](/msd/) | SDK & Developer Portal | ✅ Sprint 9 completo |
| OpenAPI 3.1 | `openapi.v1.yaml` · `/api/v1/openapi.json` | ✅ Core |
| Colecciones | [collections/](collections/README.md) | ✅ Snapshot v1 |
| Tenancy API | `app/tenancy/api_routes.py` | ✅ Parcial |

## Rutas implementadas (legacy)

| Método | Ruta MAG v1 | MAG v1 equivalente |
|--------|-------------|-------------------|
| POST | `/api/auth/login` | `/api/v1/auth/login` |
| GET | `/api/me` | `/api/v1/me` |
| GET | `/api/activos` | `/api/v1/maintenance/assets` |
| GET | `/api/activos/{id}` | `/api/v1/maintenance/assets/{id}` |
| GET | `/api/admin/resumen` | `/api/v1/admin/summary` |

## Relacionado

| Doc | Rol |
|-----|-----|
| [MAG](/mag/) | Contrato oficial · JWT · webhooks |
| [MSD](/msd/) | Portal · SDK · OpenAPI · Sprint 9 |
| [MPA-06](../mpa/chapters/06-integraciones.md) | Estrategia integraciones |
| [SDK](../sdk/README.md) | Paquetes oficiales |

→ [Índice maestro](../README.md) · [/docs/](http://127.0.0.1:5000/docs/)
