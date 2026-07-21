# MTX-UX-MEASURE · Objetivos medibles

Targets numéricos para validar si una mejora **realmente beneficia al usuario**.

Complementa definiciones en [north-star.md](north-star.md) · instrumentación en producto (analytics).

---

## Objetivos globales (Roustix)

| Métrica | Sigla | Objetivo global | Definición |
|---------|-------|-----------------|------------|
| **North Star 1** | **TTFAV** | **< 3 minutos** | Registro/login → primera acción útil del perfil |
| **North Star 2** | **TTCOT** | **< 2 minutos** | Abrir OT asignada → cerrar OT (tiempo en sistema) |
| **North Star 3** | **TTFFI** | **< 15 segundos** | Intención de búsqueda → dato visible |

> Los objetivos globales son el **piso de excelencia**. Perfiles y contextos pueden tener sub-targets en north-star.md.

---

## Cómo medir

| Métrica | Evento inicio | Evento fin | Instrumento |
|---------|---------------|------------|-------------|
| TTFAV | `session_start` / registro OK | Primera acción útil* | Analytics |
| TTCOT | `ot_open` | `ot_closed` | Analytics + timestamp servidor |
| TTFFI | `search_submit` / click nav | Resultado renderizado | RUM / manual test |

*Acción útil por perfil: OT creada · venta creada · dashboard loaded con KPI · usuario invitado.

---

## Validación de mejoras

Antes de declarar una feature «lista»:

1. Baseline medido (si existe tráfico)
2. Hipótesis: «Reduce TTCOT en campo X»
3. Post-release: comparar ventana 7 días
4. Si empeora métrica → rollback o iteración

**No shippear** mejoras UX que empeoren TTFFI sin excepción documentada (DEC / MADR).

---

## Sub-targets por perfil (referencia)

Ver [north-star.md](north-star.md) para desglose Laura/Carlos/Valentina.  
El objetivo global **3 / 2 / 15** aplica cuando el contexto es el flujo crítico principal.

| Perfil | TTFAV acción | Notas |
|--------|--------------|-------|
| Carlos | 1 OT registrada | Contribuye a TTFAV global |
| Laura | Dashboard accionable | TTFFI para drill-down |
| Andrea | 1 usuario invitado | Onboarding completo puede exceder 3 min — medir por fase |

---

## Dashboard interno (roadmap)

Métricas a visualizar en Roustix interno:

- P50 / P95 TTFAV, TTCOT, TTFFI por tenant y release
- Correlación con abandono trial
- Top pantallas con TTFFI > 15 s

---

## Relación con UX Laws

| Ley | Métrica que protege |
|-----|---------------------|
| Ley 1 | TTFAV (empty → acción) |
| Ley 2 | TTCOT (feedback → completar) |
| Ley 4 | TTFFI (siguiente paso → encontrar) |

Ver [laws.md](laws.md) · cultura de desarrollo en [docs/README.md](../README.md).
