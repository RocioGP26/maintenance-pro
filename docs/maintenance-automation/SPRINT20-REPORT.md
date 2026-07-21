# Sprint 20 · Disparadores de mantenimiento y automatizaciones configurables

**Estado:** Finalizado ✅  
**Fecha:** 2026-07-21

## Objetivo

Evaluar lecturas de activos mediante reglas configurables y ejecutar acciones
operativas trazables sin duplicar OT ni ampliar el motor hacia código arbitrario.

## Flujo

```text
Lectura registrada
      ↓
Reglas activas del tenant y medidor
      ↓
Condición + cruce + enfriamiento
      ↓
Ejecución idempotente
      ├── Aviso interno
      └── Orden de trabajo + aviso
```

## Definition of Done

- [x] Las reglas pertenecen a empresa y medidor.
- [x] Solo supervisor o administrador configura y activa reglas.
- [x] Existen operadores mayores/menores, estrictos o inclusivos.
- [x] El modo cruce evita acciones repetidas mientras persiste la condición.
- [x] El enfriamiento limita repeticiones intencionales.
- [x] Cada combinación regla + lectura se evalúa una sola vez.
- [x] Una acción puede crear aviso interno o una OT numerada.
- [x] La OT conserva activo, prioridad, tipo, técnico y contexto del disparador.
- [x] Los destinatarios respetan tenant, rol y usuario activo.
- [x] Éxitos, omisiones y fallos conservan snapshots y auditoría.
- [x] La campana muestra avisos automáticos del usuario autenticado.
- [x] Existen migración Alembic y pruebas de tenant, cruce, enfriamiento e idempotencia.
- [x] MRG, MPA, MUX, versiones y changelog quedan alineados.

## Dependencias desbloqueadas

- Sprint 21 · Asset Health avanzado y analítica de condición.
- Sprint 22 · API pública, webhooks y derechos técnicos por plan.
