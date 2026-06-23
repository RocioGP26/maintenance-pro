"""Asistente de registro y configuración inicial."""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user

from app import db
from app.models import User
from app.landing_service import formato_precio_landing
from app.platform_config_service import planes_para_registro, sectores_para_registro
from app.sector_templates import normalizar_sector
from app.branding import APP_NAME
from app.onboarding_service import completar_onboarding
from app.onboarding_session import clear_onboarding_password, pop_onboarding_password, store_onboarding_password
from app.password_policy import validar_password

onboarding_bp = Blueprint("onboarding", __name__)

STEPS = (
    ("empresa", "Tu empresa"),
    ("admin", "Administrador"),
    ("sede", "Sede principal"),
    ("plan", "Plan de servicio"),
)


def _wizard_data() -> dict:
    return session.setdefault("onboarding_wizard", {})


def _clear_wizard() -> None:
    session.pop("onboarding_wizard", None)
    session.pop("onboarding_step", None)
    clear_onboarding_password()


@onboarding_bp.route("/onboarding", methods=["GET", "POST"])
def wizard():
    if current_user.is_authenticated and current_user.onboarding_completado:
        return redirect(url_for("main.dashboard"))

    step = int(session.get("onboarding_step", 1))
    data = _wizard_data()
    prompt = (request.args.get("prompt") or "").strip()
    if prompt:
        session["onboarding_prompt"] = prompt

    if request.method == "POST":
        action = request.form.get("action", "next")
        if action == "back" and step > 1:
            session["onboarding_step"] = step - 1
            return redirect(url_for("onboarding.wizard"))

        if step == 1:
            sector = normalizar_sector(request.form.get("sector"))
            data["empresa"] = {
                "razon_social": request.form.get("razon_social", "").strip(),
                "nit": request.form.get("nit", "").strip(),
                "direccion": request.form.get("direccion", "").strip(),
                "ciudad": request.form.get("ciudad", "").strip(),
                "pais": request.form.get("pais", "Colombia").strip(),
                "sector": sector,
                "email": request.form.get("email_empresa", "").strip(),
                "telefono": request.form.get("telefono_empresa", "").strip(),
                "moneda": request.form.get("moneda", "COP").strip(),
                "zona_horaria": request.form.get("zona_horaria", "America/Bogota").strip(),
            }
            if not data["empresa"]["razon_social"]:
                flash("La razón social es obligatoria.", "danger")
                return redirect(url_for("onboarding.wizard"))
            session["onboarding_step"] = 2

        elif step == 2:
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")
            if not username or not password:
                flash("Usuario y contraseña son obligatorios.", "danger")
                return redirect(url_for("onboarding.wizard"))
            if password != password2:
                flash("Las contraseñas no coinciden.", "danger")
                return redirect(url_for("onboarding.wizard"))
            err_pwd = validar_password(password)
            if err_pwd:
                flash(err_pwd, "danger")
                return redirect(url_for("onboarding.wizard"))
            if User.query.filter_by(username=username).first():
                flash("Ese nombre de usuario ya está en uso.", "danger")
                return redirect(url_for("onboarding.wizard"))
            data["admin"] = {
                "username": username,
                "email": email,
                "nombre": request.form.get("nombre", "").strip(),
                "telefono": request.form.get("telefono", "").strip(),
            }
            store_onboarding_password(password)
            session["onboarding_step"] = 3

        elif step == 3:
            sede = request.form.get("sede_nombre", "").strip() or "Sede principal"
            data["sede_nombre"] = sede
            session["onboarding_step"] = 4

        elif step == 4:
            # Solo trial en registro público; planes de pago tras facturación confirmada.
            plan = "trial"
            admin_data = dict(data.get("admin") or {})
            password = pop_onboarding_password()
            if not password:
                flash(
                    "La sesión de registro expiró. Vuelve al paso de administrador e indica tu contraseña.",
                    "danger",
                )
                session["onboarding_step"] = 2
                return redirect(url_for("onboarding.wizard"))
            admin_data["password"] = password
            try:
                user, empresa = completar_onboarding(
                    data["empresa"],
                    admin_data,
                    data.get("sede_nombre", "Sede principal"),
                    plan,
                )
            except Exception:
                db.session.rollback()
                flash("No se pudo completar el registro. Intenta de nuevo.", "danger")
                return redirect(url_for("onboarding.wizard"))

            _clear_wizard()
            login_user(user)
            session["show_welcome"] = True
            session["show_tour"] = True
            flash(f"¡Bienvenido a {APP_NAME}, {user.etiqueta()}!", "success")
            return redirect(url_for("main.dashboard", welcome=1))

        session.modified = True
        return redirect(url_for("onboarding.wizard"))

    step = int(session.get("onboarding_step", 1))
    return render_template(
        "onboarding/wizard.html",
        step=step,
        steps=STEPS,
        data=data,
        sectores=sectores_para_registro(),
        planes=planes_para_registro(),
        total_steps=len(STEPS),
        formato_precio_landing=formato_precio_landing,
        sales_prompt=session.get("onboarding_prompt", ""),
    )


@onboarding_bp.route("/onboarding/reiniciar")
def reiniciar():
    _clear_wizard()
    return redirect(url_for("onboarding.wizard"))
