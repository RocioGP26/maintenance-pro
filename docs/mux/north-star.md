# MUX · North Star Metrics

Tres métricas que miden si Roustix cumple su promesa UX.
Origen: journey macro + goals por perfil.

## Objetivos globales (MTX-UX-MEASURE)

| Métrica | Objetivo |
|---------|----------|
| **TTFAV** | **< 3 minutos** |
| **TTCOT** | **< 2 minutos** |
| **TTFFI** | **< 15 segundos** |

Detalle e instrumentación: [measure.md](measure.md)

---

## North Star 1 · TTFAV

**Time to First Actionable Value**
*Tiempo hasta la primera acción útil.*

| Perfil | Acción | Objetivo |
|--------|--------|----------|
| Carlos (Técnico) | 1 OT registrada | ≤ 10 min post-registro |
| Valentina (Vendedor) | 1 venta o cotización | ≤ 15 min |
| Laura (Gerente) | Dashboard con dato accionable | ≤ 5 min |
| Andrea (Admin) | Empresa + 1 usuario invitado | ≤ 30 min |

**Mide:** onboarding, primera victoria, abandono trial.

---

## North Star 2 · TTCOT

**Time to Close OT**
*Tiempo para cerrar una orden de trabajo.*

Desde «OT asignada» hasta «OT cerrada con evidencia».

| Contexto | Objetivo orientativo |
|----------|---------------------|
| Correctivo simple | ≤ 15 min en sistema (excl. trabajo físico) |
| Preventivo programado | ≤ 8 min |
| Con repuestos | ≤ 20 min (incluye reserva bodega) |

**Mide:** fricción formularios, búsqueda activo, adjuntos, integración bodega.

---

## North Star 3 · TTFFI

**Time to Find Information**
*Tiempo para encontrar información.*

Desde intención («¿dónde está X?») hasta dato visible.

| Búsqueda | Objetivo |
|----------|----------|
| Activo por código | ≤ 10 s |
| OT por número | ≤ 10 s |
| Stock de referencia | ≤ 15 s |
| Cliente por nombre/NIT | ≤ 15 s |
| Reporte mensual (gerente) | ≤ 3 clics / 60 s |

**Mide:** búsqueda global, filtros, navegación, performance.

---

## Cómo usar en producto

1. **Analytics** — eventos con timestamp por paso de journey
2. **UX review** — si TTCOT sube tras un release, investigar
3. **A/B** — solo contra North Stars, no vanity metrics (page views)

## Relación con Leyes UX

| Ley | North Star afectado |
|-----|---------------------|
| Ley 1 (nunca pantalla vacía) | TTFAV |
| Ley 2 (retroalimentación) | TTCOT |
| Ley 4 (siguiente paso) | TTFFI |

Ver [laws.md](laws.md).
