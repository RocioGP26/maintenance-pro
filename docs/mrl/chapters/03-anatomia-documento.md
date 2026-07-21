# MRL-03-ANAT · Anatomía del documento

**Código:** MRL-03-ANAT · Sprint 7.3

**Todos** los documentos Roustix comparten la misma estructura. Sin excepciones por módulo.

---

## Estructura obligatoria

```
┌─────────────────────────────────────────┐
│ HEADER                                  │
│  Logo · Empresa · Título · Código       │
│  Fecha · Módulo · Usuario · Versión MRL │
├─────────────────────────────────────────┤
│ KPI ROW (opcional)                      │
│  Hasta 4 indicadores por fila           │
├─────────────────────────────────────────┤
│ CONTENIDO                               │
│  Tablas · texto · gráficos              │
├─────────────────────────────────────────┤
│ FOOTER                                  │
│  Página N de M · Generado por Roustix   │
│  Versión MRL · QR (opcional)            │
└─────────────────────────────────────────┘
```

---

## Zonas

| Zona | Obligatoria | Contenido |
|------|-------------|-----------|
| **Header** | Sí | Identidad + contexto del documento |
| **KPI row** | No | Resumen numérico antes del detalle |
| **Body** | Sí | Datos del reporte |
| **Footer** | Sí | Paginación + atribución Roustix |

---

## Página · MRL-PAGE

| Atributo | Valor |
|----------|-------|
| Formato | **A4** (210 × 297 mm) |
| Orientación | Portrait por defecto; landscape si &gt; 6 columnas |
| Márgenes | 20 mm superior/inferior · 15 mm laterales |
| Clase MDL | `mtx-pdf-page` |

---

## Flujo vertical

1. Header fijo en primera página (repetir en siguientes si documento largo — MRL-04)
2. KPI opcional inmediatamente bajo header
3. Body con secciones tituladas (`h2` visual MRL)
4. Footer en cada página

---

## Anti-patrones

- ❌ PDF sin footer «Generado por Roustix»
- ❌ Header distinto en OT vs factura
- ❌ KPIs mezclados en cuerpo sin bloque dedicado
- ❌ Márgenes «a ojo» por reporte

---

→ [MRL-04-HDR · Header](04-header-estandar.md)
