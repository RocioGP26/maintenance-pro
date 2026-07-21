# MDL v1.0 — Roustix Design Language

> Exportar a PDF: imprimir desde `/mdl/` o `pandoc MDL_v1.md -o MDL_v1.pdf`

**Roustix** · Enterprise Management Platform
**Frase:** Toda la operación. Una sola plataforma.

---

## 1. Introducción

El MDL es un **proyecto documental independiente** del Brand Book. Define componentes `mtx-*`, identificadores `MTX-*`, tokens, estados, patrones y Roustix Motion.

- Código: `static/css/mdl-tokens.css`, `static/css/mdl.css`
- Catálogo: http://127.0.0.1:5000/mdl/

## 2. Identificadores MTX-*

| ID | Nombre |
|----|--------|
| MTX-BTN-001 | Primary Button |
| MTX-BTN-002 | Secondary Button |
| MTX-CRD-001 | Card |
| MTX-INP-001 | Text Input |
| MTX-TBL-001 | Data Table |
| MTX-MDL-001 | Modal |

Registro completo: `components.md`

## 3. Tokens

- **Radius:** sm, md, lg, xl — nunca `14px` sueltos
- **Shadow:** xs, sm, md, lg, xl
- **Breakpoints:** XS 480 · SM 640 · MD 768 · LG 1024 · XL 1280 · 2XL 1536

Ver `tokens.md`

## 4. Roustix Motion

| Acción | ms |
|--------|-----|
| Hover | 150 |
| Fade | 200 |
| Modal | 250 |
| Sidebar | 300 |

## 5. Dark Mode

`.theme-dashboard-dark` · `[data-mdl-theme="dark"]` — ver `dark-mode.md`

## 6. Patrones MTX-PAT-*

Registrar OT · Buscar Activo · Importar Excel · Confirmar Acción — ver `patterns.md`

## 7. MRL

Roustix Report Language para PDF — ver `docs/mrl/README.md`

## 8. Changelog

Ver `changelog.md`

---

*MDL v1.0 · 2026 · Roustix*
