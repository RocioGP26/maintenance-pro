# MUX · Accesibilidad · MTX-UX-A11Y

Roustix opera en plantas, talleres y bodegas — pantallas con sol, guantes, ruido. A11Y no es opcional.

---

## MTX-UX-A11Y-001 · Contraste

- Texto cuerpo: **WCAG AA** mínimo (4.5:1)
- Texto grande / títulos: 3:1
- Usar tokens MDL — no grises ad hoc
- Modo oscuro: re-validar contraste en `--mdl-surface` dark

```css
/* ✅ tokens */
color: var(--mdl-text-primary);

/* ❌ */
color: #aaa;
```

---

## MTX-UX-A11Y-002 · Navegación teclado

- Todo flujo crítico completable **sin mouse**
- Orden de tab lógico (izq → der, arriba → abajo)
- Sin `tabindex > 0`
- Modales: focus trap + Escape cierra

| Flujo | Teclado |
|-------|---------|
| Formulario | Tab entre campos, Enter submit |
| Tabla | Flechas o Tab a acciones por fila |
| Modal | Tab cicla, Escape cancela |

---

## MTX-UX-A11Y-003 · Focus visible

- Nunca `outline: none` sin reemplazo
- MDL: `:focus-visible` en `mtx-btn`, `mtx-input`
- Ring 2–3px `--mdl-primary` · offset 2px

---

## MTX-UX-A11Y-004 · Lectores de pantalla

| Elemento | Requisito |
|----------|-----------|
| Botón icono | `aria-label` descriptivo |
| Modal | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| Alertas | `role="alert"` o `aria-live="polite"` |
| Tablas datos | `<th scope="col">`, caption o `aria-label` |
| Loading | `aria-busy="true"`, `aria-live` |

---

## MTX-UX-A11Y-005 · Tamaño mínimo táctil

- Targets interactivos: **44×44 px** mínimo (mobile / técnico en campo)
- Botones MDL: usar `mtx-btn-lg` en vistas móviles críticas
- Espaciado entre targets: ≥ 8px (`--mdl-space-sm`)

---

## MTX-UX-A11Y-006 · Alt text

- Imágenes informativas: `alt` descriptivo
- Decorativas: `alt=""` o `aria-hidden="true"`
- Fotos OT (evidencia): alt con contexto «Falla rodamiento CPS-001»

---

## MTX-UX-A11Y-007 · Motion reducido

Respetar `prefers-reduced-motion: reduce` — ver MDL motion.md.

---

## MTX-UX-A11Y-008 · Lenguaje claro

- Nivel lectura: secundaria comprensible
- Errores en lenguaje humano (ver messaging.md)
- Abreviaturas: expandir primera vez (OT → Orden de trabajo)

---

## Checklist A11Y por pantalla

- [ ] Contraste AA verificado
- [ ] Tab order probado
- [ ] Focus visible en todos los interactivos
- [ ] Screen reader smoke test (NVDA/VoiceOver)
- [ ] Targets ≥ 44px en mobile
- [ ] Imágenes con alt

## Herramientas

- axe DevTools · Lighthouse Accessibility · Contrast checker
- MDL componentes con A11Y en ficha (MTX-BTN-001, MTX-MDL-001, etc.)
