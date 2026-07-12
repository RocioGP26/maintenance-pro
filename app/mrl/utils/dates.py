"""Formateo de fechas tenant · MRL-11-META §3."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def format_datetime_latam(
    dt: datetime,
    timezone_name: str,
    *,
    include_time: bool = True,
) -> str:
    """Formatea UTC a hora local LatAm (DD/MM/YYYY [HH:mm])."""
    if dt.tzinfo is None:
        raise ValueError("dt debe ser timezone-aware")
    local = dt.astimezone(ZoneInfo(timezone_name))
    if include_time:
        return local.strftime("%d/%m/%Y %H:%M")
    return local.strftime("%d/%m/%Y")
