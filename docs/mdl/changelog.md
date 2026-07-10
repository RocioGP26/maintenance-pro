# MDL Changelog

## [1.0.0] — Frozen · Documentation Suite v1.0

### Status
- ✔ **Congelado** — Maintix Design Language primera edición oficial
- Tag suite: `docs-v1.0`

---

## [1.0.0] — 2026-07-09

### Added
- Proyecto MDL **independiente** en `docs/mdl/`
- Sistema de IDs `MTX-*` con fichas técnicas
- Registro en `components.md` (20+ componentes)
- Fichas iniciales: BTN-001/002, CRD-001, INP-001, TBL-001, MDL-001
- Capítulos: tokens, motion, dark mode, responsive, patterns, email
- Catálogo interactivo `/mdl/`
- Tokens ampliados: radius-sm→xl, shadow-xs→xl, breakpoints XS–2XL
- Maintix Motion oficial (150/200/250/300ms)
- Dark mode tokens en `mdl-tokens.css`
- Estados: button loading/focus, card hover/selected/loading, input error/success/readonly
- Separación Brand Book ↔ MDL ↔ MRL

### Changed
- Brand Book ya no incluye capítulos técnicos MDL (solo enlace)
- Rutas: `/brandbook/` (antes `/brand-book/`), redirect 301 legacy
- MDL catálogo movido de brandbook a `/mdl/`

### Planned (1.1)
- Fichas restantes (SEL, CHT, SDB, NAV…)
- Migración plantillas producto a `mtx-*`
- Plantillas email en `templates/email/`
- Export PDF automático desde `MDL_v1.md`
