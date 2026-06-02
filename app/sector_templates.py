"""
Catálogo de plantillas sectoriales (motor base + configuración por sector).

Un solo código base: categorías (MachineType), campos personalizados y dashboard
se provisionan al registrar la empresa según su sector industrial.
"""

from __future__ import annotations

from typing import Any

# (clave, etiqueta)
SECTOR_CHOICES: tuple[tuple[str, str], ...] = (
    ("manufactura", "Manufactura"),
    ("logistica", "Logística"),
    ("salud", "Salud"),
    ("mineria", "Minería"),
    ("alimentos", "Alimentos"),
    ("construccion", "Construcción"),
    ("educacion", "Educación"),
)

SECTOR_LABELS: dict[str, str] = dict(SECTOR_CHOICES)

# Categorías de activo por sector: (clave, nombre, prefijo)
SECTOR_CATEGORIES: dict[str, tuple[tuple[str, str, str], ...]] = {
    "manufactura": (
        ("linea_produccion", "Líneas de producción", "LP"),
        ("motor", "Motores", "MT"),
        ("bomba", "Bombas", "BM"),
        ("compresor", "Compresores", "CP"),
        ("banda_transportadora", "Bandas transportadoras", "BT"),
        ("tablero_electrico", "Tableros eléctricos", "TE"),
    ),
    "logistica": (
        ("camion", "Camiones", "CM"),
        ("tractomula", "Tractomulas", "TR"),
        ("montacargas", "Montacargas", "MC"),
        ("patineta_hidraulica", "Patinetas hidráulicas", "PH"),
        ("gps", "GPS / telemetría", "GP"),
        ("cuarto_baterias", "Cuartos de baterías", "CB"),
    ),
    "salud": (
        ("rayos_x", "Rayos X", "RX"),
        ("ecografo", "Ecógrafos", "EC"),
        ("autoclave", "Autoclaves", "AC"),
        ("monitor", "Monitores", "MN"),
        ("ventilador", "Ventiladores", "VT"),
    ),
    "mineria": (
        ("excavadora", "Excavadoras", "EX"),
        ("camion_minero", "Camiones mineros", "CM"),
        ("trituradora", "Trituradoras", "TR"),
        ("bomba_mineria", "Bombas de proceso", "BM"),
        ("ventilacion_mina", "Ventilación mina", "VM"),
    ),
    "alimentos": (
        ("linea_envasado", "Líneas de envasado", "LE"),
        ("cuarto_frio", "Cuartos fríos", "CF"),
        ("horno", "Hornos", "HN"),
        ("mezcladora", "Mezcladoras", "MZ"),
        ("intercambiador", "Intercambiadores", "IC"),
    ),
    "construccion": (
        ("grua", "Grúas", "GR"),
        ("mezcladora_concreto", "Mezcladoras de concreto", "MC"),
        ("compactador", "Compactadores", "CP"),
        ("generador", "Generadores", "GN"),
        ("equipo_soldadura", "Equipos de soldadura", "SO"),
    ),
    "educacion": (
        ("laboratorio", "Laboratorios", "LB"),
        ("aire_acondicionado", "Aire acondicionado", "AA"),
        ("computo", "Equipos de cómputo", "PC"),
        ("audiovisual", "Audiovisual", "AV"),
        ("mobiliario_tecnico", "Mobiliario técnico", "MT"),
    ),
}

# Campos personalizados: (clave, nombre, tipo, obligatorio, categoria_clave|None)
# categoria_clave None = aplica a todas las categorías del sector
SECTOR_CUSTOM_FIELDS: dict[str, tuple[tuple[str, str, str, bool, str | None], ...]] = {
    "logistica": (
        ("placa", "Placa", "text", True, None),
        ("numero_motor", "Número de motor", "text", False, None),
        ("kilometraje", "Kilometraje", "number", False, None),
        ("soat", "Vencimiento SOAT", "date", False, None),
        ("tecnomecanica", "Vencimiento tecnomecánica", "date", False, None),
    ),
    "manufactura": (
        ("potencia", "Potencia (kW)", "text", False, None),
        ("voltaje", "Voltaje", "text", False, None),
        ("rpm", "RPM", "number", False, None),
        ("capacidad_produccion", "Capacidad producción", "text", False, None),
        ("consumo_energia", "Consumo energía", "text", False, None),
    ),
    "salud": (
        ("registro_invima", "Registro INVIMA", "text", False, None),
        ("fecha_calibracion", "Próxima calibración", "date", False, None),
        ("clase_riesgo", "Clase de riesgo", "text", False, None),
    ),
    "mineria": (
        ("horometro", "Horómetro", "number", False, None),
        ("ultima_inspeccion", "Última inspección", "date", False, None),
    ),
    "alimentos": (
        ("certificacion_sanitaria", "Certificación sanitaria", "text", False, None),
        ("temperatura_operacion", "Temperatura operación (°C)", "number", False, None),
    ),
    "construccion": (
        ("horometro", "Horómetro", "number", False, None),
        ("capacidad_carga", "Capacidad de carga", "text", False, None),
    ),
    "educacion": (
        ("inventario_institucional", "Inventario institucional", "text", False, None),
        ("garantia_hasta", "Garantía hasta", "date", False, None),
    ),
}

# Agrupación dashboard (etiqueta, claves de categoría)
SECTOR_DASHBOARD_CATEGORIES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "manufactura": (
        ("Líneas y producción", ("linea_produccion", "banda_transportadora")),
        ("Motores y bombas", ("motor", "bomba", "compresor")),
        ("Eléctrico", ("tablero_electrico",)),
    ),
    "logistica": (
        ("Flota vehicular", ("camion", "tractomula")),
        ("Carga y bodega", ("montacargas", "patineta_hidraulica")),
        ("Soporte", ("gps", "cuarto_baterias")),
    ),
    "salud": (
        ("Diagnóstico", ("rayos_x", "ecografo")),
        ("Esterilización", ("autoclave",)),
        ("Soporte vital", ("monitor", "ventilador")),
    ),
    "mineria": (
        ("Extracción", ("excavadora", "trituradora")),
        ("Transporte", ("camion_minero",)),
        ("Proceso", ("bomba_mineria", "ventilacion_mina")),
    ),
    "alimentos": (
        ("Proceso", ("mezcladora", "horno", "intercambiador")),
        ("Envasado y frío", ("linea_envasado", "cuarto_frio")),
    ),
    "construccion": (
        ("Elevación", ("grua",)),
        ("Obra civil", ("mezcladora_concreto", "compactador")),
        ("Energía", ("generador", "equipo_soldadura")),
    ),
    "educacion": (
        ("Laboratorio", ("laboratorio", "mobiliario_tecnico")),
        ("Infraestructura", ("aire_acondicionado", "audiovisual")),
        ("Tecnología", ("computo",)),
    ),
}

# Icono y color de tarjeta por categoría (dashboard)
DEFAULT_SECTOR_CATEGORY_UI = (
    {"icon": "bi-grid-3x3-gap", "tone": "blue"},
    {"icon": "bi-layers", "tone": "green"},
    {"icon": "bi-tools", "tone": "purple"},
)

SECTOR_DASHBOARD_CATEGORY_UI: dict[str, tuple[dict[str, str], ...]] = {
    "logistica": (
        {"icon": "bi-truck", "tone": "blue"},
        {"icon": "bi-box-seam", "tone": "green"},
        {"icon": "bi-wrench-adjustable", "tone": "purple"},
    ),
    "manufactura": (
        {"icon": "bi-gear-wide-connected", "tone": "blue"},
        {"icon": "bi-droplet-half", "tone": "green"},
        {"icon": "bi-lightning-charge", "tone": "purple"},
    ),
    "salud": (
        {"icon": "bi-heart-pulse", "tone": "blue"},
        {"icon": "bi-shield-check", "tone": "green"},
        {"icon": "bi-lungs", "tone": "purple"},
    ),
    "mineria": (
        {"icon": "bi-minecart-loaded", "tone": "blue"},
        {"icon": "bi-truck", "tone": "green"},
        {"icon": "bi-moisture", "tone": "purple"},
    ),
    "alimentos": (
        {"icon": "bi-cup-hot", "tone": "blue"},
        {"icon": "bi-snow", "tone": "green"},
    ),
    "construccion": (
        {"icon": "bi-building", "tone": "blue"},
        {"icon": "bi-bricks", "tone": "green"},
        {"icon": "bi-plug", "tone": "purple"},
    ),
    "educacion": (
        {"icon": "bi-bezier2", "tone": "blue"},
        {"icon": "bi-wind", "tone": "green"},
        {"icon": "bi-pc-display", "tone": "purple"},
    ),
}

# KPIs del dashboard (fila de planta — mismos indicadores por sector)
from app.dashboard_kpis import PLANT_KPI_DEFINITIONS

SECTOR_DASHBOARD_KPIS: dict[str, tuple[tuple[str, str], ...]] = {
    sector: PLANT_KPI_DEFINITIONS for sector in (
        "manufactura",
        "logistica",
        "salud",
        "mineria",
        "alimentos",
        "construccion",
        "educacion",
    )
}

CRITICIDAD_CHOICES: tuple[tuple[str, str], ...] = (
    ("baja", "Baja"),
    ("media", "Media"),
    ("alta", "Alta"),
    ("critica", "Crítica"),
)

FIELD_TYPES = ("text", "number", "date", "boolean")


def sector_valido(sector: str) -> bool:
    return sector in SECTOR_LABELS


def normalizar_sector(sector: str | None) -> str:
    s = (sector or "manufactura").strip().lower()
    return s if sector_valido(s) else "manufactura"


def dashboard_config_for_sector(sector: str) -> dict[str, Any]:
    """Configuración JSON almacenable en PlantillaDashboard."""
    sector = normalizar_sector(sector)
    return {
        "sector": sector,
        "kpis": [{"key": k, "label": lb} for k, lb in SECTOR_DASHBOARD_KPIS.get(sector, SECTOR_DASHBOARD_KPIS["manufactura"])],
        "categories": [
            {"label": label, "claves": list(claves)}
            for label, claves in SECTOR_DASHBOARD_CATEGORIES.get(sector, ())
        ],
    }
