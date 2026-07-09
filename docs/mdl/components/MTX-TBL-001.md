# MTX-TBL-001 · Data Table

| Campo | Valor |
|-------|-------|
| **ID** | MTX-TBL-001 |
| **Nombre** | Data Table |
| **Clase** | `mtx-data-table` (wrapper: `mtx-table-wrap`) |

## Uso

Listados operativos: activos, OT, inventario, clientes. Datos tabulares con acciones por fila.

## No usar

- Layout de página (usar grid)
- Menos de 3 columnas sin encabezado claro
- Datos sin estado semántico cuando aplica (usar badges)

## Variantes

- Scroll horizontal: envolver en `mtx-table-wrap`
- Badges en celdas: `mtx-badge mtx-badge-success` etc.

## Estados

| Elemento | Estados |
|----------|---------|
| Fila | Default, Hover (fondo suave) |
| Header | Sticky opcional (producto) |
| Celda vacía | Guiar a empty state, no dejar hueco |

## Código

```html
<div class="mtx-table-wrap">
  <table class="mtx-data-table">
    <thead>
      <tr><th scope="col">Activo</th><th scope="col">Estado</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>CPS-001</td>
        <td><span class="mtx-badge mtx-badge-success">Operativo</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

## Accesibilidad

- `<th scope="col">` en headers
- Tabla no solo decorativa: caption o `aria-label` en `<table>`
- Ordenación: indicar con texto, no solo icono
