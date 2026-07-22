# API pública y Webhooks · Sprint 22

**Estado:** Sprint 22 · API pública y Webhooks **completo** ✅

**Implementación:** credenciales, Maintenance v1, webhooks, seguridad y docs de cierre

**Base canónica:** `/api/v1`

Sprint 22 convierte la API tenant existente y el contrato MAG en una superficie
pública, segura y operable. La documentación describe capacidades acordadas;
solo `openapi.v1.yaml` identifica rutas ya expuestas o listas para consumo.

## Documentos

| Documento | Propósito |
|---|---|
| [Guía para integradores](integrator-guide.md) | Onboarding de terceros (auth, scopes, webhooks) |
| [Ejemplos](examples.md) | curl, Python y receptor HMAC |
| [Colecciones](collections/README.md) | Postman / Insomnia y suite de pruebas |
| [Charter](charter.md) | Objetivo, alcance, decisiones y Definition of Done |
| [Arquitectura](architecture.md) | Componentes, aislamiento, outbox y observabilidad |
| [Contrato API v1](api-contract.md) | Recursos, respuestas, filtros y errores |
| [Autenticación, permisos y planes](permissions-plans.md) | JWT, API keys, scopes y derechos técnicos |
| [Contrato de webhooks](webhooks.md) | Eventos, firma, entregas y reintentos |
| [Roadmap](roadmap.md) | Sub-sprints 22.1–22.5 |
| [Reporte Sprint 22.0](SPRINT22-REPORT.md) | Evidencia de cierre documental |
| [Reporte Sprint 22.1](SPRINT22.1-REPORT.md) | Credenciales, scopes y pruebas tenant-safe |
| [Reporte Sprint 22.2](SPRINT22.2-REPORT.md) | Recursos Maintenance, idempotencia y sincronización incremental |
| [Reporte Sprint 22.3](SPRINT22.3-REPORT.md) | Outbox, HMAC, reintentos y catálogo de eventos |
| [Reporte Sprint 22.4](SPRINT22.4-REPORT.md) | Entitlements, límites, stats y aislamiento tenant |
| [Reporte Sprint 22.5](SPRINT22.5-REPORT.md) | Documentación, colección, auditoría y cierre |
| [Changelog](changelog.md) | Evolución del contrato Sprint 22 |
| [OpenAPI actual](openapi.v1.yaml) | Especificación machine-readable vigente |

## Situación inicial

- JWT y rutas `/api/v1` tenant-safe ya existen parcialmente.
- Activos, OT y resumen administrativo tienen endpoints de lectura.
- La API todavía mezcla respuestas legacy con el contrato MAG.
- Existen credenciales dedicadas con secreto de única visualización, hash
  `scrypt`, scopes, expiración, rotación, revocación y auditoría.
- Activos, OT, incidencias, medidores y lecturas exponen contrato `/api/v1`
  tenant-safe con request ID, paginación, filtros y rate limit.
- Incidencias y lecturas admiten escritura idempotente.
- Webhooks con outbox, HMAC y reintentos están operativos (Sprint 22.3).
- Entitlements de plan, rate limits dinámicos y stats de entregas (Sprint 22.4).
- Documentación de cierre, colección de pruebas y auditoría (Sprint 22.5).
- Los planes limitan capacidades vía claves técnicas, no por nombre comercial en código.

## Fuentes relacionadas

- [MAG · API Guide](../mag/README.md)
- [MAG-08 · Webhooks](../mag/chapters/08-webhooks.md)
- [MPA-06 · Integraciones](../mpa/chapters/06-integraciones.md)
- [SDK](../sdk/README.md)
