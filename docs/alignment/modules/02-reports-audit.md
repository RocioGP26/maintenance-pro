# Fase 1.3 · Dashboard y reportes · MRG-08

**Sprint 14.3** · **Estado:** 🟡 Alineado parcial · **Consolidado en Fase 7:** [08-reportes-audit.md](08-reportes-audit.md)  
**MRG:** [MRG-08-REPORTS](/mrg/chapters/08-reportes.md) · [MRG-02 §10](/mrg/chapters/02-maintenance.md)

---

## Dashboard Mantenimiento (MRG-08 §2)

| Indicador MRG | Implementación | Estado |
|---------------|----------------|--------|
| Activos operativos / en falla | Gráfico salud + resumen operativo | ✅ |
| OT abiertas | Fila resumen → listado OT | ✅ *(añadido Sprint 14.3)* |
| OT vencidas | Fila resumen → listado OT | ✅ *(añadido Sprint 14.3)* |
| Preventivos del mes | Fila resumen + cumplimiento preventivo | ✅ |
| Cumplimiento preventivo | Gauge dashboard | ✅ |
| Repuestos bajo mínimo | Fila resumen → `/reportes` | ✅ *(añadido Sprint 14.3)* |
| KPIs planta (MTBF · MTTR · disp.) | 7 tarjetas planta | ✅ |
| Próximos mantenimientos | Panel calendario | ✅ |
| Top activos críticos | Panel inferior | ✅ |

**Título:** `Dashboard · Mantenimiento`

---

## Reportes web `/reportes` (MRG-08 §4)

| Gráfico MRG | Implementación | Estado |
|-------------|----------------|--------|
| Activos por estado | Pie chart · labels `machine_status_meta` | ✅ |
| OT por tipo | Doughnut | ✅ |
| OT por estado | Bar chart | ✅ |
| Repuestos bajo mínimo | KPI + tabla detalle | 🟡 *(tabla top 10)* |
| Tendencias por período | — | 📋 Roadmap |

**Menú:** `Reportes` (antes «Reportes / Analítica»)

---

## Exportaciones (MRG-08 §5)

| Export | Estado producto |
|--------|-----------------|
| Inventario comercial Excel | ✅ (inv_comercial) |
| OT / activos Excel | 📋 Badge «Próximamente» en `/reportes` |
| PDF MRL | 📋 Roadmap |

---

## Alineación aplicada (2026-07-10)

- Fila **Resumen operativo** en dashboard (5 KPIs MRG-02 §10)
- `/reportes`: copy activos · tabla repuestos bajo mínimo · enlace dashboard
- Labels estado activo en gráficos via `machine_status_meta`
- Copy «máquina» → «activo» en hints MTTR

---

## Gaps pendientes

| ID | Gap | Prioridad |
|----|-----|-----------|
| R1 | Export Excel OT/activos | P2 |
| R2 | Tendencias temporales en `/reportes` | 📋 |
| R3 | PDF operativos (MRL) | 📋 |
| R4 | Filtro período en reportes web | P2 |

---

→ [Auditoría Fase 1](02-maintenance-audit.md) · [Checklist](../checklist.md)
