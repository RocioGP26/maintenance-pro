"""Cálculo de tiempo de trabajo (continuo y por jornada laboral)."""
from datetime import date, datetime, time, timedelta
from typing import Optional, Set


def parse_hhmm(value: str, default: time) -> time:
    raw = (value or "").strip()
    if not raw or ":" not in raw:
        return default
    parts = raw.split(":", 1)
    try:
        h, m = int(parts[0]), int(parts[1])
        if 0 <= h <= 23 and 0 <= m <= 59:
            return time(h, m)
    except ValueError:
        pass
    return default


def parse_dias_laborales(value: str) -> Set[int]:
    """Días laborales como weekday de Python (0=lunes … 6=domingo)."""
    raw = (value or "0,1,2,3,4").strip()
    dias: Set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            n = int(part)
            if 0 <= n <= 6:
                dias.add(n)
    return dias if dias else {0, 1, 2, 3, 4}


def dias_laborales_a_cadena(dias: Set[int]) -> str:
    return ",".join(str(d) for d in sorted(dias))


def combinar_fecha_hora(fecha_str: str, hora_str: str) -> Optional[datetime]:
    """Combina fecha (YYYY-MM-DD) y hora (HH:MM) en datetime."""
    raw_f = (fecha_str or "").strip()
    if not raw_f:
        return None
    try:
        d = datetime.strptime(raw_f[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    t = parse_hhmm(hora_str, time.min)
    return datetime.combine(d, t)


def parse_datetime_local(value: str) -> Optional[datetime]:
    raw = (value or "").strip()
    if not raw:
        return None
    if "T" in raw:
        try:
            return datetime.strptime(raw[:16], "%Y-%m-%dT%H:%M")
        except ValueError:
            return None
    try:
        d = datetime.strptime(raw[:10], "%Y-%m-%d").date()
        return datetime.combine(d, time.min)
    except ValueError:
        return None


def minutos_entre(inicio: datetime, fin: datetime) -> int:
    if not inicio or not fin or fin <= inicio:
        return 0
    return int((fin - inicio).total_seconds() // 60)


def minutos_laborales(
    inicio: datetime,
    fin: datetime,
    hora_inicio: time,
    hora_fin: time,
    dias_laborales: Set[int],
) -> int:
    """Minutos dentro del horario laboral entre dos fechas/horas."""
    if not inicio or not fin or fin <= inicio:
        return 0
    if hora_fin <= hora_inicio:
        return 0

    total = 0
    d: date = inicio.date()
    end_d: date = fin.date()
    one_day = timedelta(days=1)
    while d <= end_d:
        if d.weekday() in dias_laborales:
            day_start = datetime.combine(d, hora_inicio)
            day_end = datetime.combine(d, hora_fin)
            seg_start = max(inicio, day_start)
            seg_end = min(fin, day_end)
            if seg_start < seg_end:
                total += int((seg_end - seg_start).total_seconds() // 60)
        d += one_day
    return total


def formatear_duracion(minutos: Optional[int]) -> str:
    if minutos is None:
        return "—"
    if minutos < 0:
        minutos = 0
    h, m = divmod(minutos, 60)
    if h and m:
        return f"{h} h {m} min"
    if h:
        return f"{h} h"
    return f"{m} min"


def minutos_a_horas_minutos(minutos: Optional[int]) -> tuple[int, int]:
    if minutos is None or minutos < 0:
        return 0, 0
    h, m = divmod(minutos, 60)
    return h, m


def datetime_local_input(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M")


def empresa_jornada_times(empresa) -> tuple[time, time, Set[int]]:
    """Horario laboral de la empresa (valores por defecto si no hay empresa)."""
    if empresa is None:
        return time(8, 0), time(17, 0), {0, 1, 2, 3, 4}
    return (
        parse_hhmm(getattr(empresa, "jornada_hora_inicio", None) or "", time(8, 0)),
        parse_hhmm(getattr(empresa, "jornada_hora_fin", None) or "", time(17, 0)),
        parse_dias_laborales(getattr(empresa, "jornada_dias", None) or ""),
    )


def calcular_tiempo_gastado(
    inicio: datetime,
    fin: datetime,
    *,
    usar_jornada: bool,
    hora_inicio: time,
    hora_fin: time,
    dias_laborales: Set[int],
) -> int:
    if usar_jornada:
        return minutos_laborales(inicio, fin, hora_inicio, hora_fin, dias_laborales)
    return minutos_entre(inicio, fin)


def total_minutos_jornadas(jornadas) -> int:
    """Suma la duración de cada sesión de trabajo."""
    return sum(minutos_entre(j.fecha_inicio, j.fecha_fin) for j in jornadas)


def wo_tiempo_gastado_minutos(wo, empresa=None) -> Optional[int]:
    """Minutos efectivos de la OT (suma de jornadas/sesiones o valor almacenado)."""
    if wo.tiempo_gastado_minutos is not None:
        return wo.tiempo_gastado_minutos
    if wo.jornadas:
        return total_minutos_jornadas(wo.jornadas)
    if wo.fecha_inicio and wo.fecha_cierre:
        return minutos_entre(wo.fecha_inicio, wo.fecha_cierre)
    return None
