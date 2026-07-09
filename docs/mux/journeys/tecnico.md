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
| 5 | Registra trabajo | Autosave o «Guardado» | Form mínimo |
| 6 | Adjunta fotos | Preview + «Archivo subido» | Upload |
| 7 | Cierra OT | «OT #1042 cerrada» | Confirm + toast |
| 8 | — | Laura ve dashboard actualizado | Async / realtime |

## Métricas

- **TTCOT:** pasos 3–7 ≤ 15 min (correctivo simple)
- **TTFFI:** paso 4 ≤ 10 s desde código activo

## Leyes críticas

- **Ley 3:** No perder registro si pierde señal (aviso + retry)
- **Ley 5:** «Cerrar OT» es primary en paso 7

## Empty states

- Sin OTs: «No tienes órdenes asignadas» + enlace si tiene permiso crear
