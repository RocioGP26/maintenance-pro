# MRG-08-REPORTS · Indicadores y reportes

**Código:** MRG-08-REPORTS · Sprint 10.8 · **Entregado** · **v1.0.1** · Sprint 14 ALIGN ✅

> Roustix ofrece **dashboards operativos**, reportes web por módulo y **exportaciones** (Excel, estándar PDF vía MRL) para decisiones basadas en datos del tenant.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar indicadores, dashboards y exportaciones disponibles — y su relación con [MRL](/mrl/) y los procesos de [MRG-09 · Workflows](09-workflows.md).

**Estado:** 🟡 **KPIs web + Excel en producción** · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10)

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado |
| 🟡 Parcial | Gaps export/tendencias documentados |
| 📋 Roadmap | BI · PDF · API |

→ Auditoría Sprint 14: [ALIGN · Fase 7](../../alignment/modules/08-reportes-audit.md) · Mant.: [02-reports-audit.md](../../alignment/modules/02-reports-audit.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Filosofía | ✅ |
| §2 | Dashboard Mantenimiento | ✅ |
| §3 | Dashboard Inventario | ✅ |
| §4 | Reportes web | 🟡 |
| §5 | Exportaciones | 🟡 |
| §6 | KPIs comerciales | 🟡 |
| §7 | KPIs transversales | 📋 |
| §8–§9 | Integración · evolución | ✅ doc |

**Gaps abiertos (📋):** export OT/activos · PDF MRL · tendencias · BI.

---

## 1 · Filosofía de reportes · ✅

| Principio | Descripción |
|-----------|-------------|
| **Por tenant** | Todo KPI filtrado a la empresa activa |
| **Por módulo** | Mantenimiento e Inventario tienen dashboards distintos |
| **Operativo primero** | Decisiones del día a día, no BI enterprise (futuro) |
| **Exportable** | Excel hoy · PDF según MRL |

Los indicadores derivan de los **flujos operativos** — OT, compras, ventas — documentados en MRG-02 a MRG-05.

---

## 2 · Dashboard Mantenimiento · ✅

Cuando el tenant tiene módulo `mantenimiento`:

```
Dashboard Mantenimiento
│
├── Activos operativos / en falla
├── OT abiertas y vencidas
├── Preventivos del mes
├── Cumplimiento preventivo
├── Repuestos bajo mínimo
└── KPIs planta (disp. · MTBF · MTTR)
```

| Indicador | Uso |
|-----------|-----|
| Activos por estado | Salud de la flota |
| OT abiertas / vencidas | Carga de trabajo |
| OT por tipo | Correctiva vs preventiva |
| Repuestos bajo mínimo | Reposición |
| Cumplimiento preventivo | Disciplina de mantenimiento |
| MTBF / MTTR | Confiabilidad y reparación |

**Ruta funcional:** Dashboard principal → según módulos activos.

→ [MRG-02 · Mantenimiento](02-maintenance.md)

---

## 3 · Dashboard Inventario · ✅

Cuando el tenant tiene módulo `inventario`:

```
Dashboard Comercial
│
├── Ventas del día
├── Productos bajo stock
├── Valor inventario
├── CxP pendientes / vencidas
└── Alertas de reposición
```

| Indicador | Uso |
|-----------|-----|
| Ventas del día | Desempeño comercial |
| Productos bajo stock | Compras urgentes |
| Valor inventario | Capital inmovilizado |
| CxP pendientes / vencidas | Flujo de pagos |

→ [MRG-03 · Inventario](03-inventario.md) · [MRG-05 · Ventas](05-ventas.md)

---

## 4 · Reportes web (Mantenimiento) · 🟡

Página `/reportes` con gráficos:

- Distribución de activos por estado
- OT por estado y tipo
- Repuestos bajo mínimo
- Tendencias operativas del período

---

## 5 · Exportaciones · 🟡

| Tipo | Módulo | Formato | Estado |
|------|--------|---------|--------|
| Catálogo productos | Inventario | Excel | ✅ |
| Plantilla importación | Inventario | Excel | ✅ |
| Productos bajo stock | Inventario | Excel | ✅ |
| OT / activos | Mantenimiento | Excel / PDF | 📋 |
| PDF operativos | Ambos | MRL | 📋 |

→ [MRL-09 · Exportaciones](/mrl/chapters/09-exportaciones.md)

---

## 6 · Indicadores comerciales · 🟡

| KPI | Descripción |
|-----|-------------|
| Ventas del período | Valor total vendido |
| Ticket promedio | Venta promedio |
| Cartera pendiente | Crédito abierto |
| Compras del período | Abastecimiento |
| Productos más vendidos | Ranking |

→ [MRG-05 · Ventas](05-ventas.md) · [MRG-04 · Compras](04-compras.md)

---

## 7 · KPIs transversales · 📋

| KPI | Origen |
|-----|--------|
| **MTBF** | Mantenimiento — tiempo entre fallas |
| **Costo por OT** | Mantenimiento — mano de obra + repuestos |
| **Margen por venta** | Ventas − costo producto |
| **Rotación inventario** | Ventas / stock — roadmap Analytics |

→ [MRG-09 · Workflows](09-workflows.md)

---

## 8 · Integración

```
Operación (MRG-02 – 05)
        │
        ▼
Indicadores / Dashboard
        │
        ├────────► Reportes web
        ├────────► Export Excel
        ├────────► MRL (PDF)
        └────────► API / BI (roadmap · MAG)
```

---

## 9 · Evolución

| Fase | Capacidad |
|------|-----------|
| Hoy | Dashboards web · Excel Inventario |
| Corto plazo | PDF MRL en producto |
| Medio plazo | BI / Analytics (MPA-05) |
| Largo plazo | Dashboards embebidos vía API (MAG) |

---

## Relación con otros capítulos

| Capítulo | Relación |
|----------|----------|
| [MRG-09 · Workflows](09-workflows.md) | Procesos que alimentan KPIs |
| [MRL](/mrl/) | Estándar visual de documentos |
| [MAG](/mag/) | Exportación vía API |

---

## Exit Criteria

- [x] Dashboards Mantenimiento e Inventario documentados
- [x] Exportaciones y KPIs definidos
- [x] Relación MRL y MRG-09 establecida
- [x] Alineación nav Indicadores vs producto (Sprint 14 · Fase 7)
- [ ] PDF operativos en producto
- [ ] BI / Analytics módulo dedicado

---

## Filosofía del capítulo

Los reportes no son un anexo: son la **consecuencia medible** de operar bien en Roustix. Cada OT cerrada, cada venta y cada compra alimentan indicadores que permiten decidir con datos.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Reportes** | 🟡 KPIs web + Excel inv |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **MRG capítulo** | v1.0.1 |
| **Próximo paso** | MRG-09 · Flujos ([ALIGN](../../alignment/modules/09-workflows-audit.md)) |

---

→ [MRG-09 · Workflows](09-workflows.md) · [MRG-10 · Buenas prácticas](10-buenas-practicas.md) · [Índice MRG](/mrg/)
