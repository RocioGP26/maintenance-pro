# MRL · Maintix Report Language

Lenguaje de reportes PDF de Maintix. Hermano del MDL, enfocado en **documentos impresos y exportables**.

**Principio:** todos los PDF comparten la misma gramática visual. Ningún reporte inventa su propio estilo.

## Por qué MRL

Maintix genera muchísimos PDF: facturas, OT, inventario, KPIs, disponibilidad. Sin MRL, cada módulo diverge en tipografía, márgenes y tablas.

## Estructura de un reporte MRL

```
┌─────────────────────────────────────┐
│ HEADER (logo, título, meta)         │
├─────────────────────────────────────┤
│ KPI ROW (opcional)                  │
├─────────────────────────────────────┤
│ BODY (tablas, gráficas, texto)      │
├─────────────────────────────────────┤
│ FOOTER (numeración, legal)          │
│ FIRMA · QR (opcional)               │
└─────────────────────────────────────┘
```

## Registro MRL

| ID | Bloque | Clase MDL | Descripción |
|----|--------|-----------|-------------|
| MRL-HDR-001 | Header | `mtx-pdf-header` | Logo + título + fecha |
| MRL-FTR-001 | Footer | `mtx-pdf-footer` | Paginación + copyright |
| MRL-TBL-001 | Tabla | `mtx-data-table` | Misma grilla que UI |
| MRL-KPI-001 | KPIs | `mtx-kpi` | Fila métricas resumen |
| MRL-CHT-001 | Gráfica | `mtx-chart` | Barras simplificadas print |
| MRL-SIG-001 | Firma | — | Línea + nombre + cargo |
| MRL-QR-001 | QR | — | Validación documento |

## Tipografía PDF

- Títulos: `#042C53` (secondary)
- Cuerpo: `#444441`
- Metadata: `#888780` · 10pt
- Fuente: Inter o Helvetica fallback

## Página

- Formato: **A4**
- Márgenes: 20mm superior/inferior, 15mm laterales
- Clase contenedor: `mtx-pdf-page`

## Header (MRL-HDR-001)

```
[LOGO MAINTIX]                    [Factura #1024]
Reporte de disponibilidad       Empresa · Marzo 2026
```

## Footer (MRL-FTR-001)

```
Página 1 de 12          © Maintix · Generado 09/07/2026
```

## Numeración

Formato: `Página {n} de {total}` · pie derecho · 9pt secondary.

## Firma (MRL-SIG-001)

```
_________________________
Nombre Apellido
Cargo · Empresa
```

## QR (MRL-QR-001)

URL de verificación o ID documento. 24×24mm, esquina inferior derecha sobre footer.

## Reglas

1. Mismo header/footer en **todos** los tipos de reporte.
2. Tablas: zebra sutil, header `--mdl-secondary` fondo 5%.
3. No más de 6 columnas por tabla en A4; rotar a landscape si necesario.
4. Gráficas: preferir barras horizontales en print.
5. KPIs: máximo 4 por fila.

## Tipos de reporte (roadmap)

| Reporte | Módulo | Estado |
|---------|--------|--------|
| Orden de trabajo | CMMS | Planificado |
| Factura | Ventas | Planificado |
| Inventario valorizado | Inventario | Planificado |
| Disponibilidad activos | Activos | Planificado |

## Código referencia

```html
<div class="mtx-pdf-page">
  <header class="mtx-pdf-header">
    <strong>MAINTIX</strong>
    <span>OT #1042</span>
  </header>
  <!-- body -->
  <footer class="mtx-pdf-footer">Página 1 de 3</footer>
</div>
```

## Relación con MDL

| MDL (pantalla) | MRL (PDF) |
|----------------|-----------|
| `mtx-report-header` | `MRL-HDR-001` |
| `mtx-data-table` | `MRL-TBL-001` |
| `mtx-kpi` | `MRL-KPI-001` |

Ver también: `docs/mdl/components.md` · MTX-PDF-001
