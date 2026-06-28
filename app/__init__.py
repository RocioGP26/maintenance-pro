import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[], storage_uri="memory://")


def _is_production_env() -> bool:
    env = (os.environ.get("FLASK_ENV") or os.environ.get("ENV") or "").strip().lower()
    return env == "production"


def _normalize_database_url(url: str) -> str:
    """Render/Supabase entregan postgres://; SQLAlchemy 2 + psycopg v3 usa postgresql+psycopg://."""
    raw = (url or "").strip()
    if not raw:
        return raw
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql+psycopg://", 1)
    if raw.startswith("postgresql://") and "+" not in raw.split("://", 1)[0]:
        return raw.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw


def create_app():
    load_dotenv()
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    secret = os.environ.get("SECRET_KEY", "").strip()
    if not secret:
        if _is_production_env():
            raise RuntimeError(
                "SECRET_KEY debe estar definida en producción (FLASK_ENV=production)."
            )
        secret = "dev-mantenimiento-pro"
    app.config["SECRET_KEY"] = secret
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if _is_production_env():
        app.config["SESSION_COOKIE_SECURE"] = True
    database_url = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "mantenimiento.db"),
    )

    print("=" * 80)
    print("DATABASE_URL:")
    print(database_url)
    print("-" * 80)
    print("NORMALIZADA:")
    print(_normalize_database_url(database_url))
    print("=" * 80)

    app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_database_url(database_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

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

    if _is_production_env() and not os.environ.get("DATABASE_URL", "").strip():
        import logging

        logging.getLogger(__name__).warning(
            "DATABASE_URL no está configurada: se usa SQLite local. "
            "En Render los datos se pierden al reiniciar; conecta Supabase/PostgreSQL."
        )

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

    app.jinja_env.filters["cuatro_por_fila"] = seccion_campos_cuatro_por_fila
    app.jinja_env.globals["password_requirements"] = PASSWORD_REQUIREMENTS_TEXT

    @app.context_processor
    def inject_globals():
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

    with app.app_context():
        db.create_all()
        models.ensure_saas_schema()
        models.ensure_machine_tipo_equipo_column()
        models.ensure_machine_types_sector_column()
        models.seed_machine_types_if_empty()
        models.ensure_machines_machine_type_fk()
        models.seed_if_empty()
        from app.work_order_status import sincronizar_estados_ordenes

        sincronizar_estados_ordenes()
        from app.subscription_service import backfill_estado_ciclo_suscripciones, verificar_vencimientos

        backfill_estado_ciclo_suscripciones()
        verificar_vencimientos()
        from app.platform_config_service import ensure_platform_config

        ensure_platform_config()

    from app import routes
    from app.onboarding_routes import onboarding_bp
    from app.inventario_comercial.routes import inv_comercial_bp
    from app.tenancy.admin_routes import admin_bp
    from app.tenancy.api_routes import tenancy_api_bp
    from app.tenancy.platform_routes import platform_bp

    app.register_blueprint(routes.bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(inv_comercial_bp)
    app.register_blueprint(tenancy_api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(platform_bp)

    csrf.exempt(tenancy_api_bp)
    csrf.exempt(admin_bp)

    return app
