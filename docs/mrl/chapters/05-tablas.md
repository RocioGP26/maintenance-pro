# MRL-05-TBL · Tablas

**Código:** MRL-05-TBL · Sprint 7.5 · Bloque **MRL-TBL-001**

Una sola gramática para OT, inventario, compras, ventas.

---

## Apariencia

| Elemento | Estilo |
|----------|--------|
| **Cabecera** | Fondo `#042C53` · texto blanco · 10pt bold |
| **Filas** | Fondo blanco |
| **Alternancia** | `#F4F7FB` cada segunda fila (zebra suave) |
| **Bordes** | 0.5pt `#E2E8F0` horizontal; sin grid vertical pesado |
| **Totales** | Fila final fondo `#EBF4FF` · texto bold `#042C53` |
| **Alineación numérica** | Derecha · monospace opcional para cantidades |

---

## Reglas

| # | Regla |
|---|-------|
| 1 | Máximo **6 columnas** en A4 portrait |
| 2 | Más columnas → landscape o dividir tabla |
| 3 | Header repetido al cortar página larga |
| 4 | Montos con moneda tenant (`COP`, `USD`…) |
| 5 | Vacío = «—» no celda en blanco |
| 6 | Misma clase MDL: `mtx-data-table` / equivalente ReportLab |

---

## Ejemplo visual (OT)

| Código | Repuesto | Cant. | Unit. | Subtotal |
|--------|----------|-------|-------|----------|
| RP-001 | Rodamiento | 2 | $45.000 | $90.000 |
| **Total** | | | | **$90.000** |

---

## Relación MDL

Pantalla y PDF comparten semántica de tabla — ver [MDL MTX-TBL](/mdl/).

---

→ [MRL-06-KPI · KPI Cards](06-kpi-cards.md)
