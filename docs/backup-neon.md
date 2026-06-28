# Copias de seguridad con Neon PostgreSQL

Mantis soporta backups lógicos vía `pg_dump` y la recuperación point-in-time (PITR) nativa de Neon.

## 1. PITR en Neon (recomendado)

Neon guarda snapshots automáticos en planes de pago. Para restaurar:

1. Abre el [panel de Neon](https://console.neon.tech) → tu proyecto → **Branches**.
2. Crea una rama desde un punto en el tiempo (**Restore** / **Create branch from time**).
3. Actualiza `DATABASE_URL` en tu despliegue si usas la rama restaurada.

## 2. Backup lógico con pg_dump

### Manual

```powershell
# Requiere pg_dump en PATH y DATABASE_URL configurada
flask --app run:app backup-db
```

O directamente:

```powershell
python scripts/backup_neon.py
```

Los archivos se guardan en `backups/` (configurable con `BACKUP_DIR`).

### Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URI de Neon (`postgresql://...?sslmode=require`) |
| `BACKUP_DIR` | Carpeta destino (default: `backups/`) |
| `BACKUP_RETENTION_DAYS` | Días de retención local (default: 7) |

### Cron en Render

Añade un **Cron Job** en Render:

```
python scripts/backup_neon.py
```

Programación sugerida: `0 3 * * *` (diario 03:00 UTC).

### GitHub Actions (backup diario)

El workflow `.github/workflows/backup.yml` ejecuta un `pg_dump` cada día a las 03:00 UTC y guarda `backup.sql` como artefacto (`mantis-backup`, 14 días de retención).

Configuración en GitHub:

1. Repositorio → **Settings** → **Secrets and variables** → **Actions**
2. Añadir secret `DATABASE_URL` con la URI de Neon (`postgresql://...?sslmode=require`)
3. Opcional: ejecutar manualmente desde **Actions** → **Backup Neon** → **Run workflow**

## 3. Restaurar desde un dump

```powershell
# Descomprimir si es .sql.gz
gunzip backups/neon_YYYYMMDD_HHMMSS.sql.gz

# Restaurar (cuidado: sobrescribe datos)
psql $DATABASE_URL -f backups/neon_YYYYMMDD_HHMMSS.sql
```

## 4. Migraciones con Flask-Migrate

En cada despliegue, el `Procfile` ejecuta automáticamente:

```
flask db upgrade
```

Para desarrollo local:

```powershell
flask --app run:app db upgrade          # aplicar migraciones
flask --app run:app db migrate -m "descripcion"  # generar nueva migración
flask --app run:app maintenance run   # tareas periódicas (OT, suscripciones)
```

## 5. Transición desde ensure_*

Las funciones `ensure_*` en `app/models.py` quedan como respaldo legacy. Para bases existentes que aún no migraron:

```powershell
# Una sola vez
set RUN_LEGACY_SCHEMA_MIGRATIONS=true
flask --app run:app maintenance legacy-migrate
flask --app run:app db stamp head
```

En producción nueva, solo `flask db upgrade` es necesario.
