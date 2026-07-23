from flask import Flask
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config_by_name, resolve_config_name

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[], storage_uri="memory://")


def _is_production_env() -> bool:
    return resolve_config_name() == "production"


def create_app(config_name: str | None = None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    if config_name is None:
        config_name = resolve_config_name()
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    from app.logging_config import setup_logging

    setup_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)

    if (app.config.get("SQLALCHEMY_DATABASE_URI") or "").startswith("sqlite:"):
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        @event.listens_for(Engine, "connect")
        def _sqlite_pragmas(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()

    @app.teardown_appcontext
    def _finalize_db_session(exc):
        """Confirma cambios pendientes al cerrar la petición (red de seguridad)."""
        try:
            if exc is not None:
                db.session.rollback()
            elif db.session.new or db.session.dirty or db.session.deleted:
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    from app.session_management import register_session_management

    register_session_management(app)

    @app.after_request
    def _security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if _is_production_env():
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        return response

    from app.public_api.contract import register_public_api_contract
    from app.tenancy.middleware import register_tenancy_middleware

    register_public_api_contract(app)
    register_tenancy_middleware(app)

    from app.branding import (
        APP_FAVICON_PATH,
        APP_LOGO_PATH,
        APP_NAME,
        APP_TAGLINE,
        empresa_logo_url_or_none,
    )

    from app.money import formato_moneda
    from app.models import machine_status_meta, proveedor_tipo_meta, incident_prioridad_meta, wo_es_editable, wo_status_meta, wo_tipo_meta
    from app.alertas_service import resumen_alertas_campana
    from app.permissions import SOLICITANTE_ENDPOINTS, is_read_only, is_requester, is_technician, permission_flags

    @app.before_request
    def _restrict_requester_scope():
        """El solicitante solo entra al flujo de reporte y seguimiento propio."""
        from flask import flash, redirect, request, url_for

        if not current_user.is_authenticated or not is_requester(current_user):
            return None
        endpoint = request.endpoint or ""
        if (
            endpoint in SOLICITANTE_ENDPOINTS
            or endpoint == "static"
            or endpoint == "storage.media"
            or endpoint.startswith("onboarding.")
            or endpoint.startswith("health.")
            # Docs públicos (MBB / MAG / MSD / MRG / hub) + activos MKT de captación
            or endpoint.startswith((
                "brand_book.",
                "openapi.",
                "docs_hub.",
            ))
            or endpoint in (
                "mkt.assets",
                "mkt.mtx_case",
                "mag.index",
                "mag.index_no_slash",
                "mag.css",
                "mag.guide",
                "mag.chapters",
                "msd.index",
                "msd.index_no_slash",
                "msd.css",
                "msd.guide",
                "msd.chapters",
                "msd.openapi_portal",
                "msd.collections_portal",
            )
        ):
            return None
        flash("Tu rol de solicitante solo permite reportar y consultar tus incidencias.", "warning")
        return redirect(url_for("main.incidencias_list"))

    @app.before_request
    def _restrict_technician_scope():
        """Evita acceso directo a funciones de gestion fuera del trabajo asignado."""
        from flask import flash, redirect, request, url_for

        if not current_user.is_authenticated or not is_technician(current_user):
            return None
        endpoint = request.endpoint or ""
        allowed_mutations = {
            "main.logout", "main.mi_perfil", "main.session_status",
            "main.ordenes_edit", "main.ordenes_informe_upload",
            "main.incidencias_accion", "main.incident_notifications_seen",
            "main.incident_notifications_read", "main.notifications_action",
            "maintenance_execution.work_order_checklist_execute",
            "maintenance_execution.context_log",
            "maintenance_execution.context_log_notification_read",
            "maintenance_execution.asset_meter_reading",
            "maintenance_automation.notification_read",
        }
        blocked_prefixes = (
            "purchasing.", "inv_comercial.", "platform.", "main.analisis",
            "main.mantenimiento_costos", "main.reportes", "main.configuracion",
            "main.equipo", "main.seguridad", "main.proveedores",
            "main.activos_tipo", "main.ordenes_planeacion",
        )
        blocked_endpoints = {
            "main.ordenes_new", "main.ordenes_export", "main.ordenes_export_pdf", "main.activos_new",
            "main.activos_edit", "main.activos_delete", "main.activos_export",
            "main.activos_toggle_critico", "main.inventario_new",
            "main.inventario_edit", "main.inventario_entrada",
        }
        if endpoint.startswith(blocked_prefixes) or endpoint in blocked_endpoints:
            flash("Tu perfil tecnico solo permite ejecutar tareas asignadas y consultar informacion operativa.", "warning")
            return redirect(url_for("main.dashboard"))
        if request.method not in ("GET", "HEAD", "OPTIONS") and endpoint not in allowed_mutations:
            flash("Esta accion no esta habilitada para el perfil tecnico.", "warning")
            return redirect(request.referrer or url_for("main.dashboard"))
        return None

    @app.before_request
    def _enforce_global_read_only():
        """Bloquea escrituras del rol Usuario también fuera del blueprint principal."""
        from flask import flash, redirect, request, url_for

        if not current_user.is_authenticated or not is_read_only(current_user):
            return None
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return None
        if request.endpoint in ("main.logout", "main.mi_perfil", "main.session_status"):
            return None
        flash("Tu rol de usuario solo permite consultar información.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))

    app.jinja_env.globals["wo_status_meta"] = wo_status_meta
    app.jinja_env.globals["machine_status_meta"] = machine_status_meta
    app.jinja_env.globals["formato_moneda"] = formato_moneda
    app.jinja_env.globals["wo_es_editable"] = wo_es_editable
    app.jinja_env.globals["wo_tipo_meta"] = wo_tipo_meta
    app.jinja_env.globals["proveedor_tipo_meta"] = proveedor_tipo_meta
    app.jinja_env.globals["incident_prioridad_meta"] = incident_prioridad_meta

    # Los datos de instalaciones antiguas pueden contener mojibake o acentos
    # reemplazados por ``?``. Se normalizan al renderizar cualquier vista.
    from app.text_encoding import texto_legible

    app.jinja_env.finalize = texto_legible
    app.jinja_env.filters["texto_legible"] = texto_legible

    from app.file_storage import url_for_reference

    app.jinja_env.globals["media_url"] = url_for_reference

    from app.custom_fields import seccion_campos_cuatro_por_fila
    from app.password_policy import PASSWORD_REQUIREMENTS_TEXT
    from app.locale_options import zona_horaria_label
    from app.timezone_utils import (
        empresa_desde_contexto,
        formato_fecha_hora as _formato_fecha_hora,
        hoy_local,
    )

    app.jinja_env.filters["cuatro_por_fila"] = seccion_campos_cuatro_por_fila
    app.jinja_env.globals["password_requirements"] = PASSWORD_REQUIREMENTS_TEXT
    app.jinja_env.globals["hoy_local"] = hoy_local
    app.jinja_env.globals["zona_horaria_label"] = zona_horaria_label

    from jinja2 import pass_context

    @app.template_filter("formato_fecha_hora")
    @pass_context
    def jinja_formato_fecha_hora(context, dt, fmt="%d/%m/%Y %H:%M"):
        empresa = empresa_desde_contexto(context)
        return _formato_fecha_hora(dt, fmt, empresa=empresa, desde_utc=True)

    @app.template_filter("formato_fecha_local")
    def jinja_formato_fecha_local(dt, fmt="%d/%m/%Y %H:%M"):
        return _formato_fecha_hora(dt, fmt, desde_utc=False)

    @app.context_processor
    def inject_globals():
        from flask import request

        if request.endpoint and request.endpoint.startswith("health."):
            return {}

        from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO, modulos_activos_de

        empresa_actual = None
        if current_user.is_authenticated and getattr(current_user, "empresa", None):
            empresa_actual = current_user.empresa
        perm = permission_flags(current_user) if current_user.is_authenticated else permission_flags(
            None
        )
        mods = modulos_activos_de(empresa_actual)
        monedas_act = empresa_actual.monedas_activas if empresa_actual else ["COP"]
        multimoneda = empresa_actual.multimoneda if empresa_actual else False
        session_security = None
        if current_user.is_authenticated:
            from app.session_management import policy_for

            session_security = policy_for(current_user)
        return {
            "app_name": APP_NAME,
            "app_version": app.config["APP_VERSION"],
            "app_tagline": APP_TAGLINE,
            "app_logo_path": APP_LOGO_PATH,
            "app_favicon_path": APP_FAVICON_PATH,
            "empresa_actual": empresa_actual,
            "empresa_logo_url": empresa_logo_url_or_none(empresa_actual),
            "alertas_campana": resumen_alertas_campana(),
            "wo_status_meta": wo_status_meta,
            "machine_status_meta": machine_status_meta,
            "wo_es_editable": wo_es_editable,
            "wo_tipo_meta": wo_tipo_meta,
            "proveedor_tipo_meta": proveedor_tipo_meta,
            "incident_prioridad_meta": incident_prioridad_meta,
            "formato_moneda": formato_moneda,
            "perm": perm,
            "modulos_activos": mods,
            "mod_mantenimiento": MODULO_MANTENIMIENTO in mods,
            "mod_inventario": MODULO_INVENTARIO in mods,
            "monedas_activas": monedas_act,
            "multimoneda": multimoneda,
            "session_security": session_security,
        }

    from app import models  # noqa: F401
    from app.maintenance_execution import models as maintenance_execution_models  # noqa: F401
    from app.maintenance_automation import models as maintenance_automation_models  # noqa: F401
    from app.asset_health import models as asset_health_models  # noqa: F401
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return None
        try:
            raw_id, raw_version = str(user_id).split(":", 1)
            user = db.session.get(User, int(raw_id))
            if user is None or int(raw_version) != int(user.auth_version or 1):
                return None
            return user
        except (TypeError, ValueError):
            return None

    from app.startup import run_startup

    run_startup(app)

    from app import routes
    from app.health_routes import health_bp
    from app.onboarding_routes import onboarding_bp
    from app.inventario_comercial.routes import inv_comercial_bp
    from app.purchasing.routes import purchasing_bp
    from app.maintenance_execution.routes import maintenance_execution_bp
    from app.maintenance_automation.routes import maintenance_automation_bp
    from app.asset_health.routes import asset_health_bp
    from app.tenancy.admin_routes import admin_bp
    from app.tenancy.api_routes import tenancy_api_bp
    from app.tenancy.platform_routes import platform_bp
    from app.brand_book_routes import brand_book_bp, _legacy_bp
    from app.mdl_routes import mdl_bp
    from app.mux_routes import mux_bp, _legacy_ux_bp
    from app.mcm_routes import mcm_bp
    from app.mpa_routes import mpa_bp
    from app.mrl_routes import mrl_bp
    from app.mag_routes import mag_bp
    from app.msd_routes import msd_bp
    from app.mrg_routes import mrg_bp
    from app.mkt_routes import mkt_bp
    from app.mdo_routes import mdo_bp
    from app.openapi_routes import openapi_bp
    from app.docs_routes import docs_bp
    from app.file_storage import storage_bp
    from app.integrations.routes import integrations_bp
    from app.public_api.maintenance import public_maintenance_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(brand_book_bp)
    app.register_blueprint(_legacy_bp)
    app.register_blueprint(mdl_bp)
    app.register_blueprint(mux_bp)
    app.register_blueprint(_legacy_ux_bp)
    app.register_blueprint(mcm_bp)
    app.register_blueprint(mpa_bp)
    app.register_blueprint(mrl_bp)
    app.register_blueprint(mag_bp)
    app.register_blueprint(msd_bp)
    app.register_blueprint(mrg_bp)
    app.register_blueprint(mkt_bp)
    app.register_blueprint(mdo_bp)
    app.register_blueprint(openapi_bp)
    app.register_blueprint(docs_bp)
    from app.docs_access import register_docs_access

    register_docs_access(app)
    app.register_blueprint(storage_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(public_maintenance_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(inv_comercial_bp)
    app.register_blueprint(purchasing_bp)
    app.register_blueprint(maintenance_execution_bp)
    app.register_blueprint(maintenance_automation_bp)
    app.register_blueprint(asset_health_bp)
    app.register_blueprint(tenancy_api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(platform_bp)

    csrf.exempt(tenancy_api_bp)
    csrf.exempt(public_maintenance_bp)
    csrf.exempt(admin_bp)
    csrf.exempt(health_bp)

    from app.cli import register_cli

    register_cli(app)

    return app
