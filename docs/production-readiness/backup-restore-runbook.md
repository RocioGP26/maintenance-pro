# Runbook · Backup y restauración de Roustix

Documento canónico de **Fase 1 · Recuperación de backups**. Demuestra que el
respaldo no solo se genera: se **restaura**, se **valida** y se mide el **tiempo**.

**Última revisión documental:** 2026-07-29  
**Evidencia automática (CI):** workflow `Backup Neon` (`.github/workflows/backup.yml`)  
**Evidencia remota previa:** runs `30389728697`, `30406614706` (Sprint 23.1)

---

## 1. Objetivos de recuperación

| Métrica | Objetivo Fase 1 | Cómo se cumple hoy |
| --- | --- | --- |
| **RPO** (pérdida máxima de datos) | ≤ **24 horas** | Backup diario a las **03:00 UTC** + réplica S3 al bucket de recuperación |
| **RTO** (tiempo hasta servicio usable en entorno de prueba) | ≤ **2 horas** | Restaurar dump + checks SQL + muestra de archivos |
| **RTO** (reapuntar producción a BD recuperada) | ≤ **4 horas** | Neon PITR *o* `pg_restore` a rama/DB nueva + cambio de `DATABASE_URL` en Render + smoke |

> Un backup **no cuenta** como válido hasta superar una restauración real
> (automática en CI cada día, y simulacro manual al menos trimestral).

### Medición del tiempo

En cada simulacro registrar:

| Hito | Reloj |
| --- | --- |
| T0 | Inicio del simulacro (descarga del artefacto o branch Neon) |
| T1 | Dump restaurado / branch lista |
| T2 | Checks SQL de integridad OK |
| T3 | Muestra de archivos del manifiesto verificada |
| T4 | App apunta al entorno recuperado y smoke OK |
| **RTO medido** | T4 − T0 |

Plantilla de registro: [`backup-recovery-drill.md`](backup-recovery-drill.md).

---

## 2. Unidad de recuperación

Una recuperación válida requiere **ambos** componentes de la misma ventana:

1. `database.dump` — datos y esquema PostgreSQL (formato custom `pg_dump`).
2. `storage.manifest.json` — inventario de archivos en el bucket de recuperación.

También se conservan:

- `database.manifest` / `database.restore.list` — índice y lista portátil.
- Artefacto GitHub `roustix-backup-<run_id>` — retención **30 días**.
- Copia del dump e índice en el **bucket de recuperación** (SHA-256).

Restaurar solo la base deja referencias a fotos, evidencias, logos e informes
inexistentes.

---

## 3. Procedimiento

### 3.1 Variables necesarias

**Secretos**

- `DATABASE_URL`
- `STORAGE_ACCESS_KEY_ID` / `STORAGE_SECRET_ACCESS_KEY`
- `STORAGE_BACKUP_ACCESS_KEY_ID` / `STORAGE_BACKUP_SECRET_ACCESS_KEY`

**Variables**

- `STORAGE_BUCKET`, `STORAGE_ENDPOINT_URL`, `STORAGE_REGION`
- `STORAGE_BACKUP_BUCKET`, `STORAGE_BACKUP_ENDPOINT_URL` (opcional), `STORAGE_BACKUP_REGION` (opcional)
- `STORAGE_BACKUP_PREFIX` (default `roustix`)

El bucket de recuperación **debe ser distinto** del operativo. Credenciales de
recuperación: preferible fuera de Render (GitHub Secrets).

### 3.2 Backup diario (ya automatizado)

El workflow `.github/workflows/backup.yml`:

1. `pg_dump` con cliente PostgreSQL **18**.
2. Inspección con `pg_restore --list`.
3. Lista portátil (omite solo `pg_session_jwt` de Neon; el dump original intacto).
4. **Restauración real** en PostgreSQL 18 temporal.
5. Consultas de integridad (Alembic + tablas críticas).
6. Réplica incremental S3 → bucket de recuperación.
7. Publicación del artefacto protegido.

Un workflow fallido = incidente **P1**. No esperar al día siguiente.

### 3.3 Recuperación A · Neon PITR (más rápida para solo BD)

Usar cuando el incidente es corrupción/borrado reciente y Neon tiene historial:

1. Neon Console → proyecto → **Branches** → restore / create branch from time.
2. Obtener la nueva `DATABASE_URL` de la rama.
3. **No** apuntar producción aún: primero checks de la sección 4 contra esa URL.
4. Si el storage no se perdió, la unidad de recuperación está completa (BD + R2 operativo).
5. Si también falló el storage, seguir 3.4 para archivos desde el bucket de recuperación.
6. En Render, actualizar `DATABASE_URL` solo tras T2–T4 OK.
7. Redeploy / restart del servicio web y worker.

### 3.4 Recuperación B · Dump lógico + storage (DR completo)

Usar ante pérdida de proyecto Neon, migración de proveedor o simulacro formal.

1. **Obtener el artefacto**
   - Actions → **Backup Neon** → última run verde → artefacto `roustix-backup-*`, **o**
   - Objetos fechados en `STORAGE_BACKUP_BUCKET` bajo el prefijo configurado.
2. **Preparar destino aislado**
   - Crear base PostgreSQL 18 vacía (Neon branch nueva, Docker local o instancia temporal).
   - Nunca restaurar el dump directamente sobre producción sin ventana acordada.
3. **Restaurar la base**

   ```bash
   pg_restore --no-owner --no-acl --exit-on-error \
     --dbname="$RESTORE_DATABASE_URL" database.dump
   ```

   Si el destino es PostgreSQL oficial (no Neon) y falla por `pg_session_jwt`:

   ```bash
   pg_restore --no-owner --no-acl --exit-on-error \
     --use-list=database.restore.list \
     --dbname="$RESTORE_DATABASE_URL" database.dump
   ```

4. **Validar integridad SQL** (sección 4.1) → anotar T2.
5. **Validar archivos** (sección 4.2) → anotar T3.
6. **Smoke de aplicación** (sección 4.3) → anotar T4.
7. **Cortar a producción** solo con aprobación explícita: actualizar secretos en Render,
   reiniciar web + worker, monitorear `/health/ready` y el panel Platform → Infraestructura.

### 3.5 Alternativa CLI (dump gzip local)

```powershell
flask --app run:app verify-backup backups/neon_YYYYMMDD_HHMMSS.sql.gz
flask --app run:app restore-db backups/neon_YYYYMMDD_HHMMSS.sql.gz --target $RESTORE_DATABASE_URL --yes
```

Misma regla: destino temporal primero. Detalle en [`docs/backup-neon.md`](../backup-neon.md).

---

## 4. Validación de integridad

### 4.1 Base de datos (obligatorio)

```sql
-- Deben existir las 5 tablas críticas
SELECT count(*) FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'alembic_version', 'empresas', 'users', 'machines', 'work_orders'
  );
-- Esperado: 5

SELECT version_num FROM alembic_version LIMIT 1;
-- Esperado: revisión no vacía (ej. la misma o cercana a producción)

SELECT count(*) FROM empresas;
SELECT count(*) FROM users WHERE activo IS TRUE;
SELECT count(*) FROM machines;
SELECT count(*) FROM work_orders;
```

Criterio de paso: las 5 tablas presentes, revisión Alembic legible, conteos
coherentes con el tamaño del tenant (no todos en cero si producción tenía datos).

### 4.2 Almacenamiento (obligatorio en DR completo)

1. Abrir `storage.manifest.json` del mismo artefacto/ventana.
2. Tomar una **muestra** (≥ 3 objetos, o todos si hay pocos).
3. Para cada clave: comprobar existencia en `STORAGE_BACKUP_BUCKET`, **tamaño** y **ETag**.
4. Opcional: servir un logo o evidencia vía app apuntando temporalmente al bucket
   de recuperación / copia restaurada.

Criterio de paso: 100 % de la muestra coincide en tamaño y ETag.

### 4.3 Smoke funcional (obligatorio antes de declarar RTO cumplido)

Con la app contra el entorno recuperado:

1. `GET /health/live` → 200.
2. `GET /health/ready` → 200 (o degradado documentado, nunca 503 por BD).
3. Login SuperAdmin Platform o admin de un tenant de prueba.
4. Abrir listado de empresas / activos / una OT conocida.
5. Descargar o visualizar un archivo de la muestra (logo o evidencia).

Criterio de paso: login OK + lectura de datos + al menos un archivo visible.

### 4.4 Prueba continua (cada noche)

El paso *«Restaurar y verificar el dump»* del workflow es la prueba automática de
integridad de BD. Si está verde, el dump del día **sí restaura**. El manifiesto S3
y la réplica se publican en el mismo run.

---

## 5. Criterio de incidente

| Evento | Severidad | Acción |
| --- | --- | --- |
| Workflow `Backup Neon` fallido | P1 | Investigar el mismo día; no esperar al cron siguiente |
| Artefacto o réplica S3 incompleta | P1 | Re-ejecutar `workflow_dispatch` tras corregir secretos |
| Simulacro trimestral vencido (> 90 días) | P2 | Programar drill y registrar en `backup-recovery-drill.md` |
| RTO medido > objetivo | P2 | Post-mortem: cuellos (descarga, tamaño dump, DNS, secrets) |

---

## 6. Evidencia histórica (Sprint 23.1)

| Campo | Valor |
| --- | --- |
| Runs | `30389728697`, `30406614706` |
| Restauración PG 18 | OK |
| Alembic (ejemplo) | `pr7s2t84u06w_password_resets` |
| Objetos replicados (primera run) | 2 |
| Artefacto | `roustix-backup-30389728697` |

Detalle: [`SPRINT23.1-REPORT.md`](SPRINT23.1-REPORT.md).

---

## 7. Referencias

- [`backup-recovery-drill.md`](backup-recovery-drill.md) — plantilla de simulacro
- [`docs/backup-neon.md`](../backup-neon.md) — PITR Neon y CLI local
- [`docs/production-storage.md`](../production-storage.md) — storage y cutover
- Panel SuperAdmin: `/platform/infraestructura` → estado Backups
