# MTX-BTN-001 · Primary Button

| Campo | Valor |
|-------|-------|
| **ID** | MTX-BTN-001 |
| **Nombre** | Primary Button |
| **Clase** | `mtx-btn mtx-btn-primary` |
| **Versión MDL** | 1.0 |

## Uso

Acción **principal** de una pantalla, formulario o modal. Una sola por vista visible (regla 1-primary).

Ejemplos: Guardar, Crear OT, Confirmar, Entrar.

## No usar

- Acciones destructivas → `MTX-BTN-005` (Danger)
- Acciones secundarias → `MTX-BTN-002` (Secondary)
- Más de un primary en la misma barra de acciones
- Enlaces de navegación (usar link o ghost)

## Variantes

| Variante | Clase adicional |
|----------|-----------------|
| Small | `mtx-btn-sm` |
| Medium | (default) |
| Large | `mtx-btn-lg` |
| Disabled | `disabled` o `is-disabled` |
| Loading | `is-loading` |
| Icon Left | `mtx-btn` + `<i>` antes del texto |
| Icon Right | `mtx-btn` + `<i>` después del texto |
| Full Width | `mtx-btn-block` |

## Estados

| Estado | Comportamiento |
|--------|----------------|
| Default | Fondo `--mdl-primary`, texto blanco |
| Hover | Fondo `--mdl-primary-hover` · 150ms |
| Active | `translateY(1px)` |
| Focus | `outline` 2px `--mdl-primary` |
| Disabled | Opacity 0.55, `cursor: not-allowed` |
| Loading | Spinner centrado, texto oculto |

## Código

### HTML

```html
<button type="button" class="mtx-btn mtx-btn-primary">
  Guardar cambios
</button>
```

### CSS (referencia)

```css
.mtx-btn-primary {
  background: var(--mdl-primary);
  color: #fff;
  border-radius: var(--mdl-radius-button);
  transition: background var(--mdl-duration-hover) var(--mdl-ease);
}
```

### Jinja

```jinja
<button type="submit" class="mtx-btn mtx-btn-primary{% if saving %} is-loading{% endif %}"
        {% if saving %}disabled aria-busy="true"{% endif %}>
  {{ 'Guardando…' if saving else 'Guardar' }}
</button>
```

## Accesibilidad

| Atributo | Cuándo |
|----------|--------|
| `type="button"` | Si no es submit de form |
| `type="submit"` | En formularios |
| `aria-label` | Si solo icono, sin texto visible |
| `aria-busy="true"` | Estado loading |
| `disabled` | Disabled y loading |
| Focus visible | Nativo vía `:focus-visible` — no quitar outline |

## Tokens relacionados

`--mdl-primary`, `--mdl-radius-button`, `--mdl-duration-hover`, `--mdl-shadow-sm`
