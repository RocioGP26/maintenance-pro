# Sprint 23.1 · Reporte de implementación

**Fecha:** 2026-07-28  
**Estado:** implementación local completa · validación remota pendiente

## Implementado

- Workflow diario con cliente oficial PostgreSQL 18.
- Dump custom e inspección mediante `pg_restore --list`.
- Restauración automática en PostgreSQL 18 aislado.
- Restauración portátil compatible con dumps de Neon, sin retirar del respaldo
  original la extensión de infraestructura `pg_session_jwt`.
- Verificación de Alembic y tablas críticas.
- Réplica incremental e inmutable de objetos S3 sin propagar eliminaciones.
- Verificación por ETag y tamaño de objetos.
- Copia del dump y su índice al bucket de recuperación con SHA-256.
- Manifiesto diario JSON y artefacto de GitHub con retención de 30 días.
- CLI `flask backup-storage` y script para automatización.
- Runbook de restauración y configuración.

## Verificación local

- 6 pruebas focalizadas de backup: OK.
- Suite completa: 225 pruebas, OK.
- `compileall`: OK.
- YAML del workflow: parseado correctamente.
- `git diff --check`: OK.

## Pendiente operativo

GitHub Actions tiene configurados los secretos requeridos. El bucket operativo
y el bucket de recuperación ya fueron separados. Se debe completar una
ejecución remota exitosa que valide la restauración y la réplica entre ambos.

## Definition of Done

- [x] Cliente PostgreSQL 18.
- [x] Restauración automática en PostgreSQL 18.
- [x] Verificación de esquema crítico y Alembic.
- [x] Réplica incremental a otro bucket.
- [x] Manifiesto de objetos y hashes de artefactos.
- [x] Pruebas y runbook.
- [ ] Ejecución remota exitosa con credenciales reales.
- [ ] Simulacro manual documentado por un responsable.
