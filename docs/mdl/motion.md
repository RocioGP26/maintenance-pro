# Roustix Motion

Sistema de animación oficial del MDL. **Toda animación debe respetar estos valores.**

Fuente: `static/css/mdl-tokens.css`

## Duraciones

| Token | Duración | Uso |
|-------|----------|-----|
| `--mdl-duration-hover` | **150ms** | Hover botones, links, filas tabla, cards |
| `--mdl-duration-fade` | **200ms** | Fade in/out, dropdowns, toasts, overlays ligeros |
| `--mdl-duration-modal` | **250ms** | Apertura/cierre modal, popovers |
| `--mdl-duration-sidebar` | **300ms** | Sidebar collapse, drawers, paneles laterales |

## Easing

```css
--mdl-ease: cubic-bezier(0.4, 0, 0.2, 1);
```

Un solo easing para consistencia. No usar `ease-in-out` suelto.

## Ejemplos

```css
.mtx-btn {
  transition: background var(--mdl-duration-hover) var(--mdl-ease);
}

.mtx-modal-overlay {
  transition: opacity var(--mdl-duration-fade) var(--mdl-ease);
}

.mtx-modal {
  transition: transform var(--mdl-duration-modal) var(--mdl-ease),
              opacity var(--mdl-duration-modal) var(--mdl-ease);
}

.mtx-sidebar {
  transition: width var(--mdl-duration-sidebar) var(--mdl-ease);
}
```

## Reglas

1. **No animar** `width`/`height` de contenido denso (performance).
2. Preferir `opacity` y `transform`.
3. Respetar `prefers-reduced-motion: reduce` — desactivar animaciones no esenciales.
4. Nunca superar 300ms en UI operativa (salvo onboarding ilustrado).

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Prohibido

- `transition: all 0.3s` sin token
- Bounce/elastic en formularios operativos
- Delays arbitrarios > 100ms en hover
