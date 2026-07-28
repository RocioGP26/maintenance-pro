# Sprint 23.1 · Reporte de implementación

**Fecha:** 2026-07-28  
**Estado:** implementación local completa · validación remota pendiente

## Implementado

- Workflow diario con cliente oficial PostgreSQL 18.
- Dump custom e inspección mediante `pg_restore --list`.
- Restauración automática en PostgreSQL 18 aislado.
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

GitHub Actions solo tiene configurados `DATABASE_URL` y `SECRET_KEY`. Antes de
ejecutar el nuevo workflow deben configurarse:

- `STORAGE_BUCKET`
- `STORAGE_ENDPOINT_URL`
- `STORAGE_REGION`
- `STORAGE_ACCESS_KEY_ID`
- `STORAGE_SECRET_ACCESS_KEY`
- `STORAGE_BACKUP_BUCKET`
- `STORAGE_BACKUP_ENDPOINT_URL`
- `STORAGE_BACKUP_REGION`
- `STORAGE_BACKUP_ACCESS_KEY_ID`
- `STORAGE_BACKUP_SECRET_ACCESS_KEY`

## Definition of Done

- [x] Cliente PostgreSQL 18.
- [x] Restauración automática en PostgreSQL 18.
- [x] Verificación de esquema crítico y Alembic.
- [x] Réplica incremental a otro bucket.
- [x] Manifiesto de objetos y hashes de artefactos.
- [x] Pruebas y runbook.
- [ ] Ejecución remota exitosa con credenciales reales.
- [ ] Simulacro manual documentado por un responsable.
