# Sprint 23 · Production Readiness & Go-Live

## Objetivo

Cerrar las brechas técnicas y operativas que impiden utilizar Roustix con
clientes reales, sin incorporar funcionalidades nuevas de negocio.

## Bloques

| Bloque | Alcance | Estado |
| --- | --- | --- |
| 23.1 | Backup y recuperación comprobable | Implementado · validación remota aprobada |
| 23.2 | Hardening de identidad y plataforma | Implementado · desplegado en producción |
| 23.3 | CI PostgreSQL, seguridad y pruebas E2E | Implementado · validación remota aprobada |
| 23.4 | Observabilidad, workers y operación | En curso |
| 23.5 | Dominio, correo, UAT y salida controlada | Pendiente |

## Documentos activos

- `SPRINT23.4-CHARTER.md`: alcance, secuencia y criterios de cierre.
- `SPRINT23.4-REPORT.md`: avance verificable de observabilidad y alertas.
- `SPRINT23.4-WORKERS-RUNBOOK.md`: despliegue y recuperación de Redis/worker.
- `backup-restore-runbook.md`: **recuperación de backups** (RTO/RPO, procedimiento, integridad).
- `backup-recovery-drill.md`: plantilla de simulacro trimestral.
- `storage-certification.md`: evidencia y gate de certificación R2 del piloto.
- `account-recovery-certification.md`: controles y gate SMTP de recuperación de cuenta.
- `storage-capacity-certification.md`: cuotas por plan, umbrales y política del add-on.

## Regla de salida

Roustix no se considera lista para producción por la sola existencia de un
artefacto o un workflow verde. Cada control crítico debe demostrar su
funcionamiento mediante una prueba repetible y conservar evidencia auditable.
