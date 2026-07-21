# MSD Strategy · Sprint 9

## Objetivo

**Roustix SDK & Developer Portal v1.0 (MSD)** — experiencia completa para integradores y partners.

MAG describe **qué** puede hacer la API. MSD entrega **cómo** integrarla en minutos.

## Posición en la suite

| Manual | Pregunta |
|--------|----------|
| MAG (07) | ¿Cuál es el contrato de la API? |
| **MSD (08)** | ¿Cómo integro con herramientas listas para usar? |
| Developer Docs (09) | ¿Cómo contribuyo al repositorio Roustix? |

> **Nota:** MSD unifica el ecosistema externo (portal + SDK + OpenAPI). La carpeta `docs/sdk/` aloja paquetes y referencia técnica de clientes.

## Entregables Sprint 9

| # | Capítulo | Contenido |
|---|----------|-----------|
| 9.1 | Filosofía | De contrato a experiencia · MAG → MSD |
| 9.2 | Portal | developer.roustix.app · navegación · auth | ✅ MSD-02 |
| 9.3 | OpenAPI | openapi.v1.yaml · `/api/v1/openapi.json` |
| 9.4 | SDK | Python · JavaScript · PHP | ✅ MSD-04 |
| 9.5 | CLI | `roustix-cli` | ✅ MSD-05 |
| 9.6 | Sandbox | Tenant demo · API Explorer | ✅ MSD-06 |
| 9.7 | Quick Start | Guías paso a paso · primer request | ✅ MSD-07 |
| 9.8 | Colecciones | Postman · Insomnia | ✅ MSD-08 |
| 9.9 | Publicación | PyPI · npm · Packagist | ✅ MSD-09 |

## Implementación código (post-doc)

1. `docs/api/openapi.v1.yaml` — OpenAPI 3.1 desde MAG-04
2. Alias `/api/v1/*` en Flask
3. Paquete `roustix` (Python) — primer SDK publicado
4. `@roustix/sdk` (npm) · `roustix/sdk` (Composer)
5. Portal estático o integrado en `/developer/` (local: `/msd/`)
6. Colecciones generadas desde OpenAPI

## Dependencias

- **MAG v1.0** ✅ — contrato completo (Sprint 8)
- **MPA-06** — estrategia de integraciones
- **MAG-09** — ejemplos base para Quick Start

## Resultado · MSD v1.0 ✅

La documentación de Roustix pasa de **describir la API** a ofrecer una **experiencia completa** para integradores — comparable en estructura con Stripe Docs, GitHub REST + Octokit o Notion Developers.

**Sprint 9 completado (2026-07-10).** Implementación operativa de paquetes (PyPI · npm · Packagist) y CI/CD de publicación: roadmap post-doc.

**Siguiente hito:** Sprint 10 — gobernanza operativa (**MOP**) o experiencia de usuario (**MUX**), según prioridad de hoja de ruta.
