# Journey · Carlos · Técnico (MTX-UX-PER-002)

👨‍🔧 **Carlos**, 35 años · Técnico de mantenimiento

**Goal:** Registrar · **Anti-Goal:** Llenar formularios innecesarios

---

## Flujo

| Paso | Acción | Feedback (Ley 2) | UI |
|------|--------|------------------|-----|
| 1 | Inicia sesión | Redirect a «Mis OTs» | Login → home técnico |
| 2 | Ve OTs asignadas | Lista con prioridad visual | Tabla / cards |
| 3 | Abre OT | Detalle con activo linked | Vista detalle |
| 4 | Consulta activo | Historial OT + specs | Tab o panel lateral |
| 5 | Ejecuta checklist | Progreso, conformidad y evidencia visibles | Checklist versionado |
| 6 | Registra trabajo | «Avance guardado» y autoría propia | Jornada + bitácora |
| 7 | Registra lectura | Unidad, última lectura y validación inmediata | Medidor del activo desde la OT |
| 8 | Adjunta fotos | Preview + «Archivo subido» | Upload privado |
| 9 | Solicita finalización | «Ejecución registrada; pendiente de cierre» | Confirm + toast |
| 10 | — | Laura ve dashboard actualizado | Async / realtime |

## Métricas

- **TTCOT:** pasos 3–9 ≤ 15 min (correctivo simple)
- **TTFFI:** paso 4 ≤ 10 s desde código activo

## Leyes críticas

- **Ley 3:** No perder registro si pierde señal (aviso + retry)
- **Ley 5:** «Registrar ejecución» es la acción primaria; el cierre definitivo corresponde al supervisor
- Una regresión del horómetro o un valor fuera de rango nunca se acepta silenciosamente: la UI solicita tipo de novedad y justificación.
- Si una regla crea una OT o aviso a partir de la lectura, la campana muestra únicamente la entrega dirigida al técnico autenticado.

## Empty states

- Sin OTs: «No tienes órdenes asignadas» + enlace si tiene permiso crear
