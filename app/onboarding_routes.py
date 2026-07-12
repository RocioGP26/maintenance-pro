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
from app.platform_config_service import planes_para_registro, sectores_para_registro
from app.currency import monedas_desde_modo_venezuela
from app.locale_options import (
    MODO_MONEDA_TRES,
    MONEDAS_ONBOARDING,
    NOTA_MONEDA_VENEZUELA,
    PAISES_ONBOARDING,
    ZONAS_HORARIA_ONBOARDING,
    defaults_pais_preset,
    monedas_para_pais,
    pais_preset_por_nombre,
    paises_para_onboarding_json,
)
from app.money import normalizar_moneda
from app.modules import MODULO_META, normalizar_modulos
from app.sector_templates import normalizar_sector
from app.branding import APP_NAME
from app.landing_service import public_page_context
from app.onboarding_service import completar_onboarding
from app.onboarding_session import clear_onboarding_password, pop_onboarding_password, store_onboarding_password
from app.password_policy import validar_password
from app.user_service import normalizar_username

onboarding_bp = Blueprint("onboarding", __name__)

STEPS = (
    ("empresa", "Empresa"),
    ("admin", "Administrador"),
    ("sede", "Sede y datos"),
    ("plan", "Módulos y plan"),
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
            sector_raw = request.form.get("sector", "").strip()
            pais_preset = (request.form.get("pais_preset") or "colombia").strip().lower()
            pais_defaults = defaults_pais_preset(pais_preset)
            if pais_preset == "otro":
                pais_nombre = request.form.get("pais_otro", "").strip()
            else:
                pais_nombre = pais_defaults["pais"]
            moneda = normalizar_moneda(
                request.form.get("moneda"), pais_defaults["moneda"]
            )
            modo_moneda_ve = request.form.get("modo_moneda_ve", "una").strip().lower()
            if pais_preset == "venezuela" and modo_moneda_ve == MODO_MONEDA_TRES:
                monedas_activas = monedas_desde_modo_venezuela(MODO_MONEDA_TRES, moneda)
                moneda = normalizar_moneda(request.form.get("moneda_ref") or moneda, "USD")
            else:
                monedas_activas = monedas_desde_modo_venezuela("una", moneda)
            zona_horaria = (request.form.get("zona_horaria") or pais_defaults["zona_horaria"]).strip()
            data["empresa"] = {
                "razon_social": request.form.get("razon_social", "").strip(),
                "nit": request.form.get("nit", "").strip(),
                "direccion": request.form.get("direccion", "").strip(),
                "ciudad": request.form.get("ciudad", "").strip(),
                "pais": pais_nombre,
                "pais_preset": pais_preset,
                "pais_otro": request.form.get("pais_otro", "").strip(),
                "sector": sector_raw,
                "email": request.form.get("email_empresa", "").strip(),
                "telefono": request.form.get("telefono_empresa", "").strip(),
                "moneda": moneda,
                "monedas_activas": monedas_activas,
                "modo_moneda_ve": modo_moneda_ve,
                "zona_horaria": zona_horaria,
            }
            if not data["empresa"]["razon_social"]:
                flash("La razón social es obligatoria.", "danger")
                session.modified = True
                return redirect(url_for("onboarding.wizard"))
            if not sector_raw:
                flash("Selecciona el tipo de negocio.", "danger")
                session.modified = True
                return redirect(url_for("onboarding.wizard"))
            if pais_preset == "otro" and not pais_nombre:
                flash("Indica el nombre del país.", "danger")
                session.modified = True
                return redirect(url_for("onboarding.wizard"))
            if not pais_preset or pais_preset not in {p[0] for p in PAISES_ONBOARDING}:
                flash("Selecciona el país.", "danger")
                session.modified = True
                return redirect(url_for("onboarding.wizard"))
            sector = normalizar_sector(sector_raw)
            data["empresa"]["sector"] = sector
            if sector == "comercio":
                data["modulos_preset"] = "inventario"
            session["onboarding_step"] = 2

        elif step == 2:
            username = normalizar_username(request.form.get("username"))
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            password2 = request.form.get("password2", "")
            if not username or not password:
                flash("Usuario y contraseña son obligatorios.", "danger")
                return redirect(url_for("onboarding.wizard"))
            if len(username) < 3:
                flash("El usuario debe tener al menos 3 caracteres.", "danger")
                return redirect(url_for("onboarding.wizard"))
            if password != password2:
                flash("Las contraseñas no coinciden.", "danger")
                return redirect(url_for("onboarding.wizard"))
            err_pwd = validar_password(password)
            if err_pwd:
                flash(err_pwd, "danger")
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
            from app.inventario_comercial.service import modulos_desde_preset

            preset = request.form.get("modulos_preset", "mantenimiento")
            modulos = modulos_desde_preset(preset)
            # Compatibilidad con checkboxes individuales si se envían
            if request.form.getlist("modulos"):
                modulos = normalizar_modulos(request.form.getlist("modulos"))
            if not modulos:
                flash("Selecciona al menos un módulo (Mantenimiento, Inventario o Ambos).", "danger")
                return redirect(url_for("onboarding.wizard"))
            data["modulos"] = modulos
            data["modulos_preset"] = preset
            if preset == "inventario" and data.get("empresa"):
                if (data["empresa"].get("sector") or "manufactura") == "manufactura":
                    data["empresa"]["sector"] = "comercio"
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
                    data.get("modulos"),
                )
            except Exception as exc:
                import logging

                db.session.rollback()
                logging.getLogger(__name__).exception("Error al completar onboarding")
                msg = "No se pudo completar el registro. Intenta de nuevo."
                err = str(getattr(exc, "orig", exc))
                if "monedas_activas_json" in err or "modulos_activos_json" in err:
                    msg = (
                        "Falta actualizar la base de datos. Detén y reinicia la aplicación, "
                        "luego intenta de nuevo."
                    )
                elif "uq_user_empresa_username" in err or "UNIQUE constraint failed: users" in err:
                    msg = "Ese nombre de usuario ya está en uso en esta empresa."
                    session["onboarding_step"] = 2
                flash(msg, "danger")
                return redirect(url_for("onboarding.wizard"))

            _clear_wizard()
            login_user(user)
            session["show_welcome"] = True
            session["show_tour"] = True
            flash(
                f"¡Bienvenido a {APP_NAME}, {user.etiqueta()}! "
                f"Tu prueba gratuita de {public_page_context()['trial_dias']} días comenzó.",
                "success",
            )
            from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO

            mods = data.get("modulos") or []
            if MODULO_INVENTARIO in mods and MODULO_MANTENIMIENTO not in mods:
                return redirect(url_for("inv_comercial.dashboard_inventario", welcome=1))
            return redirect(url_for("main.dashboard", welcome=1))

        session.modified = True
        return redirect(url_for("onboarding.wizard"))

    emp = data.get("empresa") or {}
    if emp.get("pais_preset"):
        pais_preset_ctx = emp["pais_preset"]
    elif emp.get("pais"):
        pais_preset_ctx = pais_preset_por_nombre(emp["pais"])
    else:
        pais_preset_ctx = ""

    step = int(session.get("onboarding_step", 1))
    pub = public_page_context()
    return render_template(
        "onboarding/wizard.html",
        step=step,
        steps=STEPS,
        data=data,
        sectores=sectores_para_registro(),
        planes=planes_para_registro(),
        total_steps=len(STEPS),
        sales_prompt=session.get("onboarding_prompt", ""),
        modulos_meta=MODULO_META,
        modulos_seleccionados=data.get("modulos") or ["mantenimiento"],
        modulos_preset=data.get("modulos_preset", "mantenimiento"),
        paises_onboarding=PAISES_ONBOARDING,
        monedas_onboarding=MONEDAS_ONBOARDING,
        zonas_onboarding=ZONAS_HORARIA_ONBOARDING,
        paises_onboarding_json=paises_para_onboarding_json(),
        pais_preset=pais_preset_ctx,
        monedas_pais=monedas_para_pais(pais_preset_ctx or "colombia"),
        nota_moneda_venezuela=NOTA_MONEDA_VENEZUELA,
        modo_moneda_ve=(data.get("empresa") or {}).get("modo_moneda_ve", "una"),
        trial_dias=pub["trial_dias"],
        cta_final=pub["cta_final"],
        brand_slogan=pub["brand_slogan"],
    )


@onboarding_bp.route("/onboarding/reiniciar")
def reiniciar():
    _clear_wizard()
    return redirect(url_for("onboarding.wizard"))
