from datetime import date
import json
import math
import os
import re
import unicodedata
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Any, List, Optional, Tuple
from uuid import UUID, uuid4

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import and_, false, func, or_
from sqlalchemy.exc import IntegrityError

from app import db, limiter
from app.url_utils import is_safe_redirect
from app.password_policy import validar_password
from app.user_service import username_disponible
from app.branding import APP_LOGO_PATH, empresa_logo_url_or_none, normalizar_logo_empresa
from app.permissions import (
    CONFIG_ENDPOINT_PREFIX,
    CREATE_GET_ENDPOINTS,
    DELETE_ENDPOINTS,
    EQUIPO_MUTATION_ENDPOINTS,
    EQUIPO_ENDPOINTS,
    USER_ROLE_LABELS,
    USUARIO_POST_ENDPOINTS,
    UserRole,
    can_assign_role,
    can_create,
    can_create_work_order,
    can_delete,
    can_edit,
    can_manage_config,
    can_manage_equipo,
    can_manage_incidents,
    can_report_incident,
    is_requester,
    normalize_rol,
    roles_for_select,
    role_help_map,
)
from app.custom_fields import (
    CAMPO_ENTIDAD_ACTIVO,
    CAMPO_ENTIDAD_EQUIPO,
    CAMPO_ENTIDADES,
    CAMPO_TIPOS,
    CAMPO_TIPOS_VALIDOS,
    TEXTO_TAMANOS,
    categorias_ids_a_json,
    clave_campo_unica,
    etiqueta_categorias_campo,
    opciones_a_texto_form,
    parse_categorias_form,
    parse_opciones_texto,
    parse_texto_tamano_form,
    slugify_campo_clave,
    TIPOS_CON_OPCIONES,
    valor_campo_desde_form,
)
from app.dashboard_kpis import build_plant_kpi_cards
from app.models import (
    ActivoCampoValor,
    CampoPersonalizado,
    Empresa,
    Incident,
    IncidentDiagnosis,
    IncidentHistory,
    IncidentEstado,
    INCIDENT_ESTADO_LABELS,
    INCIDENT_AREAS_BASE,
    INCIDENT_PRIORIDADES,
    INCIDENT_TIPOS,
    IncidentPrioridad,
    incident_prioridad_meta,
    IndustrialSector,
    Machine,
    MachineStatus,
    MachineType,
    PLAN_CATALOG,
    PlanSuscripcion,
    SECTOR_LABELS,
    Sede,
    MachineMonthlyPlan,
    SparePart,
    SparePartEntry,
    Proveedor,
    PROVEEDOR_TIPOS_VALIDOS,
    ProveedorTipo,
    Technician,
    UsuarioCampoValor,
    User,
    WORK_ORDER_PRIORITIES,
    WorkOrder,
    WorkOrderEjecucionTipo,
    WorkOrderJornada,
    WorkOrderInforme,
    WorkOrderRepuesto,
    WorkOrderStatus,
    WorkOrderType,
    WORK_ORDER_TERMINAL_STATUSES,
    WORK_ORDER_PENDING_STATUSES,
    wo_es_editable,
    wo_status_meta,
    wo_tipo_meta,
    proveedor_tipo_meta,
    machine_status_meta,
)
from app.asset_standard import (
    ACTIVO_SECCIONES,
    ACTIVO_SECCION_ICONO_DEFAULT,
    ACTIVO_SECCION_ICONOS,
    ACTIVO_SECCION_KEYS,
    FRECUENCIA_BASE_CHOICES,
    MANTENIMIENTO_TIPOS,
    etiqueta_seccion_campo,
    etiqueta_seccion_campo_con_ancla,
    es_seccion_estandar,
    normalizar_seccion_ancla,
    normalizar_seccion_campo,
    calcular_garantia_hasta,
    registro_flags_checked,
    registro_flags_from_form,
    tipos_mantenimiento_from_form,
    tipos_mantenimiento_list,
)
from app.sector_service import (
    campos_para_equipo,
    campos_por_seccion_estructurado,
    ancla_de_seccion_personalizada,
    categorias_de_seccion_personalizada,
    secciones_custom_por_ancla,
    secciones_personalizadas_empresa,
    campos_para_tipo,
    crear_plantilla_sector,
    ensure_empresa_sector_setup,
    get_plantilla_dashboard,
    valores_campos_map,
    valores_campos_usuario_map,
    responsables_display_por_maquinas,
)
from app.sector_templates import (
    CRITICIDAD_CHOICES,
    normalizar_sector,
)
from app.planificacion_mensual import (
    MESES_PLANEACION,
    max_horas_mes,
    mes_anterior,
    parse_mes_anio,
)
from app.preventive_maintenance import (
    PREVENTIVE_FREQUENCY_UNITS,
    aplicar_preventivo_a_orden,
    crear_programacion_preventiva_anio,
    frecuencia_label,
    parse_frecuencia_form,
)
from app.money import (
    MONEDAS_EMPRESA,
    MONEDAS_SOPORTADAS,
    formatear_monto_sin_simbolo,
    normalizar_moneda,
    parsear_monto_form,
    simbolo_moneda_input,
)
from app.wo_numbering import asignar_numero_ot
from app.work_time import (
    combinar_fecha_hora,
    datetime_local_input,
    formatear_duracion,
    minutos_a_horas_minutos,
    parse_datetime_local,
    total_minutos_jornadas,
    wo_tiempo_gastado_minutos,
)

EMPRESA_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ACTIVO_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ZONAS_EMPRESA = (
    ("America/Bogota", "América / Bogotá"),
    ("America/Mexico_City", "América / Ciudad de México"),
    ("America/Lima", "América / Lima"),
    ("America/Santiago", "América / Santiago"),
)

bp = Blueprint("main", __name__)

MESES_CORTO = (
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
)


def _is_safe_url(target: str) -> bool:
    return is_safe_redirect(target, request.host_url)


def _current_empresa_id() -> Optional[int]:
    from app.tenancy.context import current_empresa_id

    return current_empresa_id()


def _filter_empresa(query, model=Machine):
    eid = _current_empresa_id()
    if eid and hasattr(model, "empresa_id"):
        return query.filter(model.empresa_id == eid)
    if hasattr(model, "empresa_id"):
        return query.filter(false())
    return query


def _validar_machine_id_tenant(machine_id: int) -> Tuple[Optional[Machine], Optional[str]]:
    if not machine_id:
        return None, "Selecciona un equipo válido."
    m = _filter_empresa(Machine.query.filter_by(id=machine_id), Machine).first()
    if not m:
        return None, "El equipo seleccionado no pertenece a tu empresa."
    return m, None


def _validar_technician_id_tenant(tech_id: Optional[int], label: str = "técnico") -> Optional[str]:
    if tech_id is None:
        return None
    t = _filter_empresa(Technician.query.filter_by(id=tech_id), Technician).first()
    if not t:
        return f"El {label} seleccionado no pertenece a tu empresa."
    return None


@bp.before_request
def _require_login():
    ep = request.endpoint or ""
    if ep.startswith("onboarding.") or ep in ("main.login", "main.index", "main.faq", "main.demo", "main.contacto", "main.recursos"):
        return
    if not current_user.is_authenticated:
        return redirect(url_for("main.login", next=request.url))
    if not current_user.onboarding_completado:
        return redirect(url_for("onboarding.wizard"))


@bp.before_request
def _enforce_role_permissions():
    """Aplica permisos por rol en rutas de escritura y formularios."""
    ep = request.endpoint or ""
    if ep.startswith("onboarding.") or ep in ("main.login", "main.index", "main.faq", "main.demo", "main.contacto", "main.recursos"):
        return
    if not current_user.is_authenticated:
        return

    method = request.method

    if ep.startswith(CONFIG_ENDPOINT_PREFIX):
        if method in ("GET", "POST") and not can_manage_config(current_user):
            flash("Solo el superadministrador puede acceder a la configuración.", "warning")
            return redirect(url_for("main.dashboard"))

    if method == "GET":
        if ep in CREATE_GET_ENDPOINTS and not can_create(current_user):
            flash("No tienes permiso para crear registros.", "warning")
            return redirect(url_for("main.dashboard"))
        if ep in EQUIPO_ENDPOINTS and not can_manage_equipo(current_user):
            flash("Solo los administradores pueden gestionar el equipo de trabajo.", "warning")
            return redirect(url_for("main.dashboard"))
        if ep in EQUIPO_MUTATION_ENDPOINTS and not can_manage_equipo(current_user):
            flash("No tienes permiso para gestionar el equipo.", "warning")
            return redirect(url_for("main.equipo_list"))
        return

    if method != "POST":
        return

    if ep in USUARIO_POST_ENDPOINTS:
        return

    # Reportar una incidencia es una creación autorizada para Solicitantes y
    # demás roles operativos; no concede permiso para modificar otros registros.
    if ep == "main.incidencia" and can_report_incident(current_user):
        return

    if normalize_rol(current_user.rol) == UserRole.USUARIO.value:
        flash("Tu rol solo permite consultar información.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))

    if ep in EQUIPO_MUTATION_ENDPOINTS and not can_manage_equipo(current_user):
        flash("No tienes permiso para gestionar el equipo.", "warning")
        return redirect(url_for("main.equipo_list"))

    if ep in DELETE_ENDPOINTS and not can_delete(current_user):
        flash("No tienes permiso para eliminar registros.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))

    if ep in CREATE_GET_ENDPOINTS and not can_create(current_user):
        flash("No tienes permiso para crear registros.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))

    if not can_edit(current_user):
        flash("No tienes permiso para modificar registros.", "warning")
        return redirect(request.referrer or url_for("main.dashboard"))


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per 15 minutes", methods=["POST"])
def login():
    if current_user.is_authenticated:
        if not current_user.onboarding_completado:
            return redirect(url_for("onboarding.wizard"))
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        empresa_slug = request.form.get("empresa_slug", "").strip()
        password = request.form.get("password", "")
        remember_requested = bool(request.form.get("remember"))
        from app.user_service import buscar_usuario_login, mensaje_login_ambiguo

        user = buscar_usuario_login(username, empresa_slug=empresa_slug or None)
        if user is None and username.strip():
            candidatos = User.query.filter_by(username=username.strip().lower()).count()
            if candidatos > 1:
                flash(mensaje_login_ambiguo(username), "danger")
                return render_template("login.html")
        if user is not None and user.check_password(password):
            if user.bloqueado or not user.activo:
                flash("Usuario o contraseña incorrectos.", "danger")
            else:
                if user.empresa and not user.empresa.email_verificado:
                    from app.email_service import EmailDeliveryError
                    from app.email_verification_service import ensure_verification

                    session["pending_email_verification_user_id"] = user.id
                    try:
                        ensure_verification(user)
                    except (EmailDeliveryError, ValueError):
                        import logging

                        logging.getLogger(__name__).exception(
                            "No se pudo asegurar el código de verificación durante login"
                        )
                    flash("Confirma el correo de la empresa antes de ingresar.", "warning")
                    return redirect(url_for("onboarding.verify_email"))
                from app.session_management import policy_for, start_managed_session

                remember = remember_requested and bool(policy_for(user)["remember_enabled"])
                login_user(user, remember=remember)
                start_managed_session(user, remember=remember)
                if user.empresa_id:
                    from app.tenant_activity import registrar_actividad_tenant

                    registrar_actividad_tenant(
                        user.empresa_id,
                        "login",
                        user_id=user.id,
                        username=user.username,
                        detalle="Inicio de sesión web",
                    )
                    if remember:
                        registrar_actividad_tenant(
                            user.empresa_id,
                            "remember_login",
                            user_id=user.id,
                            username=user.username,
                            detalle="Recordarme activado por el usuario",
                        )
                    db.session.commit()
                flash("Sesión iniciada correctamente.", "success")
                if not user.onboarding_completado:
                    return redirect(url_for("onboarding.wizard"))
                nxt = request.form.get("next") or request.args.get("next")
                if nxt and _is_safe_url(nxt):
                    return redirect(nxt)
                return redirect(url_for("main.dashboard"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated and current_user.empresa_id:
        from app.tenant_activity import registrar_actividad_tenant

        registrar_actividad_tenant(
            current_user.empresa_id,
            "logout",
            user_id=current_user.id,
            username=current_user.username,
        )
        db.session.commit()
    from app.session_management import current_managed_session, revoke_session

    revoke_session(current_managed_session(), reason="logout")
    db.session.commit()
    logout_user()
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.index"))


@bp.route("/sesion/estado", methods=["GET", "POST"])
def session_status():
    """Estado ligero para advertencia y renovación por interacción real."""
    from app.session_management import current_managed_session, session_payload

    item = current_managed_session()
    if not current_user.is_authenticated or item is None:
        return jsonify({"authenticated": False}), 401
    return jsonify(session_payload(item, current_user))


@bp.route("/administracion/seguridad", methods=["GET", "POST"])
def seguridad_sesiones():
    emp = _empresa_del_usuario()
    if emp is None or not can_manage_equipo(current_user):
        flash("Solo los administradores pueden gestionar las sesiones.", "warning")
        return redirect(url_for("main.dashboard"))
    from app.models import ActiveSession
    from app.session_management import SESSION_KEY, describe_user_agent, revoke_session

    if request.method == "POST":
        action = request.form.get("accion", "guardar")
        if action == "guardar":
            try:
                idle = int(request.form.get("idle_minutes", "30"))
                absolute = int(request.form.get("absolute_minutes", "480"))
                warning = int(request.form.get("warning_minutes", "2"))
            except ValueError:
                flash("Los tiempos de sesión deben ser números enteros.", "danger")
            else:
                if not 10 <= idle <= 60:
                    flash("La inactividad debe estar entre 10 y 60 minutos.", "danger")
                elif not 60 <= absolute <= 720:
                    flash("El tiempo máximo debe estar entre 1 y 12 horas.", "danger")
                elif not 1 <= warning < idle:
                    flash("La advertencia debe ser menor que el tiempo de inactividad.", "danger")
                else:
                    emp.session_idle_minutes = idle
                    emp.session_absolute_minutes = absolute
                    emp.session_warning_minutes = warning
                    emp.session_remember_enabled = bool(request.form.get("remember_enabled"))
                    emp.session_warning_enabled = bool(request.form.get("warning_enabled"))
                    emp.session_revoke_on_password = bool(request.form.get("revoke_on_password"))
                    emp.session_allow_multiple = bool(request.form.get("allow_multiple"))
                    db.session.commit()
                    flash("Política de seguridad actualizada.", "success")
                    return redirect(url_for("main.seguridad_sesiones"))
        elif action == "revocar":
            item = ActiveSession.query.filter_by(
                id=request.form.get("session_id", type=int), empresa_id=emp.id
            ).first_or_404()
            if item.session_key == session.get(SESSION_KEY):
                flash("Usa Cerrar sesión para finalizar la sesión actual.", "warning")
            else:
                revoke_session(item, reason="revocacion_admin")
                from app.tenant_activity import registrar_actividad_tenant

                registrar_actividad_tenant(
                    emp.id,
                    "session_revoked",
                    user_id=item.user_id,
                    username=item.user.username if item.user else "",
                    detalle=f"Sesión finalizada por {current_user.username}",
                )
                db.session.commit()
                flash("Sesión finalizada remotamente.", "success")
            return redirect(url_for("main.seguridad_sesiones"))
        elif action == "revocar_otras":
            from app.session_management import revoke_user_sessions

            total = revoke_user_sessions(
                current_user.id,
                reason="cerrar_otras",
                except_key=session.get(SESSION_KEY),
            )
            db.session.commit()
            flash(f"Se finalizaron {total} sesiones adicionales.", "success")
            return redirect(url_for("main.seguridad_sesiones"))

    now = datetime.utcnow()
    items = (
        ActiveSession.query.filter_by(empresa_id=emp.id, revoked_at=None)
        .filter(ActiveSession.absolute_expires_at > now)
        .order_by(ActiveSession.last_activity_at.desc())
        .all()
    )
    rows = [
        {
            "item": item,
            "browser": describe_user_agent(item.user_agent)[0],
            "system": describe_user_agent(item.user_agent)[1],
            "current": item.session_key == session.get(SESSION_KEY),
        }
        for item in items
    ]
    return render_template("configuracion/seguridad.html", empresa=emp, sesiones=rows)


@bp.route("/cuenta-suspendida")
def cuenta_suspendida():
    motivo = request.args.get("motivo", "suspendida")
    mensajes = {
        "suspendida": "Esta cuenta está suspendida. Contacta a soporte de Maintix para reactivarla.",
        "mora": "Hay pagos pendientes. Regulariza la facturación para continuar usando Maintix.",
    }
    return render_template(
        "cuenta_suspendida.html",
        motivo=motivo,
        mensaje=mensajes.get(motivo, mensajes["suspendida"]),
    )


@bp.route("/salir-impersonacion", methods=["POST"])
def salir_impersonacion():
    from flask import session

    if not session.pop("platform_impersonating", None):
        flash("No hay sesión de impersonación activa.", "warning")
        return redirect(url_for("main.dashboard"))
    empresa_id = getattr(current_user, "empresa_id", None)
    user_id = getattr(current_user, "id", None)
    username = getattr(current_user, "username", "")
    logout_user()
    if empresa_id:
        from app.platform_audit import registrar_auditoria_plataforma
        from app.tenant_activity import registrar_actividad_tenant

        registrar_auditoria_plataforma(
            "impersonate_end",
            empresa_id=empresa_id,
            user_id=user_id,
            detalle=f"Fin de impersonación de @{username}",
        )
        registrar_actividad_tenant(
            empresa_id,
            "impersonate_end",
            user_id=user_id,
            username=username,
            detalle="Fin de sesión de soporte",
        )
        db.session.commit()
    session["platform_admin"] = True
    flash("Volviste al panel de plataforma.", "info")
    return redirect(url_for("platform.empresas"))


def _period_bounds(period: str, ref: Optional[date] = None) -> Tuple[date, date, str]:
    ref = ref or date.today()
    period = (period or "mes").lower()
    if period == "dia":
        start = ref
        end = ref
    elif period == "semana":
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=6)
    elif period == "año":
        start = date(ref.year, 1, 1)
        end = date(ref.year, 12, 31)
    else:
        start = date(ref.year, ref.month, 1)
        _, last = monthrange(ref.year, ref.month)
        end = date(ref.year, ref.month, last)
    return start, end, period


def _parse_dashboard_ref() -> date:
    """Fecha de referencia del período (query ref, mes+anio o hoy)."""
    ref_s = (request.args.get("ref") or "").strip()
    if ref_s:
        for fmt, is_month in (("%Y-%m-%d", False), ("%Y-%m", True)):
            try:
                parsed = datetime.strptime(ref_s, fmt).date()
                if is_month:
                    return date(parsed.year, parsed.month, 1)
                return parsed
            except ValueError:
                continue
    period = (request.args.get("periodo") or "mes").lower()
    try:
        anio = int(request.args.get("anio", ""))
        if 2000 <= anio <= 2100:
            mes_s = request.args.get("mes", "").strip()
            if mes_s.isdigit():
                mes = int(mes_s)
                if 1 <= mes <= 12:
                    return date(anio, mes, 1)
            if period == "año":
                return date(anio, 1, 1)
    except (TypeError, ValueError):
        pass
    return date.today()


def _shift_period_ref(period: str, ref: date, delta: int) -> date:
    period = (period or "mes").lower()
    if period == "dia":
        return ref + timedelta(days=delta)
    if period == "semana":
        return ref + timedelta(days=7 * delta)
    if period == "año":
        return date(ref.year + delta, 1, 1)
    month = ref.month + delta
    year = ref.year
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1
    last = monthrange(year, month)[1]
    return date(year, month, min(ref.day, last))


def _period_display_label(period: str, start: date, end: date) -> str:
    meses = dict(MESES_PLANEACION)
    period = (period or "mes").lower()
    if period == "dia":
        return start.strftime("%d/%m/%Y")
    if period == "semana":
        if start.month == end.month and start.year == end.year:
            return f"{start.day}–{end.day} {meses.get(end.month, end.month)} {end.year}"
        return f"{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"
    if period == "año":
        return str(start.year)
    return f"{meses.get(start.month, str(start.month))} {start.year}"


def _dashboard_filtros_desde_request() -> dict[str, str]:
    return {
        "equipo": request.args.get("equipo", "").strip(),
        "ubicacion": request.args.get("ubicacion", "").strip(),
    }


def _machines_query_con_filtros(q, filtros: dict[str, str]):
    equipo = filtros.get("equipo", "")
    if equipo:
        like = f"%{equipo}%"
        q = q.filter(or_(Machine.nombre.ilike(like), Machine.codigo.ilike(like)))
    ubicacion = filtros.get("ubicacion", "")
    if ubicacion:
        like = f"%{ubicacion}%"
        q = q.filter(or_(Machine.ubicacion.ilike(like), Machine.area.ilike(like)))
    return q


def _dashboard_machine_ids(sector: str, filtros: dict[str, str]) -> Optional[list[int]]:
    """IDs de activos del sector que coinciden; None si no hay filtro activo."""
    if not any(filtros.get(k, "") for k in ("equipo", "ubicacion")):
        return None
    q = _machines_query_con_filtros(_machines_for_sector_query(sector), filtros)
    return [mid for (mid,) in q.with_entities(Machine.id).all()]


def _wo_apply_machine_ids(q, machine_ids: Optional[list[int]]):
    if machine_ids is None:
        return q
    if not machine_ids:
        return q.filter(WorkOrder.machine_id == -1)
    return q.filter(WorkOrder.machine_id.in_(machine_ids))


def _dashboard_query_params(
    period: str,
    ref: date,
    sector: str,
    sector_locked: bool,
    filtros: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    params: dict[str, str] = {"periodo": period, "ref": ref.isoformat()}
    if not sector_locked and sector:
        params["sector"] = sector
    filtros = filtros or {}
    if filtros.get("equipo"):
        params["equipo"] = filtros["equipo"]
    if filtros.get("ubicacion"):
        params["ubicacion"] = filtros["ubicacion"]
    return params


def _parse_sector(value: Optional[str]) -> str:
    return normalizar_sector(value)


def _sector_for_dashboard() -> tuple[str, bool]:
    """Sector del dashboard; bloqueado al de la empresa si existe."""
    if current_user.is_authenticated and current_user.empresa and current_user.empresa.sector:
        return _parse_sector(current_user.empresa.sector), True
    return _parse_sector(request.args.get("sector")), False


def _sector_industrial_empresa() -> Optional[str]:
    """Sector industrial de la empresa del usuario, si está definido."""
    if current_user.is_authenticated and current_user.empresa and current_user.empresa.sector:
        return _parse_sector(current_user.empresa.sector)
    return None


def _sectores_para_tipo_form() -> list[tuple[str, str]]:
    sector = _sector_industrial_empresa()
    if sector:
        return [(sector, SECTOR_LABELS.get(sector, sector))]
    return [(k, SECTOR_LABELS[k]) for k in SECTOR_LABELS]


def _tipo_pertenece_sector_empresa(tipo: MachineType) -> bool:
    sector = _sector_industrial_empresa()
    if not sector:
        return True
    return (tipo.sector_industrial or "") == sector


def _machine_ids_for_sector(sector: str) -> Any:
    q = db.session.query(Machine.id).join(MachineType).filter(
        MachineType.sector_industrial == sector
    )
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _machine_ids_for_empresa() -> Any:
    q = db.session.query(Machine.id)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _filter_work_orders_empresa(q):
    """Incluye OT de la empresa aunque empresa_id en la OT sea NULL."""
    eid = _current_empresa_id()
    if not eid:
        return q
    return q.filter(
        or_(
            WorkOrder.empresa_id == eid,
            WorkOrder.machine_id.in_(_machine_ids_for_empresa()),
        )
    )


def _get_work_order_or_404(order_id: int, *options):
    q = _filter_work_orders_empresa(WorkOrder.query.filter_by(id=order_id))
    if options:
        q = q.options(*options)
    return q.first_or_404()


def _get_spare_part_or_404(part_id: int) -> SparePart:
    return _filter_empresa(SparePart.query.filter_by(id=part_id), SparePart).first_or_404()


def _wo_status_terminal_filter():
    return or_(
        WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
        func.lower(WorkOrder.status).in_(("cerrada", "completado", "cerrado")),
    )


def _aplicar_fecha_cierre_si_terminal(wo: WorkOrder) -> None:
    st = (wo.status or "").strip().lower()
    if st in ("cerrada", "completado", "cerrado") and not wo.fecha_cierre:
        wo.fecha_cierre = datetime.utcnow()


def _machines_for_sector_query(sector: str):
    q = Machine.query.join(MachineType).filter(MachineType.sector_industrial == sector)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _wo_for_sector(sector: str):
    return WorkOrder.machine_id.in_(_machine_ids_for_sector(sector))


def _wo_in_period_query(
    start: date,
    end: date,
    sector: Optional[str] = None,
    machine_ids: Optional[list[int]] = None,
):
    q = WorkOrder.query.filter(
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada >= start,
        WorkOrder.fecha_programada <= end,
    )
    if sector:
        q = q.filter(_wo_for_sector(sector))
    eid = _current_empresa_id()
    if eid:
        q = q.filter(WorkOrder.empresa_id == eid)
    return _wo_apply_machine_ids(q, machine_ids)


def _preventivas_cumplimiento_query(
    start: date,
    end: date,
    sector: Optional[str] = None,
    *,
    sector_locked: bool = False,
    machine_ids: Optional[list[int]] = None,
):
    """OT preventivas con fecha programada dentro del período del dashboard."""
    del sector_locked  # el sector ya se aplica en _wo_in_period_query cuando corresponde
    q = _wo_in_period_query(start, end, sector, machine_ids)
    return q.filter(func.lower(WorkOrder.tipo) == WorkOrderType.PREVENTIVO.value)


def _cumplimiento_preventivo_dashboard(
    start: date,
    end: date,
    period_label: str,
    sector: Optional[str] = None,
    *,
    sector_locked: bool = False,
    machine_ids: Optional[list[int]] = None,
) -> dict[str, Any]:
    """
    Cumplimiento = preventivas programadas en el período que están completadas/cerradas.
    Devuelve listado de todas las completadas según el filtro de fechas.
    """
    del sector_locked
    programadas_q = _preventivas_cumplimiento_query(
        start, end, sector, machine_ids=machine_ids
    )
    total = programadas_q.count()
    completadas_wo = (
        programadas_q.filter(_wo_status_terminal_filter())
        .order_by(WorkOrder.fecha_programada, WorkOrder.id)
        .all()
    )
    n_ok = len(completadas_wo)
    pendientes = max(0, total - n_ok)
    status_labels = {
        WorkOrderStatus.CERRADA.value: "Cerrada",
        WorkOrderStatus.COMPLETADO.value: "Completada",
        "cerrado": "Cerrado",
    }
    items = []
    for wo in completadas_wo:
        st = (wo.status or "").strip().lower()
        items.append(
            {
                "numero": wo.numero or f"OT-{wo.id}",
                "titulo": wo.titulo,
                "status": status_labels.get(st, wo.status or "—"),
                "fecha": wo.fecha_programada,
                "fecha_fmt": wo.fecha_programada.strftime("%d/%m/%Y")
                if wo.fecha_programada
                else "—",
                "href": url_for("main.ordenes_edit", id=wo.id),
            }
        )
    if total == 0:
        return {
            "cumplimiento": 0.0,
            "total_prev": 0,
            "prev_completadas": 0,
            "prev_pendientes": 0,
            "prev_msg": "",
            "prev_completadas_items": [],
            "sin_programadas": True,
        }
    pct = round(100.0 * n_ok / total, 1)
    msg = (
        f"{n_ok} de {total} completadas en {period_label}"
        + (f" · {pendientes} pendiente{'s' if pendientes != 1 else ''}" if pendientes else "")
    )
    return {
        "cumplimiento": pct,
        "total_prev": total,
        "prev_completadas": n_ok,
        "prev_pendientes": pendientes,
        "prev_msg": msg,
        "prev_completadas_items": items,
        "sin_programadas": False,
    }


def _closed_wo_in_period_query(
    start: date,
    end: date,
    sector: Optional[str] = None,
    machine_ids: Optional[list[int]] = None,
):
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())
    q = WorkOrder.query.filter(
        WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
        WorkOrder.fecha_cierre.isnot(None),
        WorkOrder.fecha_cierre >= start_dt,
        WorkOrder.fecha_cierre <= end_dt,
    )
    if sector:
        q = q.filter(_wo_for_sector(sector))
    eid = _current_empresa_id()
    if eid:
        q = q.filter(WorkOrder.empresa_id == eid)
    return _wo_apply_machine_ids(q, machine_ids)


def _fmt_duration_hours(hours: Optional[float]) -> str:
    if hours is None:
        return "—"
    if hours >= 48:
        return f"{round(hours / 24, 1)} d"
    return f"{round(hours, 1)} h"


def _dashboard_kpis(
    start: date,
    end: date,
    total_m: int,
    operativos: int,
    sector: Optional[str] = None,
    machine_ids: Optional[list[int]] = None,
) -> dict:
    open_statuses = list(WORK_ORDER_PENDING_STATUSES)
    wo_period = _wo_in_period_query(start, end, sector, machine_ids)
    ordenes_abiertas = wo_period.filter(WorkOrder.status.in_(open_statuses)).count()
    mantenimientos_pendientes = wo_period.filter(
        WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
        WorkOrder.status.in_(open_statuses),
    ).count()
    ot_en_periodo = wo_period.count()
    disponibilidad = round(100.0 * operativos / total_m, 1) if total_m else 0.0

    repair_types = [WorkOrderType.CORRECTIVO.value, WorkOrderType.EMERGENCIA.value]
    closed_repairs = (
        _closed_wo_in_period_query(start, end, sector, machine_ids)
        .filter(
            WorkOrder.tipo.in_(repair_types),
            WorkOrder.fecha_inicio.isnot(None),
        )
        .all()
    )
    eid_kpi = _current_empresa_id()
    emp = Empresa.query.get(eid_kpi) if eid_kpi else None
    mttr_wos = [
        wo
        for wo in closed_repairs
        if wo.tipo == WorkOrderType.CORRECTIVO.value and wo.maquina_requirio_paro
    ]
    repair_hours = []
    for wo in mttr_wos:
        jornadas_paro = [j for j in wo.jornadas if bool(j.requirio_paro)]
        if jornadas_paro:
            mins = sum(j.duracion_minutos for j in jornadas_paro)
        else:
            # Compatibilidad con OT históricas: antes el paro se registraba
            # globalmente y no existía la marca por jornada.
            mins = wo_tiempo_gastado_minutos(wo, emp)
        if mins is not None:
            repair_hours.append(mins / 60.0)
        elif wo.fecha_inicio and wo.fecha_cierre:
            repair_hours.append((wo.fecha_cierre - wo.fecha_inicio).total_seconds() / 3600.0)
    mttr = round(sum(repair_hours) / len(repair_hours), 1) if repair_hours else None

    failures = (
        _closed_wo_in_period_query(start, end, sector, machine_ids)
        .filter(WorkOrder.tipo.in_(repair_types))
        .order_by(WorkOrder.machine_id, WorkOrder.fecha_cierre)
        .all()
    )
    intervals: list[float] = []
    by_machine: dict[int, list[datetime]] = {}
    for wo in failures:
        by_machine.setdefault(wo.machine_id, []).append(wo.fecha_cierre)
    for times in by_machine.values():
        times.sort()
        for i in range(1, len(times)):
            intervals.append((times[i] - times[i - 1]).total_seconds() / 3600.0)

    if intervals:
        mtbf = round(sum(intervals) / len(intervals), 1)
    elif failures and total_m:
        period_hours = ((end - start).days + 1) * 24.0
        total_repair = sum(repair_hours)
        operating = max(0.0, period_hours * total_m - total_repair)
        mtbf = round(operating / len(failures), 1)
    else:
        mtbf = None

    if mtbf is not None and mttr is not None and (mtbf + mttr) > 0:
        disponibilidad_global = round(100.0 * mtbf / (mtbf + mttr), 2)
    else:
        disponibilidad_global = None

    return {
        "activos_totales": total_m,
        "ot_en_periodo": ot_en_periodo,
        "ordenes_abiertas": ordenes_abiertas,
        "mantenimientos_pendientes": mantenimientos_pendientes,
        "disponibilidad": disponibilidad,
        "disponibilidad_global": disponibilidad_global,
        "mttr": mttr,
        "mtbf": mtbf,
        "mttr_display": _fmt_duration_hours(mttr),
        "mtbf_display": _fmt_duration_hours(mtbf),
        "_mtbf": mtbf,
        "_mttr": mttr,
        "_disp_global": disponibilidad_global,
        "_closed_repairs": closed_repairs,
        "_emp": emp,
    }


def _attach_plant_kpi_cards(
    kpis: dict,
    *,
    start: date,
    end: date,
    sector: Optional[str],
    sector_locked: bool,
    machines: list,
    operativos: int,
    machine_ids: Optional[list[int]] = None,
) -> dict:
    eid = _current_empresa_id()
    wo_period_q = _wo_in_period_query(start, end, sector, machine_ids)
    preventivas_q = _preventivas_cumplimiento_query(
        start, end, sector, sector_locked=sector_locked, machine_ids=machine_ids
    )
    kpis["plant_cards"] = build_plant_kpi_cards(
        start=start,
        end=end,
        sector=sector,
        eid=eid,
        machines=machines,
        operativos=operativos,
        mtbf=kpis.get("_mtbf"),
        mttr=kpis.get("_mttr"),
        disp_global=kpis.get("_disp_global"),
        emp=kpis.get("_emp"),
        wo_period_q=wo_period_q,
        preventivas_q=preventivas_q,
        closed_repairs=kpis.get("_closed_repairs") or [],
    )
    for k in ("_mtbf", "_mttr", "_disp_global", "_closed_repairs", "_emp"):
        kpis.pop(k, None)
    return kpis


_KPI_UI = {
    "activos_totales": ("primary", "bi-hdd-stack", None, None),
    "ordenes_abiertas": ("neutral", "bi-clipboard-check", None, None),
    "mantenimientos_pendientes": ("warning", "bi-wrench-adjustable", None, None),
    "disponibilidad": ("success", "bi-speedometer2", None, None),
    "mttr": (
        "neutral",
        "bi-stopwatch",
        "T. reparación",
        "Promedio de horas en correctivos cerrados donde el activo estuvo parado",
    ),
    "mtbf": ("neutral", "bi-arrow-repeat", "T. entre fallas", "Tiempo medio entre fallas"),
    "disponibilidad_global": (
        "success",
        "bi-pie-chart",
        "MTBF/(MTBF+MTTR)",
        "MTBF ÷ (MTBF + MTTR)",
    ),
}


def _kpi_display_value(kpis: dict, key: str) -> str:
    if key == "disponibilidad":
        return f"{kpis['disponibilidad']}%"
    if key == "disponibilidad_global":
        v = kpis.get("disponibilidad_global")
        return f"{v}%" if v is not None else "—"
    if key == "mttr":
        return kpis.get("mttr_display") or "—"
    if key == "mtbf":
        return kpis.get("mtbf_display") or "—"
    return str(kpis.get(key, "—"))


def _build_kpi_cards(kpis: dict, empresa_id: Optional[int], sector: str) -> List[dict]:
    plant_cards = kpis.get("plant_cards")
    if plant_cards:
        return plant_cards

    from app.sector_templates import dashboard_config_for_sector

    cfg = (
        get_plantilla_dashboard(empresa_id, sector)
        if empresa_id
        else dashboard_config_for_sector(sector)
    )
    items = cfg.get("kpis") or []
    cards = []
    for item in items:
        key = item.get("key") or item[0] if isinstance(item, (list, tuple)) else "activos_totales"
        label = item.get("label") if isinstance(item, dict) else item[1]
        style, icon, hint, hint_title = _KPI_UI.get(key, ("neutral", "bi-graph-up", None, None))
        cards.append(
            {
                "key": key,
                "label": label,
                "value": _kpi_display_value(kpis, key),
                "style": style,
                "icon": icon,
                "hint": hint,
                "hint_title": hint_title,
                "show_icon": True,
            }
        )
    return cards


def _dashboard_resumen_operativo(
    start: date,
    end: date,
    sector: Optional[str],
    machine_ids: Optional[list[int]],
    operativos: int,
) -> dict:
    """Indicadores MRG-02 §10 / MRG-08 §2 para la fila resumen del dashboard."""
    q = _filter_work_orders_empresa(WorkOrder.query)
    if sector:
        q = q.filter(_wo_for_sector(sector))
    q = _wo_apply_machine_ids(q, machine_ids)

    open_statuses = list(WORK_ORDER_PENDING_STATUSES)
    ordenes_abiertas = q.filter(WorkOrder.status.in_(open_statuses)).count()
    ordenes_vencidas = q.filter(WorkOrder.status == WorkOrderStatus.VENCIDA.value).count()
    preventivos_mes = (
        _wo_in_period_query(start, end, sector, machine_ids)
        .filter(func.lower(WorkOrder.tipo) == WorkOrderType.PREVENTIVO.value)
        .count()
    )
    correctivos = (
        _wo_in_period_query(start, end, sector, machine_ids)
        .filter(func.lower(WorkOrder.tipo) == WorkOrderType.CORRECTIVO.value)
        .all()
    )
    minutos_correctivos_con_paro = sum(
        jornada.duracion_minutos
        for orden in correctivos
        for jornada in orden.jornadas
        if bool(jornada.requirio_paro)
    )
    sp_q = _filter_empresa(SparePart.query, SparePart)
    repuestos_bajo_minimo = sp_q.filter(SparePart.cantidad < SparePart.stock_minimo).count()

    return {
        "activos_operativos": operativos,
        "ordenes_abiertas": ordenes_abiertas,
        "ordenes_vencidas": ordenes_vencidas,
        "preventivos_mes": preventivos_mes,
        "total_correctivos": len(correctivos),
        "minutos_correctivos_con_paro": minutos_correctivos_con_paro,
        "horas_correctivos_con_paro_label": formatear_duracion(
            minutos_correctivos_con_paro
        ),
        "repuestos_bajo_minimo": repuestos_bajo_minimo,
    }


def _parse_form_date(raw: str) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _parse_int_form(val) -> Optional[int]:
    try:
        s = (val or "").strip()
        return int(s) if s else None
    except ValueError:
        return None


def _parse_float_form(val) -> Optional[float]:
    try:
        s = (val or "").strip().replace(",", ".")
        return float(s) if s else None
    except ValueError:
        return None


def _moneda_empresa_activo(machine: Optional[Machine] = None) -> str:
    if machine and machine.empresa_id:
        emp = db.session.get(Empresa, machine.empresa_id)
        if emp:
            return normalizar_moneda(emp.moneda)
    if current_user.is_authenticated and getattr(current_user, "empresa", None):
        return normalizar_moneda(current_user.empresa.moneda)
    return "COP"


def _apply_machine_base_fields(machine: Machine, form) -> Optional[str]:
    machine.nombre = form.get("nombre", "").strip()
    machine.descripcion = form.get("descripcion", "").strip()
    machine.registro_tipo = ""
    machine.checklist_registro = registro_flags_from_form(form)
    machine.machine_type_id = int(form.get("machine_type_id") or machine.machine_type_id)
    raw_sede = (form.get("sede_id") or "").strip()
    machine.sede_id = int(raw_sede) if raw_sede.isdigit() else None
    machine.area = form.get("area", "").strip()
    machine.ubicacion = form.get("ubicacion", "").strip()
    machine.marca = form.get("marca", "").strip()
    machine.modelo = form.get("modelo", "").strip()
    machine.fabricante = form.get("fabricante", "").strip()
    machine.numero_serie = form.get("numero_serie", "").strip()
    machine.fecha_fabricacion = _parse_form_date(form.get("fecha_fabricacion"))
    machine.fecha_ingreso = _parse_form_date(form.get("fecha_ingreso"))
    machine.fecha_instalacion = _parse_form_date(form.get("fecha_instalacion"))
    machine.fecha_puesta_marcha = _parse_form_date(form.get("fecha_puesta_marcha"))
    machine.vida_util_anios = _parse_int_form(form.get("vida_util_anios"))
    machine.horas_operacion = _parse_float_form(form.get("horas_operacion"))
    machine.fecha_compra = _parse_form_date(form.get("fecha_compra"))
    machine.numero_factura = (form.get("numero_factura") or "").strip()
    moneda_emp = _moneda_empresa_activo(machine)
    machine.moneda_compra = normalizar_moneda(form.get("moneda_compra"), moneda_emp)
    machine.valor_compra = parsear_monto_form(form.get("valor_compra"), machine.moneda_compra)
    machine.proveedor = form.get("proveedor", "").strip()
    raw_proveedor = (form.get("proveedor_id") or "").strip()
    machine.proveedor_id = int(raw_proveedor) if raw_proveedor.isdigit() else None
    if machine.proveedor_id:
        proveedor = _filter_empresa(
            Proveedor.query.filter_by(id=machine.proveedor_id, activo=True), Proveedor
        ).first()
        if proveedor is None:
            return "Selecciona un proveedor activo de tu empresa."
        # Conserva el campo textual para exportaciones y registros antiguos.
        machine.proveedor = proveedor.nombre
    machine.tiempo_garantia_meses = _parse_int_form(form.get("tiempo_garantia_meses"))
    machine.garantia_hasta = calcular_garantia_hasta(
        machine.fecha_compra, machine.tiempo_garantia_meses
    )
    machine.manual_url = form.get("manual_url", "").strip()
    machine.ficha_tecnica_url = form.get("ficha_tecnica_url", "").strip()
    foto_url = form.get("foto_url", "").strip()
    if foto_url:
        machine.foto_url = foto_url
    machine.requiere_mantenimiento = bool(form.get("requiere_mantenimiento"))
    machine.tipos_mantenimiento = tipos_mantenimiento_from_form(form)
    machine.frecuencia_mantenimiento = (form.get("frecuencia_mantenimiento") or "").strip()
    raw_resp = (form.get("responsable_user_id") or "").strip()
    machine.responsable_user_id = int(raw_resp) if raw_resp.isdigit() else None
    if machine.responsable_user_id:
        responsable = User.query.filter_by(
            id=machine.responsable_user_id,
            empresa_id=machine.empresa_id,
            activo=True,
        ).first()
        if responsable is None:
            return "Selecciona un responsable activo de tu empresa."
        machine.responsable_area = responsable.area or ""
        machine.responsable_cargo = responsable.cargo or ""
    machine.criticidad = form.get("criticidad") or "media"
    machine.status = form.get("status") or MachineStatus.OPERATIVO.value
    machine.notas = form.get("notas", "").strip()
    machine.sync_criticidad_critico()
    return None


def _guardar_imagen_activo(machine: Machine, archivo) -> None:
    """Guarda la fotografía del activo dentro del espacio de su empresa."""
    if not archivo or not getattr(archivo, "filename", None):
        return
    if not machine.id or not machine.empresa_id:
        raise ValueError("El activo debe estar guardado antes de cargar la imagen.")
    nombre = secure_filename(archivo.filename)
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in ACTIVO_IMAGE_EXTENSIONS:
        raise ValueError("Formato de imagen no permitido. Use PNG, JPG o WEBP.")
    carpeta = os.path.join(
        current_app.static_folder, "uploads", "empresas", str(machine.empresa_id), "activos"
    )
    os.makedirs(carpeta, exist_ok=True)
    for old_ext in ACTIVO_IMAGE_EXTENSIONS:
        old_path = os.path.join(carpeta, f"{machine.id}.{old_ext}")
        if os.path.isfile(old_path) and old_ext != ext:
            try:
                os.remove(old_path)
            except OSError:
                pass
    archivo.save(os.path.join(carpeta, f"{machine.id}.{ext}"))
    machine.foto_url = f"uploads/empresas/{machine.empresa_id}/activos/{machine.id}.{ext}"


def _save_machine_custom_fields(
    machine: Machine, form, empresa_id: int, sector: str, machine_type_id: int
) -> Optional[str]:
    campos = campos_para_tipo(empresa_id, sector, machine_type_id)
    for campo in campos:
        val, err = valor_campo_desde_form(campo, form)
        if err:
            return err
        row = ActivoCampoValor.query.filter_by(
            machine_id=machine.id, campo_id=campo.id
        ).first()
        if row:
            row.valor = val
        else:
            db.session.add(
                ActivoCampoValor(machine_id=machine.id, campo_id=campo.id, valor=val)
            )
    return None


def _activos_form_context(
    machine: Optional[Machine],
    tipos: list,
    default_machine_type_id: Optional[int],
    codigo_sugerido: str = "",
):
    empresa = current_user.empresa if current_user.is_authenticated else None
    sector = normalizar_sector(empresa.sector if empresa else None)
    eid = empresa.id if empresa else None
    preview_id = default_machine_type_id
    if machine:
        preview_id = machine.machine_type_id
    campos = campos_para_tipo(eid, sector, preview_id) if eid else []
    campos_json = [
        {
            "id": c.id,
            "nombre": c.nombre,
            "tipo": c.tipo,
            "obligatorio": c.obligatorio,
            "categorias_ids": c.categorias_aplicables(),
            "opciones": c.opciones_lista(),
        }
        for c in CampoPersonalizado.query.filter(
            CampoPersonalizado.empresa_id == eid,
            CampoPersonalizado.sector == sector,
            CampoPersonalizado.activo.is_(True),
            or_(
                CampoPersonalizado.entidad == CAMPO_ENTIDAD_ACTIVO,
                CampoPersonalizado.entidad.is_(None),
            ),
        )
        .order_by(CampoPersonalizado.orden)
        .all()
    ] if eid else []
    valores = valores_campos_map(machine) if machine else {}
    eid = empresa.id if empresa else None
    sedes = (
        Sede.query.filter_by(empresa_id=eid).order_by(Sede.es_principal.desc(), Sede.nombre).all()
        if eid
        else []
    )
    technicians = (
        _filter_empresa(
            Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician
        ).all()
        if eid
        else []
    )
    proveedores_activo = (
        _filter_empresa(
            Proveedor.query.filter(Proveedor.activo.is_(True)).order_by(Proveedor.nombre),
            Proveedor,
        ).all()
        if eid
        else []
    )
    campos_estandar, _secciones_legacy = (
        campos_por_seccion_estructurado(eid, sector, preview_id) if eid else ({}, {})
    )
    secciones_custom_despues, secciones_custom_final = (
        secciones_custom_por_ancla(eid, sector, preview_id) if eid else ({}, [])
    )
    reg_nuevo, reg_actualizacion = registro_flags_checked(
        machine.checklist_registro if machine else None,
        machine.registro_tipo if machine else "",
    )
    moneda_empresa = normalizar_moneda(empresa.moneda if empresa else None)
    moneda_compra_sel = normalizar_moneda(
        machine.moneda_compra if machine and machine.moneda_compra else None,
        moneda_empresa,
    )
    return {
        "machine": machine,
        "machine_types": tipos,
        "default_machine_type_id": preview_id,
        "codigo_sugerido": codigo_sugerido,
        "campos_personalizados": campos,
        "campos_estandar": campos_estandar,
        "secciones_custom_despues": secciones_custom_despues,
        "secciones_custom_final": secciones_custom_final,
        "activo_secciones": ACTIVO_SECCIONES,
        "activo_secciones_labels": dict(ACTIVO_SECCIONES),
        "activo_seccion_keys_list": list(ACTIVO_SECCION_KEYS),
        "activo_seccion_iconos": ACTIVO_SECCION_ICONOS,
        "activo_seccion_icono_default": ACTIVO_SECCION_ICONO_DEFAULT,
        "campos_json": campos_json,
        "valores_campos": valores,
        "criticidad_choices": CRITICIDAD_CHOICES,
        "sector_label": SECTOR_LABELS.get(sector, sector),
        "sedes": sedes,
        "technicians": technicians,
        "usuarios_responsables": _equipo_usuarios_query().filter(User.activo.is_(True)).all() if eid else [],
        "proveedores_activo": proveedores_activo,
        "mantenimiento_tipos": MANTENIMIENTO_TIPOS,
        "frecuencia_choices": FRECUENCIA_BASE_CHOICES,
        "tipos_mant_sel": tipos_mantenimiento_list(machine.tipos_mantenimiento if machine else ""),
        "registro_nuevo_checked": reg_nuevo,
        "registro_actualizacion_checked": reg_actualizacion,
        "moneda_empresa": moneda_empresa,
        "moneda_compra_sel": moneda_compra_sel,
        "monedas_compra": MONEDAS_SOPORTADAS,
        "simbolo_moneda_compra": simbolo_moneda_input(moneda_compra_sel),
        "simbolos_moneda": {c: simbolo_moneda_input(c) for c, _ in MONEDAS_SOPORTADAS},
        "valor_compra_texto": (
            formatear_monto_sin_simbolo(machine.valor_compra, moneda_compra_sel)
            if machine and machine.valor_compra is not None
            else ""
        ),
    }


PROXIMOS_MANTENIMIENTOS_LIMITE = 8


def _proximos_mantenimientos(
    start: date,
    end: date,
    limit: int = PROXIMOS_MANTENIMIENTOS_LIMITE,
    sector: Optional[str] = None,
    machine_ids: Optional[list[int]] = None,
) -> dict[str, Any]:
    """OT futuras con fecha programada en el período del dashboard (máx. `limit` en lista)."""
    from sqlalchemy.orm import joinedload

    hoy = date.today()
    desde = max(start, hoy)
    if desde > end:
        return {"items": [], "total": 0, "limit": limit, "shown": 0}

    prox_q = _wo_in_period_query(desde, end, sector, machine_ids).filter(
        ~WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES)
    )
    total = prox_q.count()
    orders = (
        prox_q.options(joinedload(WorkOrder.machine))
        .order_by(WorkOrder.fecha_programada, WorkOrder.id)
        .limit(limit)
        .all()
    )
    items: list[dict[str, Any]] = []
    for wo in orders:
        d = wo.fecha_programada
        m = wo.machine
        codigo = (m.codigo if m and m.codigo else "") or "—"
        nombre = (m.nombre if m else "") or wo.titulo
        tipo_meta = wo_tipo_meta(wo.tipo)
        items.append(
            {
                "fecha": d,
                "fecha_dia": f"{d.day:02d}",
                "fecha_mes": MESES_CORTO[d.month - 1].upper(),
                "fecha_corta": f"{d.day:02d} {MESES_CORTO[d.month - 1].upper()}",
                "codigo": codigo,
                "nombre": nombre,
                "titulo": wo.titulo,
                "numero": wo.numero or f"OT-{wo.id}",
                "tipo": wo.tipo,
                "tipo_slug": (wo.tipo or "").strip().lower(),
                "tipo_short": tipo_meta["short"].upper(),
                "href": url_for("main.ordenes_edit", id=wo.id),
            }
        )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "shown": len(items),
    }


@bp.route("/")
def index():
    """Página pública de inicio (landing). Siempre en /, con o sin sesión."""
    from app.landing_service import landing_context

    ctx = landing_context()
    ctx["now_year"] = date.today().year
    return render_template("landing/index.html", **ctx)


@bp.route("/faq")
def faq():
    """FAQ público — contenido MCM-08-FAQ."""
    from app.landing_service import public_page_context
    from app.public_faq import FAQ_SECTIONS

    ctx = public_page_context()
    ctx["now_year"] = date.today().year
    ctx["faq_sections"] = FAQ_SECTIONS
    return render_template("landing/faq.html", **ctx)


@bp.route("/demo", methods=["GET", "POST"])
def demo():
    """Demo comercial pública — flujo MCM-07."""
    import logging

    from app.landing_service import public_page_context
    from app.platform_config_service import sectores_para_registro
    from app.public_demo import DEMO_INTRO, DEMO_PLAYS

    logger = logging.getLogger(__name__)
    ctx = public_page_context()
    ctx["now_year"] = date.today().year
    ctx["demo_intro"] = DEMO_INTRO
    ctx["demo_plays"] = DEMO_PLAYS
    ctx["sectores"] = sectores_para_registro()
    ctx["demo_sent"] = request.args.get("sent") == "1"

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        email = (request.form.get("email") or "").strip()
        empresa = (request.form.get("empresa") or "").strip()
        sector = (request.form.get("sector") or "").strip()
        mensaje = (request.form.get("mensaje") or "").strip()
        if not nombre or not email or not empresa:
            flash("Completa nombre, correo y empresa.", "warning")
        elif "@" not in email:
            flash("Ingresa un correo válido.", "warning")
        else:
            logger.info(
                "Solicitud demo Maintix: %s <%s> empresa=%s sector=%s mensaje=%s",
                nombre,
                email,
                empresa,
                sector or "—",
                (mensaje[:120] + "…") if len(mensaje) > 120 else (mensaje or "—"),
            )
            return redirect(url_for("main.demo", sent=1))

    return render_template("landing/demo.html", **ctx)


@bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    """Contacto comercial general — MKT-05."""
    import logging

    from app.branding import PUBLIC_CONTACT_EMAIL
    from app.landing_service import public_page_context
    from app.public_contact import CONTACT_INTRO, CONTACT_SUCCESS, CONTACT_TOPICS

    logger = logging.getLogger(__name__)
    ctx = public_page_context()
    ctx["now_year"] = date.today().year
    ctx["contact_intro"] = CONTACT_INTRO
    ctx["contact_topics"] = CONTACT_TOPICS
    ctx["contact_success_msg"] = CONTACT_SUCCESS
    ctx["contact_email"] = PUBLIC_CONTACT_EMAIL
    ctx["contact_sent"] = request.args.get("sent") == "1"

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        email = (request.form.get("email") or "").strip()
        asunto = (request.form.get("asunto") or "").strip()
        mensaje = (request.form.get("mensaje") or "").strip()
        if not nombre or not email or not mensaje:
            flash("Completa nombre, correo y mensaje.", "warning")
        elif "@" not in email:
            flash("Ingresa un correo válido.", "warning")
        else:
            logger.info(
                "Contacto Maintix: %s <%s> asunto=%s mensaje=%s",
                nombre,
                email,
                asunto or "—",
                (mensaje[:160] + "…") if len(mensaje) > 160 else mensaje,
            )
            return redirect(url_for("main.contacto", sent=1))

    return render_template("landing/contacto.html", **ctx)


@bp.route("/recursos")
def recursos():
    """Recursos y casos — stub MKT-09."""
    from app.landing_service import public_page_context
    from app.public_recursos import MTX_CASES, RECURSOS_INTRO, RECURSOS_LINKS

    ctx = public_page_context()
    ctx["now_year"] = date.today().year
    ctx["recursos_intro"] = RECURSOS_INTRO
    ctx["mtx_cases"] = MTX_CASES
    ctx["recursos_links"] = RECURSOS_LINKS
    return render_template("landing/recursos.html", **ctx)


@bp.route("/dashboard")
def dashboard():
    from app.modules import empresa_solo_inventario

    if current_user.is_authenticated and empresa_solo_inventario(
        getattr(current_user, "empresa", None)
    ):
        return redirect(url_for("inv_comercial.dashboard_inventario", **request.args))

    period = request.args.get("periodo", "mes")
    sector, sector_locked = _sector_for_dashboard()
    dash_filtros = _dashboard_filtros_desde_request()
    machine_ids = _dashboard_machine_ids(sector, dash_filtros)
    hay_filtros_activo = machine_ids is not None
    show_welcome = request.args.get("welcome") == "1" or session.pop("show_welcome", False)
    show_tour = session.pop("show_tour", False)
    ref = _parse_dashboard_ref()
    start, end, period = _period_bounds(period, ref)
    period_label = _period_display_label(period, start, end)
    period_range = (
        f"{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"
        if start != end
        else start.strftime("%d/%m/%Y")
    )
    dash_params = _dashboard_query_params(
        period, ref, sector, sector_locked, dash_filtros
    )
    period_prev_url = url_for(
        "main.dashboard",
        **_dashboard_query_params(
            period, _shift_period_ref(period, ref, -1), sector, sector_locked, dash_filtros
        ),
    )
    period_next_url = url_for(
        "main.dashboard",
        **_dashboard_query_params(
            period, _shift_period_ref(period, ref, 1), sector, sector_locked, dash_filtros
        ),
    )
    period_urls = {
        p: url_for(
            "main.dashboard",
            **_dashboard_query_params(p, ref, sector, sector_locked, dash_filtros),
        )
        for p in ("dia", "semana", "mes", "año")
    }
    sector_urls = (
        {
            s_key: url_for(
                "main.dashboard",
                **_dashboard_query_params(period, ref, s_key, False, dash_filtros),
            )
            for s_key, _ in (
                ("manufactura", "Manufactura"),
                ("logistica", "Logística"),
                ("alimentos", "Alimentos"),
            )
        }
        if not sector_locked
        else {}
    )
    dash_clear_filtros_url = url_for(
        "main.dashboard", **_dashboard_query_params(period, ref, sector, sector_locked)
    )
    hoy = date.today()
    periodo_anios = list(range(hoy.year - 2, hoy.year + 3))

    machines_q = _machines_query_con_filtros(_machines_for_sector_query(sector), dash_filtros)
    total_m = machines_q.count()
    op = machines_q.filter(Machine.status == MachineStatus.OPERATIVO.value).count()
    mant = machines_q.filter(Machine.status == MachineStatus.MANTENIMIENTO.value).count()
    falla = machines_q.filter(Machine.status == MachineStatus.FALLA.value).count()

    if total_m == 0:
        pct_op = pct_mant = pct_falla = 0.0
    else:
        pct_op = round(100.0 * op / total_m, 1)
        pct_mant = round(100.0 * mant / total_m, 1)
        pct_falla = round(100.0 * falla / total_m, 1)

    ot_en_periodo = _wo_in_period_query(start, end, sector, machine_ids).count()
    prev_data = _cumplimiento_preventivo_dashboard(
        start,
        end,
        period_label,
        sector,
        sector_locked=sector_locked,
        machine_ids=machine_ids,
    )
    cumplimiento = prev_data["cumplimiento"]
    total_prev = prev_data["total_prev"]
    prev_completadas = prev_data["prev_completadas"]
    prev_pendientes = prev_data["prev_pendientes"]
    prev_completadas_items = prev_data["prev_completadas_items"]
    if prev_data["sin_programadas"]:
        if ot_en_periodo == 0:
            prev_msg = f"Sin mantenimientos en {period_label}"
        else:
            prev_msg = f"Sin preventivos programados en {period_label}"
    else:
        prev_msg = prev_data["prev_msg"]

    criticos_all = (
        machines_q.filter(Machine.es_critico.is_(True)).order_by(Machine.nombre).all()
    )
    limite_criticos = max(1, (len(criticos_all) + 4) // 5) if criticos_all else 0
    critico_items = []
    for m in criticos_all[:limite_criticos]:
        st = machine_status_meta(m.status)
        critico_items.append(
            {
                "id": m.id,
                "nombre": m.nombre,
                "codigo": m.codigo,
                "ubicacion": m.ubicacion,
                "status_slug": st["slug"],
                "status_short": st["short"],
                "href": url_for("main.activos_edit", id=m.id),
            }
        )

    techs = _filter_empresa(
        Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician
    ).all()
    workload_labels = []
    workload_values = []
    for t in techs:
        wo_tech = _wo_in_period_query(start, end, sector, machine_ids).filter(
            WorkOrder.technician_id == t.id,
            WorkOrder.status.in_(list(WORK_ORDER_PENDING_STATUSES)),
        )
        n = wo_tech.count()
        workload_labels.append(t.nombre)
        workload_values.append(n)

    workload_empty = sum(workload_values) == 0
    workload_total = sum(workload_values)

    pareto_rows = (
        _wo_in_period_query(start, end, sector, machine_ids)
        .join(Machine, Machine.id == WorkOrder.machine_id)
        .filter(func.lower(WorkOrder.tipo) == WorkOrderType.CORRECTIVO.value)
        .with_entities(
            Machine.codigo,
            Machine.nombre,
            func.count(WorkOrder.id).label("total"),
        )
        .group_by(Machine.id, Machine.codigo, Machine.nombre)
        .order_by(func.count(WorkOrder.id).desc(), Machine.nombre.asc())
        .all()
    )
    pareto_items = [
        {"label": codigo, "total": int(total)}
        for codigo, _nombre, total in pareto_rows[:10]
    ]
    if len(pareto_rows) > 10:
        pareto_items.append(
            {"label": "Otros", "total": sum(int(row.total) for row in pareto_rows[10:])}
        )
    pareto_total = sum(item["total"] for item in pareto_items)
    pareto_acumulado = 0
    pareto_porcentajes = []
    for item in pareto_items:
        pareto_acumulado += item["total"]
        pareto_porcentajes.append(
            round(100.0 * pareto_acumulado / pareto_total, 1) if pareto_total else 0
        )

    machines = machines_q.all()
    kpis = _dashboard_kpis(start, end, total_m, op, sector, machine_ids)
    kpis = _attach_plant_kpi_cards(
        kpis,
        start=start,
        end=end,
        sector=sector,
        sector_locked=sector_locked,
        machines=machines,
        operativos=op,
        machine_ids=machine_ids,
    )
    proximos_data = _proximos_mantenimientos(
        start, end, sector=sector, machine_ids=machine_ids
    )
    proximos_mantenimientos = proximos_data["items"]
    proximos_mantenimientos_total = proximos_data["total"]
    proximos_mantenimientos_limite = proximos_data["limit"]
    proximos_mantenimientos_shown = proximos_data["shown"]
    empresa = current_user.empresa if current_user.is_authenticated else None
    if empresa:
        ensure_empresa_sector_setup(empresa)
    eid = empresa.id if empresa else None
    kpi_cards = _build_kpi_cards(kpis, eid, sector)
    dash_resumen = _dashboard_resumen_operativo(
        start, end, sector, machine_ids, op
    )
    dash_resumen_items = [
        {
            "key": "operativos",
            "label": "Activos operativos",
            "value": dash_resumen["activos_operativos"],
            "href": url_for("main.activos_list"),
            "style": "success",
        },
        {
            "key": "abiertas",
            "label": "OT abiertas",
            "value": dash_resumen["ordenes_abiertas"],
            "href": url_for("main.ordenes_list", status=WorkOrderStatus.ABIERTA.value),
            "style": "warning" if dash_resumen["ordenes_abiertas"] else "neutral",
        },
        {
            "key": "vencidas",
            "label": "OT vencidas",
            "value": dash_resumen["ordenes_vencidas"],
            "href": url_for("main.ordenes_list", status=WorkOrderStatus.VENCIDA.value),
            "style": "danger" if dash_resumen["ordenes_vencidas"] else "neutral",
        },
        {
            "key": "preventivos",
            "label": "Preventivos del mes",
            "value": dash_resumen["preventivos_mes"],
            "href": url_for(
                "main.ordenes_list",
                tipo=WorkOrderType.PREVENTIVO.value,
                mes=str(ref.month),
                anio=str(ref.year),
            ),
            "style": "primary",
        },
        {
            "key": "correctivos",
            "label": "Total correctivos",
            "value": dash_resumen["total_correctivos"],
            "href": url_for(
                "main.ordenes_list", tipo=WorkOrderType.CORRECTIVO.value
            ),
            "style": "warning" if dash_resumen["total_correctivos"] else "neutral",
        },
        {
            "key": "horas_correctivos_paro",
            "label": "Horas en correctivos con paro",
            "value": dash_resumen["horas_correctivos_con_paro_label"],
            "href": url_for(
                "main.ordenes_list", tipo=WorkOrderType.CORRECTIVO.value
            ),
            "style": "danger"
            if dash_resumen["minutos_correctivos_con_paro"]
            else "neutral",
        },
        {
            "key": "repuestos",
            "label": "Repuestos bajo mínimo",
            "value": dash_resumen["repuestos_bajo_minimo"],
            "href": url_for("main.reportes"),
            "style": "danger" if dash_resumen["repuestos_bajo_minimo"] else "success",
        },
    ]
    return render_template(
        "dashboard.html",
        periodo=period,
        periodo_ref=ref.isoformat(),
        periodo_label=period_label,
        periodo_rango=period_range,
        period_prev_url=period_prev_url,
        period_next_url=period_next_url,
        period_urls=period_urls,
        sector_urls=sector_urls,
        dash_params=dash_params,
        dash_filtros=dash_filtros,
        hay_filtros_activo=hay_filtros_activo,
        dash_clear_filtros_url=dash_clear_filtros_url,
        periodo_mes=ref.month,
        periodo_anio=ref.year,
        periodo_anios=periodo_anios,
        meses_planeacion=MESES_PLANEACION,
        sector=sector,
        sector_locked=sector_locked,
        sector_label=SECTOR_LABELS.get(sector, sector),
        empresa=empresa,
        show_welcome=show_welcome,
        show_tour=show_tour,
        kpis=kpis,
        kpi_cards=kpi_cards,
        proximos_mantenimientos=proximos_mantenimientos,
        proximos_mantenimientos_total=proximos_mantenimientos_total,
        proximos_mantenimientos_limite=proximos_mantenimientos_limite,
        proximos_mantenimientos_shown=proximos_mantenimientos_shown,
        health={
            "operativos": pct_op,
            "mantenimiento": pct_mant,
            "falla": pct_falla,
            "counts": {"op": op, "mant": mant, "falla": falla, "total": total_m},
        },
        cumplimiento=cumplimiento,
        prev_completadas=prev_completadas,
        prev_pendientes=prev_pendientes,
        prev_completadas_items=prev_completadas_items,
        total_prev=total_prev,
        prev_msg=prev_msg,
        critico_items=critico_items,
        workload_labels=workload_labels,
        workload_values=workload_values,
        workload_total=workload_total,
        workload_empty=workload_empty,
        pareto_labels=[item["label"] for item in pareto_items],
        pareto_values=[item["total"] for item in pareto_items],
        pareto_percentages=pareto_porcentajes,
        pareto_total=pareto_total,
        ot_en_periodo=ot_en_periodo,
        dash_resumen=dash_resumen,
        dash_resumen_items=dash_resumen_items,
    )


# --- Activos ---
def _machine_types_query():
    q = MachineType.query
    sector = _sector_industrial_empresa()
    if sector:
        q = q.filter(MachineType.sector_industrial == sector)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(or_(MachineType.empresa_id == eid, MachineType.empresa_id.is_(None)))
    return q


def _get_machine_type_or_404(type_id: int) -> MachineType:
    return _machine_types_query().filter_by(id=type_id).first_or_404()


def _machine_types_activos():
    return (
        _machine_types_query()
        .filter_by(activo=True)
        .order_by(MachineType.orden, MachineType.nombre)
        .all()
    )


def _machine_types_para_formulario(machine: Optional[Machine] = None):
    base = _machine_types_activos()
    if machine is None or not machine.machine_type_id:
        return base
    if any(mt.id == machine.machine_type_id for mt in base):
        return base
    cur = _machine_types_query().filter_by(id=machine.machine_type_id).first()
    return [cur] + base if cur else base


def _default_machine_type_id() -> Optional[int]:
    q = _machine_types_query().filter_by(activo=True)
    g = q.filter_by(clave="general").first()
    if g:
        return g.id
    first = q.order_by(MachineType.orden, MachineType.nombre).first()
    return first.id if first else None


def _machine_type_id_validado(form) -> Optional[int]:
    raw = form.get("machine_type_id")
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        return None
    mt = _machine_types_query().filter_by(id=tid, activo=True).first()
    return mt.id if mt else None


def _slugify_clave(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return (s or "tipo")[:48]


def _clave_tipo_unica(base: str) -> str:
    c = base[:48]
    n = 2
    while _machine_types_query().filter_by(clave=c).first():
        suffix = f"_{n}"
        c = (base[: 48 - len(suffix)] + suffix)[:48]
        n += 1
    return c


@bp.route("/activos")
def activos_list():
    from app.activos_list_service import activos_kpis_for_machines, build_activos_list_items

    query = _filter_empresa(Machine.query.order_by(Machine.codigo))
    machines = query.all()
    items = build_activos_list_items(machines)
    kpis = activos_kpis_for_machines(machines)
    tipos = _machine_types_activos()
    return render_template(
        "activos/list.html",
        activos_items=items,
        activos_kpis=kpis,
        machine_types=tipos,
    )


@bp.route("/activos/<int:id>/hoja-vida")
def activos_hoja_vida(id):
    """Ficha consolidada y de solo consulta del activo."""
    from sqlalchemy.orm import joinedload

    machine = _filter_empresa(
        Machine.query.options(
            joinedload(Machine.responsable),
            joinedload(Machine.responsable_usuario),
            joinedload(Machine.proveedor_relacionado),
        ).filter_by(id=id),
        Machine,
    ).first_or_404()
    tipos = _machine_types_para_formulario(machine)
    ctx = _activos_form_context(machine, tipos, machine.machine_type_id)
    ordenes = (
        _filter_work_orders_empresa(
            WorkOrder.query.options(
                joinedload(WorkOrder.technician),
                joinedload(WorkOrder.jornadas).joinedload(WorkOrderJornada.technician),
                joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
                joinedload(WorkOrder.informes),
            ).filter(WorkOrder.machine_id == machine.id)
        )
        .order_by(WorkOrder.created_at.desc())
        .all()
    )
    incidentes = (
        _incidents_scope_query()
        .filter(Incident.machine_id == machine.id)
        .order_by(Incident.reportado_en.desc())
        .all()
    )
    ctx.update(
        ordenes=ordenes,
        incidentes=incidentes,
        total_preventivos=sum(1 for orden in ordenes if orden.tipo == "preventivo"),
        total_correctivos=sum(1 for orden in ordenes if orden.tipo == "correctivo"),
        costo_repuestos=sum(orden.costo_repuestos_total for orden in ordenes),
        costo_herramientas=sum(orden.costo_herramientas_total for orden in ordenes),
        costo_mano_obra=sum(orden.costo_mano_obra_total for orden in ordenes),
        costo_servicios=sum(orden.costo_servicio_externo for orden in ordenes),
        costo_total_mantenimiento=sum(orden.costo_total_mantenimiento for orden in ordenes),
        avances_por_ot=_avances_hoja_vida(ordenes),
        status_meta=machine_status_meta(machine.status),
    )
    return render_template("activos/hoja_vida.html", **ctx)


@bp.route("/activos/<int:id>/ficha-tecnica")
def activos_ficha_tecnica(id):
    machine = _filter_empresa(Machine.query.filter_by(id=id), Machine).first_or_404()
    tipos = _machine_types_para_formulario(machine)
    ctx = _activos_form_context(machine, tipos, machine.machine_type_id)
    ctx["status_meta"] = machine_status_meta(machine.status)
    return render_template("activos/ficha_tecnica.html", **ctx)


@bp.route("/activos/<int:id>/ficha-tecnica/pdf")
def activos_ficha_tecnica_pdf(id):
    from io import BytesIO

    from flask import send_file

    from app.maintenance.asset_technical_pdf import export_asset_technical_pdf

    machine = _filter_empresa(Machine.query.filter_by(id=id), Machine).first_or_404()
    tipos = _machine_types_para_formulario(machine)
    ctx = _activos_form_context(machine, tipos, machine.machine_type_id)
    contenido, nombre = export_asset_technical_pdf(
        current_user.empresa,
        machine,
        ctx["campos_personalizados"],
        ctx["valores_campos"],
        ctx["sector_label"],
    )
    return send_file(
        BytesIO(contenido),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nombre,
    )


def _avances_hoja_vida(ordenes):
    """Organiza cada jornada y los repuestos instalados en ella."""
    resultado = {}
    for orden in ordenes:
        jornadas = list(orden.jornadas or [])
        avances = []
        for jornada in jornadas:
            fecha = jornada.fecha_inicio.date() if jornada.fecha_inicio else None
            inicio = jornada.fecha_inicio.strftime("%H:%M") if jornada.fecha_inicio else ""
            fin = jornada.fecha_fin.strftime("%H:%M") if jornada.fecha_fin else ""
            repuestos = [
                linea
                for linea in orden.repuestos
                if (
                    linea.jornada_fecha == fecha
                    and (not linea.jornada_hora_inicio or linea.jornada_hora_inicio == inicio)
                    and (not linea.jornada_hora_fin or linea.jornada_hora_fin == fin)
                )
                or (
                    len(jornadas) == 1
                    and not linea.jornada_fecha
                    and not linea.jornada_hora_inicio
                    and not linea.jornada_hora_fin
                )
            ]
            horas = jornada.duracion_minutos / 60
            avances.append(
                {
                    "jornada": jornada,
                    "fecha": fecha,
                    "hora_inicio": inicio,
                    "hora_fin": fin,
                    "duracion": f"{horas:.2f} h".replace(".00", ""),
                    "repuestos": repuestos,
                }
            )
        resultado[orden.id] = avances
    return resultado


@bp.route("/activos/<int:id>/hoja-vida/pdf")
def activos_hoja_vida_pdf(id):
    from io import BytesIO

    from flask import send_file
    from sqlalchemy.orm import joinedload

    from app.maintenance.asset_life_pdf import export_asset_life_pdf

    machine = _filter_empresa(
        Machine.query.options(
            joinedload(Machine.responsable),
            joinedload(Machine.responsable_usuario),
            joinedload(Machine.proveedor_relacionado),
        ).filter_by(id=id),
        Machine,
    ).first_or_404()
    empresa = current_user.empresa
    tipos = _machine_types_para_formulario(machine)
    ctx = _activos_form_context(machine, tipos, machine.machine_type_id)
    ordenes = (
        _filter_work_orders_empresa(
            WorkOrder.query.options(
                joinedload(WorkOrder.technician),
                joinedload(WorkOrder.jornadas).joinedload(WorkOrderJornada.technician),
                joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
                joinedload(WorkOrder.informes),
            ).filter(WorkOrder.machine_id == machine.id)
        )
        .order_by(WorkOrder.created_at.desc())
        .all()
    )
    incidentes = (
        _incidents_scope_query()
        .filter(Incident.machine_id == machine.id)
        .order_by(Incident.reportado_en.desc())
        .all()
    )
    contenido, nombre = export_asset_life_pdf(
        empresa,
        machine,
        ctx["campos_personalizados"],
        ctx["valores_campos"],
        ordenes,
        incidentes,
        ctx["sector_label"],
        _avances_hoja_vida(ordenes),
    )
    return send_file(
        BytesIO(contenido),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nombre,
    )


@bp.route("/activos/export")
@login_required
def activos_export():
    from io import BytesIO

    from flask import send_file

    from app.maintenance.mrl_exports import export_activos_excel

    machines = _filter_empresa(Machine.query.order_by(Machine.codigo)).all()
    empresa = current_user.empresa
    if not empresa:
        flash("No hay empresa asociada a tu sesión.", "danger")
        return redirect(url_for("main.activos_list"))
    contenido, nombre = export_activos_excel(empresa, machines, usuario=current_user)
    return send_file(
        BytesIO(contenido),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre,
    )


@bp.route("/activos/<int:id>/toggle-critico", methods=["POST"])
def activos_toggle_critico(id):
    m = _filter_empresa(Machine.query.filter_by(id=id)).first_or_404()
    m.es_critico = not m.es_critico
    db.session.commit()
    machines = _filter_empresa(Machine.query).all()
    from app.activos_list_service import activos_kpis_for_machines

    kpis = activos_kpis_for_machines(machines)
    return jsonify(
        {
            "ok": True,
            "id": m.id,
            "es_critico": m.es_critico,
            "criticos": kpis["criticos"],
        }
    )


@bp.route("/activos/api/sugerir-codigo")
def activos_api_sugerir_codigo():
    raw = request.args.get("type_id", "").strip()
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        tid = None
    mt = _machine_types_query().filter_by(id=tid, activo=True).first() if tid else None
    if mt is None:
        mt = _machine_types_query().filter_by(clave="general", activo=True).first()
    pref = (mt.prefijo if mt else "EQ").strip().upper() or "EQ"
    return jsonify(
        {
            "codigo": Machine.sugerir_codigo_siguiente(pref),
            "prefijo": pref,
        }
    )


@bp.route("/activos/nuevo", methods=["GET", "POST"])
def activos_new():
    tipos = _machine_types_activos()
    if not tipos:
        flash("Primero debes crear al menos un tipo de activo en Activos → Tipos de activo.", "warning")
        return redirect(url_for("main.activos_tipo_list"))

    if request.method == "POST":
        mt_id = _machine_type_id_validado(request.form)
        nombre = request.form.get("nombre", "").strip()
        auto_codigo = request.form.get("generar_codigo") == "1"
        mt = MachineType.query.get(mt_id) if mt_id else None
        if auto_codigo and mt:
            codigo = Machine.sugerir_codigo_siguiente(mt.prefijo)
        else:
            codigo = request.form.get("codigo", "").strip()
        if not mt_id:
            flash("Selecciona un tipo de activo válido.", "danger")
        elif not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not codigo:
            flash("Indica un código manual o activa la generación automática.", "danger")
        else:
            eid = _current_empresa_id()
            sede_id = None
            if eid:
                from app.models import Sede

                sede = Sede.query.filter_by(empresa_id=eid, es_principal=True).first()
                sede_id = sede.id if sede else None
            m = Machine(
                codigo=codigo,
                empresa_id=eid,
                sede_id=sede_id,
                machine_type_id=mt_id,
                nombre=nombre,
            )
            err_resp = _apply_machine_base_fields(m, request.form)
            if err_resp:
                flash(err_resp, "danger")
            else:
                db.session.add(m)
                db.session.flush()
                sector = normalizar_sector(current_user.empresa.sector if current_user.empresa else None)
                err_campo = _save_machine_custom_fields(m, request.form, eid, sector, mt_id) if eid else None
                if err_campo:
                    db.session.rollback()
                    flash(err_campo, "danger")
                else:
                    try:
                        _guardar_imagen_activo(m, request.files.get("foto_archivo"))
                        db.session.commit()
                        flash(f"Activo registrado con código {m.codigo}.", "success")
                        return redirect(url_for("main.activos_list"))
                    except ValueError as exc:
                        db.session.rollback()
                        flash(str(exc), "danger")
                    except Exception:
                        db.session.rollback()
                        flash("No se pudo guardar (¿código duplicado?).", "danger")

    preview_id = _default_machine_type_id()
    if request.method == "POST":
        raw = request.form.get("machine_type_id")
        try:
            tid = int(raw)
            if MachineType.query.filter_by(id=tid, activo=True).first():
                preview_id = tid
        except (TypeError, ValueError):
            pass
    mt_sel = MachineType.query.get(preview_id) if preview_id else None
    pref = (mt_sel.prefijo if mt_sel else "EQ").upper()
    ctx = _activos_form_context(
        None, tipos, preview_id, codigo_sugerido=Machine.sugerir_codigo_siguiente(pref)
    )
    return render_template("activos/form.html", **ctx)


@bp.route("/activos/<int:id>/editar", methods=["GET", "POST"])
def activos_edit(id):
    from sqlalchemy.orm import joinedload

    m = _filter_empresa(
        Machine.query.options(joinedload(Machine.responsable)).filter_by(id=id), Machine
    ).first_or_404()
    tipos = _machine_types_para_formulario(m)
    if not tipos:
        flash("No hay tipos de activo activos.", "warning")
        return redirect(url_for("main.activos_tipo_list"))

    if request.method == "POST":
        mt_id = _machine_type_id_validado(request.form)
        m.codigo = request.form.get("codigo", "").strip()
        if mt_id:
            m.machine_type_id = mt_id
        _apply_err = _apply_machine_base_fields(m, request.form)
        if _apply_err:
            flash(_apply_err, "danger")
        elif not m.codigo or not m.nombre:
            flash("Código y nombre son obligatorios.", "danger")
        elif not mt_id:
            flash("Selecciona un tipo de activo válido.", "danger")
        else:
            eid = _current_empresa_id()
            sector = normalizar_sector(current_user.empresa.sector if current_user.empresa else None)
            err_campo = (
                _save_machine_custom_fields(m, request.form, eid, sector, mt_id) if eid else None
            )
            if err_campo:
                flash(err_campo, "danger")
            else:
                try:
                    _guardar_imagen_activo(m, request.files.get("foto_archivo"))
                    db.session.commit()
                    flash("Activo actualizado.", "success")
                    return redirect(url_for("main.activos_list"))
                except ValueError as exc:
                    db.session.rollback()
                    flash(str(exc), "danger")
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")
    ctx = _activos_form_context(
        m,
        tipos,
        m.machine_type_id,
        codigo_sugerido=Machine.sugerir_codigo_siguiente(
            (m.machine_type.prefijo if m.machine_type else "EQ").upper()
        ),
    )
    ctx["activo_historial_ot"] = (
        WorkOrder.query.filter_by(machine_id=m.id)
        .order_by(WorkOrder.created_at.desc())
        .limit(10)
        .all()
    )
    ctx["activo_historial_incidencias"] = (
        Incident.query.filter_by(machine_id=m.id)
        .order_by(Incident.reportado_en.desc())
        .limit(5)
        .all()
    )
    return render_template("activos/form.html", **ctx)


@bp.route("/activos/api/campos")
def activos_api_campos():
    if not current_user.is_authenticated:
        return jsonify([]), 401
    empresa = current_user.empresa
    if not empresa:
        return jsonify([])
    try:
        type_id = int(request.args.get("type_id", 0))
    except (TypeError, ValueError):
        type_id = 0
    campos = campos_para_tipo(empresa.id, empresa.sector, type_id or None)
    return jsonify(
        [
            {
                "id": c.id,
                "nombre": c.nombre,
                "tipo": c.tipo,
                "obligatorio": c.obligatorio,
                "opciones": c.opciones_lista(),
            }
            for c in campos
        ]
    )


@bp.route("/activos/<int:id>/eliminar", methods=["POST"])
def activos_delete(id):
    m = _filter_empresa(Machine.query.filter_by(id=id), Machine).first_or_404()
    db.session.delete(m)
    db.session.commit()
    flash("Activo eliminado.", "info")
    return redirect(url_for("main.activos_list"))


# --- Tipos de activo (catálogo) ---
@bp.route("/activos/tipos")
def activos_tipo_list():
    sector = _sector_industrial_empresa()
    tipos = _machine_types_query().order_by(MachineType.orden, MachineType.nombre).all()
    return render_template(
        "activos/tipos_list.html",
        tipos=tipos,
        sector_labels=SECTOR_LABELS,
        sector_filtro=sector,
        sector_filtro_label=SECTOR_LABELS.get(sector, sector) if sector else None,
    )


@bp.route("/activos/tipos/nuevo", methods=["GET", "POST"])
def activos_tipo_new():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        prefijo = (request.form.get("prefijo", "").strip() or "").upper()
        try:
            orden = int(request.form.get("orden") or 0)
        except ValueError:
            orden = 0
        if not nombre:
            flash("El nombre del tipo es obligatorio.", "danger")
        elif not re.match(r"^[A-Z0-9]{2,8}$", prefijo):
            flash("El prefijo debe tener entre 2 y 8 letras o números (ej. BM, CP12).", "danger")
        else:
            base_clave = _slugify_clave(nombre)
            clave = _clave_tipo_unica(base_clave)
            sector = _sector_industrial_empresa() or _parse_sector(
                request.form.get("sector_industrial")
            )
            eid = _current_empresa_id()
            db.session.add(
                MachineType(
                    clave=clave,
                    nombre=nombre,
                    prefijo=prefijo,
                    orden=orden,
                    activo=True,
                    sector_industrial=sector,
                    empresa_id=eid,
                )
            )
            try:
                db.session.commit()
                flash("Tipo de activo creado.", "success")
                return redirect(url_for("main.activos_tipo_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿prefijo o clave duplicado?).", "danger")
    siguiente_orden = db.session.query(func.max(MachineType.orden)).scalar()
    siguiente_orden = (siguiente_orden or 0) + 1
    sector_emp = _sector_industrial_empresa()
    return render_template(
        "activos/tipo_form.html",
        tipo=None,
        siguiente_orden=siguiente_orden,
        sectores_nav=_sectores_para_tipo_form(),
        sector_locked=sector_emp is not None,
        sector_default=sector_emp or IndustrialSector.MANUFACTURA.value,
    )


@bp.route("/activos/tipos/<int:id>/editar", methods=["GET", "POST"])
def activos_tipo_edit(id):
    t = _get_machine_type_or_404(id)
    if not _tipo_pertenece_sector_empresa(t):
        flash("Este tipo no pertenece al sector industrial de tu empresa.", "warning")
        return redirect(url_for("main.activos_tipo_list"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        prefijo = (request.form.get("prefijo", "").strip() or "").upper()
        try:
            orden = int(request.form.get("orden") or 0)
        except ValueError:
            orden = t.orden
        activo = bool(request.form.get("activo"))
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not re.match(r"^[A-Z0-9]{2,8}$", prefijo):
            flash("El prefijo debe tener entre 2 y 8 letras o números.", "danger")
        else:
            other = _machine_types_query().filter(
                MachineType.prefijo == prefijo, MachineType.id != t.id
            ).first()
            if other:
                flash("Ese prefijo ya lo usa otro tipo.", "danger")
            else:
                t.nombre = nombre
                t.prefijo = prefijo
                t.orden = orden
                t.activo = activo
                sector_emp = _sector_industrial_empresa()
                t.sector_industrial = sector_emp or _parse_sector(
                    request.form.get("sector_industrial")
                )
                try:
                    db.session.commit()
                    flash("Tipo actualizado.", "success")
                    return redirect(url_for("main.activos_tipo_list"))
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")
    sector_emp = _sector_industrial_empresa()
    return render_template(
        "activos/tipo_form.html",
        tipo=t,
        siguiente_orden=t.orden,
        sectores_nav=_sectores_para_tipo_form(),
        sector_locked=sector_emp is not None,
        sector_default=sector_emp or t.sector_industrial,
    )


@bp.route("/activos/tipos/<int:id>/eliminar", methods=["POST"])
def activos_tipo_delete(id):
    t = _get_machine_type_or_404(id)
    if not _tipo_pertenece_sector_empresa(t):
        flash("Este tipo no pertenece al sector industrial de tu empresa.", "warning")
        return redirect(url_for("main.activos_tipo_list"))
    if t.machines.count() > 0:
        flash("No se puede eliminar: hay equipos asignados a este tipo. Desactívalo en su lugar.", "danger")
        return redirect(url_for("main.activos_tipo_list"))
    db.session.delete(t)
    db.session.commit()
    flash("Tipo eliminado.", "info")
    return redirect(url_for("main.activos_tipo_list"))


def _jornadas_para_formulario(wo: Optional[WorkOrder]) -> list:
    """Filas de jornadas para el formulario (sesiones guardadas o legado de una sola)."""
    if wo is None:
        return []
    if wo.jornadas:
        return list(wo.jornadas)
    if wo.fecha_inicio and wo.fecha_cierre:
        return [
            WorkOrderJornada(
                orden=1,
                fecha_inicio=wo.fecha_inicio,
                fecha_fin=wo.fecha_cierre,
            )
        ]
    return []


def _jornada_a_dict(j: WorkOrderJornada) -> dict:
    return {
        "fecha": j.fecha_inicio.strftime("%Y-%m-%d"),
        "hora_inicio": j.fecha_inicio.strftime("%H:%M"),
        "hora_fin": j.fecha_fin.strftime("%H:%M"),
        "technician_id": str(j.technician_id) if j.technician_id else "otro",
        "tecnico_nombre": j.tecnico_nombre or "",
        "tarifa_hora_aplicada": j.tarifa_hora_efectiva,
        "costo_mano_obra_manual": (
            float(j.costo_mano_obra_manual)
            if j.costo_mano_obra_manual is not None
            else None
        ),
        "costo_herramientas": j.costo_herramientas_total,
        "recibido_por": j.recibido_por or "",
        "requirio_paro": bool(j.requirio_paro),
        "descripcion": j.descripcion_avance or "",
    }


def _parse_jornadas_json(wo: Optional[WorkOrder] = None) -> Tuple[list[dict], Optional[str]]:
    raw = (request.form.get("jornadas_json") or "[]").strip()
    try:
        items = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        return [], "Los datos de las jornadas no son válidos."
    if not isinstance(items, list):
        return [], "Los datos de las jornadas no son válidos."

    parsed: list[dict] = []
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return [], f"Jornada {i}: formato inválido."
        fecha = (item.get("fecha") or "").strip()
        hora_ini = (item.get("hora_inicio") or "").strip()
        hora_fin = (item.get("hora_fin") or "").strip()
        if not fecha or not hora_ini or not hora_fin:
            return [], f"Jornada {i}: completa fecha, hora inicio y hora fin."
        inicio = combinar_fecha_hora(fecha, hora_ini)
        fin = combinar_fecha_hora(fecha, hora_fin)
        if not inicio or not fin:
            return [], f"Jornada {i}: fecha u hora no válidas."
        if fin <= inicio:
            return [], f"Jornada {i}: la hora fin debe ser posterior a la hora inicio."

        tech_raw = item.get("technician_id")
        tech_id: Optional[int] = None
        if tech_raw not in (None, "", "otro"):
            try:
                tech_id = int(tech_raw)
            except (TypeError, ValueError):
                return [], f"Jornada {i}: técnico no válido."

        technician = None
        if tech_id is not None:
            technician = _filter_empresa(
                Technician.query.filter_by(id=tech_id), Technician
            ).first()
            if not technician:
                return [], f"Jornada {i}: técnico no pertenece a tu empresa."

        nombre = (item.get("tecnico_nombre") or "").strip()
        if tech_id is None and not nombre:
            return [], f"Jornada {i}: indica el técnico realizador o su nombre."
        recibido_por = (item.get("recibido_por") or "").strip()
        if not recibido_por:
            return [], f"Jornada {i}: indica quién recibió el avance."
        try:
            costo_herramientas = round(float(item.get("costo_herramientas") or 0), 2)
        except (TypeError, ValueError):
            return [], f"Jornada {i}: el costo de herramientas no es válido."
        if not math.isfinite(costo_herramientas):
            return [], f"Jornada {i}: el costo de herramientas no es válido."
        if costo_herramientas < 0:
            return [], f"Jornada {i}: el costo de herramientas no puede ser negativo."
        if costo_herramientas > 999_999_999_999.99:
            return [], f"Jornada {i}: el costo de herramientas supera el máximo permitido."

        costo_mano_obra_manual = None
        permite_mdo_manual = bool(
            wo
            and wo.es_ejecucion_externa
        )
        if permite_mdo_manual:
            try:
                costo_mano_obra_manual = round(
                    float(item.get("costo_mano_obra_manual") or 0), 2
                )
            except (TypeError, ValueError):
                return [], f"Jornada {i}: el costo MDO no es válido."
            if not math.isfinite(costo_mano_obra_manual) or costo_mano_obra_manual < 0:
                return [], f"Jornada {i}: el costo MDO debe ser un valor válido y no negativo."
            if costo_mano_obra_manual > 999_999_999_999.99:
                return [], f"Jornada {i}: el costo MDO supera el máximo permitido."

        parsed.append(
            {
                "fecha_inicio": inicio,
                "fecha_fin": fin,
                "technician_id": tech_id,
                "tarifa_hora_aplicada": float(
                    technician.user.tarifa_hora or 0
                ) if technician and technician.user else 0.0,
                "costo_mano_obra_manual": costo_mano_obra_manual,
                "costo_herramientas": costo_herramientas,
                "tecnico_nombre": nombre if tech_id is None else "",
                "recibido_por": recibido_por,
                "requirio_paro": bool(item.get("requirio_paro")),
                "descripcion_avance": (item.get("descripcion") or "").strip(),
            }
        )
    return parsed, None


def _guardar_jornadas_orden(wo: WorkOrder) -> Optional[str]:
    """Persiste sesiones de trabajo y actualiza tiempo gastado en la OT."""
    wo.usar_jornada_laboral = False

    if request.form.get("tiempo_manual") == "1":
        try:
            h = max(0, int(request.form.get("tiempo_horas", 0) or 0))
            m = max(0, min(59, int(request.form.get("tiempo_minutos", 0) or 0)))
            wo.tiempo_gastado_minutos = h * 60 + m
        except (TypeError, ValueError):
            pass
        return None

    sesiones, err = _parse_jornadas_json(wo)
    if err:
        return err

    tarifas_existentes = {
        (j.fecha_inicio, j.fecha_fin, j.technician_id): j.tarifa_hora_aplicada
        for j in wo.jornadas
        if j.tarifa_hora_aplicada is not None
    }
    wo.jornadas.clear()
    if not sesiones:
        wo.fecha_inicio = None
        wo.fecha_cierre = None
        wo.tiempo_gastado_minutos = None
        return None

    for n, s in enumerate(sesiones, start=1):
        clave_jornada = (s["fecha_inicio"], s["fecha_fin"], s["technician_id"])
        wo.jornadas.append(
            WorkOrderJornada(
                orden=n,
                fecha_inicio=s["fecha_inicio"],
                fecha_fin=s["fecha_fin"],
                technician_id=s["technician_id"],
                tarifa_hora_aplicada=tarifas_existentes.get(
                    clave_jornada, s["tarifa_hora_aplicada"]
                ),
                costo_mano_obra_manual=s["costo_mano_obra_manual"],
                costo_herramientas=s["costo_herramientas"],
                tecnico_nombre=s["tecnico_nombre"],
                recibido_por=s["recibido_por"],
                requirio_paro=s["requirio_paro"],
                descripcion_avance=s["descripcion_avance"],
            )
        )
    wo.fecha_inicio = sesiones[0]["fecha_inicio"]
    wo.fecha_cierre = sesiones[-1]["fecha_fin"]
    wo.tiempo_gastado_minutos = total_minutos_jornadas(wo.jornadas)
    wo.maquina_requirio_paro = any(bool(j.requirio_paro) for j in wo.jornadas)
    return None


def _aplicar_estado_orden_desde_formulario(wo: WorkOrder) -> None:
    from app.work_order_status import resolver_estado_al_guardar

    tiene_jornadas = request.form.get("tiempo_manual") != "1" and bool(wo.jornadas)
    jornada_estado = (request.form.get("jornada_estado_ot") or "").strip()
    if tiene_jornadas and not jornada_estado:
        jornada_estado = WorkOrderStatus.EN_PROCESO.value
    resolver_estado_al_guardar(
        wo,
        status_manual=request.form.get("status_manual"),
        jornada_estado_ot=jornada_estado or None,
        tiene_jornadas=tiene_jornadas,
    )
    _cerrar_incidente_vinculado_si_ot_terminal(wo)


def _cerrar_incidente_vinculado_si_ot_terminal(wo: WorkOrder) -> None:
    """Cierra el incidente de origen cuando su OT queda completada o cerrada."""
    if (wo.status or "").strip().lower() not in WORK_ORDER_TERMINAL_STATUSES:
        return
    incidente = getattr(wo, "incidencia_origen", None)
    if not incidente or incidente.estado in (
        IncidentEstado.CERRADO.value,
        IncidentEstado.CANCELADO.value,
    ):
        return

    ahora = datetime.utcnow()
    detalle = f"Cierre automático por finalización de la OT {wo.numero or wo.id}."
    incidente.resuelto = True
    incidente.resuelto_en = incidente.resuelto_en or ahora
    incidente.cerrado_en = ahora
    incidente.resuelto_por_id = (
        current_user.id if current_user.is_authenticated else incidente.resuelto_por_id
    )
    incidente.notas_resolucion = incidente.notas_resolucion or detalle
    incidente.motivo_cierre = detalle
    _cambiar_estado(
        incidente,
        IncidentEstado.CERRADO.value,
        "cerrado_por_ot",
        detalle,
    )


def _spare_parts_para_formulario() -> list:
    return _filter_empresa(SparePart.query.order_by(SparePart.nombre), SparePart).all()


def _planeacion_filas(anio: int, mes: int) -> list[dict]:
    machines = _filter_empresa(Machine.query.order_by(Machine.codigo), Machine).all()
    eid = _current_empresa_id()
    q = MachineMonthlyPlan.query.filter_by(anio=anio, mes=mes)
    if eid:
        q = q.filter(MachineMonthlyPlan.empresa_id == eid)
    plans = {p.machine_id: p for p in q.all()}
    filas = []
    for m in machines:
        plan = plans.get(m.id)
        filas.append(
            {
                "machine": m,
                "plan": plan,
                "horas_meta": plan.horas_meta if plan else None,
                "configurado": bool(plan and plan.configurado),
                "solo_lectura": bool(plan and plan.solo_lectura),
            }
        )
    return filas


def _parse_costo(raw: str) -> float:
    s = (raw or "0").strip().replace(",", ".")
    try:
        return max(0.0, round(float(s), 2))
    except ValueError:
        return 0.0


def _repuesto_linea_a_dict(line: WorkOrderRepuesto) -> dict:
    p = line.spare_part
    cu = line.costo_unitario_linea
    return {
        "spare_part_id": line.spare_part_id,
        "cantidad": line.cantidad,
        "notas": line.notas or "",
        "sku": p.sku if p else "",
        "nombre": p.nombre if p else "",
        "costo_unitario": cu,
        "costo_total": line.costo_total_linea,
        "jornada_fecha": line.jornada_fecha.isoformat() if line.jornada_fecha else "",
        "jornada_hora_inicio": line.jornada_hora_inicio or "",
        "jornada_hora_fin": line.jornada_hora_fin or "",
        "jornada_tecnico": line.jornada_tecnico or "",
    }


def _revertir_repuestos_stock(wo: WorkOrder) -> None:
    for line in list(wo.repuestos):
        if line.spare_part:
            line.spare_part.cantidad = (line.spare_part.cantidad or 0) + line.cantidad
        db.session.delete(line)
    db.session.flush()


def _parse_repuestos_json() -> Tuple[list[dict], Optional[str]]:
    raw = (request.form.get("repuestos_json") or "[]").strip()
    try:
        items = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        return [], "Los datos de repuestos no son válidos."
    if not isinstance(items, list):
        return [], "Los datos de repuestos no son válidos."

    parsed: list[dict] = []
    vistos: set[int] = set()
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return [], f"Repuesto línea {i}: formato inválido."
        try:
            part_id = int(item.get("spare_part_id") or 0)
        except (TypeError, ValueError):
            return [], f"Repuesto línea {i}: selecciona un repuesto válido."
        if part_id <= 0:
            return [], f"Repuesto línea {i}: selecciona un repuesto."
        if part_id in vistos:
            return [], f"Repuesto línea {i}: no repitas el mismo ítem."
        vistos.add(part_id)
        try:
            qty = int(item.get("cantidad") or 0)
        except (TypeError, ValueError):
            return [], f"Repuesto línea {i}: cantidad inválida."
        if qty <= 0:
            return [], f"Repuesto línea {i}: la cantidad debe ser mayor a cero."
        parsed.append(
            {
                "spare_part_id": part_id,
                "cantidad": qty,
                "notas": (item.get("notas") or "").strip()[:255],
                "jornada_fecha": (item.get("jornada_fecha") or "").strip(),
                "jornada_hora_inicio": (item.get("jornada_hora_inicio") or "").strip()[:5],
                "jornada_hora_fin": (item.get("jornada_hora_fin") or "").strip()[:5],
                "jornada_tecnico": (item.get("jornada_tecnico") or "").strip()[:200],
            }
        )
    return parsed, None


def _guardar_repuestos_orden(wo: WorkOrder) -> Optional[str]:
    """Descuenta inventario por repuestos en OT correctivas."""
    if wo.tipo != WorkOrderType.CORRECTIVO.value:
        if wo.repuestos:
            _revertir_repuestos_stock(wo)
        return None

    costos_historicos = {
        (
            line.spare_part_id,
            int(line.cantidad or 0),
            line.jornada_fecha,
            line.jornada_hora_inicio or "",
            line.jornada_hora_fin or "",
        ): line.costo_unitario_linea
        for line in wo.repuestos
    }
    _revertir_repuestos_stock(wo)

    if request.form.get("usa_repuestos") != "1":
        return None

    items, err = _parse_repuestos_json()
    if err:
        return err
    if not items:
        return "Indica al menos un repuesto o desmarca «Requiere cambio de repuestos»."

    eid = _current_empresa_id()
    for item in items:
        part = db.session.get(SparePart, item["spare_part_id"])
        if part is None:
            return "Uno de los repuestos seleccionados ya no existe."
        if eid and part.empresa_id != eid:
            return f"El repuesto {part.sku} no pertenece a tu empresa."
        if (part.cantidad or 0) < item["cantidad"]:
            return (
                f"Stock insuficiente para {part.nombre} "
                f"(disponible: {part.cantidad} {part.unidad or 'pza'})."
            )

    for item in items:
        part = db.session.get(SparePart, item["spare_part_id"])
        jornada = wo.jornadas[-1] if wo.jornadas else None
        jornada_fecha = None
        if item["jornada_fecha"]:
            try:
                jornada_fecha = datetime.strptime(item["jornada_fecha"], "%Y-%m-%d").date()
            except ValueError:
                jornada_fecha = None
        if jornada_fecha is None and jornada:
            jornada_fecha = jornada.fecha_inicio.date()
        jornada_hora_inicio = item["jornada_hora_inicio"] or (
            jornada.fecha_inicio.strftime("%H:%M") if jornada else ""
        )
        jornada_hora_fin = item["jornada_hora_fin"] or (
            jornada.fecha_fin.strftime("%H:%M") if jornada else ""
        )
        costo_aplicado = costos_historicos.get(
            (
                part.id,
                item["cantidad"],
                jornada_fecha,
                jornada_hora_inicio,
                jornada_hora_fin,
            ),
            float(part.costo_unitario or 0),
        )
        part.cantidad = (part.cantidad or 0) - item["cantidad"]
        wo.repuestos.append(
            WorkOrderRepuesto(
                spare_part_id=part.id,
                cantidad=item["cantidad"],
                costo_unitario_aplicado=costo_aplicado,
                notas=item["notas"],
                jornada_fecha=jornada_fecha,
                jornada_hora_inicio=jornada_hora_inicio,
                jornada_hora_fin=jornada_hora_fin,
                jornada_tecnico=item["jornada_tecnico"] or (jornada.tecnico_label if jornada else ""),
            )
        )
    return None


def _work_order_responsables_desde_form(form) -> dict:
    return {
        "autorizado_por": (form.get("autorizado_por") or "").strip(),
        "recibido_por": (form.get("recibido_por") or "").strip(),
        "empresa_tercerizada": (form.get("empresa_tercerizada") or "").strip(),
    }


def _maquina_requirio_paro_desde_form(form, tipo: str) -> bool:
    if tipo != WorkOrderType.CORRECTIVO.value:
        return False
    return (form.get("maquina_requirio_paro") or "").strip() == "1"


def _proveedores_para_ot() -> list[Proveedor]:
    return (
        _filter_empresa(
            Proveedor.query.filter(
                Proveedor.activo.is_(True),
                Proveedor.tipo.in_(
                    (ProveedorTipo.SERVICIO.value, ProveedorTipo.AMBOS.value)
                ),
            ).order_by(Proveedor.nombre),
            Proveedor,
        ).all()
    )


def _proveedor_ot_dict(p: Proveedor) -> dict:
    tm = proveedor_tipo_meta(p.tipo)
    return {
        "id": p.id,
        "nombre": p.nombre,
        "nit": p.nit or "",
        "contacto_nombre": p.contacto_nombre or "",
        "contacto_email": p.contacto_email or "",
        "contacto_telefono": p.contacto_telefono or "",
        "tipo": p.tipo,
        "tipo_label": tm["label"],
        "badge_class": tm["badge_class"],
        "iniciales": p.iniciales,
    }


def _historial_proveedor_ot(proveedor_id: int, limit: int = 5) -> list:
    """OT cerradas/completadas ejecutadas por un proveedor concreto (no todas las del sistema)."""
    return (
        _filter_work_orders_empresa(
            WorkOrder.query.filter(
                WorkOrder.proveedor_id == proveedor_id,
                WorkOrder.ejecucion_tipo == WorkOrderEjecucionTipo.EXTERNO.value,
                WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
            )
        )
        .order_by(
            WorkOrder.fecha_cierre.desc(),
            WorkOrder.fecha_programada.desc(),
            WorkOrder.id.desc(),
        )
        .limit(limit)
        .all()
    )


def _historial_proveedor_json(proveedores: list[Proveedor], wo: Optional[WorkOrder] = None) -> dict:
    _ = wo
    out: dict[str, list] = {}
    for p in proveedores:
        out[str(p.id)] = _historial_proveedor_payload(_historial_proveedor_ot(p.id))
    return out


def _historial_proveedor_payload(rows: list) -> list[dict]:
    return [
        {
            "numero": w.numero or f"OT-{w.id}",
            "titulo": w.titulo,
            "status": w.status,
            "status_label": wo_status_meta(w.status)["label"],
            "fecha": (
                w.fecha_cierre.strftime("%d/%m/%Y")
                if w.fecha_cierre
                else (
                    w.fecha_programada.strftime("%d/%m/%Y")
                    if w.fecha_programada
                    else ""
                )
            ),
        }
        for w in rows
    ]


def _aplicar_ejecucion_desde_form(wo: WorkOrder, form) -> Optional[str]:
    ejec = (form.get("ejecucion_tipo") or WorkOrderEjecucionTipo.INTERNO.value).strip().lower()
    if ejec not in (WorkOrderEjecucionTipo.INTERNO.value, WorkOrderEjecucionTipo.EXTERNO.value):
        ejec = WorkOrderEjecucionTipo.INTERNO.value
    wo.ejecucion_tipo = ejec

    fl = (form.get("fecha_limite") or "").strip()
    if fl:
        try:
            wo.fecha_limite = datetime.strptime(fl, "%Y-%m-%d").date()
        except ValueError:
            wo.fecha_limite = None
    else:
        wo.fecha_limite = None

    if ejec == WorkOrderEjecucionTipo.INTERNO.value:
        wo.proveedor_id = None
        wo.supervisor_technician_id = None
        wo.contacto_proveedor = ""
        wo.numero_cotizacion = ""
        wo.costo_estimado = None
        wo.proveedor_incluye_insumos = False
        wo.empresa_tercerizada = ""
        wo.technician_id = (
            int(form["technician_id"]) if form.get("technician_id") else None
        )
        err = _validar_technician_id_tenant(wo.technician_id)
        if err:
            return err
        return None

    wo.technician_id = None
    pid_raw = (form.get("proveedor_id") or "").strip()
    if not pid_raw.isdigit():
        return "Selecciona un proveedor externo."
    proveedor = _filter_empresa(
        Proveedor.query.filter_by(id=int(pid_raw), activo=True), Proveedor
    ).first()
    if not proveedor:
        return "Proveedor no válido o inactivo."
    wo.proveedor_id = proveedor.id
    wo.empresa_tercerizada = proveedor.nombre
    wo.supervisor_technician_id = (
        int(form["supervisor_technician_id"])
        if form.get("supervisor_technician_id")
        else None
    )
    err = _validar_technician_id_tenant(wo.supervisor_technician_id, "supervisor")
    if err:
        return err
    wo.contacto_proveedor = (form.get("contacto_proveedor") or "").strip() or (
        proveedor.contacto_nombre or ""
    )
    wo.numero_cotizacion = (form.get("numero_cotizacion") or "").strip()
    raw_est = (form.get("costo_estimado") or "").strip()
    wo.costo_estimado = _parse_costo(raw_est) if raw_est else None
    wo.proveedor_incluye_insumos = form.get("proveedor_incluye_insumos") == "1"
    raw_real = (form.get("costo_real") or "").strip()
    if raw_real:
        wo.costo_real = _parse_costo(raw_real)
    elif wo.costo_real is None:
        wo.costo_real = None
    return None


def _sector_empresa_actual() -> str:
    if current_user.is_authenticated and getattr(current_user, "empresa", None):
        return normalizar_sector(current_user.empresa.sector)
    return normalizar_sector(None)


def _responsables_por_maquinas_ot(machines: Optional[list]) -> dict[int, str]:
    if not machines:
        return {}
    eid = _current_empresa_id()
    if not eid:
        return {m.id: "" for m in machines}
    return responsables_display_por_maquinas(machines, eid, _sector_empresa_actual())


def _jornada_estado_desde_status(status: str | None) -> str:
    key = (status or "").strip().lower()
    if key in (WorkOrderStatus.COMPLETADO.value, WorkOrderStatus.CERRADA.value):
        return WorkOrderStatus.COMPLETADO.value
    if key == WorkOrderStatus.ABIERTA.value:
        return WorkOrderStatus.ABIERTA.value
    return WorkOrderStatus.EN_PROCESO.value


def _orden_form_context(
    wo: Optional[WorkOrder], technicians: list, machines: Optional[list] = None
) -> dict:
    responsables_map = _responsables_por_maquinas_ot(machines)
    mins = wo_tiempo_gastado_minutos(wo) if wo else None
    th, tm = minutos_a_horas_minutos(mins)
    jornadas_inicial = [_jornada_a_dict(j) for j in _jornadas_para_formulario(wo)]
    jornada_estado_inicial = (
        _jornada_estado_desde_status(wo.status) if wo and jornadas_inicial else ""
    )
    catalogo = _spare_parts_para_formulario()
    repuestos_inicial = [_repuesto_linea_a_dict(r) for r in (wo.repuestos if wo else [])]
    fv = wo.frecuencia_valor if wo and wo.frecuencia_valor else 1
    fu = wo.frecuencia_unidad if wo and wo.frecuencia_unidad else "meses"
    if wo and wo.preventive_plan and not wo.frecuencia_valor:
        fv = wo.preventive_plan.frecuencia_valor or 1
        fu = wo.preventive_plan.frecuencia_unidad or "meses"
    proveedores_ot = _proveedores_para_ot()
    ejecucion_tipo = (
        wo.ejecucion_tipo if wo else WorkOrderEjecucionTipo.INTERNO.value
    )
    return {
        "jornadas_inicial": jornadas_inicial,
        "jornada_estado_inicial": jornada_estado_inicial,
        "repuestos_inicial": repuestos_inicial,
        "usa_repuestos_inicial": bool(wo and wo.repuestos),
        "frecuencia_unidades": PREVENTIVE_FREQUENCY_UNITS,
        "frecuencia_valor": fv,
        "frecuencia_unidad": fu,
        "frecuencia_label": frecuencia_label(fv, fu),
        "tiempo_horas": th,
        "tiempo_minutos": tm,
        "formatear_duracion": formatear_duracion,
        "responsables_por_maquina": responsables_map,
        "responsable_activo_nombre": (
            responsables_map.get(wo.machine_id, "") if wo and wo.machine_id else ""
        ),
        "technicians_data": [
            {
                "id": t.id,
                "nombre": t.nombre,
                "tarifa_hora": float(t.user.tarifa_hora or 0) if t.user else 0.0,
            }
            for t in technicians
        ],
        "repuestos_catalog_data": [
            {
                "id": p.id,
                "sku": p.sku,
                "nombre": p.nombre,
                "stock": p.cantidad or 0,
                "unidad": p.unidad or "pza",
                "costo_unitario": float(p.costo_unitario or 0),
            }
            for p in catalogo
        ],
        "proveedores_ot": proveedores_ot,
        "proveedores_ot_data": [_proveedor_ot_dict(p) for p in proveedores_ot],
        "ejecucion_tipo": ejecucion_tipo,
        "simbolo_moneda_ot": simbolo_moneda_input(
            current_user.empresa.moneda
            if current_user.is_authenticated and current_user.empresa
            else "COP"
        ),
        "wo_es_terminal": bool(
            wo and wo.status in WORK_ORDER_TERMINAL_STATUSES
        ),
    }


# --- Órdenes ---
@bp.route("/ordenes/planeacion", methods=["GET", "POST"])
def ordenes_planeacion():
    mes, anio = parse_mes_anio(
        request.values.get("mes", ""),
        request.values.get("anio", ""),
    )
    max_h = max_horas_mes(anio, mes)
    eid = _current_empresa_id()

    if request.method == "POST":
        accion = (request.form.get("accion") or "guardar").strip()

        if accion == "cargar_anterior":
            prev_anio, prev_mes = mes_anterior(anio, mes)
            prev_q = MachineMonthlyPlan.query.filter_by(anio=prev_anio, mes=prev_mes)
            if eid:
                prev_q = prev_q.filter(MachineMonthlyPlan.empresa_id == eid)
            prev_map = {p.machine_id: p for p in prev_q.all()}
            copiados = 0
            for m in _filter_empresa(Machine.query, Machine).all():
                prev = prev_map.get(m.id)
                if not prev or prev.horas_meta is None:
                    continue
                plan = MachineMonthlyPlan.query.filter_by(
                    machine_id=m.id, anio=anio, mes=mes
                ).first()
                if plan and plan.solo_lectura:
                    continue
                if not plan:
                    plan = MachineMonthlyPlan(
                        empresa_id=eid or m.empresa_id,
                        machine_id=m.id,
                        anio=anio,
                        mes=mes,
                    )
                    db.session.add(plan)
                plan.horas_meta = float(prev.horas_meta)
                plan.guardado_at = None
                copiados += 1
            db.session.commit()
            prev_label = dict(MESES_PLANEACION).get(prev_mes, str(prev_mes))
            flash(
                f"Horas de {prev_label} {prev_anio} cargadas en {copiados} equipo(s). "
                "Revisa y usa «Guardar seleccionadas» para fijar la meta.",
                "success",
            )
            return redirect(url_for("main.ordenes_planeacion", mes=mes, anio=anio))

        selected_ids = []
        for key in request.form:
            if key.startswith("sel_") and request.form.get(key):
                try:
                    selected_ids.append(int(key[4:]))
                except ValueError:
                    pass
        errores: list[str] = []
        guardados = 0
        for mid in selected_ids:
            raw = (request.form.get(f"horas_{mid}") or "").strip()
            if not raw:
                errores.append("Indica las horas en todas las filas seleccionadas.")
                break
            try:
                horas = round(float(raw.replace(",", ".")), 2)
            except ValueError:
                errores.append("Hay valores de horas no válidos.")
                break
            if horas < 0 or horas > max_h:
                errores.append(f"Cada meta debe estar entre 0 y {max_h} h para este mes.")
                break
            plan = MachineMonthlyPlan.query.filter_by(
                machine_id=mid, anio=anio, mes=mes
            ).first()
            if plan and plan.solo_lectura:
                continue
            machine = db.session.get(Machine, mid)
            if not machine:
                continue
            if not plan:
                plan = MachineMonthlyPlan(
                    empresa_id=eid or machine.empresa_id,
                    machine_id=mid,
                    anio=anio,
                    mes=mes,
                )
                db.session.add(plan)
            plan.horas_meta = horas
            plan.guardado_at = datetime.utcnow()
            guardados += 1

        if errores:
            db.session.rollback()
            for msg in errores[:3]:
                flash(msg, "danger")
        elif guardados:
            try:
                db.session.commit()
                flash(f"Meta guardada para {guardados} equipo(s).", "success")
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar la planeación.", "danger")
        else:
            db.session.rollback()
            flash("Selecciona equipos pendientes de guardar.", "warning")
        return redirect(url_for("main.ordenes_planeacion", mes=mes, anio=anio))

    filas = _planeacion_filas(anio, mes)
    total = len(filas)
    configurados = sum(1 for f in filas if f["configurado"])
    mes_label = dict(MESES_PLANEACION).get(mes, str(mes))
    anios = list(range(date.today().year - 2, date.today().year + 3))

    return render_template(
        "ordenes/planeacion_mensual.html",
        filas=filas,
        mes=mes,
        anio=anio,
        mes_label=mes_label,
        meses=MESES_PLANEACION,
        anios=anios,
        max_horas=max_h,
        total_equipos=total,
        total_configurados=configurados,
        total_pendientes=total - configurados,
    )


def _parse_fecha_filtro(value: str) -> Optional[date]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _ordenes_filtros_desde_request() -> dict[str, str]:
    return {
        "numero": request.args.get("numero", "").strip(),
        "equipo": request.args.get("equipo", "").strip(),
        "ubicacion": request.args.get("ubicacion", "").strip(),
        "tipo": request.args.get("tipo", "").strip(),
        "status": request.args.get("status", "").strip(),
        "mes": request.args.get("mes", "").strip(),
        "anio": request.args.get("anio", "").strip(),
        "fecha_desde": request.args.get("fecha_desde", "").strip(),
        "fecha_hasta": request.args.get("fecha_hasta", "").strip(),
        "alerta": request.args.get("alerta", "").strip(),
    }


@bp.route("/mantenimiento/analisis-costos")
def mantenimiento_costos():
    from collections import defaultdict
    from sqlalchemy.orm import joinedload

    hoy = date.today()
    fecha_desde = _parse_fecha_filtro(request.args.get("fecha_desde", "")) or date(hoy.year, 1, 1)
    fecha_hasta = _parse_fecha_filtro(request.args.get("fecha_hasta", "")) or hoy
    if fecha_desde > fecha_hasta:
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    ordenes = _filter_work_orders_empresa(
        WorkOrder.query.options(
            joinedload(WorkOrder.machine),
            joinedload(WorkOrder.proveedor),
            joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
            joinedload(WorkOrder.jornadas)
            .joinedload(WorkOrderJornada.technician)
            .joinedload(Technician.user),
        )
    ).all()

    filas = []
    por_tipo = defaultdict(float)
    por_activo = defaultdict(lambda: {
        "codigo": "", "nombre": "", "ordenes": 0, "mano_obra": 0.0,
        "herramientas": 0.0, "servicios": 0.0, "repuestos": 0.0,
    })
    por_proveedor = defaultdict(lambda: {"nombre": "", "ordenes": 0, "costo": 0.0})
    por_tecnico = defaultdict(lambda: {"nombre": "", "jornadas": 0, "horas": 0.0, "costo": 0.0})
    por_mes = defaultdict(float)
    total_mano_obra = total_herramientas = total_servicios = total_repuestos = 0.0

    for orden in ordenes:
        referencia = (
            orden.fecha_cierre.date() if orden.fecha_cierre else
            orden.fecha_programada if orden.fecha_programada else
            orden.created_at.date() if orden.created_at else None
        )
        if not referencia or referencia < fecha_desde or referencia > fecha_hasta:
            continue
        costo_servicio = orden.costo_servicio_externo
        costo_repuestos = orden.costo_repuestos_total
        costo_mano_obra = orden.costo_mano_obra_total
        costo_herramientas = orden.costo_herramientas_total
        costo_total = orden.costo_total_mantenimiento
        total_mano_obra += costo_mano_obra
        total_herramientas += costo_herramientas
        total_servicios += costo_servicio
        total_repuestos += costo_repuestos
        por_tipo[orden.tipo or "otro"] += costo_total
        por_mes[referencia.strftime("%Y-%m")] += costo_total

        machine = orden.machine
        activo_key = machine.id if machine else f"sin-{orden.id}"
        activo = por_activo[activo_key]
        activo["codigo"] = machine.codigo if machine else "—"
        activo["nombre"] = machine.nombre if machine else "Sin activo"
        activo["ordenes"] += 1
        activo["mano_obra"] += costo_mano_obra
        activo["herramientas"] += costo_herramientas
        activo["servicios"] += costo_servicio
        activo["repuestos"] += costo_repuestos

        if orden.es_ejecucion_externa:
            proveedor_nombre = orden.proveedor.nombre if orden.proveedor else (orden.empresa_tercerizada or "Sin proveedor")
            proveedor = por_proveedor[proveedor_nombre]
            proveedor["nombre"] = proveedor_nombre
            proveedor["ordenes"] += 1
            proveedor["costo"] += costo_servicio

        for jornada in orden.jornadas:
            if not jornada.technician_id:
                continue
            tecnico = por_tecnico[jornada.technician_id]
            tecnico["nombre"] = jornada.tecnico_label
            tecnico["jornadas"] += 1
            tecnico["horas"] += jornada.duracion_minutos / 60
            tecnico["costo"] += jornada.costo_mano_obra

        filas.append({
            "orden": orden, "fecha": referencia, "mano_obra": costo_mano_obra,
            "herramientas": costo_herramientas, "servicio": costo_servicio,
            "repuestos": costo_repuestos, "total": costo_total,
        })

    activos = sorted(
        ({**v, "total": v["mano_obra"] + v["herramientas"] + v["servicios"] + v["repuestos"]} for v in por_activo.values()),
        key=lambda x: x["total"], reverse=True,
    )
    proveedores = sorted(por_proveedor.values(), key=lambda x: x["costo"], reverse=True)
    tecnicos = sorted(por_tecnico.values(), key=lambda x: x["costo"], reverse=True)
    meses = []
    cursor = date(fecha_desde.year, fecha_desde.month, 1)
    limite = date(fecha_hasta.year, fecha_hasta.month, 1)
    while cursor <= limite:
        key = cursor.strftime("%Y-%m")
        meses.append({"key": key, "label": cursor.strftime("%m/%Y"), "costo": por_mes.get(key, 0.0)})
        cursor = date(cursor.year + (cursor.month == 12), 1 if cursor.month == 12 else cursor.month + 1, 1)

    total = total_mano_obra + total_herramientas + total_servicios + total_repuestos
    return render_template(
        "mantenimiento/costos.html",
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total=total,
        total_mano_obra=total_mano_obra,
        total_herramientas=total_herramientas,
        total_servicios=total_servicios,
        total_repuestos=total_repuestos,
        total_ordenes=len(filas),
        costo_promedio=(total / len(filas)) if filas else 0,
        por_tipo=por_tipo,
        activos=activos,
        proveedores=proveedores,
        tecnicos=tecnicos,
        meses=meses,
        filas=sorted(filas, key=lambda x: x["fecha"], reverse=True),
    )


def _parse_mes_anio_filtro(mes_s: str, anio_s: str) -> Optional[tuple[date, date]]:
    """Rango [inicio, fin] por mes/año de fecha programada; None si no aplica."""
    mes_s = (mes_s or "").strip()
    anio_s = (anio_s or "").strip()
    if anio_s.isdigit():
        anio = int(anio_s)
        if not (2000 <= anio <= 2100):
            return None
        if mes_s.isdigit():
            mes = int(mes_s)
            if 1 <= mes <= 12:
                ultimo = monthrange(anio, mes)[1]
                return date(anio, mes, 1), date(anio, mes, ultimo)
        return date(anio, 1, 1), date(anio, 12, 31)
    if mes_s.isdigit():
        mes = int(mes_s)
        if 1 <= mes <= 12:
            anio = date.today().year
            ultimo = monthrange(anio, mes)[1]
            return date(anio, mes, 1), date(anio, mes, ultimo)
    return None


def _ordenes_list_query(filtros: Optional[dict[str, str]] = None):
    from sqlalchemy.orm import joinedload

    filtros = filtros if filtros is not None else _ordenes_filtros_desde_request()
    q = _filter_work_orders_empresa(
        WorkOrder.query.options(
            joinedload(WorkOrder.jornadas).joinedload(WorkOrderJornada.technician),
            joinedload(WorkOrder.machine),
            joinedload(WorkOrder.technician),
            joinedload(WorkOrder.proveedor),
        )
    )

    numero = filtros.get("numero", "")
    if numero:
        like = f"%{numero}%"
        conds = [WorkOrder.numero.ilike(like)]
        num_id = numero.lstrip("#").strip()
        if num_id.isdigit():
            conds.append(WorkOrder.id == int(num_id))
        q = q.filter(or_(*conds))

    equipo = filtros.get("equipo", "")
    if equipo:
        like = f"%{equipo}%"
        mids = db.session.query(Machine.id).filter(
            or_(Machine.nombre.ilike(like), Machine.codigo.ilike(like))
        )
        eid = _current_empresa_id()
        if eid:
            mids = mids.filter(Machine.empresa_id == eid)
        q = q.filter(WorkOrder.machine_id.in_(mids))

    ubicacion = filtros.get("ubicacion", "")
    if ubicacion:
        like = f"%{ubicacion}%"
        mids_ub = db.session.query(Machine.id).filter(
            or_(Machine.ubicacion.ilike(like), Machine.area.ilike(like))
        )
        eid = _current_empresa_id()
        if eid:
            mids_ub = mids_ub.filter(Machine.empresa_id == eid)
        q = q.filter(
            or_(
                WorkOrder.ubicacion.ilike(like),
                WorkOrder.area.ilike(like),
                WorkOrder.machine_id.in_(mids_ub),
            )
        )

    tipo = filtros.get("tipo", "")
    if tipo:
        q = q.filter(func.lower(WorkOrder.tipo) == tipo.lower())

    alerta = filtros.get("alerta", "")
    if alerta:
        from app.alertas_service import aplicar_filtro_alerta_orden

        q = aplicar_filtro_alerta_orden(q, alerta)
    else:
        status = filtros.get("status", "")
        if status:
            q = q.filter(WorkOrder.status == status)

        rango_mes = _parse_mes_anio_filtro(filtros.get("mes", ""), filtros.get("anio", ""))
        if rango_mes:
            inicio_mes, fin_mes = rango_mes
            q = q.filter(
                WorkOrder.fecha_programada.isnot(None),
                WorkOrder.fecha_programada >= inicio_mes,
                WorkOrder.fecha_programada <= fin_mes,
            )

        fecha_desde = _parse_fecha_filtro(filtros.get("fecha_desde", ""))
        if fecha_desde:
            q = q.filter(WorkOrder.fecha_programada >= fecha_desde)
        fecha_hasta = _parse_fecha_filtro(filtros.get("fecha_hasta", ""))
        if fecha_hasta:
            q = q.filter(WorkOrder.fecha_programada <= fecha_hasta)

    return q.order_by(
        WorkOrder.folio_anio.desc().nullslast(),
        WorkOrder.folio_seq.desc().nullslast(),
        WorkOrder.id.desc(),
    )


_OT_LIST_TIPOS_ORDER = (
    WorkOrderType.PREVENTIVO.value,
    WorkOrderType.CORRECTIVO.value,
    WorkOrderType.EMERGENCIA.value,
)

_OT_LIST_ESTADOS_ORDER = (
    WorkOrderStatus.PROGRAMADA.value,
    WorkOrderStatus.ABIERTA.value,
    WorkOrderStatus.EN_PROCESO.value,
    WorkOrderStatus.VENCIDA.value,
    WorkOrderStatus.COMPLETADO.value,
    WorkOrderStatus.CERRADA.value,
)


def _ordenes_list_resumen(orders: list) -> dict:
    tipos_count = {k: 0 for k in _OT_LIST_TIPOS_ORDER}
    estados_count = {k: 0 for k in _OT_LIST_ESTADOS_ORDER}
    prev_key = WorkOrderType.PREVENTIVO.value
    prev_programadas = 0
    prev_abiertas = 0
    for o in orders:
        tk = (o.tipo or "").strip().lower()
        if tk in tipos_count:
            tipos_count[tk] += 1
        sk = (o.status or "").strip().lower()
        if sk in estados_count:
            estados_count[sk] += 1
        if tk == prev_key:
            if sk == WorkOrderStatus.PROGRAMADA.value:
                prev_programadas += 1
            elif sk == WorkOrderStatus.ABIERTA.value:
                prev_abiertas += 1

    corr_key = WorkOrderType.CORRECTIVO.value
    emer_key = WorkOrderType.EMERGENCIA.value
    venc_key = WorkOrderStatus.VENCIDA.value

    return {
        "total": len(orders),
        "preventivas": {
            "key": prev_key,
            "count": tipos_count[prev_key],
            "sub": f"{prev_programadas} programadas · {prev_abiertas} abiertas",
            **wo_tipo_meta(prev_key),
        },
        "correctivas": {
            "key": corr_key,
            "count": tipos_count[corr_key],
            "sub": f"{tipos_count[emer_key]} emergencias",
            **wo_tipo_meta(corr_key),
        },
        "vencidas": {
            "key": venc_key,
            "count": estados_count[venc_key],
            "sub": "requiere atención",
            **wo_status_meta(venc_key),
        },
        "estados": [
            {"key": k, "count": estados_count[k], **wo_status_meta(k)}
            for k in _OT_LIST_ESTADOS_ORDER
        ],
        "estados_por_key": estados_count,
    }


_OT_LIST_STATUS_PILLS = (
    ("", "Todas"),
    (WorkOrderStatus.ABIERTA.value, "Abiertas"),
    (WorkOrderStatus.PROGRAMADA.value, "Programadas"),
    (WorkOrderStatus.EN_PROCESO.value, "En proceso"),
    (WorkOrderStatus.VENCIDA.value, "Vencidas"),
    (WorkOrderStatus.COMPLETADO.value, "Completadas"),
    (WorkOrderStatus.CERRADA.value, "Cerradas"),
)


@bp.route("/ordenes")
def ordenes_list():
    filtros = _ordenes_filtros_desde_request()
    orders = _ordenes_list_query(filtros).all()
    filtros_stats = {**filtros, "status": "", "alerta": ""}
    ot_resumen = _ordenes_list_resumen(_ordenes_list_query(filtros_stats).all())
    hay_filtros = any(filtros.values())
    filtros_qs_base = {
        k: v for k, v in filtros.items() if v and k not in ("status", "alerta", "tipo")
    }
    status_filter = filtros.get("status", "")
    alerta = filtros.get("alerta", "")
    if alerta == "vencimientos":
        status_filter = WorkOrderStatus.VENCIDA.value
    elif alerta == WorkOrderStatus.EN_PROCESO.value or alerta == "en_proceso":
        status_filter = WorkOrderStatus.EN_PROCESO.value
    return render_template(
        "ordenes/list.html",
        orders=orders,
        ot_resumen=ot_resumen,
        ot_status_pills=_OT_LIST_STATUS_PILLS,
        filtros=filtros,
        filtros_qs_base=filtros_qs_base,
        status_filter=status_filter,
        alerta_filtro=alerta,
        hay_filtros=hay_filtros,
        meses_ot=MESES_PLANEACION,
        anios_ot=list(range(date.today().year - 2, date.today().year + 3)),
        tipos_ot=[
            ("", "Todos"),
            (WorkOrderType.PREVENTIVO.value, "Preventivo"),
            (WorkOrderType.CORRECTIVO.value, "Correctivo"),
            (WorkOrderType.EMERGENCIA.value, "Emergencia"),
        ],
    )


@bp.route("/ordenes/export")
@login_required
def ordenes_export():
    from io import BytesIO
    from flask import send_file
    from app.maintenance.mrl_exports import export_ordenes_excel

    empresa = current_user.empresa
    if not empresa:
        return redirect(url_for("main.ordenes_list"))
    content, name = export_ordenes_excel(
        empresa, _ordenes_list_query().all(), usuario=current_user
    )
    return send_file(
        BytesIO(content),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=name,
    )


@bp.route("/ordenes/export/pdf")
@login_required
def ordenes_export_pdf():
    from io import BytesIO
    from flask import send_file
    from app.maintenance.control_actividades_pdf import export_control_actividades_pdf

    empresa = current_user.empresa
    if not empresa:
        return redirect(url_for("main.ordenes_list"))
    filtros = _ordenes_filtros_desde_request()
    orders = _ordenes_list_query(filtros).all()
    mes = filtros.get("mes", "")
    anio = filtros.get("anio", "")
    meses = dict(MESES_PLANEACION)
    if mes.isdigit() and int(mes) in meses:
        periodo_label = f"{meses[int(mes)]} {anio or date.today().year}"
    elif anio:
        periodo_label = anio
    elif filtros.get("fecha_desde") or filtros.get("fecha_hasta"):
        periodo_label = " - ".join(
            value
            for value in (filtros.get("fecha_desde"), filtros.get("fecha_hasta"))
            if value
        )
    else:
        periodo_label = "Listado filtrado"
    content, name = export_control_actividades_pdf(
        empresa, orders, periodo_label=periodo_label
    )
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=name,
    )


@bp.route("/ordenes/nueva", methods=["GET", "POST"])
def ordenes_new():
    from sqlalchemy.orm import joinedload

    machines = (
        _filter_empresa(
            Machine.query.options(joinedload(Machine.responsable)).order_by(Machine.nombre),
            Machine,
        ).all()
    )
    technicians = _filter_empresa(
        Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician
    ).all()
    if request.method == "POST":
        fp = request.form.get("fecha_programada")
        fecha_prog = datetime.strptime(fp, "%Y-%m-%d").date() if fp else None
        tipo = (request.form.get("tipo") or "").strip()
        wo = WorkOrder(
            titulo=request.form.get("titulo", "").strip(),
            descripcion=request.form.get("descripcion", "").strip(),
            tipo=tipo or WorkOrderType.CORRECTIVO.value,
            status=WorkOrderStatus.ABIERTA.value,
            prioridad=request.form.get("prioridad") or "media",
            empresa_id=_current_empresa_id(),
            fecha_programada=fecha_prog,
            ubicacion=request.form.get("ubicacion", "").strip(),
            area=request.form.get("area", "").strip(),
            **_work_order_responsables_desde_form(request.form),
            machine_id=int(request.form.get("machine_id", 0)),
        )
        _, err_machine = _validar_machine_id_tenant(wo.machine_id)
        if not wo.titulo or not wo.machine_id:
            flash("Actividad y equipo son obligatorios.", "danger")
        elif err_machine:
            flash(err_machine, "danger")
        elif not tipo:
            flash("Selecciona el tipo de orden.", "danger")
        else:
            from app.work_order_status import estado_inicial_por_fecha

            wo.status = estado_inicial_por_fecha(fecha_prog)
            wo.maquina_requirio_paro = _maquina_requirio_paro_desde_form(request.form, wo.tipo)
            fl = (request.form.get("fecha_limite") or "").strip()
            if fl:
                try:
                    wo.fecha_limite = datetime.strptime(fl, "%Y-%m-%d").date()
                except ValueError:
                    wo.fecha_limite = None
            if wo.tipo == WorkOrderType.PREVENTIVO.value:
                if not fecha_prog:
                    flash(
                        "La fecha programada es obligatoria para generar el calendario preventivo del año.",
                        "danger",
                    )
                    return render_template(
                        "ordenes/form.html",
                        order=None,
                        machines=machines,
                        technicians=technicians,
                        prioridades=WORK_ORDER_PRIORITIES,
                        **_orden_form_context(None, technicians, machines),
                    )
                fv, fu = parse_frecuencia_form(request.form)
                ordenes, err_prev = crear_programacion_preventiva_anio(
                    empresa_id=wo.empresa_id,
                    machine_id=wo.machine_id,
                    technician_id=wo.technician_id,
                    titulo=wo.titulo,
                    descripcion=wo.descripcion,
                    prioridad=wo.prioridad,
                    fecha_inicio=fecha_prog,
                    frecuencia_valor=fv,
                    frecuencia_unidad=fu,
                    ubicacion=wo.ubicacion,
                    area=wo.area,
                    autorizado_por=wo.autorizado_por,
                    recibido_por=wo.recibido_por,
                    empresa_tercerizada=wo.empresa_tercerizada,
                )
                if err_prev:
                    flash(err_prev, "danger")
                    return render_template(
                        "ordenes/form.html",
                        order=None,
                        machines=machines,
                        technicians=technicians,
                        prioridades=WORK_ORDER_PRIORITIES,
                        **_orden_form_context(None, technicians, machines),
                    )
                delta_limite = None
                if wo.fecha_limite and fecha_prog:
                    delta_limite = wo.fecha_limite - fecha_prog
                for o in ordenes:
                    if delta_limite is not None and o.fecha_programada:
                        o.fecha_limite = o.fecha_programada + delta_limite
                try:
                    db.session.flush()
                    numeros = [asignar_numero_ot(o) for o in ordenes]
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar la programación preventiva.", "danger")
                    return render_template(
                        "ordenes/form.html",
                        order=None,
                        machines=machines,
                        technicians=technicians,
                        prioridades=WORK_ORDER_PRIORITIES,
                        **_orden_form_context(None, technicians, machines),
                    )
                anio = date.today().year
                if len(numeros) == 1:
                    flash(f"Orden {numeros[0]} creada.", "success")
                else:
                    flash(
                        f"Se crearon {len(numeros)} OT preventivas para {anio} "
                        f"({frecuencia_label(fv, fu)}): {numeros[0]} … {numeros[-1]}.",
                        "success",
                    )
                return redirect(url_for("main.ordenes_list"))
            else:
                wo.preventive_plan_id = None
                wo.frecuencia_valor = None
                wo.frecuencia_unidad = None
            db.session.add(wo)
            db.session.flush()
            numero = asignar_numero_ot(wo)
            # La creación solo planifica la OT. Jornadas, repuestos, tiempos y
            # decisiones de ejecución se registran al abrir la orden guardada.
            db.session.commit()
            flash(f"Orden {numero} creada. Ábrela para iniciar su ejecución.", "success")
            return redirect(url_for("main.ordenes_list"))
    return render_template(
        "ordenes/form.html",
        order=None,
        machines=machines,
        technicians=technicians,
        prioridades=WORK_ORDER_PRIORITIES,
        **_orden_form_context(None, technicians, machines),
    )


@bp.route("/ordenes/api/historial-proveedor/<int:proveedor_id>")
def ordenes_api_historial_proveedor(proveedor_id: int):
    proveedor = _filter_empresa(
        Proveedor.query.filter_by(id=proveedor_id, activo=True), Proveedor
    ).first_or_404()
    rows = _historial_proveedor_ot(proveedor.id)
    return jsonify(_historial_proveedor_payload(rows))


@bp.route("/ordenes/<int:id>/editar", methods=["GET", "POST"])
def ordenes_edit(id):
    from sqlalchemy.orm import joinedload

    wo = _get_work_order_or_404(
        id,
        joinedload(WorkOrder.machine).joinedload(Machine.responsable),
        joinedload(WorkOrder.jornadas),
        joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
        joinedload(WorkOrder.proveedor),
        joinedload(WorkOrder.supervisor),
    )
    solo_lectura = (not can_edit(current_user)) or (not wo_es_editable(wo.status))
    machines = (
        _filter_empresa(
            Machine.query.options(joinedload(Machine.responsable)).order_by(Machine.nombre),
            Machine,
        ).all()
    )
    technicians = _filter_empresa(
        Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician
    ).all()
    if request.method == "POST":
        if solo_lectura:
            flash(
                "No puedes modificar esta orden."
                if not can_edit(current_user)
                else "Esta orden está cerrada y no puede modificarse.",
                "warning",
            )
            return redirect(url_for("main.ordenes_edit", id=wo.id))
        wo.titulo = request.form.get("titulo", "").strip()
        wo.descripcion = request.form.get("descripcion", "").strip()
        wo.tipo = request.form.get("tipo") or wo.tipo
        wo.maquina_requirio_paro = _maquina_requirio_paro_desde_form(request.form, wo.tipo)
        wo.prioridad = request.form.get("prioridad") or wo.prioridad
        wo.ubicacion = request.form.get("ubicacion", "").strip()
        wo.area = request.form.get("area", "").strip()
        extra = _work_order_responsables_desde_form(request.form)
        wo.autorizado_por = extra["autorizado_por"]
        wo.recibido_por = extra["recibido_por"]
        fp = request.form.get("fecha_programada")
        wo.fecha_programada = datetime.strptime(fp, "%Y-%m-%d").date() if fp else None
        new_mid = int(request.form.get("machine_id", wo.machine_id))
        _, err_machine = _validar_machine_id_tenant(new_mid)
        if err_machine:
            flash(err_machine, "danger")
            return render_template(
                "ordenes/form.html",
                order=wo,
                machines=machines,
                technicians=technicians,
                prioridades=WORK_ORDER_PRIORITIES,
                solo_lectura=solo_lectura,
                **_orden_form_context(wo, technicians, machines),
            )
        wo.machine_id = new_mid
        err_ej = _aplicar_ejecucion_desde_form(wo, request.form)
        if err_ej:
            flash(err_ej, "danger")
        elif not wo.titulo:
            flash("La actividad es obligatoria.", "danger")
        elif wo.tipo == WorkOrderType.PREVENTIVO.value:
            fv, fu = parse_frecuencia_form(request.form)
            err_prev = aplicar_preventivo_a_orden(
                wo, request.form.get("titulo", "").strip(), fv, fu, exclude_wo_id=wo.id
            )
            if err_prev:
                flash(err_prev, "danger")
            else:
                err = _guardar_jornadas_orden(wo)
                if err:
                    db.session.rollback()
                    flash(err, "danger")
                else:
                    _aplicar_estado_orden_desde_formulario(wo)
                    _aplicar_fecha_cierre_si_terminal(wo)
                    err_rep = _guardar_repuestos_orden(wo)
                    if err_rep:
                        db.session.rollback()
                        flash(err_rep, "danger")
                    else:
                        db.session.commit()
                        flash("Orden actualizada.", "success")
                        return redirect(url_for("main.ordenes_list"))
        else:
            wo.preventive_plan_id = None
            wo.frecuencia_valor = None
            wo.frecuencia_unidad = None
            err = _guardar_jornadas_orden(wo)
            if err:
                db.session.rollback()
                flash(err, "danger")
            else:
                _aplicar_estado_orden_desde_formulario(wo)
                _aplicar_fecha_cierre_si_terminal(wo)
                err_rep = _guardar_repuestos_orden(wo)
                if err_rep:
                    db.session.rollback()
                    flash(err_rep, "danger")
                else:
                    db.session.commit()
                    flash("Orden actualizada.", "success")
                    return redirect(url_for("main.ordenes_list"))
    return render_template(
        "ordenes/form.html",
        order=wo,
        machines=machines,
        technicians=technicians,
        prioridades=WORK_ORDER_PRIORITIES,
        solo_lectura=solo_lectura,
        **_orden_form_context(wo, technicians, machines),
    )


INFORME_OT_EXTENSIONES = {"pdf", "doc", "docx", "xls", "xlsx", "png", "jpg", "jpeg", "webp"}


def _ruta_informe_ot(informe: WorkOrderInforme) -> str:
    raiz = os.path.abspath(current_app.static_folder)
    ruta = os.path.abspath(os.path.join(raiz, informe.ruta_archivo.replace("/", os.sep)))
    if os.path.commonpath([raiz, ruta]) != raiz:
        abort(404)
    return ruta


@bp.route("/ordenes/<int:id>/informes", methods=["POST"])
def ordenes_informe_upload(id):
    if not can_edit(current_user):
        abort(403)
    wo = _get_work_order_or_404(id)
    archivo = request.files.get("informe_archivo")
    if not archivo or not archivo.filename:
        flash("Selecciona el informe técnico que deseas cargar.", "warning")
        return redirect(url_for("main.ordenes_edit", id=wo.id) + "#informes-tecnicos")
    original = secure_filename(archivo.filename)
    extension = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if extension not in INFORME_OT_EXTENSIONES:
        flash("Formato no permitido. Usa PDF, Word, Excel o una imagen.", "danger")
        return redirect(url_for("main.ordenes_edit", id=wo.id) + "#informes-tecnicos")
    empresa_id = wo.empresa_id or _current_empresa_id()
    carpeta_rel = f"uploads/empresas/{empresa_id}/ordenes/{wo.id}/informes"
    carpeta_abs = os.path.join(current_app.static_folder, *carpeta_rel.split("/"))
    os.makedirs(carpeta_abs, exist_ok=True)
    nombre_guardado = f"{uuid4().hex}.{extension}"
    archivo.save(os.path.join(carpeta_abs, nombre_guardado))
    informe = WorkOrderInforme(
        empresa_id=empresa_id,
        work_order_id=wo.id,
        nombre_original=original,
        ruta_archivo=f"{carpeta_rel}/{nombre_guardado}",
        descripcion=(request.form.get("informe_descripcion") or "").strip()[:255],
        user_id=current_user.id,
    )
    db.session.add(informe)
    db.session.commit()
    flash("Informe técnico cargado.", "success")
    return redirect(url_for("main.ordenes_edit", id=wo.id) + "#informes-tecnicos")


@bp.route("/ordenes/<int:id>/informes/<int:informe_id>/descargar")
def ordenes_informe_download(id, informe_id):
    from flask import send_file

    wo = _get_work_order_or_404(id)
    informe = WorkOrderInforme.query.filter_by(
        id=informe_id, work_order_id=wo.id, empresa_id=wo.empresa_id
    ).first_or_404()
    ruta = _ruta_informe_ot(informe)
    if not os.path.isfile(ruta):
        abort(404)
    return send_file(ruta, as_attachment=True, download_name=informe.nombre_original)


@bp.route("/ordenes/<int:id>/informes/<int:informe_id>/eliminar", methods=["POST"])
def ordenes_informe_delete(id, informe_id):
    if not can_edit(current_user):
        abort(403)
    wo = _get_work_order_or_404(id)
    informe = WorkOrderInforme.query.filter_by(
        id=informe_id, work_order_id=wo.id, empresa_id=wo.empresa_id
    ).first_or_404()
    ruta = _ruta_informe_ot(informe)
    db.session.delete(informe)
    db.session.commit()
    if os.path.isfile(ruta):
        os.remove(ruta)
    flash("Informe técnico eliminado.", "success")
    return redirect(url_for("main.ordenes_edit", id=wo.id) + "#informes-tecnicos")


@bp.route("/ordenes/<int:id>/pdf")
@login_required
def ordenes_pdf(id):
    from io import BytesIO

    from flask import send_file
    from sqlalchemy.orm import joinedload

    from app.maintenance.mrl_exports import export_orden_trabajo_pdf

    wo = _get_work_order_or_404(
        id,
        joinedload(WorkOrder.machine),
        joinedload(WorkOrder.technician),
        joinedload(WorkOrder.jornadas).joinedload(WorkOrderJornada.technician),
        joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
        joinedload(WorkOrder.proveedor),
        joinedload(WorkOrder.supervisor),
    )
    empresa = current_user.empresa
    if not empresa:
        flash("No hay empresa asociada a tu sesión.", "danger")
        return redirect(url_for("main.ordenes_list"))
    contenido, nombre = export_orden_trabajo_pdf(empresa, wo, usuario=current_user)
    return send_file(
        BytesIO(contenido),
        mimetype="application/pdf",
        as_attachment=request.args.get("inline") != "1",
        download_name=nombre,
    )


# --- Calendario ---
@bp.route("/calendario")
def calendario():
    from sqlalchemy.orm import joinedload

    year = int(request.args.get("y", date.today().year))
    month = int(request.args.get("m", date.today().month))
    start = date(year, month, 1)
    _, last = monthrange(year, month)
    end = date(year, month, last)
    orders = _filter_work_orders_empresa(
        WorkOrder.query.options(joinedload(WorkOrder.machine)).filter(
            WorkOrder.fecha_programada.isnot(None),
            WorkOrder.fecha_programada >= start,
            WorkOrder.fecha_programada <= end,
        )
    ).order_by(WorkOrder.fecha_programada).all()
    by_day = {}
    for o in orders:
        d = o.fecha_programada.isoformat()
        by_day.setdefault(d, []).append(o)

    first_weekday = start.weekday()
    cells = [None] * first_weekday
    for day in range(1, last + 1):
        cells.append(day)
    while len(cells) % 7 != 0:
        cells.append(None)
    weeks = [cells[i : i + 7] for i in range(0, len(cells), 7)]

    return render_template(
        "calendario.html",
        year=year,
        month=month,
        by_day=by_day,
        start=start,
        last_day=last,
        weeks=weeks,
    )


def _proveedores_kpis(proveedores: list) -> dict:
    total = len(proveedores)
    servicio = sum(1 for p in proveedores if p.tipo == ProveedorTipo.SERVICIO.value)
    insumos = sum(1 for p in proveedores if p.tipo == ProveedorTipo.INSUMOS.value)
    ambos = sum(1 for p in proveedores if p.tipo == ProveedorTipo.AMBOS.value)
    activos = sum(1 for p in proveedores if p.activo)
    return {
        "total": total,
        "servicio": servicio,
        "insumos": insumos,
        "ambos": ambos,
        "activos": activos,
    }


def _proveedor_desde_form(form) -> dict:
    tipo = (form.get("tipo") or ProveedorTipo.SERVICIO.value).strip().lower()
    if tipo not in PROVEEDOR_TIPOS_VALIDOS:
        tipo = ProveedorTipo.SERVICIO.value
    return {
        "nombre": (form.get("nombre") or "").strip(),
        "nit": (form.get("nit") or "").strip(),
        "direccion": (form.get("direccion") or "").strip(),
        "contacto_nombre": (form.get("contacto_nombre") or "").strip(),
        "contacto_cargo": (form.get("contacto_cargo") or "").strip(),
        "contacto_email": (form.get("contacto_email") or "").strip(),
        "contacto_telefono": (form.get("contacto_telefono") or "").strip(),
        "tipo": tipo,
        "observaciones": (form.get("observaciones") or "").strip(),
        "activo": form.get("activo") == "1",
    }


def _proveedor_a_dict(p: Proveedor) -> dict:
    return {
        "id": p.id,
        "nombre": p.nombre,
        "nit": p.nit or "",
        "direccion": p.direccion or "",
        "contacto_nombre": p.contacto_nombre or "",
        "contacto_cargo": p.contacto_cargo or "",
        "contacto_email": p.contacto_email or "",
        "contacto_telefono": p.contacto_telefono or "",
        "tipo": p.tipo,
        "observaciones": p.observaciones or "",
        "activo": p.activo,
    }


# --- Proveedores ---
@bp.route("/proveedores")
def proveedores_list():
    q = request.args.get("q", "").strip()
    tipo_f = (request.args.get("tipo") or "").strip().lower()
    estado_f = (request.args.get("estado") or "").strip().lower()

    base = _filter_empresa(Proveedor.query.order_by(Proveedor.nombre), Proveedor)
    todos = base.all()
    kpis = _proveedores_kpis(todos)

    query = base
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Proveedor.nombre.ilike(like),
                Proveedor.nit.ilike(like),
                Proveedor.contacto_nombre.ilike(like),
                Proveedor.contacto_email.ilike(like),
                Proveedor.contacto_telefono.ilike(like),
            )
        )
    if tipo_f in PROVEEDOR_TIPOS_VALIDOS:
        query = query.filter(Proveedor.tipo == tipo_f)
    if estado_f == "activo":
        query = query.filter(Proveedor.activo.is_(True))
    elif estado_f == "inactivo":
        query = query.filter(Proveedor.activo.is_(False))

    items = query.all()
    return render_template(
        "proveedores/list.html",
        items=items,
        kpis=kpis,
        q=q,
        tipo_f=tipo_f,
        estado_f=estado_f,
        proveedores_json=[_proveedor_a_dict(p) for p in todos],
        tipos_proveedor=[
            ("", "Todos los tipos"),
            (ProveedorTipo.SERVICIO.value, "Servicio"),
            (ProveedorTipo.INSUMOS.value, "Insumos"),
            (ProveedorTipo.AMBOS.value, "Ambos"),
        ],
    )


@bp.route("/proveedores/guardar", methods=["POST"])
def proveedores_guardar():
    datos = _proveedor_desde_form(request.form)
    if not datos["nombre"]:
        flash("El nombre de la empresa es obligatorio.", "danger")
        return redirect(url_for("main.proveedores_list"))

    pid = request.form.get("id", "").strip()
    if pid:
        p = _filter_empresa(Proveedor.query.filter_by(id=int(pid)), Proveedor).first_or_404()
    else:
        if not can_create(current_user):
            flash("No tienes permiso para crear proveedores.", "warning")
            return redirect(url_for("main.proveedores_list"))
        p = Proveedor(empresa_id=_current_empresa_id())

    for k, v in datos.items():
        setattr(p, k, v)
    db.session.add(p)
    try:
        db.session.commit()
        flash("Proveedor actualizado." if pid else "Proveedor registrado.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo guardar el proveedor.", "danger")
    return redirect(url_for("main.proveedores_list"))


@bp.route("/proveedores/<int:id>/eliminar", methods=["POST"])
def proveedores_delete(id):
    p = _filter_empresa(Proveedor.query.filter_by(id=id), Proveedor).first_or_404()
    db.session.delete(p)
    try:
        db.session.commit()
        flash("Proveedor eliminado.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar el proveedor.", "danger")
    return redirect(url_for("main.proveedores_list"))


# --- Inventario ---
@bp.route("/inventario")
def inventario_list():
    q = request.args.get("q", "").strip()
    query = _filter_empresa(SparePart.query.order_by(SparePart.nombre), SparePart)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                SparePart.sku.ilike(like),
                SparePart.nombre.ilike(like),
            )
        )
    items = query.all()
    valor_inventario = sum(p.costo_total for p in items)
    return render_template(
        "inventario/list.html", items=items, q=q, valor_inventario=valor_inventario
    )


@bp.route("/inventario/nuevo", methods=["GET", "POST"])
def inventario_new():
    if request.method == "POST":
        p = SparePart(
            empresa_id=_current_empresa_id(),
            sku=request.form.get("sku", "").strip(),
            nombre=request.form.get("nombre", "").strip(),
            categoria=request.form.get("categoria", "").strip(),
            unidad=request.form.get("unidad", "pza").strip(),
            cantidad=int(request.form.get("cantidad") or 0),
            stock_minimo=int(request.form.get("stock_minimo") or 0),
            ubicacion_almacen=request.form.get("ubicacion_almacen", "").strip(),
            costo_unitario=_parse_costo(request.form.get("costo_unitario", "")),
        )
        if not p.sku or not p.nombre:
            flash("SKU y nombre son obligatorios.", "danger")
        else:
            db.session.add(p)
            try:
                db.session.commit()
                flash("Repuesto registrado.", "success")
                return redirect(url_for("main.inventario_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿SKU duplicado?).", "danger")
    return render_template("inventario/form.html", item=None)


@bp.route("/inventario/<int:id>/editar", methods=["GET", "POST"])
def inventario_edit(id):
    p = _get_spare_part_or_404(id)
    if request.method == "POST":
        p.sku = request.form.get("sku", "").strip()
        p.nombre = request.form.get("nombre", "").strip()
        p.categoria = request.form.get("categoria", "").strip()
        p.unidad = request.form.get("unidad", "pza").strip()
        p.cantidad = int(request.form.get("cantidad") or 0)
        p.stock_minimo = int(request.form.get("stock_minimo") or 0)
        p.ubicacion_almacen = request.form.get("ubicacion_almacen", "").strip()
        p.costo_unitario = _parse_costo(request.form.get("costo_unitario", ""))
        if not p.sku or not p.nombre:
            flash("SKU y nombre son obligatorios.", "danger")
        else:
            try:
                db.session.commit()
                flash("Repuesto actualizado.", "success")
                return redirect(url_for("main.inventario_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar.", "danger")
    return render_template("inventario/form.html", item=p)


@bp.route("/inventario/<int:id>/entrada", methods=["GET", "POST"])
def inventario_entrada(id):
    p = _get_spare_part_or_404(id)
    proveedores = _filter_empresa(
        Proveedor.query.filter(Proveedor.activo.is_(True)).order_by(Proveedor.nombre),
        Proveedor,
    ).all()
    if request.method == "POST":
        try:
            cantidad = int(request.form.get("cantidad") or 0)
        except ValueError:
            cantidad = 0
        costo = _parse_costo(request.form.get("costo_unitario", ""))
        fecha = _parse_form_date(request.form.get("fecha_compra"))
        proveedor_raw = (request.form.get("proveedor_id") or "").strip()
        proveedor_id = int(proveedor_raw) if proveedor_raw.isdigit() else None
        proveedor = None
        if proveedor_id:
            proveedor = _filter_empresa(
                Proveedor.query.filter_by(id=proveedor_id, activo=True), Proveedor
            ).first()
        nuevo_proveedor = (request.form.get("nuevo_proveedor_nombre") or "").strip()
        if cantidad <= 0:
            flash("La cantidad recibida debe ser mayor que cero.", "danger")
        elif costo < 0:
            flash("El costo unitario no puede ser negativo.", "danger")
        elif not fecha:
            flash("La fecha de compra es obligatoria.", "danger")
        elif proveedor_id and not proveedor:
            flash("Selecciona un proveedor activo de tu empresa.", "danger")
        elif proveedor_raw == "__nuevo__" and not nuevo_proveedor:
            flash("Indica el nombre del nuevo proveedor.", "danger")
        else:
            if proveedor_raw == "__nuevo__":
                proveedor = Proveedor(
                    empresa_id=p.empresa_id,
                    nombre=nuevo_proveedor,
                    nit=(request.form.get("nuevo_proveedor_nit") or "").strip(),
                    contacto_nombre=(request.form.get("nuevo_proveedor_contacto") or "").strip(),
                    contacto_telefono=(request.form.get("nuevo_proveedor_telefono") or "").strip(),
                    contacto_email=(request.form.get("nuevo_proveedor_email") or "").strip(),
                    tipo=ProveedorTipo.INSUMOS.value,
                    activo=True,
                )
                db.session.add(proveedor)
                db.session.flush()
            stock_anterior = int(p.cantidad or 0)
            costo_anterior = float(p.costo_unitario or 0)
            nuevo_stock = stock_anterior + cantidad
            p.costo_unitario = (
                ((stock_anterior * costo_anterior) + (cantidad * costo)) / nuevo_stock
                if nuevo_stock else costo
            )
            p.cantidad = nuevo_stock
            db.session.add(SparePartEntry(
                empresa_id=p.empresa_id,
                spare_part_id=p.id,
                cantidad=cantidad,
                costo_unitario=costo,
                fecha_compra=fecha,
                proveedor_id=proveedor.id if proveedor else None,
                numero_requisicion=(request.form.get("numero_requisicion") or "").strip(),
                numero_factura=(request.form.get("numero_factura") or "").strip(),
                notas=(request.form.get("notas") or "").strip(),
                user_id=current_user.id,
            ))
            db.session.commit()
            flash(f"Entrada registrada: {cantidad} {p.unidad} de {p.nombre}.", "success")
            return redirect(url_for("main.inventario_list"))
    return render_template(
        "inventario/entrada.html",
        item=p,
        proveedores=proveedores,
        hoy=date.today().isoformat(),
    )


# --- Equipo de trabajo (usuarios de la empresa) ---
def _equipo_usuarios_query():
    eid = _current_empresa_id()
    q = User.query
    if eid:
        q = q.filter(User.empresa_id == eid)
    return q.order_by(User.activo.desc(), User.nombre_visible, User.username)


def _validar_username_equipo(username: str) -> Optional[str]:
    u = (username or "").strip().lower()
    if len(u) < 3:
        return "El usuario debe tener al menos 3 caracteres."
    if not re.match(r"^[a-z0-9._-]+$", u):
        return "Solo letras, números, punto, guion y guion bajo."
    return None


def _sync_technician_for_user(user: User) -> None:
    """Mantiene un técnico vinculado para asignar OT (roles operativos de mantenimiento)."""
    if not user.empresa_id:
        return
    from app.modules import empresa_solo_inventario

    if empresa_solo_inventario(user.empresa):
        return
    tech = Technician.query.filter_by(user_id=user.id).first()
    if normalize_rol(user.rol) != UserRole.TECNICO.value:
        if tech:
            tech.nombre = user.nombre_visible or user.username
            tech.email = user.email or ""
            tech.telefono = user.telefono or ""
            tech.activo = user.activo
        return
    if not tech:
        tech = Technician(empresa_id=user.empresa_id, user_id=user.id)
        db.session.add(tech)
    tech.nombre = user.nombre_visible or user.username
    tech.email = user.email or ""
    tech.telefono = user.telefono or ""
    tech.activo = user.activo
    tech.empresa_id = user.empresa_id


def _require_admin_equipo() -> bool:
    if not can_manage_equipo(current_user):
        flash("No tienes permiso para gestionar el equipo.", "warning")
        return False
    return True


def _sedes_empresa(empresa_id: int) -> list:
    return (
        Sede.query.filter_by(empresa_id=empresa_id)
        .order_by(Sede.es_principal.desc(), Sede.nombre)
        .all()
    )


def _parse_sede_equipo(form, empresa_id: int) -> tuple[Optional[int], Optional[str]]:
    raw = (form.get("sede_id") or "").strip()
    if not raw:
        return None, None
    if not raw.isdigit():
        return None, "Selecciona una sede válida."
    sid = int(raw)
    if not Sede.query.filter_by(id=sid, empresa_id=empresa_id).first():
        return None, "La sede no pertenece a tu empresa."
    return sid, None


def _parse_tarifa_hora_equipo(form, empresa: Empresa | None) -> tuple[float, Optional[str]]:
    raw = (form.get("tarifa_hora") or "").strip()
    if not raw:
        return 0.0, None
    value = parsear_monto_form(raw, empresa.moneda if empresa else "COP")
    if value is None:
        return 0.0, "Ingresa una tarifa por hora válida."
    if value < 0:
        return 0.0, "La tarifa por hora no puede ser negativa."
    if value > 999_999_999_999.99:
        return 0.0, "La tarifa por hora supera el máximo permitido."
    return round(value, 2), None


def _save_user_custom_fields(user: User, form, empresa_id: int, sector: str) -> Optional[str]:
    campos = campos_para_equipo(empresa_id, sector)
    for campo in campos:
        val, err = valor_campo_desde_form(campo, form)
        if err:
            return err
        row = UsuarioCampoValor.query.filter_by(user_id=user.id, campo_id=campo.id).first()
        if row:
            row.valor = val
        else:
            db.session.add(
                UsuarioCampoValor(user_id=user.id, campo_id=campo.id, valor=val)
            )
    return None


def _equipo_form_context(usuario: Optional[User], empresa_id: int) -> dict:
    emp = Empresa.query.get(empresa_id)
    sector = normalizar_sector(emp.sector if emp else None)
    campos = campos_para_equipo(empresa_id, sector) if empresa_id else []
    valores = valores_campos_usuario_map(usuario) if usuario else {}
    return {
        "sedes": _sedes_empresa(empresa_id) if empresa_id else [],
        "campos_personalizados": campos,
        "valores_campos": valores,
        "tarifa_hora_valor": formatear_monto_sin_simbolo(
            usuario.tarifa_hora, emp.moneda
        ) if usuario and emp else "",
        "tarifa_hora_simbolo": simbolo_moneda_input(emp.moneda if emp else "COP"),
    }


@bp.route("/equipo")
def equipo_list():
    if not can_manage_equipo(current_user):
        flash("Solo los administradores pueden gestionar el equipo de trabajo.", "warning")
        return redirect(url_for("main.dashboard"))
    return render_template(
        "equipo/list.html",
        usuarios=_equipo_usuarios_query().all(),
        puede_gestionar=True,
    )


@bp.route("/equipo/nuevo", methods=["GET", "POST"])
def equipo_new():
    if not _require_admin_equipo():
        return redirect(url_for("main.equipo_list"))
    eid = _current_empresa_id()
    if not eid:
        flash("No hay empresa asociada a tu cuenta.", "warning")
        return redirect(url_for("main.equipo_list"))
    emp = Empresa.query.get(eid)
    sector = normalizar_sector(emp.sector if emp else None)
    roles = roles_for_select(current_user, empresa=emp)
    roles_ayuda = role_help_map(empresa=emp)
    ctx = _equipo_form_context(None, eid)

    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        nombre = request.form.get("nombre_visible", "").strip()
        area = request.form.get("area", "").strip()
        cargo = request.form.get("cargo", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        rol = (request.form.get("rol") or UserRole.TECNICO.value).strip().lower()
        activo = bool(request.form.get("activo"))
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        sede_id, err_sede = _parse_sede_equipo(request.form, eid)
        tarifa_hora, err_tarifa = _parse_tarifa_hora_equipo(request.form, emp)

        err_u = _validar_username_equipo(username)
        if err_u:
            flash(err_u, "danger")
        elif not username_disponible(username, eid):
            flash("Ese nombre de usuario ya está en uso en tu empresa.", "danger")
        elif not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not area:
            flash("El área es obligatoria.", "danger")
        elif rol not in USER_ROLE_LABELS:
            flash("Selecciona un rol válido.", "danger")
        elif not can_assign_role(current_user, rol):
            flash("No puedes asignar ese rol.", "danger")
        elif err_sede:
            flash(err_sede, "danger")
        elif err_tarifa:
            flash(err_tarifa, "danger")
        elif err_pwd := validar_password(password):
            flash(err_pwd, "danger")
        elif password != password2:
            flash("Las contraseñas no coinciden.", "danger")
        else:
            user = User(
                empresa_id=eid,
                username=username,
                nombre_visible=nombre,
                area=area,
                cargo=cargo,
                tarifa_hora=tarifa_hora,
                sede_id=sede_id,
                email=email,
                telefono=telefono,
                rol=rol,
                activo=activo,
                onboarding_completado=True,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            err_c = _save_user_custom_fields(user, request.form, eid, sector)
            if err_c:
                db.session.rollback()
                flash(err_c, "danger")
            else:
                _sync_technician_for_user(user)
                try:
                    db.session.commit()
                    flash(f"Usuario «{username}» invitado al equipo.", "success")
                    return redirect(url_for("main.equipo_list"))
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")

    return render_template(
        "equipo/form.html",
        usuario=None,
        roles=roles,
        roles_ayuda=roles_ayuda,
        es_self=False,
        **ctx,
    )


@bp.route("/mi-perfil", methods=["GET", "POST"])
def mi_perfil():
    """El administrador puede editar su propia cuenta."""
    if not _require_admin_equipo():
        return redirect(url_for("main.dashboard"))
    return equipo_edit(current_user.id)


@bp.route("/equipo/<int:id>/editar", methods=["GET", "POST"])
def equipo_edit(id):
    if not _require_admin_equipo():
        return redirect(url_for("main.dashboard"))
    eid = _current_empresa_id()
    usuario = User.query.filter_by(id=id, empresa_id=eid).first_or_404()
    es_self = usuario.id == current_user.id
    emp = Empresa.query.get(eid)
    sector = normalizar_sector(emp.sector if emp else None)
    roles = roles_for_select(current_user, empresa=emp)
    roles_ayuda = role_help_map(empresa=emp)
    ctx = _equipo_form_context(usuario, eid)

    if request.method == "POST":
        email_anterior = usuario.email or ""
        activo_anterior = bool(usuario.activo)
        username = (request.form.get("username") or "").strip().lower()
        nombre = request.form.get("nombre_visible", "").strip()
        area = request.form.get("area", "").strip()
        cargo = request.form.get("cargo", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        if es_self:
            rol = normalize_rol(usuario.rol)
            activo = bool(usuario.activo)
        else:
            rol = (request.form.get("rol") or usuario.rol).strip().lower()
            activo = bool(request.form.get("activo"))
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        sede_id, err_sede = _parse_sede_equipo(request.form, eid)
        tarifa_hora, err_tarifa = _parse_tarifa_hora_equipo(request.form, emp)

        err_u = _validar_username_equipo(username)
        if err_u:
            flash(err_u, "danger")
        elif username != usuario.username and not username_disponible(
            username, eid, excluir_user_id=usuario.id
        ):
            flash("Ese nombre de usuario ya está en uso en tu empresa.", "danger")
        elif not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not area:
            flash("El área es obligatoria.", "danger")
        elif rol not in USER_ROLE_LABELS:
            flash("Selecciona un rol válido.", "danger")
        elif not es_self and not can_assign_role(current_user, rol):
            flash("No puedes asignar ese rol.", "danger")
        elif err_sede:
            flash(err_sede, "danger")
        elif err_tarifa:
            flash(err_tarifa, "danger")
        elif es_self and not activo:
            flash("No puedes desactivar tu propia cuenta.", "danger")
        elif es_self and rol != normalize_rol(current_user.rol):
            flash("No puedes cambiar tu propio rol.", "danger")
        elif password and (err_pwd := validar_password(password)):
            flash(err_pwd, "danger")
        elif password and password != password2:
            flash("Las contraseñas no coinciden.", "danger")
        elif (
            not es_self
            and normalize_rol(usuario.rol) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)
            and usuario.activo
            and (
                not activo
                or normalize_rol(rol)
                not in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)
            )
            and User.query.filter(
                User.empresa_id == eid,
                User.activo.is_(True),
                User.rol.in_(
                    [
                        UserRole.SUPERADMIN.value,
                        UserRole.ADMIN.value,
                        "supervisor",
                    ]
                ),
            ).count()
            <= 1
        ):
            flash("Debe quedar al menos un superadministrador o administrador activo.", "warning")
        else:
            usuario.username = username
            usuario.nombre_visible = nombre
            usuario.area = area
            usuario.cargo = cargo
            usuario.tarifa_hora = tarifa_hora
            usuario.sede_id = sede_id
            usuario.email = email
            usuario.telefono = telefono
            if not es_self:
                usuario.rol = rol
                usuario.activo = activo
            if password:
                usuario.set_password(password)
            err_c = _save_user_custom_fields(usuario, request.form, eid, sector)
            if err_c:
                flash(err_c, "danger")
            else:
                _sync_technician_for_user(usuario)
                try:
                    revocar_por_password = bool(password) and bool(
                        getattr(emp, "session_revoke_on_password", True)
                    )
                    cambio_sensible = revocar_por_password or email != email_anterior or (
                        activo_anterior and not bool(usuario.activo)
                    )
                    if cambio_sensible:
                        from app.session_management import revoke_user_sessions

                        usuario.auth_version = int(usuario.auth_version or 1) + 1
                        revoke_user_sessions(usuario.id, reason="credenciales_actualizadas")
                        from app.tenant_activity import registrar_actividad_tenant

                        registrar_actividad_tenant(
                            eid,
                            "password_changed" if password else "session_revoked",
                            user_id=usuario.id,
                            username=usuario.username,
                            detalle="Sesiones revocadas por cambio de credenciales o estado",
                        )
                    db.session.commit()
                    if cambio_sensible and es_self:
                        logout_user()
                        session.clear()
                        flash("Tus credenciales cambiaron. Inicia sesión nuevamente.", "info")
                        return redirect(url_for("main.login"))
                    flash("Perfil actualizado." if es_self else "Miembro actualizado.", "success")
                    return redirect(url_for("main.equipo_list"))
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")

    return render_template(
        "equipo/form.html",
        usuario=usuario,
        roles=roles,
        roles_ayuda=roles_ayuda,
        es_self=es_self,
        **ctx,
    )


# --- Configuración empresa ---
def _empresa_del_usuario() -> Optional[Empresa]:
    if not current_user.is_authenticated or not current_user.empresa_id:
        return None
    return current_user.empresa


# --- Campos personalizados (configuración) ---
def _require_admin_empresa() -> Optional[Empresa]:
    emp = _empresa_del_usuario()
    if emp is None:
        flash("No hay una empresa asociada a tu cuenta.", "warning")
        return None
    if not can_manage_config(current_user):
        flash("Solo el superadministrador puede gestionar esta configuración.", "warning")
        return None
    return emp


def _campos_personalizados_empresa_query(empresa_id: int, sector: str):
    return CampoPersonalizado.query.filter_by(
        empresa_id=empresa_id, sector=normalizar_sector(sector)
    )


def _categorias_seleccionadas_campo(
    tipos: list, form=None, campo: Optional[CampoPersonalizado] = None
) -> list[int]:
    valid = {t.id for t in tipos}
    if form is not None:
        return parse_categorias_form(form, valid)
    if campo:
        return campo.categorias_aplicables()
    return []


def _seccion_campo_desde_form(form) -> str:
    sel = (form.get("seccion") or "").strip()
    if sel == "__nueva__":
        nombre = (form.get("seccion_nueva") or "").strip()
        return nombre or "general"
    if sel in ACTIVO_SECCION_KEYS:
        return sel
    if sel:
        return sel
    return "general"


def _categorias_campo_guardar(
    form,
    tipos: list,
    empresa_id: int,
    sector: str,
    seccion: str,
    entidad: str,
) -> list[int]:
    if entidad == CAMPO_ENTIDAD_EQUIPO:
        return []
    form_cats = _categorias_seleccionadas_campo(tipos, form=form)
    if es_seccion_estandar(seccion):
        return form_cats
    inherited = categorias_de_seccion_personalizada(empresa_id, sector, seccion)
    if inherited is None:
        return form_cats
    if inherited == []:
        return []
    if form_cats:
        return form_cats
    return inherited


def _seccion_ancla_desde_form(
    form, seccion: str, empresa_id: int, sector: str
) -> str:
    if es_seccion_estandar(seccion):
        return ""
    sel = (form.get("seccion") or "").strip()
    if sel == "__nueva__":
        return normalizar_seccion_ancla(form.get("seccion_ancla"))
    return ancla_de_seccion_personalizada(empresa_id, sector, seccion)


def _campo_form_context(
    *,
    empresa_id: int,
    sector: str,
    campo,
    tipos_maquina,
    siguiente_orden: int,
    sector_label: str,
    opciones_texto: str = "",
    categorias_seleccionadas: Optional[list[int]] = None,
    seccion_key_override: Optional[str] = None,
    seccion_nueva_valor: str = "",
    seccion_ancla_sel_override: Optional[str] = None,
) -> dict:
    cats = categorias_seleccionadas if categorias_seleccionadas is not None else (
        campo.categorias_aplicables() if campo else []
    )
    entidad = (campo.entidad if campo else CAMPO_ENTIDAD_ACTIVO) or CAMPO_ENTIDAD_ACTIVO
    sector = normalizar_sector(sector)
    sec_raw = campo.seccion if campo else "general"
    secciones_personalizadas = secciones_personalizadas_empresa(empresa_id, sector)
    if campo and not es_seccion_estandar(sec_raw):
        seccion_key = sec_raw
    elif not campo:
        seccion_key = "general"
    else:
        seccion_key = normalizar_seccion_campo(sec_raw)
    if seccion_key_override is not None:
        seccion_key = seccion_key_override
    cats_default = cats
    if (
        entidad == CAMPO_ENTIDAD_ACTIVO
        and seccion_key
        and seccion_key not in ACTIVO_SECCION_KEYS
        and seccion_key != "__nueva__"
    ):
        inherited_cats = categorias_de_seccion_personalizada(empresa_id, sector, seccion_key)
        if inherited_cats is not None:
            cats_default = inherited_cats
    ancla_sel = ""
    if seccion_ancla_sel_override is not None:
        ancla_sel = seccion_ancla_sel_override
    elif campo and not es_seccion_estandar(sec_raw):
        ancla_sel = normalizar_seccion_ancla(campo.seccion_ancla)
    elif not campo and seccion_key == "__nueva__":
        ancla_sel = "general"
    elif not campo:
        ancla_sel = "general"
    return {
        "campo": campo,
        "tipos_maquina": tipos_maquina,
        "tipos_campo": CAMPO_TIPOS,
        "texto_tamanos": TEXTO_TAMANOS,
        "entidades_campo": CAMPO_ENTIDADES,
        "entidad": entidad,
        "activo_secciones": ACTIVO_SECCIONES,
        "activo_seccion_keys_list": list(ACTIVO_SECCION_KEYS),
        "seccion_key": seccion_key,
        "seccion_nueva_valor": seccion_nueva_valor,
        "seccion_ancla_sel": ancla_sel,
        "secciones_personalizadas": secciones_personalizadas,
        "siguiente_orden": siguiente_orden,
        "sector_label": sector_label,
        "opciones_texto": opciones_texto,
        "categorias_seleccionadas": cats_default,
        "todas_categorias": len(cats_default) == 0,
        "etiqueta_seccion_campo": etiqueta_seccion_campo,
        "etiqueta_seccion_campo_con_ancla": etiqueta_seccion_campo_con_ancla,
    }


@bp.route("/configuracion/campos")
def configuracion_campos_list():
    emp = _require_admin_empresa()
    if emp is None:
        return redirect(url_for("main.dashboard"))
    sector = normalizar_sector(emp.sector)
    campos = (
        _campos_personalizados_empresa_query(emp.id, sector)
        .order_by(CampoPersonalizado.orden, CampoPersonalizado.nombre)
        .all()
    )
    tipos_map = {t.id: t.nombre for t in _machine_types_query().all()}
    return render_template(
        "configuracion/campos_list.html",
        campos=campos,
        empresa=emp,
        sector_label=SECTOR_LABELS.get(sector, sector),
        tipos_map=tipos_map,
        etiqueta_categorias_campo=etiqueta_categorias_campo,
        etiqueta_seccion_campo=etiqueta_seccion_campo,
        etiqueta_seccion_campo_con_ancla=etiqueta_seccion_campo_con_ancla,
    )


@bp.route("/configuracion/campos/nuevo", methods=["GET", "POST"])
def configuracion_campos_new():
    emp = _require_admin_empresa()
    if emp is None:
        return redirect(url_for("main.dashboard"))
    sector = normalizar_sector(emp.sector)
    tipos = _machine_types_query().filter_by(activo=True).order_by(MachineType.orden).all()
    max_orden = (
        db.session.query(func.max(CampoPersonalizado.orden))
        .filter_by(empresa_id=emp.id, sector=sector)
        .scalar()
    )
    siguiente_orden = (max_orden or 0) + 1

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        tipo = (request.form.get("tipo") or "text").strip().lower()
        texto_tamano = parse_texto_tamano_form(request.form, tipo)
        entidad = (request.form.get("entidad") or CAMPO_ENTIDAD_ACTIVO).strip().lower()
        obligatorio = bool(request.form.get("obligatorio"))
        try:
            orden = int(request.form.get("orden") or siguiente_orden)
        except ValueError:
            orden = siguiente_orden
        seccion = _seccion_campo_desde_form(request.form) if entidad == CAMPO_ENTIDAD_ACTIVO else ""
        cat_ids = _categorias_campo_guardar(
            request.form, tipos, emp.id, sector, seccion, entidad
        )
        categorias_json = categorias_ids_a_json(cat_ids) if cat_ids else ""

        if not nombre:
            flash("El nombre del campo es obligatorio.", "danger")
        elif tipo not in CAMPO_TIPOS_VALIDOS:
            flash("Selecciona un tipo de campo válido.", "danger")
        elif entidad not in (CAMPO_ENTIDAD_ACTIVO, CAMPO_ENTIDAD_EQUIPO):
            flash("Selecciona dónde aplica el campo.", "danger")
        elif entidad == CAMPO_ENTIDAD_ACTIVO and request.form.get("seccion") == "__nueva__" and not (request.form.get("seccion_nueva") or "").strip():
            flash("Indica el nombre de la nueva sección personalizada.", "danger")
        else:
            opciones_json = ""
            if tipo in TIPOS_CON_OPCIONES:
                opciones_json, err = parse_opciones_texto(request.form.get("opciones", ""))
                if err:
                    flash(err, "danger")
                    return render_template(
                        "configuracion/campo_form.html",
                        **_campo_form_context(
                            empresa_id=emp.id,
                            sector=sector,
                            campo=None,
                            tipos_maquina=tipos,
                            siguiente_orden=siguiente_orden,
                            sector_label=SECTOR_LABELS.get(sector, sector),
                            opciones_texto=request.form.get("opciones", ""),
                            categorias_seleccionadas=cat_ids,
                            seccion_key_override=(request.form.get("seccion") or "").strip(),
                            seccion_nueva_valor=(request.form.get("seccion_nueva") or "").strip(),
                            seccion_ancla_sel_override=normalizar_seccion_ancla(
                                request.form.get("seccion_ancla")
                            ),
                        ),
                    )
            clave = clave_campo_unica(
                emp.id, sector, slugify_campo_clave(nombre), entidad=entidad
            )
            ancla = (
                _seccion_ancla_desde_form(request.form, seccion, emp.id, sector)
                if entidad == CAMPO_ENTIDAD_ACTIVO
                else ""
            )
            db.session.add(
                CampoPersonalizado(
                    empresa_id=emp.id,
                    sector=sector,
                    entidad=entidad,
                    seccion=seccion if entidad == CAMPO_ENTIDAD_ACTIVO else "",
                    seccion_ancla=ancla,
                    machine_type_id=None,
                    categorias_ids=categorias_json,
                    clave=clave,
                    nombre=nombre,
                    tipo=tipo,
                    texto_tamano=texto_tamano,
                    opciones=opciones_json,
                    obligatorio=obligatorio,
                    orden=orden,
                    activo=True,
                )
            )
            try:
                db.session.commit()
                flash(f"Campo «{nombre}» creado.", "success")
                return redirect(url_for("main.configuracion_campos_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar el campo.", "danger")

    return render_template(
        "configuracion/campo_form.html",
        **_campo_form_context(
            empresa_id=emp.id,
            sector=sector,
            campo=None,
            tipos_maquina=tipos,
            siguiente_orden=siguiente_orden,
            sector_label=SECTOR_LABELS.get(sector, sector),
        ),
    )


@bp.route("/configuracion/campos/<int:id>/editar", methods=["GET", "POST"])
def configuracion_campos_edit(id):
    emp = _require_admin_empresa()
    if emp is None:
        return redirect(url_for("main.dashboard"))
    sector = normalizar_sector(emp.sector)
    campo = _campos_personalizados_empresa_query(emp.id, sector).filter_by(id=id).first_or_404()
    tipos = _machine_types_query().filter_by(activo=True).order_by(MachineType.orden).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        tipo = (request.form.get("tipo") or campo.tipo).strip().lower()
        texto_tamano = parse_texto_tamano_form(request.form, tipo)
        obligatorio = bool(request.form.get("obligatorio"))
        activo = bool(request.form.get("activo"))
        try:
            orden = int(request.form.get("orden") or campo.orden)
        except ValueError:
            orden = campo.orden
        entidad = (campo.entidad or CAMPO_ENTIDAD_ACTIVO).strip().lower()
        seccion = _seccion_campo_desde_form(request.form) if entidad == CAMPO_ENTIDAD_ACTIVO else ""
        cat_ids = _categorias_campo_guardar(
            request.form, tipos, emp.id, sector, seccion, entidad
        )
        categorias_json = categorias_ids_a_json(cat_ids) if cat_ids else ""

        if not nombre:
            flash("El nombre del campo es obligatorio.", "danger")
        elif tipo not in CAMPO_TIPOS_VALIDOS:
            flash("Selecciona un tipo de campo válido.", "danger")
        elif entidad == CAMPO_ENTIDAD_ACTIVO and request.form.get("seccion") == "__nueva__" and not (request.form.get("seccion_nueva") or "").strip():
            flash("Indica el nombre de la nueva sección personalizada.", "danger")
        else:
            opciones_json = campo.opciones or ""
            if tipo in TIPOS_CON_OPCIONES:
                opciones_json, err = parse_opciones_texto(request.form.get("opciones", ""))
                if err:
                    flash(err, "danger")
                    return render_template(
                        "configuracion/campo_form.html",
                        **_campo_form_context(
                            empresa_id=emp.id,
                            sector=sector,
                            campo=campo,
                            tipos_maquina=tipos,
                            siguiente_orden=campo.orden,
                            sector_label=SECTOR_LABELS.get(sector, sector),
                            opciones_texto=request.form.get("opciones", ""),
                            categorias_seleccionadas=cat_ids,
                            seccion_key_override=(request.form.get("seccion") or "").strip(),
                            seccion_nueva_valor=(request.form.get("seccion_nueva") or "").strip(),
                            seccion_ancla_sel_override=normalizar_seccion_ancla(
                                request.form.get("seccion_ancla")
                            ),
                        ),
                    )
            elif tipo not in TIPOS_CON_OPCIONES:
                opciones_json = ""
            campo.nombre = nombre
            campo.tipo = tipo
            campo.texto_tamano = texto_tamano
            campo.opciones = opciones_json
            campo.obligatorio = obligatorio
            campo.orden = orden
            campo.activo = activo
            campo.machine_type_id = None
            campo.categorias_ids = categorias_json
            campo.seccion = seccion if entidad == CAMPO_ENTIDAD_ACTIVO else ""
            campo.seccion_ancla = (
                _seccion_ancla_desde_form(request.form, seccion, emp.id, sector)
                if entidad == CAMPO_ENTIDAD_ACTIVO
                else ""
            )
            try:
                db.session.commit()
                flash("Campo actualizado.", "success")
                return redirect(url_for("main.configuracion_campos_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar.", "danger")

    return render_template(
        "configuracion/campo_form.html",
        **_campo_form_context(
            empresa_id=emp.id,
            sector=sector,
            campo=campo,
            tipos_maquina=tipos,
            siguiente_orden=campo.orden,
            sector_label=SECTOR_LABELS.get(sector, sector),
            opciones_texto=opciones_a_texto_form(campo),
        ),
    )


@bp.route("/configuracion/campos/<int:id>/eliminar", methods=["POST"])
def configuracion_campos_delete(id):
    emp = _require_admin_empresa()
    if emp is None:
        return redirect(url_for("main.dashboard"))
    sector = normalizar_sector(emp.sector)
    campo = _campos_personalizados_empresa_query(emp.id, sector).filter_by(id=id).first_or_404()
    n_valores = campo.valores.count() + campo.valores_usuario.count()
    if n_valores > 0:
        campo.activo = False
        db.session.commit()
        flash(
            f"El campo «{campo.nombre}» se desactivó ({n_valores} registro(s) ya lo usan).",
            "info",
        )
    else:
        db.session.delete(campo)
        db.session.commit()
        flash("Campo eliminado.", "info")
    return redirect(url_for("main.configuracion_campos_list"))


def _empresa_logo_url(empresa: Optional[Empresa]) -> str:
    if empresa and empresa.logo:
        if empresa.logo.startswith(("http://", "https://")):
            return empresa.logo
        return url_for("static", filename=empresa.logo)
    return url_for("static", filename=APP_LOGO_PATH)


def _empresa_logo_url_or_none(empresa: Optional[Empresa]) -> Optional[str]:
    return empresa_logo_url_or_none(empresa)


def _guardar_logo_empresa(empresa: Empresa, archivo) -> None:
    if not archivo or not getattr(archivo, "filename", None):
        return
    nombre = secure_filename(archivo.filename)
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EMPRESA_LOGO_EXTENSIONS:
        raise ValueError("Formato de imagen no permitido. Use PNG, JPG o WEBP.")
    carpeta = os.path.join(
        current_app.static_folder, "uploads", "empresas", str(empresa.id)
    )
    os.makedirs(carpeta, exist_ok=True)
    ruta_abs = os.path.join(carpeta, f"logo.{ext}")
    archivo.save(ruta_abs)
    empresa.logo = f"uploads/empresas/{empresa.id}/logo.{ext}"


@bp.route("/configuracion/empresa", methods=["GET", "POST"])
def configuracion_empresa():
    emp = _empresa_del_usuario()
    if emp is None:
        flash("No hay una empresa asociada a tu cuenta.", "warning")
        return redirect(url_for("main.dashboard"))
    if not can_manage_config(current_user):
        flash("Solo el superadministrador puede modificar la configuración de la empresa.", "warning")
        return redirect(url_for("main.dashboard"))

    sede_principal = Sede.query.filter_by(empresa_id=emp.id, es_principal=True).first()
    sedes = (
        Sede.query.filter_by(empresa_id=emp.id)
        .order_by(Sede.es_principal.desc(), Sede.nombre)
        .all()
    )
    plan = (
        PlanSuscripcion.query.filter_by(empresa_id=emp.id, activo=True)
        .order_by(PlanSuscripcion.id.desc())
        .first()
    )

    if request.method == "POST":
        accion = request.form.get("accion", "guardar")
        if accion == "nueva_sede":
            nombre_sede = request.form.get("nueva_sede_nombre", "").strip()
            if not nombre_sede:
                flash("Indica el nombre de la sede.", "danger")
            elif Sede.query.filter_by(empresa_id=emp.id, nombre=nombre_sede).first():
                flash("Ya existe una sede con ese nombre.", "danger")
            else:
                db.session.add(Sede(empresa_id=emp.id, nombre=nombre_sede, es_principal=False))
                db.session.commit()
                flash("Sede agregada.", "success")
            return redirect(url_for("main.configuracion_empresa"))

        emp.razon_social = request.form.get("razon_social", "").strip()
        emp.nit = request.form.get("nit", "").strip()
        emp.direccion = request.form.get("direccion", "").strip()
        emp.ciudad = request.form.get("ciudad", "").strip()
        emp.pais = request.form.get("pais", "Colombia").strip()
        emp.telefono = request.form.get("telefono", "").strip()
        emp.email = request.form.get("email", "").strip()
        sector = request.form.get("sector", emp.sector)
        if sector in SECTOR_LABELS:
            nuevo = normalizar_sector(sector)
            if nuevo != emp.sector and Machine.query.filter_by(empresa_id=emp.id).count() == 0:
                crear_plantilla_sector(emp.id, nuevo)
            emp.sector = nuevo
        emp.moneda = request.form.get("moneda", emp.moneda) or "COP"
        emp.zona_horaria = request.form.get("zona_horaria", emp.zona_horaria) or "America/Bogota"
        logo_url = request.form.get("logo_url", "").strip()
        if logo_url:
            logo_norm = normalizar_logo_empresa(logo_url)
            if logo_norm is None:
                flash("URL de logo no válida. Use https:// o una ruta bajo uploads/.", "danger")
                return redirect(url_for("main.configuracion_empresa"))
            emp.logo = logo_norm
        if not emp.razon_social:
            flash("La razón social es obligatoria.", "danger")
            return redirect(url_for("main.configuracion_empresa"))
        if sede_principal:
            sede_principal.nombre = request.form.get("sede_principal_nombre", "").strip() or sede_principal.nombre
        try:
            _guardar_logo_empresa(emp, request.files.get("logo_archivo"))
            db.session.commit()
            flash("Configuración de la empresa guardada.", "success")
            return redirect(url_for("main.configuracion_empresa"))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), "danger")
        except Exception:
            import logging

            db.session.rollback()
            logging.getLogger(__name__).exception("Error al guardar configuración de empresa")
            flash("No se pudo guardar la configuración.", "danger")

    from app.platform_config_service import catalogo_plan_meta

    plan_meta = catalogo_plan_meta(plan.plan) if plan else {}
    from app.platform_audit import PLATFORM_AUDIT_LABELS, auditoria_visible_empresa

    return render_template(
        "configuracion/empresa.html",
        empresa=emp,
        sede_principal=sede_principal,
        sedes=sedes,
        plan=plan,
        plan_meta=plan_meta,
        sectores=list(SECTOR_LABELS.items()),
        monedas=MONEDAS_EMPRESA,
        zonas=ZONAS_EMPRESA,
        logo_url=_empresa_logo_url(emp),
        auditoria_plataforma=auditoria_visible_empresa(emp.id),
        audit_labels=PLATFORM_AUDIT_LABELS,
    )


# --- Reportes ---
@bp.route("/reportes")
def reportes():
    m_q = _filter_empresa(Machine.query, Machine)
    wo_q = _filter_work_orders_empresa(WorkOrder.query)
    sp_q = _filter_empresa(SparePart.query, SparePart)
    total_m = m_q.count()
    by_status = (
        m_q.with_entities(Machine.status, func.count(Machine.id))
        .group_by(Machine.status)
        .all()
    )
    wo_by_type = (
        wo_q.with_entities(WorkOrder.tipo, func.count(WorkOrder.id)).group_by(WorkOrder.tipo).all()
    )
    wo_by_status = (
        wo_q.with_entities(WorkOrder.status, func.count(WorkOrder.id))
        .group_by(WorkOrder.status)
        .all()
    )
    bajo_minimo = sp_q.filter(SparePart.cantidad < SparePart.stock_minimo).count()
    bajo_minimo_items = (
        sp_q.filter(SparePart.cantidad < SparePart.stock_minimo)
        .order_by(SparePart.nombre)
        .limit(10)
        .all()
    )
    return render_template(
        "reportes.html",
        total_m=total_m,
        by_status=by_status,
        wo_by_type=wo_by_type,
        wo_by_status=wo_by_status,
        bajo_minimo=bajo_minimo,
        bajo_minimo_items=bajo_minimo_items,
        chart_estado_labels=[machine_status_meta(r[0])["label"] for r in by_status],
        chart_estado_data=[r[1] for r in by_status],
        chart_tipo_labels=[wo_tipo_meta(r[0])["label"] for r in wo_by_type],
        chart_tipo_data=[r[1] for r in wo_by_type],
        chart_tipo_colors=[wo_tipo_meta(r[0])["color"] for r in wo_by_type],
        chart_wo_labels=[wo_status_meta(r[0])["label"] for r in wo_by_status],
        chart_wo_data=[r[1] for r in wo_by_status],
        chart_wo_colors=[wo_status_meta(r[0])["color"] for r in wo_by_status],
    )


# --- Incidencias ---
def _areas_incidencia_empresa(empresa_id: Optional[int]) -> list[str]:
    areas = {a.strip() for a in INCIDENT_AREAS_BASE if a.strip()}
    if current_user.is_authenticated and (current_user.area or "").strip():
        areas.add(current_user.area.strip())
    if empresa_id:
        q = db.session.query(Machine.area).filter(
            Machine.empresa_id == empresa_id,
            Machine.area.isnot(None),
            Machine.area != "",
        ).distinct()
        areas.update((row[0] or "").strip() for row in q if (row[0] or "").strip())
    return sorted(areas, key=str.lower)


def _incidencia_form_defaults() -> dict:
    u = current_user if current_user.is_authenticated else None
    tel = (getattr(u, "telefono", None) or "").strip() if u else ""
    area = (getattr(u, "area", None) or "").strip() if u else ""
    return {
        "reportado_por": u.etiqueta() if u else "",
        "cargo_reportante": (getattr(u, "cargo", None) or "").strip() if u else "",
        "telefono_contacto": tel,
        "area": area,
        "area_responsable": "",
        "ubicacion": "",
        "titulo": "",
        "machine_id": "",
        "tipo": "",
        "descripcion": "",
        "prioridad": IncidentPrioridad.MEDIA.value,
        "equipo_detenido": False,
        "fecha_evento": "",
        "hora_evento": "",
    }


def _incidencia_desde_form(form) -> tuple[dict, Optional[str]]:
    data = {
        "reportado_por": (form.get("reportado_por") or "").strip(),
        "cargo_reportante": (form.get("cargo_reportante") or "").strip(),
        "telefono_contacto": (form.get("telefono_contacto") or "").strip(),
        "area": (form.get("area") or "").strip(),
        "area_responsable": (form.get("area_responsable") or "").strip(),
        "ubicacion": (form.get("ubicacion") or "").strip(),
        "titulo": (form.get("titulo") or "").strip(),
        "machine_id": (form.get("machine_id") or "").strip(),
        "tipo": (form.get("tipo") or "").strip(),
        "descripcion": (form.get("descripcion") or "").strip(),
        "prioridad": (form.get("prioridad") or IncidentPrioridad.MEDIA.value).strip().lower(),
        "equipo_detenido": form.get("equipo_detenido") == "1",
        "fecha_evento": (form.get("fecha_evento") or "").strip(),
        "hora_evento": (form.get("hora_evento") or "").strip(),
    }
    if not data["reportado_por"]:
        return data, "Indica el nombre de quien reporta la falla."
    if not data["area"]:
        return data, "Selecciona el área del reportante."
    if not data["area_responsable"]:
        return data, "Selecciona el área responsable que recibirá el incidente."
    if not data["titulo"]:
        return data, "Describe brevemente la incidencia."
    if not data["tipo"]:
        return data, "Selecciona el tipo de incidencia."
    if not data["descripcion"]:
        return data, "Incluye una descripción detallada."
    valid_prioridades = {p[0] for p in INCIDENT_PRIORIDADES}
    if data["prioridad"] not in valid_prioridades:
        data["prioridad"] = IncidentPrioridad.MEDIA.value
    valid_tipos = {t[0] for t in INCIDENT_TIPOS}
    if data["tipo"] not in valid_tipos:
        return data, "Tipo de incidencia no válido."
    if data["fecha_evento"]:
        try:
            datetime.strptime(data["fecha_evento"], "%Y-%m-%d")
        except ValueError:
            return data, "Fecha del evento no válida."
    if data["hora_evento"]:
        try:
            datetime.strptime(data["hora_evento"], "%H:%M")
        except ValueError:
            return data, "Hora del evento no válida."
    return data, None


def _asignar_numero_incidencia(inc: Incident) -> str:
    year = date.today().year % 100
    prefix = f"INC-{year:02d}-"
    q = Incident.query.filter(Incident.numero.like(f"{prefix}%"))
    if inc.empresa_id:
        q = q.filter(Incident.empresa_id == inc.empresa_id)
    last = q.order_by(Incident.id.desc()).first()
    seq = 1
    if last and last.numero:
        try:
            seq = int(str(last.numero).split("-")[-1]) + 1
        except ValueError:
            seq = 1
    inc.numero = f"{prefix}{seq:04d}"
    return inc.numero


def _incidencia_preview_numero(empresa_id: Optional[int]) -> str:
    year = date.today().year % 100
    prefix = f"INC-{year:02d}-"
    q = Incident.query.filter(Incident.numero.like(f"{prefix}%"))
    if empresa_id:
        q = q.filter(Incident.empresa_id == empresa_id)
    last = q.order_by(Incident.id.desc()).first()
    seq = 1
    if last and last.numero:
        try:
            seq = int(str(last.numero).split("-")[-1]) + 1
        except ValueError:
            seq = 1
    return f"{prefix}{seq:04d}"


@bp.route("/incidencia", methods=["GET", "POST"])
def incidencia():
    eid = _current_empresa_id()
    machines = _filter_empresa(Machine.query.order_by(Machine.nombre), Machine).all()
    areas = _areas_incidencia_empresa(eid)
    form_data = _incidencia_form_defaults()
    ahora = datetime.now()
    preview_numero = _incidencia_preview_numero(eid)
    idempotency_key = str(uuid4())

    if request.method == "POST":
        submitted_key = (request.form.get("idempotency_key") or "").strip()
        try:
            idempotency_key = str(UUID(submitted_key))
        except (ValueError, AttributeError):
            flash("El formulario expiró. Recarga la página e intenta nuevamente.", "danger")
            return redirect(url_for("main.incidencia"))

        existing = Incident.query.filter_by(idempotency_key=idempotency_key).first()
        if existing is not None:
            flash(f"La incidencia {existing.numero} ya había sido registrada.", "info")
            return redirect(url_for("main.incidencias_detail", id=existing.id))

        form_data, err = _incidencia_desde_form(request.form)
        if err:
            flash(err, "danger")
        else:
            mid = form_data["machine_id"]
            machine_id = int(mid) if mid.isdigit() else None
            machine = None
            if machine_id:
                machine = _filter_empresa(
                    Machine.query.filter_by(id=machine_id), Machine
                ).first()
                if machine is None:
                    flash("El activo seleccionado no pertenece a tu empresa.", "danger")
                    return render_template(
                        "incidencia.html",
                        machines=machines,
                        areas=areas,
                        form=form_data,
                        tipos_incidencia=INCIDENT_TIPOS,
                        prioridades_incidencia=INCIDENT_PRIORIDADES,
                        preview_numero=preview_numero,
                        ahora=ahora,
                        idempotency_key=idempotency_key,
                    )
            fecha_ev = None
            if form_data["fecha_evento"]:
                fecha_ev = datetime.strptime(form_data["fecha_evento"], "%Y-%m-%d").date()
            inc = Incident(
                idempotency_key=idempotency_key,
                titulo=form_data["titulo"],
                descripcion=form_data["descripcion"],
                machine_id=machine.id if machine else None,
                empresa_id=eid,
                user_id=current_user.id if current_user.is_authenticated else None,
                reportado_por=form_data["reportado_por"],
                cargo_reportante=form_data["cargo_reportante"],
                telefono_contacto=form_data["telefono_contacto"],
                area=form_data["area"],
                area_responsable=form_data["area_responsable"],
                ubicacion=form_data["ubicacion"],
                tipo=form_data["tipo"],
                prioridad=form_data["prioridad"],
                equipo_detenido=form_data["equipo_detenido"],
                fecha_evento=fecha_ev,
                hora_evento=form_data["hora_evento"],
            )
            db.session.add(inc)
            db.session.flush()
            numero = _asignar_numero_incidencia(inc)
            _registrar_historial(inc, "reportado", "", IncidentEstado.REPORTADO.value,
                                f"Asignado al área {inc.area_responsable}")
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                existing = Incident.query.filter_by(idempotency_key=idempotency_key).first()
                if existing is None:
                    raise
                flash(f"La incidencia {existing.numero} ya había sido registrada.", "info")
                return redirect(url_for("main.incidencias_detail", id=existing.id))
            flash(f"Incidencia {numero} registrada. El supervisor será notificado.", "success")
            return redirect(url_for("main.incidencias_detail", id=inc.id))

    return render_template(
        "incidencia.html",
        machines=machines,
        areas=areas,
        form=form_data,
        tipos_incidencia=INCIDENT_TIPOS,
        prioridades_incidencia=INCIDENT_PRIORIDADES,
        preview_numero=preview_numero,
        ahora=ahora,
        idempotency_key=idempotency_key,
    )


def _filter_incidents_empresa(q):
    eid = _current_empresa_id()
    if not eid:
        return q
    return q.filter(
        or_(
            Incident.empresa_id == eid,
            Incident.machine_id.in_(_machine_ids_for_empresa()),
        )
    )


def _incidents_scope_query():
    q = _filter_incidents_empresa(Incident.query)
    if normalize_rol(current_user.rol) == UserRole.USUARIO.value or is_requester(current_user):
        q = q.filter(Incident.user_id == current_user.id)
    return q


def _get_incident_or_404(incident_id: int):
    from sqlalchemy.orm import joinedload

    inc = (
        _incidents_scope_query()
        .options(
            joinedload(Incident.machine),
            joinedload(Incident.usuario),
            joinedload(Incident.resuelto_por),
            joinedload(Incident.work_order),
        )
        .filter_by(id=incident_id)
        .first()
    )
    if inc is None:
        abort(404)
    return inc


def _registrar_historial(inc, accion, anterior="", nuevo="", comentario=""):
    db.session.add(IncidentHistory(
        incident_id=inc.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        accion=accion,
        estado_anterior=anterior or "",
        estado_nuevo=nuevo or "",
        comentario=comentario or "",
    ))


def _cambiar_estado(inc, nuevo, accion, comentario=""):
    anterior = inc.estado or IncidentEstado.REPORTADO.value
    inc.estado = nuevo
    inc.resuelto = nuevo in (IncidentEstado.RESUELTO.value, IncidentEstado.CERRADO.value)
    _registrar_historial(inc, accion, anterior, nuevo, comentario)


def _incidentes_kpis(base_q) -> dict:
    pendientes_q = base_q.filter(Incident.resuelto.is_(False))
    return {
        "total": base_q.count(),
        "pendientes": pendientes_q.count(),
        "criticas": pendientes_q.filter(
            Incident.prioridad == IncidentPrioridad.CRITICA.value
        ).count(),
        "resueltas": base_q.filter(Incident.resuelto.is_(True)).count(),
        "mis_pendientes": base_q.filter(
            Incident.user_id == current_user.id,
            Incident.resuelto.is_(False),
        ).count()
        if current_user.is_authenticated
        else 0,
    }


def _usuario_solo_mis_incidencias() -> bool:
    return normalize_rol(current_user.rol) == UserRole.USUARIO.value or is_requester(current_user)


@bp.route("/incidencias")
def incidencias_list():
    from sqlalchemy.orm import joinedload

    q = _incidents_scope_query().options(
        joinedload(Incident.machine), joinedload(Incident.usuario)
    )
    estado_f = (request.args.get("estado") or "").strip().lower()
    area_f = (request.args.get("area") or "").strip()
    prio_f = (request.args.get("prioridad") or "").strip().lower()
    mias_f = request.args.get("mias") == "1"
    q_str = (request.args.get("q") or "").strip()
    solo_gestion = not _usuario_solo_mis_incidencias()

    if mias_f and solo_gestion:
        q = q.filter(Incident.user_id == current_user.id)
    if estado_f == "pendiente":
        q = q.filter(Incident.resuelto.is_(False))
    elif estado_f == "resuelta":
        q = q.filter(Incident.resuelto.is_(True))
    if area_f:
        q = q.filter(Incident.area_responsable == area_f)
    if prio_f:
        q = q.filter(Incident.prioridad == prio_f)
    if q_str:
        like = f"%{q_str}%"
        q = q.filter(
            or_(
                Incident.numero.ilike(like),
                Incident.titulo.ilike(like),
                Incident.reportado_por.ilike(like),
                Incident.descripcion.ilike(like),
            )
        )

    kpis = _incidentes_kpis(_incidents_scope_query())
    items = q.order_by(Incident.resuelto.asc(), Incident.reportado_en.desc()).all()
    areas = _areas_incidencia_empresa(_current_empresa_id())

    return render_template(
        "incidencias/list.html",
        items=items,
        kpis=kpis,
        areas=areas,
        estado_f=estado_f,
        area_f=area_f,
        prioridad_f=prio_f,
        mias_f=mias_f,
        q=q_str,
        solo_gestion=solo_gestion,
        prioridades_incidencia=INCIDENT_PRIORIDADES,
    )


@bp.route("/incidencias/<int:id>")
def incidencias_detail(id):
    inc = _get_incident_or_404(id)
    tecnicos = _filter_empresa(Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician).all()
    return render_template(
        "incidencias/detail.html",
        inc=inc,
        puede_gestionar=can_manage_incidents(current_user),
        puede_crear_ot=can_create_work_order(current_user),
        tecnicos=tecnicos,
        areas=_areas_incidencia_empresa(_current_empresa_id()),
        estados_labels=INCIDENT_ESTADO_LABELS,
    )


@bp.route("/incidencias/<int:id>/accion", methods=["POST"])
def incidencias_accion(id):
    inc = _get_incident_or_404(id)
    accion = (request.form.get("accion") or "").strip()
    comentario = (request.form.get("comentario") or "").strip()
    es_reportante = current_user.is_authenticated and inc.user_id == current_user.id
    if accion in ("validar", "reabrir"):
        if not es_reportante and not can_manage_incidents(current_user):
            abort(403)
    elif not can_manage_incidents(current_user):
        abort(403)


    ahora = datetime.utcnow()
    if accion == "recibir" and inc.estado in ("reportado", "reasignado"):
        inc.responsable_area_id = current_user.id
        inc.recibido_en = ahora
        inc.prioridad_confirmada = (request.form.get("prioridad_confirmada") or inc.prioridad).strip()
        _cambiar_estado(inc, "recibido", "recibido", comentario)
    elif accion == "asignar" and inc.estado in ("reportado", "reasignado", "recibido", "asignado"):
        tid = request.form.get("tecnico_id", type=int)
        tecnico = _filter_empresa(Technician.query.filter_by(id=tid, activo=True), Technician).first() if tid else None
        if not tecnico:
            flash("Selecciona un técnico válido.", "danger")
            return redirect(url_for("main.incidencias_detail", id=id))
        if inc.estado in ("reportado", "reasignado"):
            inc.responsable_area_id = current_user.id
            inc.recibido_en = ahora
            inc.prioridad_confirmada = inc.prioridad
        inc.tecnico_asignado_id, inc.asignado_en = tecnico.id, ahora
        _cambiar_estado(inc, "asignado", "tecnico_asignado", f"{tecnico.nombre}. {comentario}".strip())
    elif accion == "iniciar" and inc.estado == "asignado":
        inc.iniciado_en = ahora
        _cambiar_estado(inc, "en_atencion", "atencion_iniciada", comentario)
    elif accion == "diagnosticar" and inc.estado in ("en_atencion", "diagnosticado"):
        resultado = (request.form.get("resultado") or "").strip()
        destinos = {"solucionado": "solucionado_visita", "ot": "diagnosticado", "reemplazo": "pendiente_reemplazo", "pendiente": "pendiente_usuario", "reasignar": "reasignado"}
        hallazgo = (request.form.get("hallazgo") or "").strip()
        if not hallazgo or resultado not in destinos:
            flash("Registra el hallazgo y selecciona una conclusión.", "danger")
            return redirect(url_for("main.incidencias_detail", id=id))
        db.session.add(IncidentDiagnosis(incident_id=inc.id, technician_id=inc.tecnico_asignado_id,
            hallazgo=hallazgo, causa=(request.form.get("causa") or "").strip(),
            pruebas=(request.form.get("pruebas") or "").strip(), recomendacion=(request.form.get("recomendacion") or "").strip(), resultado=resultado))
        inc.diagnosticado_en = ahora
        if resultado == "reasignar":
            area = (request.form.get("area_responsable") or "").strip()
            if not area:
                flash("Selecciona el área destino.", "danger")
                return redirect(url_for("main.incidencias_detail", id=id))
            inc.area_responsable, inc.responsable_area_id, inc.tecnico_asignado_id = area, None, None
        _cambiar_estado(inc, destinos[resultado], "diagnostico_registrado", hallazgo)
    elif accion == "resolver" and inc.estado in ("solucionado_visita", "pendiente_ot", "pendiente_reemplazo"):
        inc.resuelto_en, inc.resuelto_por_id, inc.notas_resolucion = ahora, current_user.id, comentario
        _cambiar_estado(inc, "resuelto", "resuelto", comentario)
    elif accion == "validar" and inc.estado == "resuelto":
        inc.cerrado_en, inc.motivo_cierre = ahora, comentario or "Solución validada"
        _cambiar_estado(inc, "cerrado", "cerrado", inc.motivo_cierre)
    elif accion == "reabrir" and inc.estado in ("resuelto", "cerrado"):
        inc.resuelto, inc.cerrado_en = False, None
        _cambiar_estado(inc, "recibido", "reabierto", comentario or "La falla persiste")
    else:
        flash("La acción no es válida para el estado actual.", "warning")
        return redirect(url_for("main.incidencias_detail", id=id))
    db.session.commit()
    flash(f"Incidente {inc.numero} actualizado: {inc.estado_label}.", "success")
    return redirect(url_for("main.incidencias_detail", id=id))


@bp.route("/incidencias/<int:id>/resolver", methods=["POST"])
def incidencias_resolver(id):
    if not can_manage_incidents(current_user):
        flash("No tienes permiso para resolver incidencias.", "warning")
        return redirect(url_for("main.incidencias_list"))
    inc = _get_incident_or_404(id)
    if inc.estado not in (IncidentEstado.SOLUCIONADO_VISITA.value,
                          IncidentEstado.PENDIENTE_OT.value,
                          IncidentEstado.PENDIENTE_REEMPLAZO.value):
        flash("Primero debe registrarse un diagnóstico y una conclusión.", "warning")
        return redirect(url_for("main.incidencias_detail", id=inc.id))
    if inc.resuelto:
        flash("Esta incidencia ya está resuelta.", "info")
        return redirect(url_for("main.incidencias_detail", id=inc.id))
    inc.resuelto = True
    inc.resuelto_en = datetime.utcnow()
    inc.resuelto_por_id = current_user.id
    inc.notas_resolucion = (request.form.get("notas_resolucion") or "").strip()
    _cambiar_estado(inc, IncidentEstado.RESUELTO.value, "resuelto", inc.notas_resolucion)
    db.session.commit()
    flash(f"Incidencia {inc.numero or inc.id} marcada como resuelta.", "success")
    return redirect(url_for("main.incidencias_detail", id=inc.id))


@bp.route("/incidencias/<int:id>/crear-ot", methods=["POST"])
def incidencias_crear_ot(id):
    if not can_create_work_order(current_user):
        flash("No tienes permiso para crear órdenes de trabajo.", "warning")
        return redirect(url_for("main.incidencias_list"))
    inc = _get_incident_or_404(id)
    if inc.estado != IncidentEstado.DIAGNOSTICADO.value:
        flash("La OT solo puede crearse después de un diagnóstico que la recomiende.", "warning")
        return redirect(url_for("main.incidencias_detail", id=inc.id))
    if inc.work_order_id and inc.work_order:
        flash(f"Ya existe la OT {inc.work_order.numero}.", "info")
        return redirect(url_for("main.ordenes_edit", id=inc.work_order_id))
    if not inc.machine_id:
        flash("El reporte no tiene equipo relacionado. Edítalo o crea la OT manualmente.", "danger")
        return redirect(url_for("main.incidencias_detail", id=inc.id))
    from app.work_order_status import estado_inicial_por_fecha

    hoy = date.today()
    prio = (inc.prioridad or "media").strip().lower()
    if prio not in {p[0] for p in WORK_ORDER_PRIORITIES}:
        prio = "media"
    wo_tipo = (request.form.get("tipo_ot") or "").strip().lower()
    tipos_ot_validos = {
        WorkOrderType.PREVENTIVO.value,
        WorkOrderType.CORRECTIVO.value,
        WorkOrderType.EMERGENCIA.value,
    }
    if wo_tipo not in tipos_ot_validos:
        flash("Selecciona el tipo de orden de trabajo.", "danger")
        return redirect(url_for("main.incidencias_detail", id=inc.id))
    desc = (inc.descripcion or "").strip()
    if inc.numero:
        desc = f"{desc}\n\n[Origen: incidencia {inc.numero}]".strip()
    wo = WorkOrder(
        titulo=inc.titulo,
        descripcion=desc,
        tipo=wo_tipo,
        status=estado_inicial_por_fecha(hoy),
        prioridad=prio,
        empresa_id=inc.empresa_id or _current_empresa_id(),
        fecha_programada=hoy,
        machine_id=inc.machine_id,
        technician_id=inc.tecnico_asignado_id,
        area=inc.area or "",
        ubicacion=inc.ubicacion or "",
        maquina_requirio_paro=False,
    )
    db.session.add(wo)
    db.session.flush()
    numero = asignar_numero_ot(wo)
    inc.work_order_id = wo.id
    _cambiar_estado(inc, IncidentEstado.PENDIENTE_OT.value, "ot_creada", f"OT {numero} vinculada")
    db.session.commit()
    flash(
        f"OT {numero} creada desde la incidencia {inc.numero}. Ábrela cuando vayas a iniciar su ejecución.",
        "success",
    )
    return redirect(url_for("main.ordenes_list"))
