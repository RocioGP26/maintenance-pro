# MAG Strategy · Sprint 8

## Objetivo

**Roustix API Guide v1.0** — contrato oficial para integradores externos.

## Posición en la suite

| Manual | Pregunta |
|--------|----------|
| MPA (05) | ¿Cómo está construido por dentro? |
| **MAG (07)** | ¿Cómo me integro desde fuera? |
| SDK (08) | ¿Hay cliente listo para usar? |

## Entregables Sprint 8

| # | Capítulo | Contenido |
|---|----------|-----------|
| 8.1 | Filosofía | API como producto · REST · tenant-first |
| 8.2 | Auth | JWT · login · Bearer |
| 8.3 | Multi-tenant | Aislamiento · roles · `/me` |
| 8.4 | Recursos | assets · work-orders · inventory |
| 8.5 | Convenciones | URLs · JSON · headers |
| 8.6 | Errores | Códigos · formato · HTTP |
| 8.7 | Versionado | `/api/v1` · deprecación |
| 8.8 | Webhooks | Eventos · firma HMAC |
| 8.9 | Ejemplos | curl · Python · JS |
| 8.10 | Límites | Rate limits · buenas prácticas |

## Implementación código (post-doc)

1. Alias `/api/v1/*` sobre rutas tenancy existentes
2. Recursos `work-orders` · `inventory`
3. Formato error estructurado MAG-06
4. OpenAPI `docs/api/openapi.v1.yaml`
5. Webhooks MAG-08

## Código existente

- `app/tenancy/api_routes.py` — login, me, activos, admin
- `app/tenancy/jwt_auth.py` — generar/verificar token
- `app/tenancy/decorators.py` — `@tenant_required`, `@rol_required`
