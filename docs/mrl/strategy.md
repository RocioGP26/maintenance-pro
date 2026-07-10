# MRL Strategy · Sprint 7

## Objetivo

**Maintix Report Language v1.0** — estándar único para PDF, Excel, CSV y documentos impresos.

## Posición en la suite

| Ya definimos | Ahora definimos |
|--------------|-----------------|
| MDL · cómo se ve la UI | MRL · cómo se ven los **documentos** |
| MUX · cómo se usa | Legibilidad en export |
| MPA · cómo está construido | ReportLab · exportaciones |

## Entregables Sprint 7

| # | Capítulo | Contenido |
|---|----------|-----------|
| 7.1 | Filosofía | PDF = extensión del producto |
| 7.2 | Tipos DOC-001–010 | Catálogo documentos |
| 7.3 | Anatomía | Header · KPI · body · footer |
| 7.4 | Header | MRL-HDR-001 |
| 7.5 | Tablas | MRL-TBL-001 |
| 7.6 | KPI Cards | MRL-KPI-001 |
| 7.7 | Colores | MDL reuse |
| 7.8 | Gráficos | Sin 3D · sin degradados |
| 7.9 | Exportaciones | PDF · Excel · CSV |
| 7.10 | Roadmap | Power BI · BI · IA |

## Implementación código (post-doc)

1. `app/mrl_styles.py` — estilos ReportLab compartidos
2. Migrar reportes existentes a bloques MRL
3. Validación visual en PR (checklist MRL-12 / MPA-12)

## Motor

**ReportLab** — toda la experiencia previa de encabezados, tablas y OT se formaliza aquí.
