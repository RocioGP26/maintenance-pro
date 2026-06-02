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

Crea un archivo `.env` en la raíz (no se sube a Git) o exporta variables en la sesión:

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Flask |
| `DATABASE_URL` | URI SQLAlchemy (por defecto: SQLite local) |
| `DEFAULT_ADMIN_PASSWORD` | Contraseña del usuario `admin` inicial |

Ejemplo `.env`:

```env
SECRET_KEY=cambia-esto-en-produccion
DATABASE_URL=sqlite:///mantenimiento.db
```

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
