import os

from flask import Flask
from flask_login import LoginManager
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
        models.ensure_machine_tipo_equipo_column()
        models.seed_machine_types_if_empty()
        models.ensure_machines_machine_type_fk()
        models.seed_if_empty()

    from app import routes

    app.register_blueprint(routes.bp)

    return app
