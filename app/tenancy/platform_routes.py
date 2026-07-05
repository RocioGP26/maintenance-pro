"""Panel web de superadministración de plataforma (dueña de Mantis)."""

from __future__ import annotations

import os
from datetime import date
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_user

from app import db, limiter
from app.url_utils import is_safe_redirect
from app.models import Empresa, FacturaEmpresa, User
from app.platform_billing import (
    FACTURA_ESTADO_CHOICES,
    crear_factura_mensual,
    factura_estado_label,
    facturas_empresa,
    kpis_facturacion,
    listar_facturas_platform,
    monto_suscripcion_empresa,
)
from app.subscription_service import marcar_factura_pagada
from app.platform_service import (
    ESTADO_META,
    activos_por_empresa,
    admin_empresa,
    empresa_a_fila,
    estado_choices_platform,
    kpis_platform,
    listar_empresas_platform,
    plan_choices_platform,
    sector_choices_platform,
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
from app.platform_mfa import totp_habilitado, verificar_totp
from app.tenant_activity import ACTIVITY_LABELS, registrar_actividad_tenant, ultima_actividad_empresa

platform_bp = Blueprint("platform", __name__, url_prefix="/platform")

MFA_PENDING_KEY = "platform_mfa_pending"


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
            detalle="Acceso de soporte Mantis (registro auditable)",
        )


def _clave_plataforma_configurada() -> str:
    return os.environ.get("PLATFORM_ADMIN_KEY", "").strip()


def platform_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("platform_admin"):
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
@limiter.limit("5 per 15 minutes", methods=["POST"])
def login():
    clave = _clave_plataforma_configurada()
    if not clave:
        return render_template("platform/login.html", sin_clave=True), 503
    if request.args.get("cancel") == "1":
        session.pop(MFA_PENDING_KEY, None)
        flash("Verificación cancelada.", "info")
        return redirect(url_for("platform.login"))
    if request.method == "POST":
        if request.form.get("action") == "totp":
            if not session.get(MFA_PENDING_KEY):
                flash("La verificación expiró. Vuelve a ingresar la clave de plataforma.", "warning")
                return redirect(url_for("platform.login"))
            if verificar_totp(request.form.get("totp", "")):
                session.pop(MFA_PENDING_KEY, None)
                session["platform_admin"] = True
                session["platform_actor"] = "Soporte Mantis (Plataforma)"
                session.permanent = True
                return _redirect_tras_login_plataforma()
            flash("Código de autenticación incorrecto.", "danger")
            return render_template(
                "platform/login.html",
                sin_clave=False,
                mfa_step=True,
                totp_habilitado=True,
            )

        ingresada = (request.form.get("clave") or "").strip()
        if ingresada and ingresada == clave:
            if totp_habilitado():
                session[MFA_PENDING_KEY] = True
                session.permanent = True
                return render_template(
                    "platform/login.html",
                    sin_clave=False,
                    mfa_step=True,
                    totp_habilitado=True,
                )
            session["platform_admin"] = True
            session["platform_actor"] = "Soporte Mantis (Plataforma)"
            session.permanent = True
            return _redirect_tras_login_plataforma()
        flash("Clave de plataforma incorrecta.", "danger")
    if session.get("platform_admin"):
        return redirect(url_for("platform.empresas"))
    if session.get(MFA_PENDING_KEY) and totp_habilitado():
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
    session.pop("platform_admin", None)
    session.pop(MFA_PENDING_KEY, None)
    session.pop("platform_impersonating", None)
    session.pop("platform_actor", None)
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
    q = request.args.get("q", "")
    filas = listar_empresas_platform(sector=sector, plan=plan, estado=estado, q=q)
    return render_template(
        "platform/empresas.html",
        filas=filas,
        kpis=kpis_platform(filas),
        filtros={"sector": sector, "plan": plan, "estado": estado, "q": q},
        sectores=sector_choices_platform(),
        planes=plan_choices_platform(),
        estados=estado_choices_platform(),
        estado_meta=ESTADO_META,
    )


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
    )


@platform_bp.route("/empresas/<int:id>/facturas/nueva", methods=["POST"])
@platform_login_required
def empresa_nueva_factura(id: int):
    empresa = Empresa.query.get_or_404(id)
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
