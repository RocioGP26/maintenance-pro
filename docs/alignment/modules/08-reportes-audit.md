# Fase 7 · Auditoría MRG-08 · Indicadores y reportes

**Sprint 14.25–14.28** · **Estado:** ✅ **Fase 7 cerrada** (2026-07-10)  
**MRG:** [MRG-08-REPORTS](/mrg/chapters/08-reportes.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Dashboard mantenimiento · dashboard comercial · `/reportes` gráficos · export Excel inventario |
| ¿Qué hace? | KPIs operativos por tenant y módulo |
| ¿Qué falta? | Export OT/activos Excel · PDF MRL · tendencias · BI/API |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | Reportes web solo mantenimiento; comercial en dashboard inv |

**Estado módulo:** 🟡 **Parcial** · **Sprint 14 Fase 7:** ✅ **Cerrado**

→ Detalle mantenimiento (Sprint 14.3): [02-reports-audit.md](02-reports-audit.md)

---

## 2 · MRG §1 · Filosofía

| Principio | Estado |
|-----------|--------|
| Por tenant | ✅ |
| Por módulo | ✅ dashboards separados |
| Operativo primero | ✅ |
| Exportable | 🟡 Excel inv · OT 📋 |

---

## 3 · MRG §2 · Dashboard Mantenimiento

| Indicador | Estado |
|-----------|--------|
| Activos operativos / en falla | ✅ |
| OT abiertas / vencidas | ✅ resumen operativo |
| Preventivos del mes | ✅ |
| Cumplimiento preventivo | ✅ gauge |
| Repuestos bajo mínimo | ✅ |
| MTBF · MTTR · disponibilidad | ✅ |
| Próximos mantenimientos | ✅ |
| Top activos críticos | ✅ |

**Ruta:** `/dashboard` · título `Dashboard · Mantenimiento`

---

## 4 · MRG §3 · Dashboard Inventario comercial

| Indicador | Estado |
|-----------|--------|
| Ventas del día | ✅ |
| Productos bajo stock | ✅ |
| Valor inventario | ✅ |
| CxP vencidas / por vencer | ✅ |
| Top productos mes | ✅ |

**Ruta:** `/comercial/dashboard` · solo-inventario → redirect desde `/dashboard`

---

## 5 · MRG §4 · Reportes web mantenimiento

| Gráfico | Estado |
|---------|--------|
| Activos por estado | ✅ pie |
| OT por tipo | ✅ doughnut |
| OT por estado | ✅ bar |
| Repuestos bajo mínimo | ✅ KPI + tabla |
| Tendencias período | 📋 |

**Ruta:** `/reportes`

---

## 6 · MRG §5 · Exportaciones

| Export | Estado |
|--------|--------|
| Catálogo / plantilla / bajo stock Excel | ✅ inv_comercial |
| OT / activos Excel | 📋 badge próximamente |
| PDF MRL | 📋 |

---

## 7 · MRG §6–§7 · KPIs comerciales y transversales

| KPI | Estado |
|-----|--------|
| Ventas período / día | ✅ dashboard comercial |
| Cartera por cobrar | ✅ ventas filtro |
| Compras / CxP | ✅ dashboard + CxP |
| Ticket promedio · rotación | 📋 |
| Costo por OT · margen venta | 🟡 parcial |

---

## 8 · Menús y copy

| Elemento | Estado |
|----------|--------|
| Nav «Reportes» (solo mant) | ✅ |
| Submenú Indicadores (ambos módulos) | ✅ |
| Enlace cruzado reportes ↔ dashboard comercial | ✅ |
| Copy activos vs máquinas | ✅ |

---

## 9 · Checklist Fase 7 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Dashboard mantenimiento | ✅ |
| 2 | Dashboard comercial | ✅ |
| 3 | Reportes web | ✅ |
| 4 | Export Excel inventario | ✅ |
| 5 | Nav indicadores | ✅ |
| 6 | Export OT/activos | 📋 |
| 7 | MRG badges | ✅ |

---

## 10 · Rutas verificadas

```
/dashboard · /reportes
/comercial/dashboard
/comercial/productos/export*
```

---

## 11 · Gaps abiertos (📋)

- Export Excel OT y activos
- PDF operativos MRL
- Tendencias temporales `/reportes`
- BI / Analytics · API reportes

---

## 12 · Próximos pasos

1. ~~**Cerrar MRG-08 Fase 7**~~ — ✅ 2026-07-10
2. **Fase 8** — MRG-09 Flujos ✅ ([checklist](../checklist.md#fase-8--mrg-09--flujos-transversal))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
