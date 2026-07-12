"""
Catálogo de plantillas sectoriales (motor base + configuración por sector).

Un solo código base: categorías (MachineType), campos personalizados y dashboard
se provisionan al registrar la empresa según su sector industrial.
"""

from __future__ import annotations

from typing import Any

# (clave, etiqueta)
SECTOR_CHOICES: tuple[tuple[str, str], ...] = (
    ("comercio", "Comercio / Retail / Tienda"),
    ("manufactura", "Manufactura"),
    ("logistica", "Logística"),
    ("salud", "Salud"),
    ("mineria", "Minería"),
    ("alimentos", "Alimentos"),
    ("construccion", "Construcción"),
    ("educacion", "Educación"),
    ("hoteleria", "Hotelería"),
    ("transporte", "Transporte"),
)

SECTOR_LABELS: dict[str, str] = dict(SECTOR_CHOICES)

# Categorías de activo por sector: (clave, nombre, prefijo)
SECTOR_CATEGORIES: dict[str, tuple[tuple[str, str, str], ...]] = {
    "comercio": (),  # Solo inventario comercial — sin plantilla de activos
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
    "hoteleria": (
        ("habitacion", "Habitaciones", "HB"),
        ("aire_acondicionado", "Aires acondicionados", "AA"),
        ("ascensor", "Ascensores", "AS"),
        ("lavanderia", "Equipos de lavandería", "LV"),
        ("cocina_hotel", "Equipos de cocina", "CC"),
    ),
    "transporte": (
        ("vehiculo_liviano", "Vehículos livianos", "VL"),
        ("camion", "Camiones", "CM"),
        ("bus", "Buses", "BS"),
        ("remolque", "Remolques", "RM"),
        ("gps", "GPS / telemetría", "GP"),
    ),
}

# Campos personalizados: (clave, nombre, tipo, obligatorio, categoria_clave|None)
# categoria_clave None = aplica a todas las categorías del sector
SECTOR_CUSTOM_FIELDS: dict[str, tuple[tuple[str, str, str, bool, str | None], ...]] = {
    "comercio": (),
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
        ("amperaje", "Amperaje", "text", False, None),
        ("rpm", "RPM", "number", False, None),
        ("lubricante", "Lubricante", "text", False, None),
        ("capacidad", "Capacidad", "text", False, None),
        ("capacidad_produccion", "Capacidad producción", "text", False, None),
        ("consumo_energia", "Consumo energía", "text", False, None),
        ("planta", "Planta", "text", False, None),
        ("linea_produccion", "Línea de producción", "text", False, None),
        ("proceso_asociado", "Proceso asociado", "text", False, None),
        ("centro_costo", "Centro de costo", "text", False, None),
        ("impacto_produccion", "Impacto en producción", "text", False, None),
        ("oee_objetivo", "OEE objetivo (%)", "number", False, None),
        ("loto", "Requiere LOTO", "boolean", False, None),
        ("riesgos", "Riesgos", "text", False, None),
        ("puntos_inspeccion", "Puntos de inspección", "text", False, None),
        ("epp_requerido", "EPP requerido", "text", False, None),
        ("normas", "Normas aplicables", "text", False, None),
    ),
    "salud": (
        ("registro_invima", "Registro INVIMA", "text", False, None),
        ("fecha_calibracion", "Próxima calibración", "date", False, None),
        ("clase_riesgo", "Clase de riesgo", "text", False, None),
        ("metrologia", "Control metrológico", "text", False, None),
        ("certificados", "Certificados", "text", False, None),
        ("riesgo_biomedico", "Riesgo biomédico", "text", False, None),
        ("ubicacion_clinica", "Ubicación clínica", "text", False, None),
        ("servicio_clinico", "Servicio", "text", False, None),
        ("contrato_mantenimiento", "Contrato de mantenimiento", "text", False, None),
        ("proveedor_autorizado", "Proveedor autorizado", "text", False, None),
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
        ("dependencia", "Dependencia", "text", False, None),
        ("funcionario_responsable", "Funcionario responsable", "text", False, None),
        ("licencias_software", "Licencias de software", "text", False, None),
        ("antivirus", "Antivirus", "text", False, None),
    ),
    "hoteleria": (
        ("habitacion", "Habitación", "text", False, None),
        ("piso", "Piso", "text", False, None),
        ("edificio", "Edificio", "text", False, None),
        ("consumo", "Consumo", "text", False, None),
        ("garantia_hasta", "Garantía hasta", "date", False, None),
    ),
    "transporte": (
        ("placa", "Placa", "text", True, None),
        ("numero_motor", "Número de motor", "text", False, None),
        ("chasis", "Chasis", "text", False, None),
        ("soat", "Vencimiento SOAT", "date", False, None),
        ("tecnomecanica", "Vencimiento tecnomecánica", "date", False, None),
        ("gps", "Identificador GPS", "text", False, None),
        ("kilometraje", "Kilometraje", "number", False, None),
        ("conductor", "Conductor", "text", False, None),
        ("ruta", "Ruta", "text", False, None),
        ("consumo_combustible", "Consumo de combustible", "number", False, None),
    ),
}

SECTOR_CUSTOM_FIELD_SECTIONS: dict[str, str] = {
    "potencia": "tecnica", "voltaje": "tecnica", "amperaje": "tecnica", "rpm": "tecnica",
    "lubricante": "tecnica", "capacidad": "tecnica",
    "numero_motor": "tecnica", "chasis": "tecnica", "registro_invima": "documentacion",
    "clase_riesgo": "mantenimiento", "riesgo_biomedico": "mantenimiento",
    "fecha_calibracion": "mantenimiento", "metrologia": "mantenimiento",
    "loto": "mantenimiento", "riesgos": "mantenimiento", "puntos_inspeccion": "mantenimiento",
    "epp_requerido": "mantenimiento", "normas": "documentacion", "certificados": "documentacion",
    "placa": "general", "kilometraje": "operativa", "horometro": "operativa",
    "soat": "documentacion", "tecnomecanica": "documentacion", "garantia_hasta": "financiera",
    "dependencia": "ubicacion", "funcionario_responsable": "general",
    "planta": "ubicacion", "linea_produccion": "operativa", "proceso_asociado": "operativa",
    "centro_costo": "financiera", "impacto_produccion": "operativa", "oee_objetivo": "operativa",
    "ubicacion_clinica": "ubicacion", "servicio_clinico": "ubicacion",
    "contrato_mantenimiento": "documentacion", "proveedor_autorizado": "documentacion",
    "habitacion": "ubicacion", "piso": "ubicacion", "edificio": "ubicacion",
    "conductor": "operativa", "ruta": "operativa", "gps": "operativa",
    "consumo": "operativa", "consumo_combustible": "operativa",
    "licencias_software": "documentacion", "antivirus": "documentacion",
}

# Agrupación dashboard (etiqueta, claves de categoría)
SECTOR_DASHBOARD_CATEGORIES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "comercio": (),
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
    "hoteleria": (
        ("Habitaciones", ("habitacion", "aire_acondicionado")),
        ("Servicios", ("ascensor", "lavanderia")),
        ("Alimentos y bebidas", ("cocina_hotel",)),
    ),
    "transporte": (
        ("Flota", ("vehiculo_liviano", "camion", "bus")),
        ("Carga", ("remolque",)),
        ("Telemetría", ("gps",)),
    ),
}

# Icono y color de tarjeta por categoría (dashboard)
DEFAULT_SECTOR_CATEGORY_UI = (
    {"icon": "bi-grid-3x3-gap", "tone": "blue"},
    {"icon": "bi-layers", "tone": "green"},
    {"icon": "bi-tools", "tone": "purple"},
)

SECTOR_DASHBOARD_CATEGORY_UI: dict[str, tuple[dict[str, str], ...]] = {
    "comercio": (
        {"icon": "bi-cart3", "tone": "blue"},
        {"icon": "bi-box-seam", "tone": "green"},
    ),
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
    "hoteleria": (
        {"icon": "bi-building", "tone": "blue"},
        {"icon": "bi-tools", "tone": "green"},
        {"icon": "bi-cup-hot", "tone": "purple"},
    ),
    "transporte": (
        {"icon": "bi-truck", "tone": "blue"},
        {"icon": "bi-box-seam", "tone": "green"},
        {"icon": "bi-broadcast", "tone": "purple"},
    ),
}

# KPIs del dashboard (fila de planta — mismos indicadores por sector)
from app.dashboard_kpis import PLANT_KPI_DEFINITIONS

SECTOR_DASHBOARD_KPIS: dict[str, tuple[tuple[str, str], ...]] = {
    sector: PLANT_KPI_DEFINITIONS for sector in (
        "comercio",
        "manufactura",
        "logistica",
        "salud",
        "mineria",
        "alimentos",
        "construccion",
        "educacion",
        "hoteleria",
        "transporte",
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


SECTOR_COMERCIO = "comercio"


def sector_es_comercio(sector: str | None) -> bool:
    return normalizar_sector(sector) == SECTOR_COMERCIO


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
