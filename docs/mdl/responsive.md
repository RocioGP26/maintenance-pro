# MDL · Responsive

Breakpoints oficiales Roustix. Usar **solo estos** en `@media` y clases utilitarias.

## Escala

| Nombre | Token | Min-width | Dispositivo típico |
|--------|-------|-----------|-------------------|
| **XS** | `--mdl-bp-xs` | 0 – 479px | Móvil pequeño |
| **SM** | `--mdl-bp-sm` | 480 – 639px | Móvil grande |
| **MD** | `--mdl-bp-md` | 640 – 767px | Tablet portrait |
| **LG** | `--mdl-bp-lg` | 768 – 1023px | Tablet landscape / laptop pequeño |
| **XL** | `--mdl-bp-xl` | 1024 – 1279px | Desktop |
| **2XL** | `--mdl-bp-2xl` | 1280px+ | Desktop ancho |

## Media queries

```css
/* Mobile first */
@media (min-width: 480px) { /* SM+ */ }
@media (min-width: 640px) { /* MD+ */ }
@media (min-width: 768px) { /* LG+ */ }
@media (min-width: 1024px) { /* XL+ */ }
@media (min-width: 1280px) { /* 2XL+ */ }

/* Max-width (utilidades hide) */
@media (max-width: 767px) { /* < LG */ }
```

## Clases utilitarias

| Clase | Comportamiento |
|-------|----------------|
| `mtx-hide-sm` | Oculto en viewport < 768px |
| `mtx-hide-md-up` | Oculto en ≥ 769px |
| `mtx-stack-sm` | Flex column en < 768px |

## Reglas por componente

| Componente | < LG (768px) | ≥ LG |
|------------|--------------|------|
| Sidebar | Full width, colapsable | Fixed 240px |
| Data table | Scroll horizontal | Ancho completo |
| Modal | 100% - 32px margin | Max 480px |
| Landing hero | H2 size | H1 size |
| KPI grid | 1 columna | 2–4 columnas |

## Dashboard

Roustix es **desktop-first** en operación densa. En móvil: priorizar lectura y alertas, no edición masiva.

## Prohibido

- Breakpoints arbitrarios (`@media (max-width: 812px)`)
- `viewport` sin `width=device-width`
