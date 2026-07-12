# MRL · Maintix Report Language

**Código:** MRL · Suite docs **06**  
**Versión docs:** v1.1.0 · Sprint 15  
**Versión especificación:** v1.0.1 · Sprint 7  
**Frase:** Toda la operación. Una sola plataforma.

> El lenguaje oficial para **reportes, PDF y documentos** generados por Maintix.

## Ver manual

```powershell
python run.py
```

→ http://127.0.0.1:5000/mrl/

---

## Sprint 15 · MRL Foundation — Report & Document Engine

Tras Sprint 14 ALIGN, MRL pasa de **especificación documental** a **infraestructura de código**.

| Documento | Descripción |
|-----------|-------------|
| [SPRINT15-REPORT.md](SPRINT15-REPORT.md) | Charter Sprint 15 · sub-sprints · DoD |
| [architecture.md](architecture.md) | Diseño `app/mrl/` · motores Excel/PDF |
| [standards.md](standards.md) | Reglas obligatorias de implementación |
| [roadmap.md](roadmap.md) | Roadmap de código Sprint 15+ |
| [templates/README.md](templates/README.md) | Registro MRL-TPL y plantillas |

**Estado Sprint 15.1:** ✅ Núcleo `app/mrl/` · smoke test verde  
**Estado Sprint 15.2:** ✅ Excel Engine · export Activos migrado · siguiente: 15.3 PDF Engine

---

## Objetivo

Un estándar único para que **cualquier PDF o Excel** se reconozca como Maintix — sin depender del logo.

Sprint 7 definió **qué** es un documento Maintix.  
Sprint 15 define **cómo** el código lo genera.

---

## Capítulos · Especificación (Sprint 7)

| # | Código | Título |
|---|--------|--------|
| 01 | MRL-01-PHIL | [Filosofía](chapters/01-filosofia.md) |
| 02 | MRL-02-DOC | [Tipos de documentos](chapters/02-tipos-documentos.md) |
| 03 | MRL-03-ANAT | [Anatomía del documento](chapters/03-anatomia-documento.md) |
| 04 | MRL-04-HDR | [Header estándar](chapters/04-header-estandar.md) |
| 05 | MRL-05-TBL | [Tablas](chapters/05-tablas.md) |
| 06 | MRL-06-KPI | [KPI Cards](chapters/06-kpi-cards.md) |
| 07 | MRL-07-COL | [Colores](chapters/07-colores.md) |
| 08 | MRL-08-CHT | [Gráficos](chapters/08-graficos.md) |
| 09 | MRL-09-EXP | [Exportaciones](chapters/09-exportaciones.md) |
| 10 | MRL-10-ROAD | [Roadmap funcional](chapters/10-roadmap.md) |

### Complementos

| # | Código | Título |
|---|--------|--------|
| 11 | MRL-11-META | [Metadata del documento](chapters/11-metadata-documento.md) |
| 12 | MRL-12-TPL | [Versionado de plantillas](chapters/12-versionado-plantillas.md) |
| 13 | MRL-13-A11Y | [Accesibilidad](chapters/13-accesibilidad.md) |

---

## Implementación · Código (Sprint 15+)

```
app/mrl/
├── colors.py · typography.py · metadata.py · styles.py · utils.py
├── excel/   → BaseExcelExporter
└── pdf/     → BasePdfExporter
```

→ [architecture.md](architecture.md) · [standards.md](standards.md)

---

## Relacionado

| Doc | Rol |
|-----|-----|
| [MDL](/mdl/) | Tokens · `mtx-pdf-*` |
| [MUX](/mux/) | Legibilidad export |
| [MPA](/mpa/) | Integraciones · capas |
| [MRG-08](/mrg/chapters/08-reportes.md) | Indicadores y reportes |
| [Sprint 14 ALIGN](/alignment/SPRINT14-REPORT.md) | Predecesor |

## Maintix Documentation Suite

| Meta | Enlace |
|------|--------|
| Índice | [/docs/](http://127.0.0.1:5000/docs/) |
| Fundación 1.0 | [RELEASE-FOUNDATION-1.0.md](../RELEASE-FOUNDATION-1.0.md) |
| Versiones | [VERSIONS.md](../VERSIONS.md) |
| Changelog MRL | [changelog.md](changelog.md) |
