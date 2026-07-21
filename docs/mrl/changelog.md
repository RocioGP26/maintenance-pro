# MRL Changelog

## [1.2.0] — 2026-07-11 · Sprint 15.5 · Integración

### Changed
- Exportaciones de OT, activos y productos consolidadas en `BaseExcelExporter`.
- Nuevas exportaciones MRL para compras y ventas, respetando filtros tenant.
- `/reportes` publica las descargas operativas y retira «Próximamente».
- La plantilla de importación de productos permanece fuera de MRL por diseño.

### Status
- ✅ Sprint 15 finalizado · MRL Foundation operativo de extremo a extremo.

---

## [1.1.4] — 2026-07-11 · Sprint 15.4 · DOC-001

### Added
- **DOC-001 Orden de Trabajo** como primer documento PDF oficial de Roustix.
- Adaptador Maintenance con datos generales, KPI, ejecución, jornadas, repuestos y autorizaciones.
- Ruta tenant-safe `GET /ordenes/<id>/pdf` y descarga desde la vista de la OT.
- `tests/test_mrl_doc001.py` — generación independiente de Flask y desacoplamiento MRL.

### Status
- ✅ Sprint 15.4 cerrado · 15.5 Integración pendiente.

---

## [1.1.3] — 2026-07-11 · Sprint 15.3 · PDF Engine

### Added
- **`app/mrl/pdf/`** — motor PDF MRL sobre ReportLab.
- `BasePdfExporter` / `PdfExporter` con header, footer, tablas y KPI cards.
- Numeración automática, propiedades corporativas y watermark opcional.
- `tests/test_mrl_pdf.py` — generación PDF válida y desacoplamiento del negocio.

### Status
- ✅ Sprint 15.3 cerrado · 15.4 DOC-001 pendiente.

---

## [1.1.2] — 2026-07-10 · Sprint 15.2 · Excel Engine

### Added
- **`app/mrl/excel/`** — motor Excel MRL
- `BaseExcelExporter` / `ExcelExporter` — metadata, header institucional, tablas, filtros, freeze, autofit
- `formatting.py` · `worksheet.py` · `autofit.py` · `validations.py` (placeholder)
- `app/maintenance/mrl_exports.py` — adaptador exportación **Activos**
- Ruta `GET /activos/export` · botón en listado de activos
- `tests/test_mrl_excel.py` — generación xlsx válida · multi-hoja · desacoplamiento

### Changed
- `app/mrl/__init__.py` — exporta `ExcelExporter`
- `standards.md` — regla: módulos no importan `openpyxl`

### Status
- ✅ Sprint 15.2 cerrado · 15.3 PDF Engine pendiente

---

## [1.1.1] — 2026-07-10 · Sprint 15.1 · MRL Foundation (código)

### Added
- **`app/mrl/`** — paquete foundation Sprint 15.1
- `colors.py` — tokens PRIMARY, SECONDARY, SUCCESS, WARNING, DANGER, GRAY, BORDER, HEADER
- `typography.py` — Calibri (Excel), Helvetica (PDF), tamaños título/subtítulo/header/body/pie
- `metadata.py` — `MRLDocumentMeta` · MRL-11 · validación DOC-001…010
- `constants.py` — filas Excel, logo, márgenes PDF, bloques MRL-HDR/TBL/KPI/FTR
- `styles.py` — fachada `MRLStyle.header/table/kpi/footer/bundle`
- `utils/dates.py` — formateo fecha LatAm
- `excel/` · `pdf/` — placeholders Sprint 15.2 / 15.3
- `tests/test_mrl_smoke.py` — 10 tests unittest (sin generación de archivos)

### Status
- ✅ Sprint 15.1 cerrado · 15.2 BaseExcelExporter pendiente

---

## [1.1.0] — 2026-07-10 · Sprint 15.0 · MRL Foundation (documentación)

### Added
- **Sprint 15 · MRL Foundation — Report & Document Engine**
- [SPRINT15-REPORT.md](SPRINT15-REPORT.md) — charter, sub-sprints 15.0–15.5, Definition of Done
- [architecture.md](architecture.md) — diseño `app/mrl/`, motores Excel/PDF, smoke test
- [standards.md](standards.md) — reglas obligatorias DOC, colores, metadata, checklist PR
- [roadmap.md](roadmap.md) — roadmap de implementación Sprint 15+ y sprints desbloqueados
- [templates/README.md](templates/README.md) — registro MRL-TPL-002 (DOC-001) y guía de plantillas
- README actualizado — sección Sprint 15 e índice implementación

### Changed
- Estrategia implementación: `mrl_styles.py` monolítico → paquete `app/mrl/` modular
- Roadmap funcional cap. 10 referenciado desde `roadmap.md` de implementación

### Status
- 🚧 Sprint 15.0 documentación · 15.1+ código pendiente

---

## [1.0.1] — 2026-07-10 · Complementos Sprint 7

### Added
- **MRL-11-META** · Metadata del documento (DOC, versión, tenant, usuario, fecha, zona, idioma, hash)
- **MRL-12-TPL** · Versionado de plantillas (`MRL-TPL-001` …)
- **MRL-13-A11Y** · Accesibilidad (impresión, escala de grises, tipografía mínima)
- Registro **MRL-TPL-001** – **MRL-TPL-003** en NOMENCLATURE
- Catálogo `/mrl/` · secciones 11–13 y nav Complementos
- Enlaces cruzados MRL-04 (header) y MRL-09 (exportaciones)

---

## [1.0.0] — 2026-07-10 · Sprint 7 completo

### Added
- **MRL v1.0** — Roustix Report Language (10 capítulos)
- Catálogo HTML `/mrl/`
- Códigos MRL-01-PHIL … MRL-10-ROAD
- Registro **DOC-001** – **DOC-010**
- Bloques **MRL-HDR-001**, **MRL-TBL-001**, **MRL-KPI-001**, **MRL-CHT-001**
- Estándares PDF (ReportLab) · Excel · CSV
- Filosofía: PDF = extensión de Roustix, no archivo suelto

### Capítulos
- MRL-01 · Filosofía
- MRL-02 · Tipos de documentos
- MRL-03 · Anatomía
- MRL-04 · Header estándar
- MRL-05 · Tablas
- MRL-06 · KPI Cards
- MRL-07 · Colores (MDL)
- MRL-08 · Gráficos
- MRL-09 · Exportaciones
- MRL-10 · Roadmap

### Implementación pendiente
- Módulo `mrl_styles` ReportLab
- Migración reportes producto a bloques MRL
