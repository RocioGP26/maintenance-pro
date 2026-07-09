# MDL · Maintix Design Language

Proyecto documental **independiente** del Brand Book.

**Versión:** 1.0  
**Frase:** Toda la operación. Una sola plataforma.

## Qué es el MDL

El MDL no es un capítulo de marca. Es la **herramienta de desarrollo** de interfaz de Maintix:

- Identificadores únicos (`MTX-BTN-001`)
- Fichas técnicas por componente
- Estados completos (default, hover, focus, disabled, loading…)
- Tokens oficiales (color, radius, shadow, motion, breakpoints)
- Patrones de flujo (no solo piezas sueltas)
- Modo oscuro documentado

## Estructura

```
docs/mdl/
├── README.md           ← Este archivo
├── MDL_v1.md           ← Fuente para exportar PDF
├── tokens.md           ← Design tokens
├── components.md       ← Registro MTX-* (índice)
├── components/         ← Fichas individuales
├── patterns.md         ← Patrones de flujo
├── dark-mode.md        ← Modo oscuro
├── motion.md           ← Maintix Motion
├── responsive.md       ← Breakpoints XS–2XL
├── email.md            ← Plantillas de correo
├── changelog.md        ← Historial de versiones
├── index.html          ← Catálogo interactivo
└── css/mdl-docs.css
```

## Código en producto

| Archivo | Contenido |
|---------|-----------|
| `static/css/mdl-tokens.css` | Variables `--mdl-*` |
| `static/css/mdl.css` | Clases `mtx-*` |

## Ver catálogo

```powershell
python run.py
```

→ http://127.0.0.1:5000/mdl/

## Proyectos relacionados

| Proyecto | Carpeta |
|----------|---------|
| Brand Book | `docs/brandbook/` |
| MRL (PDF) | `docs/mrl/` |
| Ecosistema | `docs/README.md` |

## Convención de identificadores

```
MTX-{CATEGORÍA}-{NÚMERO}
```

| Prefijo | Categoría |
|---------|-----------|
| `BTN` | Botones |
| `CRD` | Cards |
| `INP` | Inputs / formularios |
| `SEL` | Selects |
| `TBL` | Tablas |
| `CHT` | Charts |
| `WDG` | Widgets |
| `EMP` | Empty states |
| `LDR` | Loaders |
| `ALT` | Alerts |
| `BDG` | Badges |
| `MDL` | Modals |
| `SDB` | Sidebar |
| `NAV` | Navbar |
| `LGN` | Login |
| `LND` | Landing |
| `RPT` | Report UI |
| `PDF` | PDF (ver MRL) |
| `EML` | Email |
| `PAT` | Patrones |

## Reglas de oro

1. **Nunca** `border-radius: 14px` — siempre `var(--mdl-radius-lg)`.
2. **Nunca** `padding: 13px` — solo tokens de espaciado.
3. **Toda** animación respeta Maintix Motion.
4. **Todo** componente nuevo recibe un ID `MTX-*` antes de merge.
