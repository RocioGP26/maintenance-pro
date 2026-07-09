# MTX-MDL-001 · Modal

| Campo | Valor |
|-------|-------|
| **ID** | MTX-MDL-001 |
| **Nombre** | Modal |
| **Clase** | `mtx-modal` (+ overlay en producto) |

## Uso

Confirmaciones, formularios cortos, detalle sin cambiar de ruta.

## No usar

- Flujos largos multi-paso → página dedicada
- Información solo lectura extensa → drawer o página
- Más de un modal apilado

## Variantes

| Parte | Clase |
|-------|-------|
| Header | `mtx-modal-header` + `mtx-modal-title` |
| Body | `mtx-modal-body` |
| Footer | `mtx-modal-footer` |

## Estados

| Estado | Motion |
|--------|--------|
| Enter | Fade overlay 200ms + modal 250ms |
| Exit | Inverso |
| Focus trap | Primer focusable al abrir |

## Código

```html
<div class="mtx-modal-overlay" role="presentation">
  <div class="mtx-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="mtx-modal-header">
      <h2 id="modal-title" class="mtx-modal-title">Confirmar acción</h2>
    </div>
    <div class="mtx-modal-body">¿Cerrar esta orden de trabajo?</div>
    <div class="mtx-modal-footer">
      <button type="button" class="mtx-btn mtx-btn-ghost">Cancelar</button>
      <button type="button" class="mtx-btn mtx-btn-primary">Confirmar</button>
    </div>
  </div>
</div>
```

## Accesibilidad

- `role="dialog"`, `aria-modal="true"`
- `aria-labelledby` o `aria-label`
- Cerrar con Escape
- Devolver focus al elemento que abrió el modal

## Tokens

`--mdl-radius-modal`, `--mdl-shadow-xl`, `--mdl-duration-modal`, `--mdl-duration-fade`
