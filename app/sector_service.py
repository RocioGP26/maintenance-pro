"""Provisionamiento de plantilla sectorial por empresa."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import or_

from app import db
from app.models import (
    CampoPersonalizado,
    Machine,
    MachineStatus,
    MachineType,
    PlantillaDashboard,
    Sede,
)
from app.sector_templates import (
    SECTOR_CATEGORIES,
    SECTOR_CUSTOM_FIELDS,
    dashboard_config_for_sector,
    normalizar_sector,
)

# Activos de ejemplo al completar onboarding (categoria_base, nombre, estado)
SAMPLE_ASSETS_BY_SECTOR: dict[str, tuple[tuple[str, str, str], ...]] = {
    "manufactura": (
        ("motor", "Motor línea 1", MachineStatus.OPERATIVO.value),
        ("compresor", "Compresor principal", MachineStatus.OPERATIVO.value),
        ("linea_produccion", "Línea de producción A", MachineStatus.MANTENIMIENTO.value),
    ),
    "logistica": (
        ("montacargas", "Montacargas 3", MachineStatus.OPERATIVO.value),
        ("camion", "Camión reparto 12", MachineStatus.OPERATIVO.value),
        ("gps", "Unidad GPS flota", MachineStatus.OPERATIVO.value),
    ),
    "salud": (
        ("monitor", "Monitor UCI 2", MachineStatus.OPERATIVO.value),
        ("autoclave", "Autoclave central", MachineStatus.OPERATIVO.value),
        ("ventilador", "Ventilador mecánico 4", MachineStatus.MANTENIMIENTO.value),
    ),
    "mineria": (
        ("excavadora", "Excavadora 01", MachineStatus.OPERATIVO.value),
        ("camion_minero", "Camión 793F", MachineStatus.OPERATIVO.value),
        ("bomba_mineria", "Bomba de lodos", MachineStatus.OPERATIVO.value),
    ),
    "alimentos": (
        ("cuarto_frio", "Cuarto frío principal", MachineStatus.OPERATIVO.value),
        ("horno", "Horno túnel 2", MachineStatus.OPERATIVO.value),
        ("mezcladora", "Mezcladora batch", MachineStatus.OPERATIVO.value),
    ),
    "construccion": (
        ("grua", "Grúa torre A", MachineStatus.OPERATIVO.value),
        ("generador", "Generador 250 kVA", MachineStatus.OPERATIVO.value),
        ("compactador", "Compactador", MachineStatus.MANTENIMIENTO.value),
    ),
    "educacion": (
        ("laboratorio", "Laboratorio química", MachineStatus.OPERATIVO.value),
        ("computo", "Sala de cómputo B", MachineStatus.OPERATIVO.value),
        ("aire_acondicionado", "HVAC biblioteca", MachineStatus.OPERATIVO.value),
    ),
}


def _clave_tipo_empresa(empresa_id: int, base: str) -> str:
    return f"e{empresa_id}_{base}"


def _prefijo_empresa(empresa_id: int, base: str) -> str:
    base = (base or "EQ").upper()[:4]
    return f"{base}{empresa_id}"[:8]


def crear_plantilla_sector(empresa_id: int, sector: str) -> dict[str, Any]:
    """
    Configura categorías (MachineType), campos personalizados y plantilla de dashboard
    para una empresa recién registrada.
    """
    sector = normalizar_sector(sector)
    categorias = SECTOR_CATEGORIES.get(sector, SECTOR_CATEGORIES["manufactura"])
    tipos: dict[str, MachineType] = {}
    orden = 0

    for clave_base, nombre, prefijo in categorias:
        clave = _clave_tipo_empresa(empresa_id, clave_base)
        existente = MachineType.query.filter_by(empresa_id=empresa_id, clave=clave).first()
        if existente:
            mt = existente
        else:
            mt = MachineType(
                empresa_id=empresa_id,
                clave=clave,
                nombre=nombre,
                prefijo=_prefijo_empresa(empresa_id, prefijo),
                orden=orden,
                activo=True,
                sector_industrial=sector,
            )
            db.session.add(mt)
        tipos[clave_base] = mt
        orden += 1

    db.session.flush()

    campos_defs = SECTOR_CUSTOM_FIELDS.get(sector, ())
    orden_c = 0
    for clave_c, nombre_c, tipo_c, obligatorio, cat_base in campos_defs:
        mt_id = None
        if cat_base and cat_base in tipos:
            mt_id = tipos[cat_base].id
        clave_full = _clave_tipo_empresa(empresa_id, clave_c) if not cat_base else clave_c
        existe = CampoPersonalizado.query.filter_by(
            empresa_id=empresa_id, clave=clave_c, sector=sector
        ).first()
        if not existe:
            db.session.add(
                CampoPersonalizado(
                    empresa_id=empresa_id,
                    sector=sector,
                    machine_type_id=mt_id,
                    clave=clave_c,
                    nombre=nombre_c,
                    tipo=tipo_c,
                    obligatorio=obligatorio,
                    orden=orden_c,
                    activo=True,
                )
            )
        orden_c += 1

    config = dashboard_config_for_sector(sector)
    plantilla = PlantillaDashboard.query.filter_by(empresa_id=empresa_id).first()
    if plantilla:
        plantilla.sector = sector
        plantilla.config_json = json.dumps(config, ensure_ascii=False)
    else:
        db.session.add(
            PlantillaDashboard(
                empresa_id=empresa_id,
                sector=sector,
                config_json=json.dumps(config, ensure_ascii=False),
            )
        )

    db.session.flush()
    return {"tipos": tipos, "sector": sector, "config": config}


def crear_activos_ejemplo(empresa_id: int, sede: Sede, tipos: dict[str, MachineType], sector: str) -> None:
    sector = normalizar_sector(sector)
    samples = SAMPLE_ASSETS_BY_SECTOR.get(sector, SAMPLE_ASSETS_BY_SECTOR["manufactura"])
    pref_counters: dict[str, int] = {}
    for cat_base, nombre, status in samples:
        mt = tipos.get(cat_base)
        if not mt:
            continue
        pref = mt.prefijo
        pref_counters[pref] = pref_counters.get(pref, 0) + 1
        n = pref_counters[pref]
        codigo = f"{pref}-{n:03d}"
        m = Machine(
            empresa_id=empresa_id,
            sede_id=sede.id,
            machine_type_id=mt.id,
            codigo=codigo,
            nombre=nombre,
            ubicacion=sede.nombre,
            status=status,
            criticidad="alta" if n == 1 else "media",
        )
        m.sync_criticidad_critico()
        db.session.add(m)
    db.session.flush()


def get_plantilla_dashboard(empresa_id: int, sector: str) -> dict[str, Any]:
    sector = normalizar_sector(sector)
    row = PlantillaDashboard.query.filter_by(empresa_id=empresa_id).first()
    if row and row.config_json:
        try:
            return json.loads(row.config_json)
        except json.JSONDecodeError:
            pass
    return dashboard_config_for_sector(sector)


def ensure_empresa_sector_setup(empresa) -> None:
    """Empresas legacy sin categorías: aplica plantilla del sector."""
    if not empresa or not empresa.id:
        return
    n = MachineType.query.filter_by(empresa_id=empresa.id).count()
    if n == 0:
        crear_plantilla_sector(empresa.id, empresa.sector or "manufactura")
        db.session.commit()


def campos_para_tipo(empresa_id: int, sector: str, machine_type_id: int | None) -> list[CampoPersonalizado]:
    sector = normalizar_sector(sector)
    q = CampoPersonalizado.query.filter_by(empresa_id=empresa_id, sector=sector, activo=True)
    if machine_type_id:
        q = q.filter(
            or_(
                CampoPersonalizado.machine_type_id.is_(None),
                CampoPersonalizado.machine_type_id == machine_type_id,
            )
        )
    else:
        q = q.filter(CampoPersonalizado.machine_type_id.is_(None))
    return q.order_by(CampoPersonalizado.orden, CampoPersonalizado.nombre).all()


def valores_campos_map(machine: Machine) -> dict[int, str]:
    return {v.campo_id: (v.valor or "") for v in machine.valores_campos}
