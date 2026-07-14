"""Campos y categorías estándar multisectoriales para activos (SaaS)."""

from __future__ import annotations

import calendar
import json
from datetime import date
from typing import Optional

# Categorías creadas al registrar cada empresa
UNIVERSAL_CATEGORIES: tuple[tuple[str, str, str], ...] = (
    ("equipos", "Equipos", "EQ"),
    ("motores", "Motores", "MT"),
    ("vehiculos", "Vehículos", "VH"),
    ("infraestructura", "Infraestructura", "IN"),
    ("herramientas", "Herramientas", "HR"),
    ("instrumentos", "Instrumentos", "IT"),
    ("sistemas_ti", "Sistemas TI", "TI"),
)

MANTENIMIENTO_TIPOS: tuple[tuple[str, str], ...] = (
    ("preventivo", "Preventivo"),
    ("correctivo", "Correctivo"),
    ("predictivo", "Predictivo"),
    ("legal", "Legal"),
    ("calibracion", "Calibración"),
)

# Claves de sección del formulario de activo (campos personalizados)
ACTIVO_SECCIONES: tuple[tuple[str, str], ...] = (
    ("general", "Información general"),
    ("tecnica", "Información técnica"),
    ("ubicacion", "Ubicación"),
    ("operativa", "Información operativa"),
    ("financiera", "Información financiera"),
    ("documentacion", "Documentación"),
    ("observaciones", "Observaciones"),
    ("mantenimiento", "Clasificación para mantenimiento"),
)

ACTIVO_SECCION_KEYS = frozenset(k for k, _ in ACTIVO_SECCIONES)

# Iconos Bootstrap para el encabezado de cada sección del formulario de activo
ACTIVO_SECCION_ICONOS: dict[str, str] = {
    "general": "bi-info-circle-fill",
    "tecnica": "bi-gear-wide-connected",
    "ubicacion": "bi-geo-alt-fill",
    "operativa": "bi-clock-history",
    "financiera": "bi-cash-stack",
    "documentacion": "bi-folder-fill",
    "observaciones": "bi-journal-text",
    "mantenimiento": "bi-wrench-adjustable-circle-fill",
}
ACTIVO_SECCION_ICONO_DEFAULT = "bi-lightning-fill"

# Etiquetas legibles antiguas → clave
_SECCION_ALIASES: dict[str, str] = {
    "personalizada": "general",
    "información general": "general",
    "informacion general": "general",
    "ubicación": "ubicacion",
    "ubicacion": "ubicacion",
    "información técnica": "tecnica",
    "informacion tecnica": "tecnica",
    "información operativa": "operativa",
    "informacion operativa": "operativa",
    "información financiera": "financiera",
    "informacion financiera": "financiera",
    "documentación": "documentacion",
    "documentacion": "documentacion",
    "observaciones": "observaciones",
    "clasificación para mantenimiento": "mantenimiento",
    "clasificacion para mantenimiento": "mantenimiento",
    "clasificación mantenimiento": "mantenimiento",
}

FRECUENCIA_BASE_CHOICES: tuple[tuple[str, str], ...] = (
    ("", "— Sin definir —"),
    ("diaria", "Diaria"),
    ("semanal", "Semanal"),
    ("mensual", "Mensual"),
    ("trimestral", "Trimestral"),
    ("semestral", "Semestral"),
    ("anual", "Anual"),
)

# Activos de ejemplo al onboarding (categoría universal, nombre, estado)
SAMPLE_ASSETS_UNIVERSAL: dict[str, tuple[tuple[str, str, str], ...]] = {
    "manufactura": (
        ("equipos", "Compresor principal", "operativo"),
        ("motores", "Motor línea 1", "operativo"),
        ("infraestructura", "Línea de producción A", "mantenimiento"),
    ),
    "logistica": (
        ("vehiculos", "Montacargas 3", "operativo"),
        ("vehiculos", "Camión reparto 12", "operativo"),
        ("sistemas_ti", "Unidad GPS flota", "operativo"),
    ),
    "salud": (
        ("instrumentos", "Monitor UCI 2", "operativo"),
        ("equipos", "Autoclave central", "operativo"),
        ("equipos", "Ventilador mecánico 4", "mantenimiento"),
    ),
    "mineria": (
        ("vehiculos", "Excavadora 01", "operativo"),
        ("vehiculos", "Camión 793F", "operativo"),
        ("equipos", "Bomba de lodos", "operativo"),
    ),
    "alimentos": (
        ("infraestructura", "Cuarto frío principal", "operativo"),
        ("equipos", "Horno túnel 2", "operativo"),
        ("equipos", "Mezcladora batch", "operativo"),
    ),
    "construccion": (
        ("infraestructura", "Grúa torre A", "operativo"),
        ("equipos", "Generador 250 kVA", "operativo"),
        ("herramientas", "Compactador", "mantenimiento"),
    ),
    "educacion": (
        ("infraestructura", "Laboratorio química", "operativo"),
        ("sistemas_ti", "Sala de cómputo B", "operativo"),
        ("equipos", "HVAC biblioteca", "operativo"),
    ),
    "hoteleria": (
        ("infraestructura", "Habitación 101", "operativo"),
        ("equipos", "Aire acondicionado piso 2", "operativo"),
        ("equipos", "Lavadora industrial", "mantenimiento"),
    ),
    "transporte": (
        ("vehiculos", "Camión de reparto 01", "operativo"),
        ("vehiculos", "Bus de operación 02", "operativo"),
        ("sistemas_ti", "GPS flota principal", "operativo"),
    ),
}


def _sin_prefijo_numerico(texto: str) -> str:
    import re

    return re.sub(r"^\d+\.\s*", "", (texto or "").strip())


def normalizar_seccion_campo(seccion: Optional[str]) -> str:
    """Clave de sección estándar o nombre libre para sección personalizada."""
    s = (seccion or "").strip()
    if not s:
        return "general"
    low = s.lower()
    low_sin_num = _sin_prefijo_numerico(s).lower()
    if low in ACTIVO_SECCION_KEYS:
        return low
    if low_sin_num in ACTIVO_SECCION_KEYS:
        return low_sin_num
    if low in _SECCION_ALIASES:
        return _SECCION_ALIASES[low]
    if low_sin_num in _SECCION_ALIASES:
        return _SECCION_ALIASES[low_sin_num]
    for key, label in ACTIVO_SECCIONES:
        if low == label.lower() or low_sin_num == label.lower():
            return key
    return s


def normalizar_seccion_ancla(ancla: Optional[str]) -> str:
    """Clave de sección estándar tras la cual insertar una sección personalizada."""
    a = (ancla or "").strip()
    if not a:
        return ""
    key = normalizar_seccion_campo(a)
    return key if key in ACTIVO_SECCION_KEYS else ""


def etiqueta_seccion_campo(seccion: Optional[str]) -> str:
    key = normalizar_seccion_campo(seccion)
    if key in ACTIVO_SECCION_KEYS:
        return dict(ACTIVO_SECCIONES).get(key, key)
    return (seccion or "").strip() or "Sección personalizada"


def etiqueta_seccion_campo_con_ancla(seccion: Optional[str], ancla: Optional[str]) -> str:
    base = etiqueta_seccion_campo(seccion)
    anchor = normalizar_seccion_ancla(ancla)
    if anchor and not es_seccion_estandar(seccion):
        despues = dict(ACTIVO_SECCIONES).get(anchor, anchor)
        return f"{base} (después de {despues})"
    return base


def es_seccion_estandar(seccion: Optional[str]) -> bool:
    return normalizar_seccion_campo(seccion) in ACTIVO_SECCION_KEYS


def etiquetas_to_json(texto: str) -> str:
    items = [t.strip() for t in (texto or "").replace(";", ",").split(",") if t.strip()]
    return json.dumps(items, ensure_ascii=False) if items else "[]"


def etiquetas_from_json(raw: Optional[str]) -> str:
    if not raw:
        return ""
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return ", ".join(str(x).strip() for x in data if str(x).strip())
    except json.JSONDecodeError:
        pass
    return (raw or "").strip()


def tipos_mantenimiento_from_form(form) -> str:
    keys = form.getlist("tipos_mantenimiento")
    valid = {k for k, _ in MANTENIMIENTO_TIPOS}
    items = [k for k in keys if k in valid]
    return json.dumps(items, ensure_ascii=False)


def sumar_meses(fecha: date, meses: int) -> date:
    y = fecha.year + (fecha.month - 1 + meses) // 12
    m = (fecha.month - 1 + meses) % 12 + 1
    ultimo = calendar.monthrange(y, m)[1]
    return date(y, m, min(fecha.day, ultimo))


def calcular_garantia_hasta(
    fecha_compra: Optional[date], tiempo_garantia_meses: Optional[int]
) -> Optional[date]:
    if not fecha_compra or not tiempo_garantia_meses or tiempo_garantia_meses < 1:
        return None
    return sumar_meses(fecha_compra, tiempo_garantia_meses)


def estado_garantia_etiqueta(fecha_hasta: Optional[date], ref: Optional[date] = None) -> str:
    if not fecha_hasta:
        return "—"
    ref = ref or date.today()
    return "Activa" if fecha_hasta >= ref else "Vencida"


def estado_garantia_badge_class(etiqueta: str) -> str:
    if etiqueta == "Activa":
        return "success"
    if etiqueta == "Vencida":
        return "danger"
    return "secondary"


REGISTRO_FLAG_KEYS = frozenset({"nuevo", "actualizacion"})


def registro_flags_from_form(form) -> str:
    items = []
    if form.get("registro_nuevo"):
        items.append("nuevo")
    if form.get("registro_actualizacion"):
        items.append("actualizacion")
    return json.dumps(items, ensure_ascii=False)


def registro_flags_checked(raw: Optional[str], registro_tipo_legacy: Optional[str] = "") -> tuple[bool, bool]:
    sel: set[str] = set()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                sel.update(str(x).strip() for x in data if str(x).strip())
            elif isinstance(data, dict) and isinstance(data.get("items"), list):
                sel.update(str(x).strip() for x in data["items"] if str(x).strip())
        except json.JSONDecodeError:
            pass
    legacy = (registro_tipo_legacy or "").strip()
    if legacy in REGISTRO_FLAG_KEYS:
        sel.add(legacy)
    return "nuevo" in sel, "actualizacion" in sel


def tipos_mantenimiento_list(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data]
    except json.JSONDecodeError:
        pass
    return []
