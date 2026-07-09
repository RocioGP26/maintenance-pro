# MTX-BTN-002 · Secondary Button

| Campo | Valor |
|-------|-------|
| **ID** | MTX-BTN-002 |
| **Nombre** | Secondary Button |
| **Clase** | `mtx-btn mtx-btn-secondary` |

## Uso

Acción importante pero **no principal**. Acompaña al primary en footers de modal, toolbars y formularios.

Ejemplos: Exportar, Filtrar, Ver detalle.

## No usar

- Como única CTA de una pantalla vacía
- Acciones destructivas
- Más de dos botones filled en la misma fila

## Variantes

Igual que MTX-BTN-001 (`mtx-btn-sm`, `mtx-btn-lg`, `is-loading`, `mtx-btn-block`, etc.).

## Estados

Default · Hover · Active · Focus · Disabled · Loading — mismas reglas que MTX-BTN-001.

## Código

```html
<button type="button" class="mtx-btn mtx-btn-secondary">Exportar</button>
```

```jinja
<a href="{{ url_for('activos.export') }}" class="mtx-btn mtx-btn-secondary">Exportar</a>
```

## Accesibilidad

Si es `<a>`, incluir texto descriptivo. No usar `aria-label` genérico tipo "botón".
