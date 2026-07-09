# Maintix UX Laws · Cultura de desarrollo

Estas no son sugerencias ni decoración de manual. Son la **cultura de desarrollo de Maintix**.

Cada nueva funcionalidad debe cumplir las **cinco UX Laws** antes de considerarse lista para producción.  
**Si incumple una sola ley, se rediseña antes del merge.**

IDs: **MTX-UX-LAW-001** … **005**

Documentos de apoyo obligatorios en review:

- [decision-matrix.md](decision-matrix.md) · MTX-UX-DEC
- [copy.md](copy.md) · MTX-UX-COPY
- [measure.md](measure.md) · MTX-UX-MEASURE

---

## MTX-UX-LAW-001

**Nunca mostrar una pantalla vacía.**

Sin datos ≠ sin valor. Todo empty state explica qué es la pantalla y ofrece CTA.

→ MDL: `MTX-EMP-001` · DEC-005 · [copy.md](copy.md)

---

## MTX-UX-LAW-002

**Toda acción debe tener retroalimentación.**

Guardar, eliminar, enviar, importar — el usuario **siempre** sabe que el sistema recibió la acción.

→ Toast, alert, loading · DEC-004 · Maintix Motion ≤ 300ms

---

## MTX-UX-LAW-003

**Nunca hacer perder información al usuario.**

Autosave o aviso «cambios sin guardar» · confirmación destructivas · no timeout silencioso.

→ DEC-002 · DEC-012 · `MTX-PAT-007`

---

## MTX-UX-LAW-004

**Siempre explicar el siguiente paso.**

Error, empty state, onboarding — [Qué pasó] + [Qué hacer ahora].

→ DEC-003 · [copy.md](copy.md)

---

## MTX-UX-LAW-005

**La acción principal siempre es evidente.**

Un solo primary por vista · DEC-006 · NAV-005

---

## Gate de producción (obligatorio)

```
PR con UI/templates/copy
    ↓
□ 5 Laws cumplidas
□ DEC matrix consultada
□ COPY revisado
□ NSM no degradado (si hay baseline)
    ↓
Merge permitido
```

Excepción: issue `ux-exception` + aprobación · ver DEC matrix.

---

## Jerarquía documental

```
UX Laws (cultura — este doc)
    ↓
Decision Matrix (DEC)
    ↓
Goals / Anti-Goals
    ↓
MDL patterns + mtx-*
```

## Checklist pre-merge

- [ ] Ley 1–5
- [ ] [decision-matrix.md](decision-matrix.md)
- [ ] [copy.md](copy.md)
- [ ] Perfil MUX identificado

Ver [docs/README.md](../README.md) · Filosofía de desarrollo.
