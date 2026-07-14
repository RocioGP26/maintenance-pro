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

from app import db, limiter
from app.models import User
from app.landing_service import formato_precio_landing
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
from app.email_service import EmailDeliveryError
from app.email_verification_service import (
    ResendCooldown,
    VerificationStatus,
    is_valid_email,
    issue_verification,
    masked_email,
    send_welcome_email,
    verify_code,
)

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
            if not is_valid_email(email):
                flash("Indica un correo válido para confirmar la cuenta empresarial.", "danger")
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
            if not data["empresa"].get("email"):
                data["empresa"]["email"] = admin_data.get("email", "")
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
            session["pending_email_verification_user_id"] = user.id
            try:
                issue_verification(user)
                flash("Te enviamos un código de verificación de 6 dígitos.", "info")
            except EmailDeliveryError:
                import logging

                logging.getLogger(__name__).exception("No se pudo enviar el código de verificación")
                flash(
                    "La cuenta fue creada, pero no pudimos enviar el correo. "
                    "Revisa la configuración SMTP y usa Reenviar código.",
                    "warning",
                )
            return redirect(url_for("onboarding.verify_email"))

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
        formato_precio_landing=formato_precio_landing,
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


def _pending_verification_user() -> User | None:
    raw_id = session.get("pending_email_verification_user_id")
    if raw_id is None and current_user.is_authenticated:
        raw_id = current_user.id
    try:
        user = db.session.get(User, int(raw_id))
    except (TypeError, ValueError):
        return None
    if user is None or user.empresa is None:
        return None
    return user


def _verified_destination(user: User):
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO, modulos_activos_de

    mods = modulos_activos_de(user.empresa)
    if MODULO_INVENTARIO in mods and MODULO_MANTENIMIENTO not in mods:
        return redirect(url_for("inv_comercial.dashboard_inventario", welcome=1))
    return redirect(url_for("main.dashboard", welcome=1))


@onboarding_bp.route("/onboarding/verificar-correo", methods=["GET", "POST"])
@limiter.limit("10 per 15 minutes", methods=["POST"])
def verify_email():
    user = _pending_verification_user()
    if user is None:
        flash("Inicia sesión para continuar con la verificación.", "warning")
        return redirect(url_for("main.login"))
    if user.empresa.email_verificado:
        login_user(user)
        session.pop("pending_email_verification_user_id", None)
        return _verified_destination(user)

    if request.method == "POST":
        status = verify_code(user, request.form.get("code", ""))
        if status == VerificationStatus.VERIFIED:
            login_user(user)
            session.pop("pending_email_verification_user_id", None)
            session["show_welcome"] = True
            session["show_tour"] = True
            try:
                send_welcome_email(user)
            except EmailDeliveryError:
                import logging

                logging.getLogger(__name__).exception("No se pudo enviar el correo de bienvenida")
            flash(
                f"¡Correo confirmado! Bienvenido a {APP_NAME}, {user.etiqueta()}.",
                "success",
            )
            return _verified_destination(user)
        if status == VerificationStatus.EXPIRED:
            flash("El código expiró. Solicita uno nuevo.", "warning")
        elif status == VerificationStatus.LOCKED:
            flash("Se agotaron los intentos. Solicita un código nuevo.", "danger")
        elif status == VerificationStatus.MISSING:
            flash("No hay un código activo. Solicita uno nuevo.", "warning")
        else:
            flash("Código incorrecto.", "danger")

    return render_template(
        "onboarding/verify_email.html",
        masked_email=masked_email(user.email),
    )


@onboarding_bp.route("/onboarding/reenviar-codigo", methods=["POST"])
@limiter.limit("3 per 15 minutes")
def resend_verification():
    user = _pending_verification_user()
    if user is None:
        flash("Inicia sesión para solicitar un código nuevo.", "warning")
        return redirect(url_for("main.login"))
    if user.empresa.email_verificado:
        return redirect(url_for("main.login"))
    try:
        issue_verification(user, enforce_cooldown=True)
        flash("Enviamos un código nuevo. Revisa también la carpeta de spam.", "info")
    except ResendCooldown as exc:
        flash(f"Espera {exc.seconds} segundos antes de reenviar.", "warning")
    except (EmailDeliveryError, ValueError):
        import logging

        logging.getLogger(__name__).exception("No se pudo reenviar el código de verificación")
        flash("No pudimos enviar el código. Intenta nuevamente más tarde.", "danger")
    return redirect(url_for("onboarding.verify_email"))


@onboarding_bp.route("/onboarding/reiniciar")
def reiniciar():
    _clear_wizard()
    return redirect(url_for("onboarding.wizard"))
