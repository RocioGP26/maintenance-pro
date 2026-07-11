# MRL Strategy · Sprint 7 → Sprint 15

## Objetivo

**Maintix Report Language v1.0** — estándar único para PDF, Excel, CSV y documentos impresos.

## Posición en la suite

| Ya definimos | Ahora definimos |
|--------------|-----------------|
| MDL · cómo se ve la UI | MRL · cómo se ven los **documentos** |
| MUX · cómo se usa | Legibilidad en export |
| MPA · cómo está construido | ReportLab · exportaciones |

## Entregables Sprint 7 (cerrado ✅)

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

## Implementación código · Sprint 15

Sprint 7 documentó el estándar. **Sprint 15 lo implementa.**

| Documento | Rol |
|-----------|-----|
| [SPRINT15-REPORT.md](SPRINT15-REPORT.md) | Charter y fases 15.0–15.5 |
| [architecture.md](architecture.md) | Paquete `app/mrl/` |
| [standards.md](standards.md) | Reglas de código |
| [roadmap.md](roadmap.md) | Cronograma implementación |

### Estructura de código (Sprint 15+)

```
app/mrl/
├── colors.py · typography.py · metadata.py · styles.py · utils.py
├── excel/base.py · excel/exporter.py
└── pdf/base.py · pdf/exporter.py
```

> **Nota:** el patrón original `app/mrl_styles.py` monolítico queda reemplazado por el paquete modular anterior.

## Motor

**ReportLab** (PDF) · **openpyxl** (Excel) — toda la experiencia previa de encabezados, tablas y OT se formaliza en `app/mrl/`.

## Validación

Checklist PR en [standards.md](standards.md) §11 · smoke test en `tests/test_mrl_smoke.py` (Sprint 15.1).
