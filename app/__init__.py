import os

from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-mantenimiento-pro")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "mantenimiento.db"),
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.tenancy.middleware import register_tenancy_middleware

    register_tenancy_middleware(app)

    from app.branding import APP_LOGO_PATH, APP_NAME, APP_TAGLINE, empresa_logo_url_or_none

    from app.money import formato_moneda
    from app.models import machine_status_meta, wo_es_editable, wo_status_meta, wo_tipo_meta
    from app.alertas_service import resumen_alertas_campana
    from app.permissions import permission_flags

    app.jinja_env.globals["wo_status_meta"] = wo_status_meta
    app.jinja_env.globals["machine_status_meta"] = machine_status_meta
    app.jinja_env.globals["formato_moneda"] = formato_moneda
    app.jinja_env.globals["wo_es_editable"] = wo_es_editable
    app.jinja_env.globals["wo_tipo_meta"] = wo_tipo_meta

    from app.custom_fields import seccion_campos_cuatro_por_fila

    app.jinja_env.filters["cuatro_por_fila"] = seccion_campos_cuatro_por_fila

    @app.context_processor
    def inject_globals():
        empresa_actual = None
        if current_user.is_authenticated and getattr(current_user, "empresa", None):
            empresa_actual = current_user.empresa
        perm = permission_flags(current_user) if current_user.is_authenticated else permission_flags(
            None
        )
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
            "formato_moneda": formato_moneda,
            "perm": perm,
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

    from app import routes
    from app.onboarding_routes import onboarding_bp
    from app.tenancy.admin_routes import admin_bp
    from app.tenancy.api_routes import tenancy_api_bp

    app.register_blueprint(routes.bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(tenancy_api_bp)
    app.register_blueprint(admin_bp)

    return app
