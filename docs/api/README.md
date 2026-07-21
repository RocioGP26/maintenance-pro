# API pública y Webhooks · Sprint 22

**Estado:** Sprint 22.0 · Diseño y contrato finalizado

**Implementación:** planificada desde Sprint 22.1

**Base canónica:** `/api/v1`

Sprint 22 convierte la API tenant existente y el contrato MAG en una superficie
pública, segura y operable. La documentación describe capacidades acordadas;
solo `openapi.v1.yaml` identifica rutas ya expuestas o listas para consumo.

## Documentos

| Documento | Propósito |
|---|---|
| [Charter](charter.md) | Objetivo, alcance, decisiones y Definition of Done |
| [Arquitectura](architecture.md) | Componentes, aislamiento, outbox y observabilidad |
| [Contrato API v1](api-contract.md) | Recursos, respuestas, filtros y errores |
| [Autenticación, permisos y planes](permissions-plans.md) | JWT, API keys, scopes y derechos técnicos |
| [Contrato de webhooks](webhooks.md) | Eventos, firma, entregas y reintentos |
| [Roadmap](roadmap.md) | Sub-sprints 22.1–22.5 |
| [Reporte Sprint 22.0](SPRINT22-REPORT.md) | Evidencia de cierre documental |
| [Changelog](changelog.md) | Evolución del contrato Sprint 22 |
| [OpenAPI actual](openapi.v1.yaml) | Especificación machine-readable vigente |

## Situación inicial

- JWT y rutas `/api/v1` tenant-safe ya existen parcialmente.
- Activos, OT y resumen administrativo tienen endpoints de lectura.
- La API todavía mezcla respuestas legacy con el contrato MAG.
- No existen credenciales dedicadas a integraciones ni entrega de webhooks.
- Los planes actuales limitan principalmente activos; Sprint 22 añade derechos
  técnicos sin acoplar el código a etiquetas comerciales.

## Fuentes relacionadas

- [MAG · API Guide](../mag/README.md)
- [MAG-08 · Webhooks](../mag/chapters/08-webhooks.md)
- [MPA-06 · Integraciones](../mpa/chapters/06-integraciones.md)
- [SDK](../sdk/README.md)
