# MDL · Dark Mode

Maintix ya opera en **modo oscuro híbrido** en dashboard. Este capítulo define tokens y reglas para escalarlo a toda la plataforma.

## Selectores

| Selector | Alcance actual |
|----------|----------------|
| `.theme-dashboard-dark` | Dashboard (producto) |
| `[data-mdl-theme="dark"]` | Futuro global / por módulo |

Definidos en `static/css/mdl-tokens.css`.

## Tokens dark

| Token | Light | Dark |
|-------|-------|------|
| `--mdl-background` | `#E6F1FB` | `#0F1419` |
| `--mdl-surface` | `#FFFFFF` | `#1A2332` |
| `--mdl-sidebar` | `#1A2332` | `#151B26` |
| `--mdl-text-primary` | `#444441` | `rgba(255,255,255,0.88)` |
| `--mdl-text-secondary` | `#888780` | `rgba(255,255,255,0.5)` |
| `--mdl-border` | `#E5E7EB` | `rgba(255,255,255,0.08)` |

Primary, success, warning, danger **no cambian** de matiz — solo ajustar contraste en badges sobre fondo oscuro.

## Shadows en dark

Las sombras usan negro semitransparente, no azul corporativo:

```css
--mdl-shadow-md: 0 4px 14px rgba(0, 0, 0, 0.2);
--mdl-shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.35);
```

## Componentes con variantes dark exclusivas

| Componente | Notas |
|------------|-------|
| Charts | Grid `--dash-chart-grid`, barras `--dash-chart-bar` |
| Sidebar | Ya nativo oscuro |
| Cards | `--dash-card-bg`, borde 8% white |
| Inputs | Fondo surface, borde sutil |
| Modals | Surface + shadow-xl dark |

## Reglas

1. **Nunca** hardcodear `#fff` en dark — usar `--mdl-text-primary`.
2. Probar contraste WCAG AA en primary sobre surface dark.
3. Iconos outline: opacidad 0.55 → 1.0 en hover.
4. No mezclar cards light dentro de shell dark.

## Activación (futuro)

```html
<html data-mdl-theme="dark">
```

O toggle usuario que persista en localStorage / preferencia cuenta.
