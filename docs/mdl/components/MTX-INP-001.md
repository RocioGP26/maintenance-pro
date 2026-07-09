# MTX-INP-001 · Text Input

| Campo | Valor |
|-------|-------|
| **ID** | MTX-INP-001 |
| **Nombre** | Text Input |
| **Clase** | `mtx-input` |

## Uso

Entrada de texto corto: códigos, nombres, búsqueda, email.

## No usar

- Texto multilínea → `MTX-INP-002` (Textarea)
- Selección de opciones → `MTX-SEL-001`

## Variantes

Dentro de `mtx-form-group` con `mtx-label` y opcional `mtx-form-hint`.

## Estados

| Estado | Clase / pseudo |
|--------|----------------|
| Default | Borde `--mdl-border` |
| Hover | (sin cambio visual fuerte) |
| Focus | Borde primary + ring 3px |
| Error | `is-error` |
| Success | `is-success` |
| Disabled | `disabled` |
| ReadOnly | `readonly` — fondo `--mdl-background` |

## Código

```html
<div class="mtx-form-group">
  <label class="mtx-label" for="codigo">Código activo</label>
  <input id="codigo" name="codigo" class="mtx-input" placeholder="CPS-001"
         aria-describedby="codigo-hint">
  <p id="codigo-hint" class="mtx-form-hint">Formato: SECTOR-NUM</p>
</div>
```

```jinja
<input class="mtx-input{% if form.codigo.errors %} is-error{% endif %}"
       name="codigo" value="{{ form.codigo.data or '' }}"
       aria-invalid="{{ 'true' if form.codigo.errors else 'false' }}">
```

## Accesibilidad

- Siempre `<label for="">` asociado
- Errores: `aria-invalid="true"` + texto de error visible
- No depender solo de color para error
