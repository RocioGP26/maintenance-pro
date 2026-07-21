# Nomenclatura · MRL

**Código:** MRL · Roustix Report Language
**Suite docs:** 06 · Sprint 7

## Capítulos · Núcleo (01 – 10)

| Código | Archivo | Título |
|--------|---------|--------|
| **MRL-01-PHIL** | `01-filosofia.md` | Filosofía |
| **MRL-02-DOC** | `02-tipos-documentos.md` | Tipos de documentos |
| **MRL-03-ANAT** | `03-anatomia-documento.md` | Anatomía del documento |
| **MRL-04-HDR** | `04-header-estandar.md` | Header estándar |
| **MRL-05-TBL** | `05-tablas.md` | Tablas |
| **MRL-06-KPI** | `06-kpi-cards.md` | KPI Cards |
| **MRL-07-COL** | `07-colores.md` | Colores |
| **MRL-08-CHT** | `08-graficos.md` | Gráficos |
| **MRL-09-EXP** | `09-exportaciones.md` | Exportaciones |
| **MRL-10-ROAD** | `10-roadmap.md` | Roadmap |

## Complementos (11 – 13)

| Código | Archivo | Título |
|--------|---------|--------|
| **MRL-11-META** | `11-metadata-documento.md` | Metadata del documento |
| **MRL-12-TPL** | `12-versionado-plantillas.md` | Versionado de plantillas |
| **MRL-13-A11Y** | `13-accesibilidad.md` | Accesibilidad |

## Códigos de documento (DOC)

| Código | Tipo |
|--------|------|
| **DOC-001** | Orden de Trabajo |
| **DOC-002** | Activo |
| **DOC-003** | Inventario |
| **DOC-004** | Factura |
| **DOC-005** | Cotización |
| **DOC-006** | Compra |
| **DOC-007** | Dashboard PDF |
| **DOC-008** | Auditoría |
| **DOC-009** | Reporte Ejecutivo |
| **DOC-010** | Exportación |

## Plantillas (TPL)

| Código | Nombre | DOC |
|--------|--------|-----|
| **MRL-TPL-001** | Reporte Ejecutivo | DOC-009 |
| **MRL-TPL-002** | Orden de Trabajo | DOC-001 |
| **MRL-TPL-003** | Inventario valorizado | DOC-003 |

## Bloques MRL (implementación)

| ID | Bloque |
|----|--------|
| MRL-HDR-001 | Header |
| MRL-FTR-001 | Footer |
| MRL-TBL-001 | Tabla |
| MRL-KPI-001 | KPI row |
| MRL-CHT-001 | Gráfico |
| MRL-SIG-001 | Firma |
| MRL-QR-001 | QR |

## Implementación · Sprint 15+

| Documento | Enlace |
|-----------|--------|
| Sprint 15 charter | [SPRINT15-REPORT.md](SPRINT15-REPORT.md) |
| Arquitectura código | [architecture.md](architecture.md) |
| Estándares | [standards.md](standards.md) |
| Roadmap implementación | [roadmap.md](roadmap.md) |
| Plantillas | [templates/README.md](templates/README.md) |

## Relación

| Doc | Rol |
|-----|-----|
| MDL | Tokens y `mtx-pdf-*` en pantalla |
| MUX | Legibilidad, jerarquía, A11Y |
| MPA | Integraciones PDF/Excel (MPA-06) |
