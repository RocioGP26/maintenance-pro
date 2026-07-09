# MTX-CRD-001 · Card

| Campo | Valor |
|-------|-------|
| **ID** | MTX-CRD-001 |
| **Nombre** | Card |
| **Clase** | `mtx-card` |

## Uso

Contenedor estándar para agrupar contenido relacionado: listas, formularios parciales, detalle de entidad.

## No usar

- KPIs numéricos destacados → `MTX-CRD-002` (Stat Card)
- Contenido sin título ni contexto en dashboards densos

## Variantes

| Parte | Clase |
|-------|-------|
| Header | `mtx-card-head` + `mtx-card-head-title` |
| Body | `mtx-card-body` |
| Interactiva | `mtx-card--interactive` |
| Seleccionada | `is-selected` o `mtx-card--selected` |
| Loading | `is-loading` o `mtx-card--loading` |

## Estados

| Estado | Clase / comportamiento |
|--------|------------------------|
| Default | `box-shadow: var(--mdl-shadow-md)` |
| Hover | `mtx-card--interactive:hover` → shadow-lg |
| Selected | Borde `--mdl-primary` |
| Loading | Opacity 0.65, sin interacción |

## Código

```html
<div class="mtx-card mtx-card--interactive">
  <div class="mtx-card-head">
    <h3 class="mtx-card-head-title">Activos críticos</h3>
  </div>
  <div class="mtx-card-body">
    <!-- contenido -->
  </div>
</div>
```

## Accesibilidad

Si la card es clickeable entera, usar `<a>` o `<button>` con rol adecuado, o `tabindex="0"` + `aria-label` descriptivo.
