"""KPIs de planta para el dashboard (fila de 7 indicadores)."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

META_DISP_PLANTA = 90.0
META_CUMPL = 98.0

PLANT_KPI_DEFINITIONS: tuple[tuple[str, str], ...] = (
    ("disp_total_planta", "Disp. total (planta)"),
    ("disp_global", "Disp. global"),
    ("horas_meta", "Horas meta"),
    ("cumpl_preventivo", "Cumpl. preventivo"),
    ("cumpl_correctivo", "Cumpl. correctivo"),
    ("mtbf_planta", "MTBF planta"),
    ("mttr_prom", "MTTR prom."),
)


def _fmt_pct(value: Optional[float], decimals: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}f}%"


def _fmt_hours(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if value >= 48:
        return f"{round(value / 24, 1)} d"
    return f"{round(value, 1)} h"


def _card(
    key: str,
    label: str,
    value: str,
    hint: str,
    style: str = "neutral",
    hint_title: Optional[str] = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "value": value,
        "hint": hint,
        "hint_title": hint_title,
        "style": style,
        "show_icon": False,
    }


def _style_vs_meta(value: Optional[float], meta: float) -> str:
    if value is None:
        return "neutral"
    if value >= meta:
        return "success"
    if value >= meta * 0.85:
        return "warning"
    return "danger"


def _horas_meta_mes(
    anio: int, mes: int, eid: Optional[int], machine_ids: Optional[list[int]]
) -> tuple[float, dict]:
    from app.models import MachineMonthlyPlan

    q = MachineMonthlyPlan.query.filter_by(anio=anio, mes=mes)
    if eid:
        q = q.filter(MachineMonthlyPlan.empresa_id == eid)
    if machine_ids is not None:
        if not machine_ids:
            return 0.0, {}
        q = q.filter(MachineMonthlyPlan.machine_id.in_(machine_ids))
    plans = q.all()
    by_machine = {p.machine_id: p for p in plans if p.horas_meta is not None}
    total = sum(float(p.horas_meta) for p in by_machine.values())
    return total, by_machine


def _wo_horas_periodo(wo_list: list, emp) -> float:
    from app.work_time import wo_tiempo_gastado_minutos
    total = 0.0
    for wo in wo_list:
        mins = wo_tiempo_gastado_minutos(wo, emp)
        if mins is not None:
            total += mins / 60.0
        elif wo.fecha_inicio and wo.fecha_cierre:
            total += (wo.fecha_cierre - wo.fecha_inicio).total_seconds() / 3600.0
    return round(total, 1)


def build_plant_kpi_cards(
    *,
    start: date,
    end: date,
    sector: Optional[str],
    eid: Optional[int],
    machines: list,
    operativos: int,
    mtbf: Optional[float],
    mttr: Optional[float],
    disp_global: Optional[float],
    emp,
    wo_period_q,
    closed_repairs: list,
    preventivas_q=None,
) -> list[dict[str, Any]]:
    from app.models import MachineStatus, WorkOrder, WorkOrderType, WORK_ORDER_TERMINAL_STATUSES

    total_m = len(machines)
    anio, mes = end.year, end.month
    mes_label = "mes"  # footer corto

    machine_ids = [m.id for m in machines]
    horas_meta_total, plan_by_machine = _horas_meta_mes(anio, mes, eid, machine_ids or None)

    weighted = 0.0
    meta_sum = 0.0
    for m in machines:
        plan = plan_by_machine.get(m.id)
        h = float(plan.horas_meta) if plan and plan.horas_meta else 0.0
        if h <= 0:
            continue
        meta_sum += h
        if m.status == MachineStatus.OPERATIVO.value:
            weighted += h
        elif m.status == MachineStatus.MANTENIMIENTO.value:
            weighted += h * 0.5

    if meta_sum > 0:
        disp_total = round(100.0 * weighted / meta_sum, 2)
    elif total_m:
        disp_total = round(100.0 * operativos / total_m, 2)
    else:
        disp_total = 0.0

    if preventivas_q is None:
        preventivas_q = wo_period_q.filter(WorkOrder.tipo == WorkOrderType.PREVENTIVO.value)
    prev_total = preventivas_q.count()
    from sqlalchemy import func, or_

    terminal_prev = or_(
        WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
        func.lower(WorkOrder.status).in_(("cerrada", "completado", "cerrado")),
    )
    prev_done = preventivas_q.filter(terminal_prev).count()
    prev_closed = list(preventivas_q.filter(terminal_prev).all())
    prev_horas = _wo_horas_periodo(prev_closed, emp)
    if prev_total:
        cumpl_prev = round(100.0 * prev_done / prev_total, 0)
        prev_val = f"{int(cumpl_prev)}%"
        prev_hint = f"Meta {int(META_CUMPL)}% — {prev_done}/{prev_total} ({mes_label}) — {prev_horas:.1f} h"
    else:
        cumpl_prev = None
        prev_val = "—"
        prev_hint = f"Meta {int(META_CUMPL)}% — 0/0 ({mes_label}) — 0.0 h"

    correctivo_q = wo_period_q.filter(WorkOrder.tipo == WorkOrderType.CORRECTIVO.value)
    corr_total = correctivo_q.count()
    corr_done = correctivo_q.filter(
        WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES)
    ).count()
    correctivo_cerrados = list(
        correctivo_q.filter(WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES)).all()
    )
    corr_horas = _wo_horas_periodo(correctivo_cerrados, emp)

    if corr_total:
        cumpl_corr = round(100.0 * corr_done / corr_total, 0)
        corr_val = f"{int(cumpl_corr)}%"
    else:
        cumpl_corr = None
        corr_val = "—"

    corr_hint = (
        f"Meta {int(META_CUMPL)}% — {corr_done}/{corr_total} ({mes_label}) · "
        f"Total {corr_total} correctivos · {corr_horas:.1f} h en correctivos"
    )
    corr_hint_title = (
        "Solo tipo correctivo con fecha programada en el período seleccionado "
        "(Día / Semana / Mes / Año). Las horas suman el tiempo de las OT cerradas."
    )

    n_correctivos = len(
        [w for w in (closed_repairs or []) if w.tipo == WorkOrderType.CORRECTIVO.value]
    )
    mtbf_hint = f"Meta ÷ correctivos ({mes_label})"
    if mtbf is not None and horas_meta_total > 0 and n_correctivos:
        mtbf_hint = f"{horas_meta_total:.0f} h meta ÷ {n_correctivos} corr. ({mes_label})"

    cards = [
        _card(
            "disp_total_planta",
            "Disp. total (planta)",
            _fmt_pct(disp_total, 0),
            f"Ponderado horas meta — meta {int(META_DISP_PLANTA)}%",
            _style_vs_meta(disp_total, META_DISP_PLANTA),
            "Disponibilidad ponderada por horas meta del mes",
        ),
        _card(
            "disp_global",
            "Disp. global",
            _fmt_pct(disp_global, 2),
            "MTBF÷(MTBF+MTTR)×100",
            _style_vs_meta(disp_global, META_DISP_PLANTA) if disp_global is not None else "neutral",
            "MTBF ÷ (MTBF + MTTR) × 100",
        ),
        _card(
            "horas_meta",
            "Horas meta",
            f"{horas_meta_total:.1f} h" if horas_meta_total else "0.0 h",
            "Planeación mensual (planta)",
            "primary",
        ),
        _card(
            "cumpl_preventivo",
            "Cumpl. preventivo",
            prev_val,
            prev_hint,
            _style_vs_meta(cumpl_prev, META_CUMPL) if cumpl_prev is not None else "neutral",
        ),
        _card(
            "cumpl_correctivo",
            "Cumpl. correctivo",
            corr_val,
            corr_hint,
            _style_vs_meta(cumpl_corr, META_CUMPL) if cumpl_corr is not None else "neutral",
            corr_hint_title,
        ),
        _card(
            "mtbf_planta",
            "MTBF planta",
            _fmt_hours(mtbf),
            mtbf_hint,
            "neutral",
        ),
        _card(
            "mttr_prom",
            "MTTR prom.",
            _fmt_hours(mttr),
            f"Correctivos con paro ({mes_label})",
            "neutral",
            "Promedio de horas en OT correctivas cerradas donde el activo estuvo parado",
        ),
    ]
    return cards


def kpi_config_for_sector(sector: str) -> list[dict[str, str]]:
    return [{"key": k, "label": lb} for k, lb in PLANT_KPI_DEFINITIONS]
