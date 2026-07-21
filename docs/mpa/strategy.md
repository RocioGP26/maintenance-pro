# MPA Strategy · Sprint 6

## Objetivo

Entregar el **Roustix Platform Architecture (MPA)** — handbook de plataforma que deja de hablar de marketing y empieza a hablar de **producto e ingeniería**.

## Audiencia

- Desarrolladores actuales y futuros
- Arquitectos de software
- Product managers técnicos
- Onboarding de equipo

## Entregables

| # | Capítulo | Entregable |
|---|----------|------------|
| 6.1 | Visión de plataforma | EMP vs CMMS vs ERP |
| 6.2 | Ecosistema | Mapa oficial de módulos |
| 6.3 | Arquitectura modular | Tenant → Módulos → Permisos → Datos → Dashboards |
| 6.4 | Arquitectura SaaS | Multi-tenant, planes, facturación |
| 6.5 | Roadmap módulos | Hoy / próximo / largo plazo |
| 6.6 | Integraciones | Excel, PDF, API, webhooks… |
| 6.7 | Seguridad | Auth, permisos, auditoría, backups |
| 6.8 | Escalabilidad | 10 → 10 000 empresas |
| 6.9 | Filosofía técnica | Código al servicio de la plataforma |
| 6.10 | Roadmap 2030 | Visión 2026–2030 |

## Reorganización suite

MPA ocupa el **05** en la nueva numeración profesional:

01 MBB · 02 MDL · 03 MUX · 04 MCM · **05 MPA** · 06 MRL · 07 MAG · 08 SDK · 09 Developer · 10 Release Notes

## Criterio de calidad

- Alineado al código real (`modules.py`, `tenancy/`, `models.py`)
- Sin tutorial Flask — eso va en Developer Docs (09)
- Enlaza MCM para narrativa, MUX/MDL para implementación UI
