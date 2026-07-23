"""Cronograma anual de mantenimiento preventivo por activo.

Matriz ENE–DIC × semanas 1–4 con filas PROG / EJEC.
PROG y EJEC se derivan de las OT preventivas (no se editan a mano).
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional

from app import db
from app.models import (
    Machine,
    PreventiveMaintenancePlan,
    WorkOrder,
    WorkOrderType,
    WORK_ORDER_TERMINAL_STATUSES,
)
from app.preventive_maintenance import (
    actividad_key,
    crear_programacion_preventiva_anio,
    get_or_create_plan,
)
from app.sector_templates import normalizar_sector

# Códigos del formato clásico 62-MT-TP
TIPO_ACTIVIDAD_CHOICES: tuple[tuple[str, str], ...] = (
    ("I", "Inspección"),
    ("L", "Lubricación"),
    ("A", "Ajuste"),
    ("LZ", "Limpieza"),
    ("MG", "Mantenimiento general"),
    ("R", "Revisión"),
    ("C", "Calibración"),
)

FRECUENCIA_CODIGO_CHOICES: tuple[tuple[str, str, int, str], ...] = (
    # codigo, etiqueta corta, valor, unidad interna
    ("S", "Semanal", 1, "semanas"),
    ("M", "Mensual", 1, "meses"),
    ("BI", "Bimensual", 2, "meses"),
    ("TR", "Trimestral", 3, "meses"),
    ("SE", "Semestral", 6, "meses"),
    ("AN", "Anual", 12, "meses"),
)

MESES_ES = (
    "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
    "JUL", "AGO", "SEP", "OCT", "NOV", "DIC",
)

# Plantillas por sector industrial → actividades preventivas sugeridas
# (actividad, tipo_codigo, frecuencia_codigo)
SECTOR_PREVENTIVE_TEMPLATES: dict[str, tuple[tuple[str, str, str], ...]] = {
    "manufactura": (
        (
            "Verificar sistema de lubricación, refrigeración, neumático, "
            "piezas móviles, pantalla de mando y limpieza de caja filtrante",
            "L",
            "M",
        ),
        (
            "Inspección de mandos eléctricos, tableros y reguladores eléctricos",
            "I",
            "TR",
        ),
        (
            "Revisión general mecánica y ajuste de holguras",
            "MG",
            "SE",
        ),
    ),
    "salud": (
        (
            "Inspección visual, limpieza externa y verificación de alarmas",
            "I",
            "M",
        ),
        (
            "Calibración / verificación metrológica según protocolo",
            "C",
            "SE",
        ),
        (
            "Mantenimiento general preventivo del equipo",
            "MG",
            "AN",
        ),
    ),
    "logistica": (
        (
            "Inspección de fluidos, frenos, luces y elementos de seguridad",
            "I",
            "M",
        ),
        (
            "Lubricación de puntos críticos y revisión de neumáticos",
            "L",
            "M",
        ),
        (
            "Mantenimiento general según horómetro / kilometraje",
            "MG",
            "TR",
        ),
    ),
    "alimentos": (
        (
            "Limpieza sanitaria, sellos y verificación de temperaturas",
            "LZ",
            "M",
        ),
        (
            "Inspección de sensores, tableros y sistemas de seguridad",
            "I",
            "TR",
        ),
        (
            "Mantenimiento general de línea / equipo de proceso",
            "MG",
            "SE",
        ),
    ),
    "mineria": (
        (
            "Inspección estructural, hidráulica y de seguridad",
            "I",
            "M",
        ),
        (
            "Lubricación de componentes críticos",
            "L",
            "M",
        ),
        (
            "Mantenimiento general preventivo de equipo pesado",
            "MG",
            "TR",
        ),
    ),
    "construccion": (
        (
            "Inspección de seguridad, fluidos y desgaste",
            "I",
            "M",
        ),
        (
            "Lubricación y ajuste de componentes móviles",
            "L",
            "M",
        ),
        (
            "Mantenimiento general del equipo",
            "MG",
            "TR",
        ),
    ),
    "educacion": (
        (
            "Inspección y limpieza de equipos técnicos",
            "LZ",
            "M",
        ),
        (
            "Revisión preventiva de instalaciones / equipos",
            "R",
            "TR",
        ),
    ),
    "hoteleria": (
        (
            "Inspección y limpieza de equipos de servicio",
            "LZ",
            "M",
        ),
        (
            "Mantenimiento preventivo general",
            "MG",
            "TR",
        ),
    ),
    "transporte": (
        (
            "Inspección preoperacional y de seguridad",
            "I",
            "M",
        ),
        (
            "Lubricación y revisión de tren motriz",
            "L",
            "M",
        ),
        (
            "Mantenimiento general preventivo",
            "MG",
            "TR",
        ),
    ),
}

# Fallback genérico (comercio u otros)
_DEFAULT_TEMPLATES: tuple[tuple[str, str, str], ...] = (
    ("Inspección general del activo", "I", "M"),
    ("Lubricación / limpieza preventiva", "L", "TR"),
    ("Mantenimiento general preventivo", "MG", "SE"),
)


def frecuencia_desde_codigo(codigo: str) -> tuple[int, str]:
    code = (codigo or "M").strip().upper()
    for c, _label, valor, unidad in FRECUENCIA_CODIGO_CHOICES:
        if c == code:
            return valor, unidad
    return 1, "meses"


def codigo_desde_frecuencia(valor: int, unidad: str) -> str:
    valor = max(1, int(valor or 1))
    unidad = (unidad or "meses").lower()
    for c, _label, v, u in FRECUENCIA_CODIGO_CHOICES:
        if v == valor and u == unidad:
            return c
    if unidad == "semanas":
        return "S"
    if unidad == "meses":
        if valor == 1:
            return "M"
        if valor == 2:
            return "BI"
        if valor == 3:
            return "TR"
        if valor == 6:
            return "SE"
        if valor >= 12:
            return "AN"
    return "M"


def semana_del_mes(dia: int) -> int:
    """SEM.1–4 según día del mes (1–7, 8–14, 15–21, 22–31)."""
    if dia <= 7:
        return 1
    if dia <= 14:
        return 2
    if dia <= 21:
        return 3
    return 4


def templates_for_sector(sector: str | None) -> tuple[tuple[str, str, str], ...]:
    key = normalizar_sector(sector or "")
    return SECTOR_PREVENTIVE_TEMPLATES.get(key) or _DEFAULT_TEMPLATES


def aplicar_plantillas_sector(
    machine: Machine,
    *,
    sector: str | None = None,
) -> list[PreventiveMaintenancePlan]:
    """Crea planes preventivos desde plantilla del sector (sin generar OT)."""
    sector_key = sector or (
        machine.empresa.sector if getattr(machine, "empresa", None) else None
    )
    creados: list[PreventiveMaintenancePlan] = []
    for actividad, tipo, frec in templates_for_sector(sector_key):
        valor, unidad = frecuencia_desde_codigo(frec)
        plan = get_or_create_plan(
            machine_id=machine.id,
            empresa_id=machine.empresa_id,
            actividad=actividad,
            frecuencia_valor=valor,
            frecuencia_unidad=unidad,
            tipo_codigo=tipo,
        )
        creados.append(plan)
    return creados


def generar_ot_cronograma_anio(
    machine: Machine,
    *,
    anio: int,
    fecha_inicio: date | None = None,
    technician_id: int | None = None,
) -> tuple[int, list[str]]:
    """Genera OT preventivas del año para todos los planes activos del activo."""
    inicio = fecha_inicio or date(anio, 1, 1)
    if inicio.year != anio:
        inicio = date(anio, 1, 1)
    total = 0
    errores: list[str] = []
    planes = (
        PreventiveMaintenancePlan.query.filter_by(machine_id=machine.id, activo=True)
        .order_by(PreventiveMaintenancePlan.id)
        .all()
    )
    for plan in planes:
        ordenes, err = crear_programacion_preventiva_anio(
            empresa_id=machine.empresa_id,
            machine_id=machine.id,
            technician_id=technician_id,
            titulo=plan.actividad,
            descripcion="",
            prioridad="media",
            fecha_inicio=inicio,
            frecuencia_valor=plan.frecuencia_valor,
            frecuencia_unidad=plan.frecuencia_unidad,
            ubicacion=machine.ubicacion or "",
            area=machine.area or "",
            omitir_validacion_actividad_abierta=True,
        )
        if err and not ordenes:
            # Si ya existen OT del año, no es error bloqueante
            if "Ya existen" in err:
                continue
            errores.append(f"{plan.actividad[:60]}: {err}")
            continue
        total += len(ordenes)
    return total, errores


@dataclass
class CeldaSemana:
    prog: str = ""
    ejec: str = ""
    wo_prog_id: int | None = None
    wo_ejec_id: int | None = None


@dataclass
class FilaActividad:
    plan_id: int
    numero: int
    actividad: str
    tipo_codigo: str
    frecuencia_codigo: str
    frecuencia_label: str
    # meses[1..12][1..4]
    celdas: dict[int, dict[int, CeldaSemana]] = field(default_factory=dict)


@dataclass
class CronogramaActivo:
    machine: Machine
    anio: int
    filas: list[FilaActividad]
    observaciones: list[dict[str, Any]]
    cumplimiento: dict[str, Any]


def _ot_ejecutada(wo: WorkOrder) -> bool:
    return (wo.status or "").strip().lower() in WORK_ORDER_TERMINAL_STATUSES


def _fecha_ejecucion(wo: WorkOrder) -> date | None:
    if wo.fecha_cierre:
        if isinstance(wo.fecha_cierre, datetime):
            return wo.fecha_cierre.date()
        return wo.fecha_cierre
    return wo.fecha_programada


def construir_cronograma(machine: Machine, anio: int) -> CronogramaActivo:
    planes = (
        PreventiveMaintenancePlan.query.filter_by(machine_id=machine.id, activo=True)
        .order_by(PreventiveMaintenancePlan.id)
        .all()
    )
    ot_list = (
        WorkOrder.query.filter(
            WorkOrder.machine_id == machine.id,
            WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
            WorkOrder.fecha_programada.isnot(None),
        )
        .order_by(WorkOrder.fecha_programada)
        .all()
    )
    ot_anio = [wo for wo in ot_list if wo.fecha_programada and wo.fecha_programada.year == anio]

    filas: list[FilaActividad] = []
    for idx, plan in enumerate(planes, start=1):
        tipo = (getattr(plan, "tipo_codigo", None) or "I").upper()
        frec = codigo_desde_frecuencia(plan.frecuencia_valor, plan.frecuencia_unidad)
        celdas: dict[int, dict[int, CeldaSemana]] = {
            m: {s: CeldaSemana() for s in range(1, 5)} for m in range(1, 13)
        }
        for wo in ot_anio:
            same_plan = wo.preventive_plan_id == plan.id
            same_act = actividad_key(wo.titulo or "") == plan.actividad_key
            if not (same_plan or same_act):
                continue
            fp = wo.fecha_programada
            assert fp is not None
            sem = semana_del_mes(fp.day)
            cel = celdas[fp.month][sem]
            if not cel.prog:
                cel.prog = tipo
                cel.wo_prog_id = wo.id
            if _ot_ejecutada(wo):
                fe = _fecha_ejecucion(wo) or fp
                if fe.year == anio:
                    sem_e = semana_del_mes(fe.day)
                    cel_e = celdas[fe.month][sem_e]
                    cel_e.ejec = "ok"
                    cel_e.wo_ejec_id = wo.id
        filas.append(
            FilaActividad(
                plan_id=plan.id,
                numero=idx,
                actividad=plan.actividad,
                tipo_codigo=tipo,
                frecuencia_codigo=frec,
                frecuencia_label=dict((c, l) for c, l, *_ in FRECUENCIA_CODIGO_CHOICES).get(
                    frec, frec
                ),
                celdas=celdas,
            )
        )

    observaciones: list[dict[str, Any]] = []
    for wo in ot_anio:
        if not _ot_ejecutada(wo):
            continue
        fe = _fecha_ejecucion(wo)
        texto = (wo.descripcion or "").strip() or (wo.titulo or "").strip()
        if not texto:
            continue
        observaciones.append(
            {
                "fecha": fe,
                "texto": texto[:500],
                "wo_id": wo.id,
                "numero": wo.numero or f"#{wo.id}",
            }
        )
    observaciones.sort(key=lambda o: o["fecha"] or date.min)

    prog_total = 0
    ejec_total = 0
    por_mes: dict[int, dict[str, Any]] = {}
    for m in range(1, 13):
        p = e = 0
        for fila in filas:
            for s in range(1, 5):
                if fila.celdas[m][s].prog:
                    p += 1
                if fila.celdas[m][s].ejec:
                    e += 1
        prog_total += p
        ejec_total += e
        pct = round((e / p) * 100, 1) if p else None
        por_mes[m] = {"prog": p, "ejec": e, "pct": pct}

    cumplimiento = {
        "prog_total": prog_total,
        "ejec_total": ejec_total,
        "pct_total": round((ejec_total / prog_total) * 100, 1) if prog_total else None,
        "por_mes": por_mes,
    }
    return CronogramaActivo(
        machine=machine,
        anio=anio,
        filas=filas,
        observaciones=observaciones,
        cumplimiento=cumplimiento,
    )
