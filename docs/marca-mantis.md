# Guía de marca — Mantis CMMS

Referencia para mantener consistencia visual en plantillas, CSS y gráficos (Chart.js).

**Fuente de verdad en código:** variables en `static/css/app.css` (`:root`). Usar siempre variables CSS en estilos nuevos; no hardcodear hex salvo en datos de gráficos donde Bootstrap/CSS no aplique.

---

## Paleta de colores

| Nombre       | Hex       | Variable CSS      | Uso recomendado                                      |
|-------------|-----------|-------------------|------------------------------------------------------|
| Primario    | `#042C53` | `--primario`      | Títulos, encabezados, hover de botones primarios     |
| Acento      | `#185FA5` | `--acento`        | Botones, enlaces, barras de gráficos, nav activo     |
| Claro       | `#378ADD` | `--claro`         | Iconos sobre fondos oscuros, acentos secundarios     |
| Fondo       | `#E6F1FB` | `--fondo`         | Fondo de página, bloques suaves, segmentos vacíos    |
| Sidebar     | `#1a2332` | `--sidebar-bg`    | Barra lateral fija                                   |
| Texto       | `#444441` | `--texto`         | Cuerpo de texto, etiquetas principales               |
| Secundario  | `#888780` | `--secundario`    | Metadatos, hints, separadores suaves                 |

### Colores semánticos (estado)

No forman parte del logotipo, pero se usan para legibilidad operativa:

| Estado    | Hex       | Variable CSS       |
|----------|-----------|--------------------|
| Éxito    | `#38a169` | `--success-green`  |
| Advertencia | `#ed8936` | `--warning-orange` |
| Peligro  | `#e53e3e` | `--danger-red`     |

---

## Tipografía

- **Cuerpo:** [Inter](https://fonts.google.com/specimen/Inter), peso **400** (ya cargada en `base.html`, `login.html` y `onboarding/wizard.html`).
- **Wordmark / nombre de app:** Inter (o DM Sans), peso **500–600**.
- **Tagline** (`{{ app_tagline }}` → «CMMS — INDUSTRIAL»): clase `.app-tagline` — mayúsculas, `letter-spacing: 0.14em`, peso 500.

Constantes en `app/branding.py`:

- `APP_NAME` — «Mantis»
- `APP_TAGLINE` — «CMMS — Industrial»
- `APP_LOGO_PATH` — `img/mantis-logo.png`

**Isotipo / logo:** altura mínima recomendada **24px** en UI compacta; en auth/onboarding usar clases `.auth-logo` / `.onboarding-logo`.

---

## Uso en plantillas HTML

```html
<!-- Preferir clases y variables existentes -->
<h1 class="page-title">Título</h1>
<p class="app-tagline">{{ app_tagline }}</p>
<button class="btn btn-primary">Guardar</button>
<span class="text-primary">Destacado</span>
```

```css
/* En CSS propio del módulo */
.mi-bloque {
  background: var(--fondo);
  color: var(--texto);
  border: 1px solid var(--border-soft);
}
```

---

## Gráficos (Chart.js)

Usar la paleta de marca en series principales; reservar verde/naranja/rojo para **estado de equipos u OT**:

| Propósito        | Hex sugerido |
|-----------------|--------------|
| Serie principal | `#185FA5`    |
| Serie secundaria| `#378ADD`    |
| Serie terciaria | `#042C53`    |
| Fondo / vacío   | `#E6F1FB`    |
| Operativo       | `#38a169`    |
| Mantenimiento   | `#ed8936`    |
| Falla           | `#e53e3e`    |
| Neutro / otros  | `#888780`    |

Ejemplo en `templates/dashboard.html` y `templates/reportes.html`.

---

## Pantallas con fondo dividido

Login y onboarding comparten el gradiente definido en `.login-page` / `.onboarding-page`:

`sidebar-bg` → `primario` → `fondo` (aprox. 42% de altura para la zona clara).

Texto hero sobre la zona oscura: **blanco** (`.onboarding-hero-tagline`).

---

## Dashboard (profundidad visual)

Clases reutilizables en `app.css`:

- `.dash-toolbar` / `.dash-pill-group` — filtros tipo píldora
- `.dash-card-head` / `.dash-card-head-icon` — cabecera de widgets con icono
- `.kpi-card`, `.kpi-card--primary|warning|success|neutral` — tarjetas KPI con borde superior e icono
- `.sector-cat` — mini tarjetas con hover en el panel sectorial
- `.health-legend` — leyenda de gráficos de estado

---

## Checklist para pantallas nuevas

1. Extender `base.html` (o incluir `app.css` + fuente Inter).
2. No introducir azules Chakra legacy (`#3182ce`, `#edf2f7`, `#1a202c`).
3. Botones primarios: `btn-primary` (ya mapeado a `--acento`).
4. Fondo de contenido: dejar que `body` use `--fondo`; tarjetas en blanco con `.card-dashboard` si aplica.
5. Documentar aquí cualquier excepción aprobada por diseño.

---

*Última revisión: alineado con `static/css/app.css` — paleta corporativa Mantis.*
