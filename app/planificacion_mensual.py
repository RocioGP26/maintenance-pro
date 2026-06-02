"""Utilidades para planeación mensual de horas por activo."""

from calendar import monthrange
from datetime import date
from typing import Optional

MESES_PLANEACION = (
    (1, "Enero"),
    (2, "Febrero"),
    (3, "Marzo"),
    (4, "Abril"),
    (5, "Mayo"),
    (6, "Junio"),
    (7, "Julio"),
    (8, "Agosto"),
    (9, "Septiembre"),
    (10, "Octubre"),
    (11, "Noviembre"),
    (12, "Diciembre"),
)


def max_horas_mes(anio: int, mes: int) -> int:
    """Máximo teórico: 24 h × días del mes."""
    return 24 * monthrange(anio, mes)[1]


def mes_anterior(anio: int, mes: int) -> tuple[int, int]:
    if mes <= 1:
        return anio - 1, 12
    return anio, mes - 1


def parse_mes_anio(
    mes_raw: str, anio_raw: str, hoy: Optional[date] = None
) -> tuple[int, int]:
    hoy = hoy or date.today()
    try:
        mes = int(mes_raw)
    except (TypeError, ValueError):
        mes = hoy.month
    try:
        anio = int(anio_raw)
    except (TypeError, ValueError):
        anio = hoy.year
    if mes < 1 or mes > 12:
        mes = hoy.month
    if anio < 2000 or anio > 2100:
        anio = hoy.year
    return mes, anio
