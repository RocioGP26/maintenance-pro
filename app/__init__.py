from dotenv import load_dotenv
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
    load_dotenv()
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

    from app.tenancy.middleware import register_tenancy_middleware

    register_tenancy_middleware(app)

    from app.branding import APP_LOGO_PATH, APP_NAME, APP_TAGLINE, empresa_logo_url_or_none

    from app.money import formato_moneda
    from app.models import machine_status_meta, proveedor_tipo_meta, incident_prioridad_meta, wo_es_editable, wo_status_meta, wo_tipo_meta
    from app.alertas_service import resumen_alertas_campana
    from app.permissions import permission_flags

    app.jinja_env.globals["wo_status_meta"] = wo_status_meta
    app.jinja_env.globals["machine_status_meta"] = machine_status_meta
    app.jinja_env.globals["formato_moneda"] = formato_moneda
    app.jinja_env.globals["wo_es_editable"] = wo_es_editable
    app.jinja_env.globals["wo_tipo_meta"] = wo_tipo_meta
    app.jinja_env.globals["proveedor_tipo_meta"] = proveedor_tipo_meta
    app.jinja_env.globals["incident_prioridad_meta"] = incident_prioridad_meta

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
        return {
            "app_name": APP_NAME,
            "app_tagline": APP_TAGLINE,
            "app_logo_path": APP_LOGO_PATH,
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
        }

    from app import models  # noqa: F401
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return None
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    from app.startup import run_startup

    run_startup(app)

    from app import routes
    from app.health_routes import health_bp
    from app.onboarding_routes import onboarding_bp
    from app.inventario_comercial.routes import inv_comercial_bp
    from app.tenancy.admin_routes import admin_bp
    from app.tenancy.api_routes import tenancy_api_bp
    from app.tenancy.platform_routes import platform_bp
    from app.brand_book_routes import brand_book_bp, _legacy_bp
    from app.mdl_routes import mdl_bp
    from app.mux_routes import mux_bp, _legacy_ux_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(routes.bp)
    app.register_blueprint(brand_book_bp)
    app.register_blueprint(_legacy_bp)
    app.register_blueprint(mdl_bp)
    app.register_blueprint(mux_bp)
    app.register_blueprint(_legacy_ux_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(inv_comercial_bp)
    app.register_blueprint(tenancy_api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(platform_bp)

    csrf.exempt(tenancy_api_bp)
    csrf.exempt(admin_bp)
    csrf.exempt(health_bp)

    from app.cli import register_cli

    register_cli(app)

    return app
