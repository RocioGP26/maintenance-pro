# Mantis — Mantenimiento industrial (CMMS)

Aplicación web para gestión de mantenimiento: activos, órdenes de trabajo, inventario, incidencias, planeación preventiva y dashboard por sector industrial.

**Repositorio:** [github.com/RocioGP26/maintenance-pro](https://github.com/RocioGP26/maintenance-pro)

## Requisitos

- Python 3.11 o superior (probado con 3.13)
- Git

## Instalación

```powershell
git clone https://github.com/RocioGP26/maintenance-pro.git
cd maintenance-pro

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Ejecución

```powershell
python run.py
```

Abre en el navegador: **http://127.0.0.1:5000**

En el primer arranque se crea la base SQLite `mantenimiento.db` en la raíz del proyecto y, si no hay usuarios, una cuenta de administrador por defecto.

| Campo      | Valor por defecto |
|-----------|-------------------|
| Usuario   | `admin`           |
| Contraseña| `admin123`        |

> Cambia la contraseña en producción. Puedes definir `DEFAULT_ADMIN_PASSWORD` antes del primer arranque para fijar otra desde el inicio.

Tras iniciar sesión, el asistente de **onboarding** guía la configuración de la empresa (sector, sedes, plan, etc.).

## Variables de entorno (opcional)

Crea un archivo `.env` en la raíz (no se sube a Git). Ver `.env.example` para la lista completa.

| Variable | Descripción |
|----------|-------------|
| `FLASK_ENV` | `development` (default) o `production` |
| `SECRET_KEY` | Clave secreta de Flask (obligatoria en producción) |
| `DATABASE_URL` | URI SQLAlchemy (SQLite local o Neon PostgreSQL) |
| `DEFAULT_ADMIN_PASSWORD` | Contraseña del usuario `admin` inicial (solo dev) |
| `LOG_LEVEL` | Nivel de log: DEBUG, INFO, WARNING, ERROR |
| `RUN_LEGACY_SCHEMA_MIGRATIONS` | `true` para ejecutar `ensure_*` legacy (transición) |

## Migraciones de base de datos

```powershell
pip install -r requirements.txt
flask --app run:app db upgrade              # aplicar migraciones
flask --app run:app db migrate -m "cambio"  # generar nueva migración
flask --app run:app maintenance run         # tareas periódicas (OT, suscripciones)
flask --app run:app backup-db               # copia de seguridad
```

Bases existentes creadas con `ensure_*`: ejecutar una vez `flask --app run:app db stamp head`.

Documentación de backups Neon: `docs/backup-neon.md`.

## Salud y despliegue

| Endpoint | Uso |
|----------|-----|
| `GET /health/live` | Liveness (app responde) |
| `GET /health` | Readiness (BD + revisión Alembic) |

**Render:** importa `render.yaml` o conecta el repo; configura `DATABASE_URL` (Neon) y `PLATFORM_ADMIN_KEY`.

**Migraciones en Render (plan Free):** el campo *Pre-Deploy Command* no está disponible. Usa este **Build Command**:

```text
pip install -r requirements.txt && python scripts/migrate_deploy.py
```

*Start Command:* `gunicorn run:app`

En plan Starter o superior puedes mover las migraciones a *Pre-Deploy Command* (`python scripts/migrate_deploy.py`) y dejar el build solo en `pip install -r requirements.txt`.

**GitHub Actions** (secrets en Settings → Actions):

| Secret | Uso |
|--------|-----|
| `DATABASE_URL` | Backup diario + mantenimiento |
| `SECRET_KEY` | Workflow de mantenimiento |

Workflows: `backup.yml` (03:00 UTC), `maintenance.yml` (04:00 UTC).

## Estructura principal

```
app/              # Lógica Flask (rutas, modelos, KPIs, sectores)
templates/        # Plantillas HTML
static/           # CSS, imágenes (uploads de empresa en static/uploads/, ignorado por Git)
docs/             # Documentación de marca y arquitectura por sectores
run.py            # Punto de entrada
requirements.txt
```

## Funcionalidades

- Multi-empresa con onboarding por sector industrial
- Activos y tipos de máquina con campos personalizados por plantilla
- Órdenes de trabajo (correctivas, preventivas, numeración por año)
- Inventario de repuestos, equipo técnico, calendario e incidencias
- Dashboard con KPIs y planeación mensual preventiva
- Configuración de empresa (logo, jornada laboral, moneda)

## Documentación adicional

- [Marca y UI](docs/marca-mantis.md)
- [Arquitectura por sectores](docs/arquitectura-sectores.md)

## Licencia

Uso privado del propietario del repositorio salvo que se indique otra licencia.
