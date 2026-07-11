# MRL · Roadmap de implementación

**Código:** MRL-ROAD-IMPL · Sprint 15  
**Versión:** v1.1.0  
**Estado:** 🚧 Activo

> Roadmap **de código e implementación** — Sprint 15 en adelante.  
> Visión funcional y catálogo DOC: [MRL-10-ROAD · capítulo 10](chapters/10-roadmap.md) (Sprint 7).

---

## Línea temporal

```
Sprint 7   · MRL v1.0.1 docs (cerrado ✅)
Sprint 15  · MRL Foundation — Report & Document Engine
Sprint 16+ · Módulos reutilizan MRL sin rediseño
```

---

## Sprint 15 · MRL Foundation

**Charter:** [SPRINT15-REPORT.md](SPRINT15-REPORT.md)

| Fase | Entregable | DoD |
|------|------------|-----|
| **15.0** | Docs: architecture, standards, roadmap, templates | README + changelog actualizados |
| **15.1** | `app/mrl/` foundation + smoke test | Test verde, sin motores completos |
| **15.2** | `BaseExcelExporter` | Excel con header MRL desde código |
| **15.3** | `BasePdfExporter` (bloques) | Header, footer, tabla, KPI, watermark |
| **15.4** | **DOC-001** OT PDF | PDF descargable desde producto |
| **15.5** | Migración exports | Inventario + maintenance Excel; badge «Próximamente» retirado |

### Checklist Sprint 15

- [x] Sprint 7 · documentación MRL v1.0.1
- [x] Sprint 15.0 · documentación implementación
- [x] Sprint 15.1 · `colors`, `typography`, `metadata`, `styles`, smoke test
- [x] Sprint 15.2 · Excel Engine · `BaseExcelExporter`
- [ ] Sprint 15.3 · PDF Engine + ReportLab en requirements
- [ ] Sprint 15.4 · DOC-001 OT PDF
- [ ] Sprint 15.5 · Migrar exports inventario + maintenance

---

## v1.1 · Post-Sprint 15 (corto plazo)

| Entrega | DOC | Depende de |
|---------|-----|------------|
| OT PDF completo MRL | DOC-001 | Sprint 15.4 ✅ |
| Ficha activo PDF | DOC-002 | 15.3 motor |
| Compra PDF | DOC-006 | Sprint 16 Purchasing |
| Footer + QR | MRL-QR-001 | 15.3 |
| Excel OT + activos en `/reportes` | DOC-010 | 15.5 |

---

## v1.2 · Medio plazo

| Entrega | DOC | Sprint sugerido |
|---------|-----|-----------------|
| Dashboard PDF | DOC-007 | 20 |
| Reporte ejecutivo | DOC-009 | 20 |
| Auditoría plataforma | DOC-008 | — |
| Firma digital visual | MRL-SIG-001 | — |
| Tendencias temporales web | MRG-08 | 20 |

---

## Sprints desbloqueados (post-Sprint 15)

| Sprint | Módulo | Uso MRL |
|--------|--------|---------|
| **16** | Purchasing | DOC-006 OC, recepción, CxP export |
| **17** | MAG v1 | Exports vía API con metadata MRL |
| **18** | CRM | DOC-005 cotizaciones, actividades |
| **19** | Analytics | DOC-007, KPI MRL-CHT-001 |
| **20** | Reportes avanzados | DOC-009, programados, tendencias |

---

## Largo plazo

| Capacidad | Notas |
|-----------|-------|
| **Power BI** | Datasets alineados semántica MRL |
| **Reportes programados** | Email PDF MRL |
| **BI embebido** | KPIs MRL en producto |
| **IA generando reportes** | Narrativa + gráficos MRL-compliant |

Detalle: [MRL-10-ROAD · cap. 10](chapters/10-roadmap.md).

---

## Criterio de éxito · Sprint 15

Al cerrar Sprint 15, un operador puede:

1. Descargar **OT en PDF** (DOC-001) reconocible como Maintix
2. Exportar **Excel inventario y maintenance** con mismo header/tablas MRL
3. Añadir un export nuevo en un módulo usando solo adaptador + `BaseExcelExporter` / `BasePdfExporter`

Sin ver el isotipo, el documento debe sentirse Maintix — objetivo de [MRL-01-PHIL](chapters/01-filosofia.md).

---

## Deuda técnica a eliminar

| Item | Resolución |
|------|------------|
| `_escribir_encabezado_empresa` duplicado | 15.5 |
| Excel sin `#042C53` en inventario | 15.2 + 15.5 |
| `strategy.md` → `mrl_styles.py` monolítico | Reemplazado por `app/mrl/` |
| ReportLab ausente | 15.3 |
| Badge «Próximamente» en `/reportes` | 15.5 |

---

→ [architecture.md](architecture.md) · [standards.md](standards.md) · [SPRINT15-REPORT.md](SPRINT15-REPORT.md)

---

*MRL-ROAD-IMPL · Sprint 15 · Maintix · 2026-07-10*
