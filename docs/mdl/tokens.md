# MDL · Design Tokens

Fuente de verdad: `static/css/mdl-tokens.css`

## Color

| Token | Valor light | Uso |
|-------|-------------|-----|
| `--mdl-primary` | `#185FA5` | CTA, links, focus |
| `--mdl-primary-hover` | `#042C53` | Hover botones primarios |
| `--mdl-secondary` | `#042C53` | Títulos, navbar |
| `--mdl-accent-light` | `#378ADD` | Acentos, gráficas |
| `--mdl-background` | `#E6F1FB` | Fondo de página |
| `--mdl-surface` | `#FFFFFF` | Cards, inputs, modales |
| `--mdl-sidebar` | `#1A2332` | Sidebar |
| `--mdl-text-primary` | `#444441` | Cuerpo |
| `--mdl-text-secondary` | `#888780` | Metadata, hints |
| `--mdl-border` | `#E5E7EB` | Bordes 1px universal |
| `--mdl-success` | `#38A169` | OK, operativo |
| `--mdl-warning` | `#ED8936` | Advertencia, OT |
| `--mdl-danger` | `#E53E3E` | Error, destructivo |

## Radius

**Regla:** nunca valores sueltos. Siempre la escala oficial.

| Token | Valor | Uso |
|-------|-------|-----|
| `--mdl-radius-sm` | `8px` | Chips, tags pequeños |
| `--mdl-radius-md` | `12px` | Inputs, selects |
| `--mdl-radius-lg` | `16px` | Cards, panels |
| `--mdl-radius-xl` | `20px` | Modales, sheets |
| `--mdl-radius-full` | `999px` | Badges, pills |

### Alias por componente

| Componente | Token | Resuelve a |
|------------|-------|------------|
| Button | `--mdl-radius-button` | `10px` |
| Input | `--mdl-radius-input` | `--mdl-radius-md` |
| Card | `--mdl-radius-card` | `--mdl-radius-lg` |
| Modal | `--mdl-radius-modal` | `--mdl-radius-xl` |
| Badge | `--mdl-radius-badge` | `--mdl-radius-full` |

```css
/* ✅ Correcto */
.mtx-card { border-radius: var(--mdl-radius-card); }

/* ❌ Prohibido */
.card { border-radius: 14px; }
```

## Shadow

| Token | Uso |
|-------|-----|
| `--mdl-shadow-xs` | Elementos planos, inputs elevados |
| `--mdl-shadow-sm` | Botones, dropdowns |
| `--mdl-shadow-md` | Cards default |
| `--mdl-shadow-lg` | Cards hover, popovers |
| `--mdl-shadow-xl` | Modales, drawers |

## Spacing (grid 8px)

| Token | Valor |
|-------|-------|
| `--mdl-space-xs` | 4px |
| `--mdl-space-sm` | 8px |
| `--mdl-space-md` | 16px |
| `--mdl-space-lg` | 24px |
| `--mdl-space-xl` | 32px |
| `--mdl-space-2xl` | 48px |
| `--mdl-space-3xl` | 64px |

## Typography

| Rol | Size / Line-height |
|-----|-------------------|
| H1 | 48 / 56 |
| H2 | 36 / 44 |
| H3 | 28 / 36 |
| H4 | 22 / 28 |
| Body | 16 / 24 |
| Small | 14 / 20 |
| Caption | 12 / 16 |

Fuente: **Inter** (`--mdl-font-family`).

## Breakpoints

Ver [responsive.md](responsive.md).

| Token | Valor |
|-------|-------|
| `--mdl-bp-xs` | 480px |
| `--mdl-bp-sm` | 640px |
| `--mdl-bp-md` | 768px |
| `--mdl-bp-lg` | 1024px |
| `--mdl-bp-xl` | 1280px |
| `--mdl-bp-2xl` | 1536px |

## Motion

Ver [motion.md](motion.md).

## Dark mode

Ver [dark-mode.md](dark-mode.md).

Selector producto: `.theme-dashboard-dark` y `[data-mdl-theme="dark"]`.
