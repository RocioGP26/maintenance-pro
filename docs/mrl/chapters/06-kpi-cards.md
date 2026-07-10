# MRL-06-KPI · KPI Cards

**Código:** MRL-06-KPI · Sprint 7.6 · Bloque **MRL-KPI-001**

---

## Layout

Fila horizontal de **1 a 4** tarjetas iguales bajo el header.

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Disponib.   │ │    MTTR     │ │    MTBF     │ │  OT abiertas│
│   94.2%     │ │   2.4 h     │ │  180 h      │ │     12      │
│  ▲ +1.2%    │ │  ▼ -0.3h    │ │  —          │ │  ▲ +2       │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

---

## KPIs por dominio

| Dominio | KPIs típicos |
|---------|--------------|
| **Maintenance** | Disponibilidad · MTTR · MTBF · OT abiertas · Preventivos vencidos |
| **Inventory** | Stock valorizado · Rotación · SKUs bajo mínimo · Ventas período |
| **Comercial** | Cartera · Cotizaciones abiertas · Ticket promedio |
| **Ejecutivo** | Mezcla según módulos activos |

---

## Estilo tarjeta

| Atributo | Valor |
|----------|-------|
| Borde | 1pt `#E2E8F0` |
| Radius | 4pt (print-safe) |
| Label | 9pt · `#888780` uppercase |
| Valor | 18pt bold · `#042C53` |
| Delta | 8pt · verde/rojo MRL-07 |

---

## Reglas

- Máximo 4 KPIs por fila
- Segunda fila solo si reporte ejecutivo (DOC-009)
- Sin gráficos mini dentro de KPI — solo número y delta
- Mismo componente que `mtx-kpi` en MDL

---

→ [MRL-07-COL · Colores](07-colores.md)
