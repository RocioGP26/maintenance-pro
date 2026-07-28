# Sprint 23.1 · Backup y recuperación

## Objetivo

Garantizar que la base PostgreSQL y los archivos privados de clientes puedan
recuperarse juntos después de una pérdida o corrupción del entorno productivo.

## Alcance

- Dump diario con herramientas compatibles con PostgreSQL 18.
- Validación estructural del dump.
- Restauración automática en una base PostgreSQL temporal.
- Verificación de tablas críticas y revisión Alembic.
- Réplica incremental e inmutable de objetos S3 a un bucket de recuperación
  distinto; cada versión se identifica por ETag y tamaño.
- Manifiesto diario de objetos con tamaño, ETag y fecha.
- Artefacto auditable con dump, manifiesto PostgreSQL y manifiesto S3.
- Runbook de restauración y checklist de simulacro.

## Fuera de alcance

- Alta disponibilidad multi-región de la aplicación.
- Recuperación punto en el tiempo administrada por el proveedor.
- Replicación entre proveedores con APIs no compatibles con S3.

## Reglas de seguridad

1. El bucket de recuperación debe ser diferente al bucket operativo.
2. Sus credenciales deben tener privilegios mínimos y almacenarse como secretos.
3. Los logs nunca deben imprimir URLs de conexión ni claves.
4. Una copia no cuenta como válida hasta superar una restauración real.
5. No se eliminan objetos del bucket de recuperación cuando desaparecen del origen.

## Definition of Done

- [x] El workflow usa cliente PostgreSQL 18.
- [x] El dump de Neon se restaura en PostgreSQL 18 temporal.
- [x] La restauración contiene `alembic_version` y tablas críticas.
- [x] Los objetos S3 se replican incrementalmente a otro bucket.
- [x] Se genera y conserva un manifiesto de los objetos.
- [x] Existen pruebas unitarias para réplica, omisión y configuración insegura.
- [x] Existe un runbook ejecutable de recuperación.
- [x] Se obtiene al menos una ejecución remota exitosa.
