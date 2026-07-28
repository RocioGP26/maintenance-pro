# Runbook · Backup y restauración de Roustix

## Unidad de recuperación

Una recuperación válida requiere dos componentes tomados en la misma ventana:

1. `database.dump`: datos y esquema PostgreSQL.
2. `storage.manifest.json`: inventario de archivos replicados en el bucket de
   recuperación.

El dump, su índice y el manifiesto también se guardan en el bucket de
recuperación bajo prefijos fechados; el artefacto de GitHub es una copia
operativa adicional de 30 días.

Restaurar solamente la base puede dejar referencias a fotografías, evidencias,
logos e informes inexistentes.

## Variables de GitHub Actions

### Secretos

- `DATABASE_URL`
- `STORAGE_ACCESS_KEY_ID`
- `STORAGE_SECRET_ACCESS_KEY`
- `STORAGE_BACKUP_ACCESS_KEY_ID`
- `STORAGE_BACKUP_SECRET_ACCESS_KEY`

### Variables o secretos según el proveedor

- `STORAGE_BUCKET`
- `STORAGE_ENDPOINT_URL`
- `STORAGE_REGION`
- `STORAGE_BACKUP_BUCKET`
- `STORAGE_BACKUP_ENDPOINT_URL`
- `STORAGE_BACKUP_REGION`

El bucket operativo y el bucket de recuperación deben ser distintos. Se
recomienda que el segundo tenga versionado, bloqueo de objetos y credenciales de
administración separadas de Render.

La réplica utiliza claves inmutables derivadas del ETag y el tamaño. Una nueva
versión de un archivo crea otra clave en lugar de sobrescribir la anterior; por
eso puede aplicarse una regla de Bucket Lock a todo el bucket de recuperación.

## Ejecución diaria

El workflow `.github/workflows/backup.yml` realiza:

1. dump remoto con `postgres:18`;
2. inspección con `pg_restore --list`;
3. creación de una lista de restauración portátil que omite únicamente
   extensiones de infraestructura de Neon no disponibles en PostgreSQL oficial;
4. restauración en PostgreSQL 18 temporal, conservando intacto el dump original;
5. consultas de integridad sobre Alembic y tablas críticas;
6. réplica incremental de S3;
7. publicación de los manifiestos y el dump como artefacto protegido.

Actualmente la única exclusión portátil permitida es `pg_session_jwt`. Roustix
no depende de esa extensión: Neon la administra como parte de su plataforma. La
exclusión no modifica `database.dump`, de modo que una recuperación sobre Neon
conserva toda la definición original.

## Simulacro manual

1. Ejecutar `Backup Neon` mediante `workflow_dispatch`.
2. Descargar el artefacto de la ejecución.
3. Crear una base PostgreSQL vacía y aislada.
4. Restaurar con:

   ```bash
   pg_restore --no-owner --no-acl --exit-on-error \
     --dbname="$RESTORE_DATABASE_URL" database.dump
   ```

5. Comprobar `alembic_version`, `empresas`, `users`, `machines` y
   `work_orders`.
6. Seleccionar una muestra de archivos del manifiesto y comparar tamaño y ETag.
7. Iniciar Roustix contra el entorno temporal y ejecutar el smoke test funcional.
8. Registrar fecha, responsable, tiempos de restauración y hallazgos.

## Criterio de incidente

Un workflow de backup fallido es un incidente operativo de prioridad alta. No
debe esperarse a la siguiente ejecución diaria sin investigar su causa.
