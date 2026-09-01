"""Panel web de superadministración de plataforma (dueña de Roustix)."""

from __future__ import annotations

import hmac
import time
from datetime import date
from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user

from app import db, limiter
from app.url_utils import is_safe_redirect
from app.models import Empresa, FacturaEmpresa, SuscripcionEstado, User
from app.platform_billing import (
    FACTURA_ESTADO_CHOICES,
    crear_factura_mensual,
    factura_estado_label,
    facturas_empresa,
    kpis_facturacion,
    listar_facturas_platform,
    monto_suscripcion_empresa,
)
from app.subscription_service import (
    cambiar_plan_manual,
    marcar_factura_pagada,
    preparar_conversion_comercial,
)
from app.platform_service import (
    ESTADO_META,
    activos_por_empresa,
    admin_empresa,
    empresa_a_fila,
    estado_choices_platform,
    infra_snapshot,
    kpis_platform,
    listar_empresas_platform,
    plan_choices_platform,
    sector_choices_platform,
    tipo_choices_platform,
    usuarios_por_empresa,
)
from app.platform_audit import PLATFORM_AUDIT_LABELS, registrar_auditoria_plataforma
from app.platform_config_service import (
    crear_plan,
    crear_sector,
    guardar_plan,
    guardar_reglas,
    guardar_sector,
    listar_planes_catalogo,
    listar_sectores_catalogo,
    parse_caracteristicas_form,
    plan_a_meta,
    planes_comerciales_piloto,
    planes_claves_validas,
    reglas_para_formulario,
    trial_dias,
)
from app.platform_users_service import (
    ESTADO_USUARIO_CHOICES,
    ROL_USUARIO_CHOICES,
    bloquear_usuario,
    desbloquear_usuario,
    empresas_para_filtro_usuarios,
    generar_password_temporal,
    kpis_usuarios_platform,
    listar_usuarios_platform,
)
from app.platform_mfa import totp_habilitado, totp_requerido, verificar_totp
from app.tenant_activity import ACTIVITY_LABELS, registrar_actividad_tenant, ultima_actividad_empresa

platform_bp = Blueprint("platform", __name__, url_prefix="/platform")

MFA_PENDING_KEY = "platform_mfa_pending"
MFA_PENDING_AT_KEY = "platform_mfa_pending_at"
PLATFORM_STARTED_AT_KEY = "platform_started_at"
PLATFORM_LAST_ACTIVITY_KEY = "platform_last_activity_at"


def _now_epoch() -> int:
    return int(time.time())


def _clear_platform_state() -> None:
    impersonating = bool(session.get("platform_impersonating"))
    for key in (
        "platform_admin",
        "platform_actor",
        "platform_impersonating",
        MFA_PENDING_KEY,
        MFA_PENDING_AT_KEY,
        PLATFORM_STARTED_AT_KEY,
        PLATFORM_LAST_ACTIVITY_KEY,
    ):
        session.pop(key, None)
    if impersonating and current_user.is_authenticated:
        logout_user()


def _audit_platform_security(action: str, detail: str) -> None:
    registrar_auditoria_plataforma(
        action,
        detalle=detail,
        visible_cliente=False,
    )
    db.session.commit()


def _complete_platform_login() -> None:
    now = _now_epoch()
    session.pop(MFA_PENDING_KEY, None)
    session.pop(MFA_PENDING_AT_KEY, None)
    session["platform_admin"] = True
    session["platform_actor"] = "Soporte Roustix (Plataforma)"
    session[PLATFORM_STARTED_AT_KEY] = now
    session[PLATFORM_LAST_ACTIVITY_KEY] = now
    session.permanent = False
    _audit_platform_security("platform_login", "Acceso privilegiado completado")


def _platform_expiration_reason() -> str | None:
    try:
        started = int(session.get(PLATFORM_STARTED_AT_KEY) or 0)
        last_activity = int(session.get(PLATFORM_LAST_ACTIVITY_KEY) or 0)
    except (TypeError, ValueError):
        return "invalid_session"
    if not started or not last_activity:
        return "invalid_session"
    now = _now_epoch()
    idle_seconds = max(1, int(current_app.config.get("PLATFORM_SESSION_IDLE_MINUTES", 15))) * 60
    absolute_seconds = max(1, int(current_app.config.get("PLATFORM_SESSION_ABSOLUTE_MINUTES", 120))) * 60
    if now - started >= absolute_seconds:
        return "absolute_timeout"
    if now - last_activity >= idle_seconds:
        return "idle_timeout"
    return None


def _mfa_pending_expired() -> bool:
    try:
        created_at = int(session.get(MFA_PENDING_AT_KEY) or 0)
    except (TypeError, ValueError):
        return True
    ttl = max(1, int(current_app.config.get("PLATFORM_MFA_PENDING_MINUTES", 5))) * 60
    return not created_at or _now_epoch() - created_at >= ttl


def _iniciar_impersonacion_usuario(user: User) -> None:
    registrar_auditoria_plataforma(
        "impersonate_start",
        empresa_id=user.empresa_id,
        user_id=user.id,
        detalle=f"Impersonación de {user.etiqueta()} (@{user.username})",
    )
    session["platform_impersonating"] = True
    session["platform_admin"] = True
    login_user(user, remember=False)
    if user.empresa_id:
        registrar_actividad_tenant(
            user.empresa_id,
            "impersonate_start",
            user_id=user.id,
            username=user.username,
            detalle="Acceso de soporte Roustix (registro auditable)",
        )


def _clave_plataforma_configurada() -> str:
    return str(current_app.config.get("PLATFORM_ADMIN_KEY") or "").strip()


def platform_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("platform_admin"):
            reason = _platform_expiration_reason()
            if reason:
                _audit_platform_security("platform_session_expired", reason)
                _clear_platform_state()
                flash("La sesión de plataforma expiró por seguridad.", "warning")
                return redirect(url_for("platform.login", expired=reason, next=request.path))
            session[PLATFORM_LAST_ACTIVITY_KEY] = _now_epoch()
            return view(*args, **kwargs)
        if session.get(MFA_PENDING_KEY) and totp_habilitado():
            return redirect(url_for("platform.login", next=request.path))
        return redirect(url_for("platform.login", next=request.path))

    return wrapped


def _redirect_tras_login_plataforma():
    destino = request.args.get("next") or request.form.get("next") or url_for("platform.empresas")
    if not is_safe_redirect(destino, request.host_url):
        destino = url_for("platform.empresas")
    return redirect(destino)


@platform_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per 15 minutes", methods=["POST"])
def login():
    clave = _clave_plataforma_configurada()
    if not clave:
        return render_template("platform/login.html", sin_clave=True), 503
    if totp_requerido() and not totp_habilitado():
        return render_template(
            "platform/login.html",
            sin_clave=False,
            config_error=(
                "PLATFORM_ADMIN_TOTP_SECRET debe estar configurada para habilitar "
                "la superadministración en producción."
            ),
        ), 503

    if session.get("platform_admin"):
        reason = _platform_expiration_reason()
        if reason is None:
            return redirect(url_for("platform.empresas"))
        _audit_platform_security("platform_session_expired", reason)
        _clear_platform_state()
        flash("La sesión de plataforma expiró por seguridad.", "warning")

    if request.args.get("cancel") == "1":
        session.pop(MFA_PENDING_KEY, None)
        session.pop(MFA_PENDING_AT_KEY, None)
        flash("Verificación cancelada.", "info")
        return redirect(url_for("platform.login"))

    if request.method == "POST":
        if request.form.get("action") == "totp":
            if not session.get(MFA_PENDING_KEY) or _mfa_pending_expired():
                session.pop(MFA_PENDING_KEY, None)
                session.pop(MFA_PENDING_AT_KEY, None)
                _audit_platform_security("platform_mfa_expired", "Desafío TOTP expirado")
                flash("La verificación expiró. Vuelve a ingresar la clave de plataforma.", "warning")
                return redirect(url_for("platform.login"))
            if verificar_totp(request.form.get("totp", "")):
                _complete_platform_login()
                return _redirect_tras_login_plataforma()
            _audit_platform_security("platform_mfa_failed", "Código TOTP inválido")
            flash("Código de autenticación incorrecto.", "danger")
            return render_template(
                "platform/login.html",
                sin_clave=False,
                mfa_step=True,
                totp_habilitado=True,
            )

        ingresada = (request.form.get("clave") or "").strip()
        if ingresada and hmac.compare_digest(ingresada, clave):
            if totp_habilitado():
                session[MFA_PENDING_KEY] = True
                session[MFA_PENDING_AT_KEY] = _now_epoch()
                session.permanent = False
                return render_template(
                    "platform/login.html",
                    sin_clave=False,
                    mfa_step=True,
                    totp_habilitado=True,
                )
            _complete_platform_login()
            return _redirect_tras_login_plataforma()
        _audit_platform_security("platform_login_failed", "Clave privilegiada inválida")
        flash("Clave de plataforma incorrecta.", "danger")

    if session.get(MFA_PENDING_KEY) and totp_habilitado():
        if _mfa_pending_expired():
            session.pop(MFA_PENDING_KEY, None)
            session.pop(MFA_PENDING_AT_KEY, None)
        else:
            return render_template(
                "platform/login.html",
                sin_clave=False,
                mfa_step=True,
                totp_habilitado=True,
            )
    return render_template(
        "platform/login.html",
        sin_clave=False,
        mfa_step=False,
        totp_habilitado=totp_habilitado(),
    )


@platform_bp.route("/logout", methods=["POST"])
def logout():
    if session.get("platform_admin"):
        _audit_platform_security("platform_logout", "Cierre voluntario de plataforma")
    _clear_platform_state()
    flash("Sesión de plataforma cerrada.", "info")
    return redirect(url_for("platform.login"))

@platform_bp.route("/")
@platform_login_required
def index():
    return redirect(url_for("platform.empresas"))


@platform_bp.route("/facturacion")
@platform_login_required
def facturacion():
    estado = request.args.get("estado", "")
    q = request.args.get("q", "")
    facturas = listar_facturas_platform(estado=estado, q=q)
    return render_template(
        "platform/facturacion.html",
        facturas=facturas,
        kpis=kpis_facturacion(),
        filtros={"estado": estado, "q": q},
        estados_factura=FACTURA_ESTADO_CHOICES,
        factura_estado_label=factura_estado_label,
    )


@platform_bp.route("/facturacion/<int:factura_id>/pagar", methods=["POST"])
@platform_login_required
def facturacion_pagar(factura_id: int):
    factura = FacturaEmpresa.query.get_or_404(factura_id)
    empresa = factura.empresa
    if empresa and empresa.es_prueba:
        flash("Las empresas de prueba están excluidas de facturación.", "warning")
        return redirect(request.referrer or url_for("platform.facturacion"))
    marcar_factura_pagada(
        factura,
        metodo=request.form.get("metodo", "manual"),
        referencia=request.form.get("referencia", ""),
        notas=request.form.get("notas", ""),
    )
    if empresa:
        registrar_actividad_tenant(
            empresa.id,
            "factura_pagada",
            detalle=f"{factura.numero} — {factura.monto}",
        )
    db.session.commit()
    flash(f"Pago registrado: {factura.numero}.", "success")
    return redirect(request.referrer or url_for("platform.facturacion"))


@platform_bp.route("/empresas")
@platform_login_required
def empresas():
    sector = request.args.get("sector", "")
    plan = request.args.get("plan", "")
    estado = request.args.get("estado", "")
    tipo = request.args.get("tipo", "")
    q = request.args.get("q", "")
    filas = listar_empresas_platform(sector=sector, plan=plan, estado=estado, tipo=tipo, q=q)
    return render_template(
        "platform/empresas.html",
        filas=filas,
        kpis=kpis_platform(filas),
        filtros={"sector": sector, "plan": plan, "estado": estado, "tipo": tipo, "q": q},
        sectores=sector_choices_platform(),
        planes=plan_choices_platform(),
        estados=estado_choices_platform(),
        tipos=tipo_choices_platform(),
        estado_meta=ESTADO_META,
    )


@platform_bp.route("/infraestructura")
@platform_login_required
def infraestructura():
    probe = request.args.get("probe_smtp", "1") != "0"
    return render_template(
        "platform/infraestructura.html",
        infra=infra_snapshot(probe_smtp=probe),
    )


@platform_bp.post("/infraestructura/probar-alerta")
@platform_login_required
@limiter.limit("2 per hour")
def infraestructura_probar_alerta():
    from app.observability import emit_operational_alert

    emitted = emit_operational_alert(
        "operations",
        "controlled_test",
        "Controlled operational alert requested from the Roustix platform panel",
        severity="warning",
        dedupe_key=f"platform_ops_test:{int(time.time())}",
    )
    registrar_auditoria_plataforma(
        "ops_alert_test",
        detalle="Prueba controlada de Sentry y correo operativo.",
        visible_cliente=False,
    )
    db.session.commit()
    flash(
        "Alerta de prueba enviada a los canales configurados."
        if emitted
        else "La alerta fue omitida por la ventana de deduplicación.",
        "success" if emitted else "warning",
    )
    return redirect(url_for("platform.infraestructura", probe_smtp="0"))


@platform_bp.route("/empresas/<int:id>")
@platform_login_required
def empresa_detail(id: int):
    empresa = Empresa.query.get_or_404(id)
    fila = empresa_a_fila(
        empresa,
        activos_map=activos_por_empresa(),
        usuarios_map=usuarios_por_empresa(),
    )
    return render_template(
        "platform/empresa_detail.html",
        fila=fila,
        empresa=empresa,
        estado_meta=ESTADO_META,
        facturas=facturas_empresa(id),
        actividad=ultima_actividad_empresa(id),
        activity_labels=ACTIVITY_LABELS,
        factura_estado_label=factura_estado_label,
        monto_sugerido=monto_suscripcion_empresa(empresa),
        planes_comerciales=planes_comerciales_piloto(),
    )


@platform_bp.route("/empresas/<int:id>/plan", methods=["POST"])
@platform_login_required
def empresa_cambiar_plan(id: int):
    empresa = Empresa.query.get_or_404(id)
    nuevo_key = (request.form.get("plan") or "").strip().lower()
    sub_actual = empresa.plan_activo
    conversion = bool(
        sub_actual
        and sub_actual.estado_ciclo
        in {
            SuscripcionEstado.TRIAL.value,
            SuscripcionEstado.MORA.value,
            SuscripcionEstado.SUSPENDIDA.value,
        }
    )
    try:
        if conversion:
            _sub, factura, anterior_key, changed = preparar_conversion_comercial(
                empresa, nuevo_key
            )
        else:
            _sub, anterior_key, changed = cambiar_plan_manual(empresa, nuevo_key)
            factura = None
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("platform.empresa_detail", id=id))

    if not changed:
        if conversion and factura:
            flash(
                f"La conversión a {plan_a_meta_key(nuevo_key)} ya está preparada; "
                f"la factura {factura.numero} continúa pendiente.",
                "info",
            )
        else:
            flash(f"{empresa.razon_social} ya tiene ese plan activo.", "info")
        return redirect(url_for("platform.empresa_detail", id=id))

    anterior = plan_a_meta_key(anterior_key)
    nuevo = plan_a_meta_key(nuevo_key)
    detalle = (
        f"{anterior} → {nuevo} · conversión comercial; factura {factura.numero} pendiente"
        if factura
        else f"{anterior} → {nuevo} · cambio de plan activo"
    )
    registrar_auditoria_plataforma(
        "plan_change",
        empresa_id=empresa.id,
        detalle=detalle,
        visible_cliente=True,
    )
    registrar_actividad_tenant(
        empresa.id,
        "plan_changed",
        detalle=detalle,
    )
    db.session.commit()
    if factura:
        flash(
            f"Conversión preparada a {nuevo}. La activación ocurrirá al registrar el pago "
            f"de la factura {factura.numero}.",
            "success",
        )
    else:
        flash(f"Plan actualizado: {nuevo}.", "success")
    return redirect(url_for("platform.empresa_detail", id=id))


def plan_a_meta_key(plan_key: str) -> str:
    if plan_key == "sin_plan":
        return "Sin plan"
    from app.platform_config_service import catalogo_plan_meta

    meta = catalogo_plan_meta(plan_key)
    return str(meta.get("short_label") or meta.get("label") or plan_key)


@platform_bp.route("/empresas/<int:id>/storage-addon", methods=["POST"])
@platform_login_required
def empresa_storage_addon(id: int):
    from app.storage_quota import (
        ADDON_STG_2G_LABEL,
        ADDON_STG_2G_MB,
        ADDON_STG_2G_SKU,
        has_addon_stg_2g,
        set_addon_stg_2g,
    )

    empresa = Empresa.query.get_or_404(id)
    accion = (request.form.get("accion") or "").strip().lower()
    active = accion == "activar"
    if accion not in {"activar", "desactivar"}:
        flash("Acción de add-on no válida.", "danger")
        return redirect(url_for("platform.empresa_detail", id=id))

    antes = has_addon_stg_2g(empresa)
    set_addon_stg_2g(empresa, active=active)
    despues = has_addon_stg_2g(empresa)
    if antes == despues:
        flash(
            f"El add-on {ADDON_STG_2G_LABEL} ya estaba "
            f"{'activo' if despues else 'inactivo'} para {empresa.razon_social}.",
            "info",
        )
        return redirect(url_for("platform.empresa_detail", id=id))

    registrar_auditoria_plataforma(
        "storage_addon_activate" if active else "storage_addon_deactivate",
        empresa_id=empresa.id,
        detalle=(
            f"{ADDON_STG_2G_SKU} ({ADDON_STG_2G_LABEL} · {ADDON_STG_2G_MB} MB) "
            f"{'activado' if active else 'desactivado'}."
        ),
        visible_cliente=True,
    )
    db.session.commit()
    flash(
        f"Add-on {ADDON_STG_2G_LABEL} "
        f"{'activado' if active else 'desactivado'} para {empresa.razon_social}. "
        f"Cuota adicional: {empresa.storage_addon_mb} MB.",
        "success",
    )
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/facturas/nueva", methods=["POST"])
@platform_login_required
def empresa_nueva_factura(id: int):
    empresa = Empresa.query.get_or_404(id)
    if empresa.es_prueba:
        flash("Las empresas de prueba están excluidas de facturación.", "warning")
        return redirect(url_for("platform.empresa_detail", id=id))
    try:
        monto = float(request.form.get("monto") or monto_suscripcion_empresa(empresa))
    except (TypeError, ValueError):
        monto = monto_suscripcion_empresa(empresa)
    periodo = (request.form.get("periodo") or "").strip() or date.today().strftime("%Y-%m")
    crear_factura_mensual(empresa, periodo=periodo, monto=monto)
    db.session.commit()
    flash(f"Factura creada para {empresa.razon_social}.", "success")
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/facturas/<int:factura_id>/pagar", methods=["POST"])
@platform_login_required
def empresa_pagar_factura(id: int, factura_id: int):
    empresa = Empresa.query.get_or_404(id)
    if empresa.es_prueba:
        flash("Las empresas de prueba están excluidas de facturación.", "warning")
        return redirect(url_for("platform.empresa_detail", id=id))
    factura = FacturaEmpresa.query.filter_by(id=factura_id, empresa_id=empresa.id).first_or_404()
    marcar_factura_pagada(
        factura,
        metodo=request.form.get("metodo", "manual"),
        referencia=request.form.get("referencia", ""),
        notas=request.form.get("notas", ""),
    )
    registrar_actividad_tenant(
        empresa.id,
        "factura_pagada",
        detalle=f"{factura.numero} — {factura.monto}",
    )
    db.session.commit()
    flash(f"Pago registrado: {factura.numero}.", "success")
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/suspender", methods=["POST"])
@platform_login_required
def empresa_suspender(id: int):
    empresa = Empresa.query.get_or_404(id)
    empresa.suspendida = True
    from app.session_management import revoke_company_sessions

    revoke_company_sessions(empresa.id, reason="empresa_suspendida")
    db.session.commit()
    flash(f"{empresa.razon_social} suspendida.", "warning")
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/reactivar", methods=["POST"])
@platform_login_required
def empresa_reactivar(id: int):
    empresa = Empresa.query.get_or_404(id)
    empresa.suspendida = False
    db.session.commit()
    flash(f"{empresa.razon_social} reactivada.", "success")
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/clasificacion", methods=["POST"])
@platform_login_required
def empresa_clasificacion(id: int):
    empresa = Empresa.query.get_or_404(id)
    es_prueba = request.form.get("es_prueba") == "1"
    if empresa.es_prueba == es_prueba:
        flash("La clasificación de la empresa no cambió.", "info")
        return redirect(url_for("platform.empresa_detail", id=id))
    empresa.es_prueba = es_prueba
    detalle = "Empresa clasificada como prueba" if es_prueba else "Empresa clasificada como cliente"
    registrar_auditoria_plataforma(
        "company_test_classification",
        empresa_id=empresa.id,
        detalle=detalle,
        visible_cliente=False,
    )
    registrar_actividad_tenant(empresa.id, "classification_changed", detalle=detalle)
    db.session.commit()
    flash(f"{empresa.razon_social}: {detalle.lower()}.", "success")
    return redirect(url_for("platform.empresa_detail", id=id))


@platform_bp.route("/empresas/<int:id>/impersonar", methods=["POST"])
@platform_login_required
def empresa_impersonar(id: int):
    empresa = Empresa.query.get_or_404(id)
    admin = admin_empresa(empresa)
    if not admin:
        flash("Esta empresa no tiene un superadministrador activo.", "danger")
        return redirect(url_for("platform.empresa_detail", id=id))
    _iniciar_impersonacion_usuario(admin)
    db.session.commit()
    flash(f"Ingresaste como {admin.username} en {empresa.razon_social}. Quedó registrado en auditoría.", "info")
    return redirect(url_for("main.dashboard"))


@platform_bp.route("/usuarios")
@platform_login_required
def usuarios():
    empresa_id = request.args.get("empresa_id", "")
    rol = request.args.get("rol", "")
    estado = request.args.get("estado", "")
    q = request.args.get("q", "")
    filas = listar_usuarios_platform(empresa_id=empresa_id, rol=rol, estado=estado, q=q)
    temp_password = session.pop("platform_temp_password", None)
    return render_template(
        "platform/usuarios.html",
        filas=filas,
        kpis=kpis_usuarios_platform(),
        filtros={"empresa_id": empresa_id, "rol": rol, "estado": estado, "q": q},
        empresas_filtro=empresas_para_filtro_usuarios(),
        roles_filtro=ROL_USUARIO_CHOICES,
        estados_filtro=ESTADO_USUARIO_CHOICES,
        audit_labels=PLATFORM_AUDIT_LABELS,
        temp_password=temp_password,
    )


@platform_bp.route("/usuarios/<int:user_id>/impersonar", methods=["POST"])
@platform_login_required
def usuario_impersonar(user_id: int):
    if request.form.get("confirmar_auditoria") != "1":
        flash("Debes confirmar que la impersonación queda registrada en auditoría.", "warning")
        return redirect(url_for("platform.usuarios"))
    user = User.query.get_or_404(user_id)
    if not user.empresa_id:
        flash("El usuario no pertenece a una empresa.", "danger")
        return redirect(url_for("platform.usuarios"))
    if user.bloqueado:
        flash("No puedes impersonar un usuario bloqueado.", "warning")
        return redirect(url_for("platform.usuarios"))
    _iniciar_impersonacion_usuario(user)
    db.session.commit()
    flash(f"Impersonando a {user.etiqueta()}. La acción quedó en el log de auditoría.", "info")
    return redirect(url_for("main.dashboard"))


@platform_bp.route("/usuarios/<int:user_id>/reset-password", methods=["POST"])
@platform_login_required
def usuario_reset_password(user_id: int):
    user = User.query.get_or_404(user_id)
    temp = generar_password_temporal()
    user.set_password(temp)
    user.auth_version = int(user.auth_version or 1) + 1
    from app.session_management import revoke_user_sessions

    revoke_user_sessions(user.id, reason="password_reset_platform")
    registrar_auditoria_plataforma(
        "reset_password",
        empresa_id=user.empresa_id,
        user_id=user.id,
        detalle=f"Contraseña restablecida para @{user.username}",
    )
    db.session.commit()
    session["platform_temp_password"] = {
        "username": user.username,
        "nombre": user.etiqueta(),
        "password": temp,
    }
    flash(
        f"Contraseña restablecida para {user.username}. Cópiala ahora; no se volverá a mostrar.",
        "warning",
    )
    return redirect(url_for("platform.usuarios"))


@platform_bp.route("/usuarios/<int:user_id>/bloquear", methods=["POST"])
@platform_login_required
def usuario_bloquear(user_id: int):
    user = User.query.get_or_404(user_id)
    motivo = (request.form.get("motivo") or "").strip()
    bloquear_usuario(user)
    user.auth_version = int(user.auth_version or 1) + 1
    from app.session_management import revoke_user_sessions

    revoke_user_sessions(user.id, reason="usuario_bloqueado")
    registrar_auditoria_plataforma(
        "block_user",
        empresa_id=user.empresa_id,
        user_id=user.id,
        detalle=motivo or f"Usuario @{user.username} bloqueado por plataforma",
    )
    db.session.commit()
    flash(f"{user.etiqueta()} bloqueado. No podrá iniciar sesión.", "warning")
    return redirect(url_for("platform.usuarios"))


@platform_bp.route("/usuarios/<int:user_id>/desbloquear", methods=["POST"])
@platform_login_required
def usuario_desbloquear(user_id: int):
    user = User.query.get_or_404(user_id)
    desbloquear_usuario(user)
    registrar_auditoria_plataforma(
        "unblock_user",
        empresa_id=user.empresa_id,
        user_id=user.id,
        detalle=f"Usuario @{user.username} desbloqueado",
    )
    db.session.commit()
    flash(f"{user.etiqueta()} desbloqueado.", "success")
    return redirect(url_for("platform.usuarios"))


@platform_bp.route("/configuracion")
@platform_login_required
def configuracion():
    tab = request.args.get("tab", "planes")
    if tab not in ("planes", "reglas", "sectores"):
        tab = "planes"
    planes = listar_planes_catalogo()
    return render_template(
        "platform/configuracion.html",
        tab=tab,
        planes=planes,
        planes_meta=[plan_a_meta(p) for p in planes],
        reglas=reglas_para_formulario(),
        sectores=listar_sectores_catalogo(),
        trial_dias=trial_dias(),
        planes_claves=planes_claves_validas(),
    )


@platform_bp.route("/configuracion/planes/<int:plan_id>", methods=["POST"])
@platform_login_required
def configuracion_plan_guardar(plan_id: int):
    data = {
        "label": request.form.get("label"),
        "short_label": request.form.get("short_label"),
        "descripcion": request.form.get("descripcion"),
        "precio_mensual": request.form.get("precio_mensual"),
        "precio_anual": request.form.get("precio_anual"),
        "max_usuarios": request.form.get("max_usuarios"),
        "max_activos": request.form.get("max_activos"),
        "storage_mb": request.form.get("storage_mb"),
        "soporte": request.form.get("soporte"),
        "visible_registro": request.form.get("visible_registro"),
        "destacado": request.form.get("destacado"),
        "caracteristicas": parse_caracteristicas_form(request.form),
    }
    guardar_plan(plan_id, data)
    db.session.commit()
    flash("Plan actualizado.", "success")
    return redirect(url_for("platform.configuracion", tab="planes"))


@platform_bp.route("/configuracion/planes/nuevo", methods=["POST"])
@platform_login_required
def configuracion_plan_nuevo():
    try:
        crear_plan(
            {
                "clave": request.form.get("clave"),
                "label": request.form.get("label"),
                "short_label": request.form.get("short_label"),
                "descripcion": request.form.get("descripcion"),
                "precio_mensual": request.form.get("precio_mensual") or 0,
            }
        )
        db.session.commit()
        flash("Plan creado.", "success")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "danger")
    return redirect(url_for("platform.configuracion", tab="planes"))


@platform_bp.route("/configuracion/reglas", methods=["POST"])
@platform_login_required
def configuracion_reglas_guardar():
    guardar_reglas(
        {
            "trial_dias": request.form.get("trial_dias"),
            "dias_gracia_mora": request.form.get("dias_gracia_mora"),
            "dias_periodo_pago": request.form.get("dias_periodo_pago"),
            "plan_tras_trial": request.form.get("plan_tras_trial"),
            "dias_alerta_mora": request.form.get("dias_alerta_mora"),
        }
    )
    db.session.commit()
    flash("Reglas de trial y mora actualizadas.", "success")
    return redirect(url_for("platform.configuracion", tab="reglas"))


@platform_bp.route("/configuracion/sectores/<int:sector_id>", methods=["POST"])
@platform_login_required
def configuracion_sector_guardar(sector_id: int):
    guardar_sector(
        sector_id,
        {
            "etiqueta": request.form.get("etiqueta"),
            "visible_registro": request.form.get("visible_registro"),
            "activo": request.form.get("activo"),
        },
    )
    db.session.commit()
    flash("Sector actualizado.", "success")
    return redirect(url_for("platform.configuracion", tab="sectores"))


@platform_bp.route("/configuracion/sectores/nuevo", methods=["POST"])
@platform_login_required
def configuracion_sector_nuevo():
    try:
        crear_sector(
            {
                "clave": request.form.get("clave"),
                "etiqueta": request.form.get("etiqueta"),
            }
        )
        db.session.commit()
        flash("Sector agregado.", "success")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "danger")
    return redirect(url_for("platform.configuracion", tab="sectores"))


# Catálogo de documentación interna (suite privada · acceso SuperAdmin)
_INTERNAL_DOC_GROUPS = (
    {
        "title": "Comercial y marketing",
        "docs": (
            {
                "code": "MCM",
                "name": "Manual Comercial",
                "href": "/mcm/",
                "desc": "Playbooks, objeciones y secreto comercial",
            },
            {
                "code": "MKT",
                "name": "Marketing (portal)",
                "href": "/mkt/",
                "desc": "Biblia de mensajes, guiones y estilo",
            },
        ),
    },
    {
        "title": "Producto y diseño",
        "docs": (
            {
                "code": "MDL",
                "name": "Design Language",
                "href": "/mdl/",
                "desc": "Tokens UI y sistema visual interno",
            },
            {
                "code": "MUX",
                "name": "UX / Producto",
                "href": "/mux/",
                "desc": "Flujos UX y criterios de diseño",
            },
            {
                "code": "MRL",
                "name": "Report Language",
                "href": "/mrl/",
                "desc": "Lenguaje de reportes e informes",
            },
            {
                "code": "MRG",
                "name": "Reference Guide (fuente)",
                "href": "/mrg/",
                "desc": "Markdown interno · ALIGN · gaps",
            },
        ),
    },
    {
        "title": "Ingeniería y operaciones",
        "docs": (
            {
                "code": "MPA",
                "name": "Arquitectura",
                "href": "/mpa/",
                "desc": "Infra, tenancy, seguridad y despliegue",
            },
            {
                "code": "DEV",
                "name": "Developer Docs",
                "href": "/docs/developer/README.md",
                "desc": "Handbook, MADR y runbooks",
            },
            {
                "code": "MDO",
                "name": "Ops del portal doc",
                "href": "/mdo/",
                "desc": "Operación de la suite documental",
            },
            {
                "code": "PUB",
                "name": "Publishing",
                "href": "/docs/publishing/README.md",
                "desc": "Blueprint MkDocs / Docusaurus · DevOps",
            },
            {
                "code": "ACCESS",
                "name": "Política de acceso",
                "href": "/docs/ACCESS.md",
                "desc": "Matriz oficial público / privado",
            },
        ),
    },
)


@platform_bp.route("/documentacion")
@platform_login_required
def documentacion():
    """Hub de documentación interna dentro del SuperAdmin Panel."""
    return render_template(
        "platform/documentacion.html",
        doc_groups=_INTERNAL_DOC_GROUPS,
        public_shortcuts=(
            {"name": "MAG · API Guide", "href": "/mag/"},
            {"name": "MSD · Developer Portal", "href": "/msd/"},
            {"name": "Guía de producto", "href": "/guia"},
            {"name": "OpenAPI", "href": "/api/v1/openapi.yaml"},
            {"name": "Índice Docs", "href": "/docs/"},
        ),
    )


@platform_bp.route("/legal")
@platform_login_required
def legal():
    """Catálogo LEG · descarga PDF de borradores (solo SuperAdmin)."""
    from app.public_legal import list_legal_pages

    return render_template(
        "platform/legal.html",
        legal_docs=list_legal_pages(),
    )


@platform_bp.route("/legal/<slug>/pdf")
@platform_login_required
def legal_pdf(slug: str):
    """Descarga PDF de un documento LEG (mismo motor de marca que el paquete piloto)."""
    from io import BytesIO

    from flask import abort, send_file

    from app.legal_pdf import export_legal_pdf
    from app.public_legal import get_legal_page

    if get_legal_page(slug) is None:
        abort(404)
    try:
        content, filename = export_legal_pdf(slug)
    except (FileNotFoundError, ValueError):
        abort(404)
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@platform_bp.route("/comercial")
@platform_login_required
def comercial():
    """Catálogo COM · descarga PDF de planes, add-ons y piloto."""
    from app.com_docs import list_com_pages

    return render_template(
        "platform/comercial.html",
        com_docs=list_com_pages(),
    )


@platform_bp.route("/comercial/<slug>/pdf")
@platform_login_required
def com_pdf(slug: str):
    """Descarga PDF de un documento COM."""
    from io import BytesIO

    from flask import abort, send_file

    from app.com_docs import get_com_page
    from app.legal_pdf import export_com_pdf

    if get_com_page(slug) is None:
        abort(404)
    try:
        content, filename = export_com_pdf(slug)
    except (FileNotFoundError, ValueError):
        abort(404)
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
