import json
import os
import re
import unicodedata
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func, or_

from app import db
from app.branding import APP_LOGO_PATH
from app.dashboard_kpis import build_plant_kpi_cards
from app.models import (
    ActivoCampoValor,
    CampoPersonalizado,
    Empresa,
    Incident,
    IndustrialSector,
    Machine,
    MachineStatus,
    MachineType,
    PLAN_CATALOG,
    PlanSuscripcion,
    SECTOR_DASHBOARD_CATEGORIES,
    SECTOR_LABELS,
    Sede,
    MachineMonthlyPlan,
    SparePart,
    Technician,
    User,
    UserRole,
    WORK_ORDER_PRIORITIES,
    WorkOrder,
    WorkOrderJornada,
    WorkOrderRepuesto,
    WorkOrderStatus,
    WorkOrderType,
    WORK_ORDER_TERMINAL_STATUSES,
    wo_es_editable,
    wo_status_meta,
    wo_tipo_meta,
    machine_status_meta,
)
from app.sector_service import (
    campos_para_tipo,
    crear_plantilla_sector,
    ensure_empresa_sector_setup,
    get_plantilla_dashboard,
    valores_campos_map,
)
from app.sector_templates import (
    CRITICIDAD_CHOICES,
    DEFAULT_SECTOR_CATEGORY_UI,
    SECTOR_DASHBOARD_CATEGORY_UI,
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
    frecuencia_label,
    parse_frecuencia_form,
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

EMPRESA_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg"}
MONEDAS_EMPRESA = (("COP", "COP — Peso colombiano"), ("USD", "USD — Dólar"), ("MXN", "MXN — Peso mexicano"))
ZONAS_EMPRESA = (
    ("America/Bogota", "América / Bogotá"),
    ("America/Mexico_City", "América / Ciudad de México"),
    ("America/Lima", "América / Lima"),
    ("America/Santiago", "América / Santiago"),
)

bp = Blueprint("main", __name__)

MAINT_ALERT_WARN_DAYS = 30
MAINT_ALERT_CRIT_DAYS = 45
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
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


def _current_empresa_id() -> Optional[int]:
    if not current_user.is_authenticated:
        return None
    return current_user.empresa_id


def _filter_empresa(query, model=Machine):
    eid = _current_empresa_id()
    if eid and hasattr(model, "empresa_id"):
        return query.filter(model.empresa_id == eid)
    return query


@bp.before_request
def _require_login():
    ep = request.endpoint or ""
    if ep.startswith("onboarding.") or ep == "main.login":
        return
    if not current_user.is_authenticated:
        return redirect(url_for("main.login", next=request.url))
    if not current_user.onboarding_completado:
        return redirect(url_for("onboarding.wizard"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if not current_user.onboarding_completado:
            return redirect(url_for("onboarding.wizard"))
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(username=username).first()
        if user is not None and user.activo and user.check_password(password):
            login_user(user, remember=remember)
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
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.login"))


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


def _parse_sector(value: Optional[str]) -> str:
    return normalizar_sector(value)


def _sector_for_dashboard() -> tuple[str, bool]:
    """Sector del dashboard; bloqueado al de la empresa si existe."""
    if current_user.is_authenticated and current_user.empresa and current_user.empresa.sector:
        return _parse_sector(current_user.empresa.sector), True
    return _parse_sector(request.args.get("sector")), False


def _machine_ids_for_sector(sector: str) -> Any:
    q = db.session.query(Machine.id).join(MachineType).filter(
        MachineType.sector_industrial == sector
    )
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _machines_for_sector_query(sector: str):
    q = Machine.query.join(MachineType).filter(MachineType.sector_industrial == sector)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _wo_for_sector(sector: str):
    return WorkOrder.machine_id.in_(_machine_ids_for_sector(sector))


def _wo_in_period_query(start: date, end: date, sector: Optional[str] = None):
    q = WorkOrder.query.filter(
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada >= start,
        WorkOrder.fecha_programada <= end,
    )
    if sector:
        q = q.filter(_wo_for_sector(sector))
    return q


def _closed_wo_in_period_query(start: date, end: date, sector: Optional[str] = None):
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
    return q


def _fmt_duration_hours(hours: Optional[float]) -> str:
    if hours is None:
        return "—"
    if hours >= 48:
        return f"{round(hours / 24, 1)} d"
    return f"{round(hours, 1)} h"


def _tipo_clave_base(mt: MachineType) -> str:
    if mt.empresa_id and mt.clave.startswith(f"e{mt.empresa_id}_"):
        return mt.clave[len(f"e{mt.empresa_id}_") :]
    return mt.clave


def _sector_categoria_resumen(total: int, operativos: int, falla: int) -> str:
    eq = "equipo" if total == 1 else "equipos"
    if total == 0:
        return f"0 {eq}"
    texto = f"{total} {eq} · {operativos} op."
    if falla:
        texto += f" · {falla} falla"
    return texto


def _dashboard_sector_categorias(sector: str) -> List[dict[str, Any]]:
    eid = _current_empresa_id()
    categorias = []
    ui_defs = SECTOR_DASHBOARD_CATEGORY_UI.get(sector, DEFAULT_SECTOR_CATEGORY_UI)
    for idx, (label, claves) in enumerate(SECTOR_DASHBOARD_CATEGORIES.get(sector, ())):
        ui = ui_defs[idx % len(ui_defs)]
        types_q = MachineType.query.filter(MachineType.sector_industrial == sector)
        if eid:
            types_q = types_q.filter(
                or_(MachineType.empresa_id == eid, MachineType.empresa_id.is_(None))
            )
        type_ids = [t.id for t in types_q.all() if _tipo_clave_base(t) in claves or t.clave in claves]
        if not type_ids:
            categorias.append(
                {
                    "label": label,
                    "total": 0,
                    "operativos": 0,
                    "falla": 0,
                    "icon": ui["icon"],
                    "tone": ui["tone"],
                    "resumen": _sector_categoria_resumen(0, 0, 0),
                }
            )
            continue
        machines_q = Machine.query.filter(Machine.machine_type_id.in_(type_ids))
        if eid:
            machines_q = machines_q.filter(Machine.empresa_id == eid)
        machines = machines_q.all()
        total = len(machines)
        operativos = sum(1 for m in machines if m.status == MachineStatus.OPERATIVO.value)
        falla = sum(1 for m in machines if m.status == MachineStatus.FALLA.value)
        categorias.append(
            {
                "label": label,
                "total": total,
                "operativos": operativos,
                "falla": falla,
                "icon": ui["icon"],
                "tone": ui["tone"],
                "resumen": _sector_categoria_resumen(total, operativos, falla),
            }
        )
    return categorias


def _dashboard_kpis(
    start: date, end: date, total_m: int, operativos: int, sector: Optional[str] = None
) -> dict:
    open_statuses = [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
    wo_base = WorkOrder.query
    if sector:
        wo_base = wo_base.filter(_wo_for_sector(sector))
    ordenes_abiertas = wo_base.filter(WorkOrder.status.in_(open_statuses)).count()
    mantenimientos_pendientes = wo_base.filter(
        WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
        WorkOrder.status.in_(open_statuses),
    ).count()
    disponibilidad = round(100.0 * operativos / total_m, 1) if total_m else 0.0

    repair_types = [WorkOrderType.CORRECTIVO.value, WorkOrderType.EMERGENCIA.value]
    closed_repairs = (
        _closed_wo_in_period_query(start, end, sector)
        .filter(
            WorkOrder.tipo.in_(repair_types),
            WorkOrder.fecha_inicio.isnot(None),
        )
        .all()
    )
    eid_kpi = _current_empresa_id()
    emp = Empresa.query.get(eid_kpi) if eid_kpi else None
    repair_hours = []
    for wo in closed_repairs:
        mins = wo_tiempo_gastado_minutos(wo, emp)
        if mins is not None:
            repair_hours.append(mins / 60.0)
        elif wo.fecha_inicio and wo.fecha_cierre:
            repair_hours.append((wo.fecha_cierre - wo.fecha_inicio).total_seconds() / 3600.0)
    mttr = round(sum(repair_hours) / len(repair_hours), 1) if repair_hours else None

    failures = (
        _closed_wo_in_period_query(start, end, sector)
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
    machines: list,
    operativos: int,
) -> dict:
    eid = _current_empresa_id()
    wo_period_q = _wo_in_period_query(start, end, sector)
    if eid:
        wo_period_q = wo_period_q.filter(WorkOrder.empresa_id == eid)
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
    "mttr": ("neutral", "bi-stopwatch", "T. reparación", "Tiempo medio de reparación"),
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


def _parse_form_date(raw: str) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _apply_machine_base_fields(machine: Machine, form) -> None:
    machine.nombre = form.get("nombre", "").strip()
    machine.descripcion = form.get("descripcion", "").strip()
    machine.ubicacion = form.get("ubicacion", "").strip()
    machine.marca = form.get("marca", "").strip()
    machine.modelo = form.get("modelo", "").strip()
    machine.numero_serie = form.get("numero_serie", "").strip()
    machine.proveedor = form.get("proveedor", "").strip()
    machine.manual_url = form.get("manual_url", "").strip()
    machine.foto_url = form.get("foto_url", "").strip()
    machine.criticidad = form.get("criticidad") or "media"
    machine.fecha_compra = _parse_form_date(form.get("fecha_compra"))
    machine.status = form.get("status") or MachineStatus.OPERATIVO.value
    machine.notas = form.get("notas", "").strip()
    machine.sync_criticidad_critico()


def _save_machine_custom_fields(
    machine: Machine, form, empresa_id: int, sector: str, machine_type_id: int
) -> Optional[str]:
    campos = campos_para_tipo(empresa_id, sector, machine_type_id)
    for campo in campos:
        raw = form.get(f"campo_{campo.id}", "")
        if campo.tipo == "boolean":
            val = "1" if raw in ("1", "on", "true") else ""
        else:
            val = (raw or "").strip()
        if campo.obligatorio and not val:
            return f"El campo «{campo.nombre}» es obligatorio."
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
            "machine_type_id": c.machine_type_id,
        }
        for c in CampoPersonalizado.query.filter_by(empresa_id=eid, sector=sector, activo=True)
        .order_by(CampoPersonalizado.orden)
        .all()
    ] if eid else []
    valores = valores_campos_map(machine) if machine else {}
    return {
        "machine": machine,
        "machine_types": tipos,
        "default_machine_type_id": preview_id,
        "codigo_sugerido": codigo_sugerido,
        "campos_personalizados": campos,
        "campos_json": campos_json,
        "valores_campos": valores,
        "criticidad_choices": CRITICIDAD_CHOICES,
        "sector_label": SECTOR_LABELS.get(sector, sector),
    }


def _days_since_last_maintenance(machine: Machine, ref: date) -> int:
    last = (
        WorkOrder.query.filter(
            WorkOrder.machine_id == machine.id,
            WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
            WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
            WorkOrder.fecha_cierre.isnot(None),
        )
        .order_by(WorkOrder.fecha_cierre.desc())
        .first()
    )
    if last and last.fecha_cierre:
        last_date = last.fecha_cierre.date()
    else:
        closed = (
            WorkOrder.query.filter(
                WorkOrder.machine_id == machine.id,
                WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
                WorkOrder.fecha_cierre.isnot(None),
            )
            .order_by(WorkOrder.fecha_cierre.desc())
            .first()
        )
        if closed and closed.fecha_cierre:
            last_date = closed.fecha_cierre.date()
        elif machine.created_at:
            last_date = machine.created_at.date()
        else:
            last_date = ref
    return (ref - last_date).days


def _dashboard_alertas(
    ref: Optional[date] = None, sector: Optional[str] = None
) -> List[dict[str, Any]]:
    ref = ref or date.today()
    open_statuses = [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
    alertas: list[dict[str, Any]] = []

    machines_q = Machine.query.order_by(Machine.nombre)
    if sector:
        machines_q = machines_q.join(MachineType).filter(MachineType.sector_industrial == sector)
    for m in machines_q.all():
        dias_sin = _days_since_last_maintenance(m, ref)
        if dias_sin >= MAINT_ALERT_WARN_DAYS:
            nivel = "critical" if dias_sin >= MAINT_ALERT_CRIT_DAYS or m.es_critico else "warning"
            alertas.append(
                {
                    "nivel": nivel,
                    "titulo": m.nombre,
                    "mensaje": f"Sin mantenimiento hace {dias_sin} días",
                    "prioridad": dias_sin,
                    "machine_id": m.id,
                }
            )

        tipo_clave = m.machine_type.clave if m.machine_type else ""
        notas = (m.notas or "").lower()
        if m.status == MachineStatus.FALLA.value and tipo_clave == "motor":
            alertas.append(
                {
                    "nivel": "critical",
                    "titulo": m.nombre if m.codigo == m.nombre else f"{m.nombre} ({m.codigo})",
                    "mensaje": "Vibración fuera de rango",
                    "prioridad": 10_000,
                    "machine_id": m.id,
                }
            )
        elif m.status == MachineStatus.FALLA.value and m.es_critico:
            alertas.append(
                {
                    "nivel": "critical",
                    "titulo": m.nombre,
                    "mensaje": "Equipo crítico en falla",
                    "prioridad": 9_000,
                    "machine_id": m.id,
                }
            )
        elif "vibr" in notas and m.status != MachineStatus.OPERATIVO.value:
            alertas.append(
                {
                    "nivel": "warning",
                    "titulo": m.nombre,
                    "mensaje": "Vibración fuera de rango (nota en activo)",
                    "prioridad": 5_000,
                    "machine_id": m.id,
                }
            )

    for inc in Incident.query.filter_by(resuelto=False).all():
        texto = f"{inc.titulo} {inc.descripcion}".lower()
        if "vibr" not in texto or not inc.machine_id:
            continue
        m = inc.machine
        if not m:
            continue
        if sector and (not m.machine_type or m.machine_type.sector_industrial != sector):
            continue
        if any(a.get("machine_id") == m.id and "Vibración" in a.get("mensaje", "") for a in alertas):
            continue
        alertas.append(
            {
                "nivel": "critical" if m.es_critico else "warning",
                "titulo": m.nombre,
                "mensaje": "Vibración fuera de rango",
                "prioridad": 8_000,
                "machine_id": m.id,
            }
        )

    vencidas_q = WorkOrder.query.filter(
        WorkOrder.status.in_(open_statuses),
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada < ref,
    )
    if sector:
        vencidas_q = vencidas_q.filter(_wo_for_sector(sector))
    vencidas = vencidas_q.order_by(WorkOrder.fecha_programada).all()
    for wo in vencidas:
        dias = (ref - wo.fecha_programada).days
        alertas.append(
            {
                "nivel": "critical" if dias >= 3 else "warning",
                "titulo": f"OT-{wo.id}",
                "mensaje": f"Vencida hace {dias} día{'s' if dias != 1 else ''}",
                "prioridad": 7_000 + dias,
                "wo_id": wo.id,
            }
        )

    nivel_rank = {"critical": 0, "warning": 1}
    alertas.sort(key=lambda a: (nivel_rank.get(a["nivel"], 2), -a.get("prioridad", 0)))

    seen: set[tuple[str, str]] = set()
    unicas: list[dict[str, Any]] = []
    for a in alertas:
        key = (a["titulo"], a["mensaje"])
        if key in seen:
            continue
        seen.add(key)
        if a.get("machine_id"):
            a["href"] = url_for("main.activos_edit", id=a["machine_id"])
        elif a.get("wo_id"):
            a["href"] = url_for("main.ordenes_edit", id=a["wo_id"])
        unicas.append(a)
    return unicas[:12]


def _proximos_mantenimientos(
    ref: Optional[date] = None,
    limit: int = 8,
    horizon_days: int = 120,
    sector: Optional[str] = None,
) -> List[dict[str, Any]]:
    ref = ref or date.today()
    horizon = ref + timedelta(days=horizon_days)
    open_statuses = [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
    prox_q = WorkOrder.query.filter(
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada >= ref,
        WorkOrder.fecha_programada <= horizon,
        WorkOrder.status.in_(open_statuses),
    )
    if sector:
        prox_q = prox_q.filter(_wo_for_sector(sector))
    orders = prox_q.order_by(WorkOrder.fecha_programada, WorkOrder.id).limit(limit).all()
    items: list[dict[str, Any]] = []
    for wo in orders:
        d = wo.fecha_programada
        m = wo.machine
        if m:
            equipo = m.nombre
            if m.codigo and m.codigo.lower() not in (m.nombre or "").lower():
                equipo = f"{m.nombre} ({m.codigo})"
        else:
            equipo = wo.titulo
        tipo_meta = wo_tipo_meta(wo.tipo)
        items.append(
            {
                "fecha": d,
                "fecha_dia": f"{d.day:02d}",
                "fecha_mes": MESES_CORTO[d.month - 1].upper(),
                "fecha_corta": f"{d.day:02d} {MESES_CORTO[d.month - 1].upper()}",
                "equipo": equipo,
                "titulo": wo.titulo,
                "tipo": wo.tipo,
                "tipo_slug": (wo.tipo or "").strip().lower(),
                "tipo_short": tipo_meta["short"].upper(),
                "href": url_for("main.ordenes_edit", id=wo.id),
            }
        )
    return items


@bp.route("/")
def dashboard():
    period = request.args.get("periodo", "mes")
    sector, sector_locked = _sector_for_dashboard()
    show_welcome = request.args.get("welcome") == "1" or session.pop("show_welcome", False)
    show_tour = session.pop("show_tour", False)
    start, end, period = _period_bounds(period)

    machines_q = _machines_for_sector_query(sector)
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

    wo_period = _wo_in_period_query(start, end, sector)
    preventivas = wo_period.filter(WorkOrder.tipo == WorkOrderType.PREVENTIVO.value)
    total_prev = preventivas.count()
    prev_cerradas = preventivas.filter(
        WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES)
    ).count()
    if total_prev == 0:
        cumplimiento = 0.0
        prev_msg = "Sin órdenes preventivas en el período"
    else:
        cumplimiento = round(100.0 * prev_cerradas / total_prev, 1)
        prev_msg = f"{prev_cerradas} de {total_prev} preventivos cerrados"

    criticos_q = (
        machines_q.filter(Machine.es_critico.is_(True))
        .order_by(Machine.nombre)
        .limit(5)
    )
    critico_items = []
    for m in criticos_q.all():
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

    techs = Technician.query.filter_by(activo=True).order_by(Technician.nombre).all()
    workload_labels = []
    workload_values = []
    for t in techs:
        wo_tech = WorkOrder.query.filter(
            WorkOrder.technician_id == t.id,
            WorkOrder.fecha_programada.isnot(None),
            WorkOrder.fecha_programada >= start,
            WorkOrder.fecha_programada <= end,
            WorkOrder.status.in_(
                [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
            ),
        )
        if sector:
            wo_tech = wo_tech.filter(_wo_for_sector(sector))
        n = wo_tech.count()
        workload_labels.append(t.nombre)
        workload_values.append(n)

    workload_empty = sum(workload_values) == 0
    workload_total = sum(workload_values)
    machines = machines_q.all()
    kpis = _dashboard_kpis(start, end, total_m, op, sector)
    kpis = _attach_plant_kpi_cards(
        kpis, start=start, end=end, sector=sector, machines=machines, operativos=op
    )
    alertas = _dashboard_alertas(sector=sector)
    proximos_mantenimientos = _proximos_mantenimientos(sector=sector)
    sector_categorias = _dashboard_sector_categorias(sector)

    empresa = current_user.empresa if current_user.is_authenticated else None
    if empresa:
        ensure_empresa_sector_setup(empresa)
    eid = empresa.id if empresa else None
    kpi_cards = _build_kpi_cards(kpis, eid, sector)
    return render_template(
        "dashboard.html",
        periodo=period,
        sector=sector,
        sector_locked=sector_locked,
        sector_label=SECTOR_LABELS.get(sector, sector),
        sector_categorias=sector_categorias,
        empresa=empresa,
        empresa_logo_url=_empresa_logo_url_or_none(empresa),
        show_welcome=show_welcome,
        show_tour=show_tour,
        kpis=kpis,
        kpi_cards=kpi_cards,
        alertas=alertas,
        proximos_mantenimientos=proximos_mantenimientos,
        health={
            "operativos": pct_op,
            "mantenimiento": pct_mant,
            "falla": pct_falla,
            "counts": {"op": op, "mant": mant, "falla": falla, "total": total_m},
        },
        cumplimiento=cumplimiento,
        prev_cerradas=prev_cerradas,
        total_prev=total_prev,
        prev_msg=prev_msg,
        critico_items=critico_items,
        workload_labels=workload_labels,
        workload_values=workload_values,
        workload_total=workload_total,
        workload_empty=workload_empty,
    )


# --- Activos ---
def _machine_types_activos():
    q = MachineType.query.filter_by(activo=True)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(or_(MachineType.empresa_id == eid, MachineType.empresa_id.is_(None)))
    return q.order_by(MachineType.orden, MachineType.nombre).all()


def _machine_types_para_formulario(machine: Optional[Machine] = None):
    base = _machine_types_activos()
    if machine is None or not machine.machine_type_id:
        return base
    if any(mt.id == machine.machine_type_id for mt in base):
        return base
    cur = MachineType.query.get(machine.machine_type_id)
    return [cur] + base if cur else base


def _default_machine_type_id() -> Optional[int]:
    g = MachineType.query.filter_by(clave="general", activo=True).first()
    if g:
        return g.id
    first = MachineType.query.filter_by(activo=True).order_by(MachineType.orden, MachineType.nombre).first()
    return first.id if first else None


def _machine_type_id_validado(form) -> Optional[int]:
    raw = form.get("machine_type_id")
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        return None
    mt = MachineType.query.filter_by(id=tid, activo=True).first()
    return mt.id if mt else None


def _slugify_clave(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return (s or "tipo")[:48]


def _clave_tipo_unica(base: str) -> str:
    c = base[:48]
    n = 2
    while MachineType.query.filter_by(clave=c).first():
        suffix = f"_{n}"
        c = (base[: 48 - len(suffix)] + suffix)[:48]
        n += 1
    return c


@bp.route("/activos")
def activos_list():
    q = request.args.get("q", "").strip()
    query = _filter_empresa(Machine.query.order_by(Machine.codigo))
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Machine.codigo.ilike(like),
                Machine.nombre.ilike(like),
                Machine.ubicacion.ilike(like),
            )
        )
    return render_template("activos/list.html", machines=query.all(), q=q)


@bp.route("/activos/api/sugerir-codigo")
def activos_api_sugerir_codigo():
    raw = request.args.get("type_id", "").strip()
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        tid = None
    mt = MachineType.query.filter_by(id=tid, activo=True).first() if tid else None
    if mt is None:
        mt = MachineType.query.filter_by(clave="general", activo=True).first()
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
        flash("Primero debes crear al menos un tipo de máquina en Activos → Tipos de máquina.", "warning")
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
            flash("Selecciona un tipo de máquina válido.", "danger")
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
            _apply_machine_base_fields(m, request.form)
            db.session.add(m)
            db.session.flush()
            sector = normalizar_sector(current_user.empresa.sector if current_user.empresa else None)
            err_campo = _save_machine_custom_fields(m, request.form, eid, sector, mt_id) if eid else None
            if err_campo:
                db.session.rollback()
                flash(err_campo, "danger")
            else:
                try:
                    db.session.commit()
                    flash(f"Activo registrado con código {m.codigo}.", "success")
                    return redirect(url_for("main.activos_list"))
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
    m = Machine.query.get_or_404(id)
    tipos = _machine_types_para_formulario(m)
    if not tipos:
        flash("No hay tipos de máquina activos.", "warning")
        return redirect(url_for("main.activos_tipo_list"))

    if request.method == "POST":
        mt_id = _machine_type_id_validado(request.form)
        m.codigo = request.form.get("codigo", "").strip()
        if mt_id:
            m.machine_type_id = mt_id
        _apply_machine_base_fields(m, request.form)
        if not m.codigo or not m.nombre:
            flash("Código y nombre son obligatorios.", "danger")
        elif not mt_id:
            flash("Selecciona un tipo de máquina válido.", "danger")
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
                    db.session.commit()
                    flash("Activo actualizado.", "success")
                    return redirect(url_for("main.activos_list"))
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
            }
            for c in campos
        ]
    )


@bp.route("/activos/<int:id>/eliminar", methods=["POST"])
def activos_delete(id):
    m = Machine.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("Activo eliminado.", "info")
    return redirect(url_for("main.activos_list"))


# --- Tipos de máquina (catálogo) ---
@bp.route("/activos/tipos")
def activos_tipo_list():
    tipos = MachineType.query.order_by(MachineType.orden, MachineType.nombre).all()
    return render_template(
        "activos/tipos_list.html",
        tipos=tipos,
        sector_labels=SECTOR_LABELS,
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
            sector = _parse_sector(request.form.get("sector_industrial"))
            db.session.add(
                MachineType(
                    clave=clave,
                    nombre=nombre,
                    prefijo=prefijo,
                    orden=orden,
                    activo=True,
                    sector_industrial=sector,
                )
            )
            try:
                db.session.commit()
                flash("Tipo de máquina creado.", "success")
                return redirect(url_for("main.activos_tipo_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿prefijo o clave duplicado?).", "danger")
    siguiente_orden = db.session.query(func.max(MachineType.orden)).scalar()
    siguiente_orden = (siguiente_orden or 0) + 1
    return render_template(
        "activos/tipo_form.html",
        tipo=None,
        siguiente_orden=siguiente_orden,
        sectores_nav=[(k, SECTOR_LABELS[k]) for k in SECTOR_LABELS],
    )


@bp.route("/activos/tipos/<int:id>/editar", methods=["GET", "POST"])
def activos_tipo_edit(id):
    t = MachineType.query.get_or_404(id)
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
            other = MachineType.query.filter(MachineType.prefijo == prefijo, MachineType.id != t.id).first()
            if other:
                flash("Ese prefijo ya lo usa otro tipo.", "danger")
            else:
                t.nombre = nombre
                t.prefijo = prefijo
                t.orden = orden
                t.activo = activo
                t.sector_industrial = _parse_sector(request.form.get("sector_industrial"))
                try:
                    db.session.commit()
                    flash("Tipo actualizado.", "success")
                    return redirect(url_for("main.activos_tipo_list"))
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")
    return render_template(
        "activos/tipo_form.html",
        tipo=t,
        siguiente_orden=t.orden,
        sectores_nav=[(k, SECTOR_LABELS[k]) for k in SECTOR_LABELS],
    )


@bp.route("/activos/tipos/<int:id>/eliminar", methods=["POST"])
def activos_tipo_delete(id):
    t = MachineType.query.get_or_404(id)
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
        "descripcion": j.descripcion_avance or "",
    }


def _parse_jornadas_json() -> Tuple[list[dict], Optional[str]]:
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

        nombre = (item.get("tecnico_nombre") or "").strip()
        if tech_id is None and not nombre:
            return [], f"Jornada {i}: indica el técnico realizador o su nombre."

        parsed.append(
            {
                "fecha_inicio": inicio,
                "fecha_fin": fin,
                "technician_id": tech_id,
                "tecnico_nombre": nombre if tech_id is None else "",
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

    sesiones, err = _parse_jornadas_json()
    if err:
        return err

    wo.jornadas.clear()
    if not sesiones:
        wo.fecha_inicio = None
        wo.fecha_cierre = None
        wo.tiempo_gastado_minutos = None
        return None

    for n, s in enumerate(sesiones, start=1):
        wo.jornadas.append(
            WorkOrderJornada(
                orden=n,
                fecha_inicio=s["fecha_inicio"],
                fecha_fin=s["fecha_fin"],
                technician_id=s["technician_id"],
                tecnico_nombre=s["tecnico_nombre"],
                descripcion_avance=s["descripcion_avance"],
            )
        )
    wo.fecha_inicio = sesiones[0]["fecha_inicio"]
    wo.fecha_cierre = sesiones[-1]["fecha_fin"]
    wo.tiempo_gastado_minutos = total_minutos_jornadas(wo.jornadas)
    return None


def _spare_parts_para_formulario() -> list:
    eid = _current_empresa_id()
    q = SparePart.query.order_by(SparePart.nombre)
    if eid:
        q = q.filter(or_(SparePart.empresa_id == eid, SparePart.empresa_id.is_(None)))
    return q.all()


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
            }
        )
    return parsed, None


def _guardar_repuestos_orden(wo: WorkOrder) -> Optional[str]:
    """Descuenta inventario por repuestos en OT correctivas."""
    if wo.tipo != WorkOrderType.CORRECTIVO.value:
        if wo.repuestos:
            _revertir_repuestos_stock(wo)
        return None

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
        if eid and part.empresa_id not in (None, eid):
            return f"El repuesto {part.sku} no pertenece a tu empresa."
        if (part.cantidad or 0) < item["cantidad"]:
            return (
                f"Stock insuficiente para {part.nombre} "
                f"(disponible: {part.cantidad} {part.unidad or 'pza'})."
            )

    for item in items:
        part = db.session.get(SparePart, item["spare_part_id"])
        part.cantidad = (part.cantidad or 0) - item["cantidad"]
        wo.repuestos.append(
            WorkOrderRepuesto(
                spare_part_id=part.id,
                cantidad=item["cantidad"],
                notas=item["notas"],
            )
        )
    return None


def _orden_form_context(wo: Optional[WorkOrder], technicians: list) -> dict:
    mins = wo_tiempo_gastado_minutos(wo) if wo else None
    th, tm = minutos_a_horas_minutos(mins)
    jornadas_inicial = [_jornada_a_dict(j) for j in _jornadas_para_formulario(wo)]
    catalogo = _spare_parts_para_formulario()
    repuestos_inicial = [_repuesto_linea_a_dict(r) for r in (wo.repuestos if wo else [])]
    fv = wo.frecuencia_valor if wo and wo.frecuencia_valor else 1
    fu = wo.frecuencia_unidad if wo and wo.frecuencia_unidad else "meses"
    if wo and wo.preventive_plan and not wo.frecuencia_valor:
        fv = wo.preventive_plan.frecuencia_valor or 1
        fu = wo.preventive_plan.frecuencia_unidad or "meses"
    return {
        "jornadas_inicial": jornadas_inicial,
        "repuestos_inicial": repuestos_inicial,
        "usa_repuestos_inicial": bool(wo and wo.repuestos),
        "frecuencia_unidades": PREVENTIVE_FREQUENCY_UNITS,
        "frecuencia_valor": fv,
        "frecuencia_unidad": fu,
        "frecuencia_label": frecuencia_label(fv, fu),
        "tiempo_horas": th,
        "tiempo_minutos": tm,
        "formatear_duracion": formatear_duracion,
        "technicians_json": json.dumps(
            [{"id": t.id, "nombre": t.nombre} for t in technicians], ensure_ascii=False
        ),
        "repuestos_catalog_json": json.dumps(
            [
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
            ensure_ascii=False,
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


@bp.route("/ordenes")
def ordenes_list():
    status = request.args.get("status", "")
    from sqlalchemy.orm import joinedload

    q = (
        WorkOrder.query.options(joinedload(WorkOrder.jornadas))
        .order_by(WorkOrder.fecha_programada.desc(), WorkOrder.id.desc())
    )
    if status:
        q = q.filter_by(status=status)
    return render_template("ordenes/list.html", orders=q.all(), status_filter=status)


@bp.route("/ordenes/nueva", methods=["GET", "POST"])
def ordenes_new():
    machines = _filter_empresa(Machine.query.order_by(Machine.nombre)).all()
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
            status=request.form.get("status") or WorkOrderStatus.ABIERTA.value,
            prioridad=request.form.get("prioridad") or "media",
            empresa_id=_current_empresa_id(),
            fecha_programada=fecha_prog,
            machine_id=int(request.form.get("machine_id", 0)),
            technician_id=int(request.form["technician_id"])
            if request.form.get("technician_id")
            else None,
        )
        if not wo.titulo or not wo.machine_id:
            flash("Actividad y equipo son obligatorios.", "danger")
        elif not tipo:
            flash("Selecciona el tipo de orden.", "danger")
        else:
            wo.tipo = tipo
            if wo.tipo == WorkOrderType.PREVENTIVO.value:
                fv, fu = parse_frecuencia_form(request.form)
                err_prev = aplicar_preventivo_a_orden(wo, wo.titulo, fv, fu)
                if err_prev:
                    flash(err_prev, "danger")
                    return render_template(
                        "ordenes/form.html",
                        order=None,
                        machines=machines,
                        technicians=technicians,
                        prioridades=WORK_ORDER_PRIORITIES,
                        **_orden_form_context(None, technicians),
                    )
            else:
                wo.preventive_plan_id = None
                wo.frecuencia_valor = None
                wo.frecuencia_unidad = None
            db.session.add(wo)
            db.session.flush()
            numero = asignar_numero_ot(wo)
            err = _guardar_jornadas_orden(wo)
            if err:
                db.session.rollback()
                flash(err, "danger")
            else:
                err_rep = _guardar_repuestos_orden(wo)
                if err_rep:
                    db.session.rollback()
                    flash(err_rep, "danger")
                else:
                    db.session.commit()
                    flash(f"Orden {numero} creada.", "success")
                    return redirect(url_for("main.ordenes_list"))
    return render_template(
        "ordenes/form.html",
        order=None,
        machines=machines,
        technicians=technicians,
        prioridades=WORK_ORDER_PRIORITIES,
        **_orden_form_context(None, technicians),
    )


@bp.route("/ordenes/<int:id>/editar", methods=["GET", "POST"])
def ordenes_edit(id):
    from sqlalchemy.orm import joinedload

    wo = WorkOrder.query.options(
        joinedload(WorkOrder.jornadas),
        joinedload(WorkOrder.repuestos).joinedload(WorkOrderRepuesto.spare_part),
    ).get_or_404(id)
    solo_lectura = not wo_es_editable(wo.status)
    machines = _filter_empresa(Machine.query.order_by(Machine.nombre)).all()
    technicians = _filter_empresa(
        Technician.query.filter_by(activo=True).order_by(Technician.nombre), Technician
    ).all()
    if request.method == "POST":
        if solo_lectura:
            flash("Esta orden está cerrada y no puede modificarse.", "warning")
            return redirect(url_for("main.ordenes_edit", id=wo.id))
        wo.titulo = request.form.get("titulo", "").strip()
        wo.descripcion = request.form.get("descripcion", "").strip()
        wo.tipo = request.form.get("tipo") or wo.tipo
        wo.status = request.form.get("status") or wo.status
        wo.prioridad = request.form.get("prioridad") or wo.prioridad
        fp = request.form.get("fecha_programada")
        wo.fecha_programada = datetime.strptime(fp, "%Y-%m-%d").date() if fp else None
        wo.machine_id = int(request.form.get("machine_id", wo.machine_id))
        wo.technician_id = (
            int(request.form["technician_id"]) if request.form.get("technician_id") else None
        )
        if not wo.titulo:
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
                    flash(err, "danger")
                else:
                    err_rep = _guardar_repuestos_orden(wo)
                    if err_rep:
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
                flash(err, "danger")
            else:
                err_rep = _guardar_repuestos_orden(wo)
                if err_rep:
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
        **_orden_form_context(wo, technicians),
    )


# --- Calendario ---
@bp.route("/calendario")
def calendario():
    year = int(request.args.get("y", date.today().year))
    month = int(request.args.get("m", date.today().month))
    start = date(year, month, 1)
    _, last = monthrange(year, month)
    end = date(year, month, last)
    orders = (
        WorkOrder.query.filter(
            WorkOrder.fecha_programada.isnot(None),
            WorkOrder.fecha_programada >= start,
            WorkOrder.fecha_programada <= end,
        )
        .order_by(WorkOrder.fecha_programada)
        .all()
    )
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
    p = SparePart.query.get_or_404(id)
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


# --- Equipo técnico ---
@bp.route("/equipo")
def equipo_list():
    return render_template(
        "equipo/list.html",
        technicians=Technician.query.order_by(Technician.nombre).all(),
    )


@bp.route("/equipo/nuevo", methods=["GET", "POST"])
def equipo_new():
    if request.method == "POST":
        t = Technician(
            nombre=request.form.get("nombre", "").strip(),
            especialidad=request.form.get("especialidad", "").strip(),
            telefono=request.form.get("telefono", "").strip(),
            email=request.form.get("email", "").strip(),
            activo=bool(request.form.get("activo")),
        )
        if not t.nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            db.session.add(t)
            db.session.commit()
            flash("Técnico registrado.", "success")
            return redirect(url_for("main.equipo_list"))
    return render_template("equipo/form.html", tech=None)


@bp.route("/equipo/<int:id>/editar", methods=["GET", "POST"])
def equipo_edit(id):
    t = Technician.query.get_or_404(id)
    if request.method == "POST":
        t.nombre = request.form.get("nombre", "").strip()
        t.especialidad = request.form.get("especialidad", "").strip()
        t.telefono = request.form.get("telefono", "").strip()
        t.email = request.form.get("email", "").strip()
        t.activo = bool(request.form.get("activo"))
        if not t.nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            db.session.commit()
            flash("Técnico actualizado.", "success")
            return redirect(url_for("main.equipo_list"))
    return render_template("equipo/form.html", tech=t)


# --- Configuración empresa ---
def _empresa_del_usuario() -> Optional[Empresa]:
    if not current_user.is_authenticated or not current_user.empresa_id:
        return None
    return current_user.empresa


def _empresa_logo_url(empresa: Optional[Empresa]) -> str:
    if empresa and empresa.logo:
        if empresa.logo.startswith(("http://", "https://")):
            return empresa.logo
        return url_for("static", filename=empresa.logo)
    return url_for("static", filename=APP_LOGO_PATH)


def _empresa_logo_url_or_none(empresa: Optional[Empresa]) -> Optional[str]:
    if not empresa or not (empresa.logo or "").strip():
        return None
    return _empresa_logo_url(empresa)


def _guardar_logo_empresa(empresa: Empresa, archivo) -> None:
    if not archivo or not getattr(archivo, "filename", None):
        return
    nombre = secure_filename(archivo.filename)
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in EMPRESA_LOGO_EXTENSIONS:
        raise ValueError("Formato de imagen no permitido. Use PNG, JPG, WEBP o SVG.")
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
    if current_user.rol != UserRole.ADMIN.value:
        flash("Solo los administradores pueden modificar la configuración de la empresa.", "warning")
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
            emp.logo = logo_url
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
            db.session.rollback()
            flash("No se pudo guardar la configuración.", "danger")

    plan_meta = PLAN_CATALOG.get(plan.plan, {}) if plan else {}
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
    )


# --- Reportes ---
@bp.route("/reportes")
def reportes():
    total_m = Machine.query.count()
    by_status = (
        db.session.query(Machine.status, func.count(Machine.id))
        .group_by(Machine.status)
        .all()
    )
    wo_by_type = (
        db.session.query(WorkOrder.tipo, func.count(WorkOrder.id)).group_by(WorkOrder.tipo).all()
    )
    wo_by_status = (
        db.session.query(WorkOrder.status, func.count(WorkOrder.id))
        .group_by(WorkOrder.status)
        .all()
    )
    bajo_minimo = SparePart.query.filter(SparePart.cantidad < SparePart.stock_minimo).count()
    return render_template(
        "reportes.html",
        total_m=total_m,
        by_status=by_status,
        wo_by_type=wo_by_type,
        wo_by_status=wo_by_status,
        bajo_minimo=bajo_minimo,
        chart_estado_labels=[r[0] for r in by_status],
        chart_estado_data=[r[1] for r in by_status],
        chart_tipo_labels=[wo_tipo_meta(r[0])["label"] for r in wo_by_type],
        chart_tipo_data=[r[1] for r in wo_by_type],
        chart_tipo_colors=[wo_tipo_meta(r[0])["color"] for r in wo_by_type],
        chart_wo_labels=[wo_status_meta(r[0])["label"] for r in wo_by_status],
        chart_wo_data=[r[1] for r in wo_by_status],
        chart_wo_colors=[wo_status_meta(r[0])["color"] for r in wo_by_status],
    )


# --- Incidencias ---
@bp.route("/incidencia", methods=["GET", "POST"])
def incidencia():
    machines = Machine.query.order_by(Machine.nombre).all()
    if request.method == "POST":
        mid = request.form.get("machine_id")
        inc = Incident(
            titulo=request.form.get("titulo", "").strip(),
            descripcion=request.form.get("descripcion", "").strip(),
            machine_id=int(mid) if mid else None,
        )
        if not inc.titulo:
            flash("Describe brevemente la incidencia.", "danger")
        else:
            db.session.add(inc)
            db.session.commit()
            flash("Incidencia registrada. El supervisor será notificado.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("incidencia.html", machines=machines)
