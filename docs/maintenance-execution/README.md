# Sprint 19 · Maintenance Execution Foundation

**Estado:** Sprint 19 completo ✅ · 19.0–19.5 implementados  
**Módulo:** `mantenimiento` · **Capacidad:** ejecución guiada y datos operativos

Sprint 19 estandariza cómo se ejecuta y documenta una intervención en Roustix.
No crea un módulo independiente: amplía Maintenance y reutiliza activos, órdenes
de trabajo, incidencias, usuarios, permisos, auditoría y notificaciones.

## Objetivo

Construir una base común para:

1. procedimientos y checklists versionados;
2. bitácora contextual de OT, incidencia y activo;
3. medidores y lecturas históricas por activo.

Estos datos serán la fuente para los disparadores, automatizaciones y Asset
Health de los siguientes sprints.

## Principios

1. Toda entidad operativa pertenece a un `empresa_id`.
2. Una versión publicada de un procedimiento es inmutable.
3. La OT conserva una copia histórica del procedimiento que ejecutó.
4. Se diferencia el ejecutor del trabajo del usuario que registra la información.
5. La bitácora es trazabilidad; las correcciones se agregan, no se sobreescriben.
6. Las lecturas de medidor son históricas y no sustituyen el maestro del activo.
7. Sprint 19 registra hechos; Sprint 20 decidirá y ejecutará automatizaciones.

## Sub-sprints

| Sprint | Entrega | Estado |
|---|---|---|
| 19.0 | Charter, arquitectura, contratos y migración | ✅ |
| 19.1 | Catálogo y versionado de procedimientos | ✅ |
| 19.2 | Checklist ejecutable dentro de la OT | ✅ |
| 19.3 | Evidencias, no conformidades, firma y auditoría | ✅ |
| 19.4 | Bitácora contextual y archivos adjuntos | ✅ |
| 19.5 | Medidores, lecturas, integración y cierre | ✅ |

## Documentos

- [Charter, alcance y Definition of Done](SPRINT19-REPORT.md)
- [Arquitectura y modelos](architecture.md)
- [Estados, permisos, eventos y contratos](contracts.md)
- [Compatibilidad y migración](migration.md)
