# Simulacro de recuperación · Registro

Completar **al menos una vez por trimestre** (o tras un cambio mayor de
infraestructura). El runbook canónico es
[`backup-restore-runbook.md`](backup-restore-runbook.md).

## Cabecera

| Campo | Valor |
| --- | --- |
| Fecha (UTC) | |
| Responsable | |
| Tipo | Neon PITR · Dump lógico · Completo (BD + storage) |
| Origen del backup | Artefacto GitHub `roustix-backup-____` · Bucket recuperación · Branch Neon |
| Run / commit de referencia | |
| Entorno destino | (nunca producción en el primer intento) |

## Tiempos

| Hito | Hora (UTC) | Notas |
| --- | --- | --- |
| T0 Inicio | | |
| T1 BD restaurada / branch lista | | |
| T2 Integridad SQL OK | | |
| T3 Muestra de archivos OK | | |
| T4 Smoke app OK | | |
| **RTO medido (T4 − T0)** | | Objetivo ≤ 2 h (prueba) / ≤ 4 h (corte prod.) |

| Métrica | Objetivo | Resultado |
| --- | --- | --- |
| RPO implícito del artefacto usado | ≤ 24 h | |
| RTO medido | ver arriba | ☐ Cumple · ☐ No cumple |

## Checklist de integridad

### Base de datos

- [ ] `alembic_version`, `empresas`, `users`, `machines`, `work_orders` presentes
- [ ] `version_num` Alembic: `________________`
- [ ] Conteos coherentes (`empresas` / `users` / `machines` / `work_orders`)

### Almacenamiento

- [ ] Manifiesto de la misma ventana (`storage.manifest.json`)
- [ ] Muestra ≥ 3 objetos: tamaño y ETag coinciden
- [ ] (Opcional) Archivo visible desde la app

### Smoke

- [ ] `/health/live` 200
- [ ] `/health/ready` usable
- [ ] Login OK
- [ ] Lectura de activos / OT
- [ ] Archivo de muestra OK

## Hallazgos y acciones

| Hallazgo | Severidad | Acción | Dueño |
| --- | --- | --- | --- |
| | | | |

## Firma

| Rol | Nombre | Fecha |
| --- | --- | --- |
| Ejecutor | | |
| Revisor (ops / founder) | | |

## Histórico de simulacros

| Fecha | Responsable | RTO | Resultado | Enlace / notas |
| --- | --- | --- | --- | --- |
| 2026-07-28 | CI automático | (workflow diario) | OK · runs `30389728697`, `30406614706` | Sprint 23.1 |
| | | | | |
