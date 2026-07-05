"""Conversión y formato de fechas según zona horaria de la empresa."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TZ = "America/Bogota"


def resolve_timezone_name(empresa: Any = None, tz_name: str | None = None) -> str:
    if tz_name:
        return tz_name
    if empresa is not None:
        from app.locale_options import zona_horaria_por_pais

        raw = (getattr(empresa, "zona_horaria", None) or "").strip()
        pais = (getattr(empresa, "pais", None) or "").strip()
        inferred = zona_horaria_por_pais(pais) if pais else None

        # Empresas legacy: país Venezuela/México/etc. con zona por defecto Bogotá
        if raw and not (raw == DEFAULT_TZ and inferred and inferred != DEFAULT_TZ):
            return raw
        if inferred:
            return inferred
        if raw:
            return raw
    return DEFAULT_TZ


def timezone_obj(empresa: Any = None, tz_name: str | None = None) -> ZoneInfo:
    name = resolve_timezone_name(empresa, tz_name)
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TZ)


def as_utc(dt: datetime | None) -> datetime | None:
    """Interpreta datetimes naive como UTC (como datetime.utcnow en BD)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def utc_a_local(
    dt: datetime | None,
    *,
    empresa: Any = None,
    tz_name: str | None = None,
) -> datetime | None:
    if dt is None:
        return None
    return as_utc(dt).astimezone(timezone_obj(empresa, tz_name))


def hoy_local(empresa: Any = None, tz_name: str | None = None) -> date:
    return utc_a_local(datetime.now(timezone.utc), empresa=empresa, tz_name=tz_name).date()


def formato_fecha_hora(
    dt: datetime | None,
    fmt: str = "%d/%m/%Y %H:%M",
    *,
    empresa: Any = None,
    tz_name: str | None = None,
    desde_utc: bool = True,
    vacio: str = "—",
) -> str:
    if not dt:
        return vacio
    if desde_utc:
        dt = utc_a_local(dt, empresa=empresa, tz_name=tz_name)
    return dt.strftime(fmt)


def empresa_desde_contexto(context: dict) -> Any:
    for key in ("e", "empresa", "empresa_actual"):
        val = context.get(key)
        if val is not None:
            return val
    fila = context.get("fila")
    if fila is not None and getattr(fila, "empresa", None) is not None:
        return fila.empresa
    return None
