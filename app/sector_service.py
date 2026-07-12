"""Provisionamiento de plantilla por empresa (categorías universales + dashboard)."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, List, Optional

from sqlalchemy import or_
from app import db
from app.asset_standard import (
    ACTIVO_SECCIONES,
    ACTIVO_SECCION_KEYS,
    SAMPLE_ASSETS_UNIVERSAL,
    UNIVERSAL_CATEGORIES,
    es_seccion_estandar,
    normalizar_seccion_ancla,
    normalizar_seccion_campo,
)
from app.custom_fields import (
    CAMPO_ENTIDAD_ACTIVO,
    CAMPO_ENTIDAD_EQUIPO,
    campo_aplica_a_tipo,
    categorias_ids_desde_campo,
)
from app.models import (
    ActivoCampoValor,
    CampoPersonalizado,
    Machine,
    MachineType,
    PlantillaDashboard,
    Sede,
)
from app.sector_templates import (
    SECTOR_CUSTOM_FIELDS,
    SECTOR_CUSTOM_FIELD_SECTIONS,
    dashboard_config_for_sector,
    normalizar_sector,
)


def _clave_tipo_empresa(empresa_id: int, base: str) -> str:
    return f"e{empresa_id}_{base}"


def _prefijo_empresa(empresa_id: int, base: str) -> str:
    base = (base or "EQ").upper()[:4]
    return f"{base}{empresa_id}"[:8]


def _prefijo_ocupado(prefijo: str, exclude_id: Optional[int] = None) -> bool:
    q = MachineType.query.filter_by(prefijo=prefijo.upper()[:8])
    if exclude_id:
        q = q.filter(MachineType.id != exclude_id)
    return q.first() is not None


def _prefijo_unico(empresa_id: int, base: str, exclude_id: Optional[int] = None) -> str:
    """Prefijo único global (columna prefijo es UNIQUE en toda la tabla)."""
    base = (base or "EQ").upper()[:4]
    candidatos = [
        _prefijo_empresa(empresa_id, base),
        f"{base[:2]}{empresa_id:02d}"[:8],
        f"{base[0]}{empresa_id}{base[1:3]}"[:8],
    ]
    for n in range(1, 200):
        candidatos.append(f"{base[:3]}{empresa_id}{n}"[:8])
    vistos: set[str] = set()
    for raw in candidatos:
        p = raw.upper()[:8]
        if len(p) < 2 or p in vistos:
            continue
        vistos.add(p)
        if not _prefijo_ocupado(p, exclude_id):
            return p
    return f"X{empresa_id}{base[:2]}"[:8].upper()


def _buscar_tipo_universal(empresa_id: int, clave: str, clave_base: str, nombre: str) -> Optional[MachineType]:
    mt = MachineType.query.filter_by(empresa_id=empresa_id, clave=clave).first()
    if mt:
        return mt
    if clave_base.endswith("s"):
        alt = _clave_tipo_empresa(empresa_id, clave_base[:-1])
        mt = MachineType.query.filter_by(empresa_id=empresa_id, clave=alt).first()
        if mt:
            return mt
    return MachineType.query.filter_by(empresa_id=empresa_id, nombre=nombre).first()


def crear_categorias_universales(empresa_id: int, sector: str) -> dict[str, MachineType]:
    """Categorías multisectoriales base para cualquier empresa."""
    sector = normalizar_sector(sector)
    tipos: dict[str, MachineType] = {}
    with db.session.no_autoflush:
        for orden, (clave_base, nombre, prefijo_base) in enumerate(UNIVERSAL_CATEGORIES):
            clave = _clave_tipo_empresa(empresa_id, clave_base)
            existente = _buscar_tipo_universal(empresa_id, clave, clave_base, nombre)
            if existente:
                existente.clave = clave
                existente.nombre = nombre
                existente.orden = orden
                existente.activo = True
                existente.sector_industrial = sector
                mt = existente
            else:
                mt = MachineType(
                    empresa_id=empresa_id,
                    clave=clave,
                    nombre=nombre,
                    prefijo=_prefijo_unico(empresa_id, prefijo_base),
                    orden=orden,
                    activo=True,
                    sector_industrial=sector,
                )
                db.session.add(mt)
            tipos[clave_base] = mt
    db.session.flush()
    return tipos


def crear_campos_hoja_vida_sector(empresa_id: int, sector: str) -> list[CampoPersonalizado]:
    """Aprovisiona los campos sectoriales sin modificar campos creados por la empresa."""
    sector = normalizar_sector(sector)
    creados: list[CampoPersonalizado] = []
    for orden, (clave, nombre, tipo, obligatorio, _categoria) in enumerate(
        SECTOR_CUSTOM_FIELDS.get(sector, ())
    ):
        existente = CampoPersonalizado.query.filter_by(
            empresa_id=empresa_id,
            sector=sector,
            entidad=CAMPO_ENTIDAD_ACTIVO,
            clave=clave,
        ).first()
        if existente:
            continue
        campo = CampoPersonalizado(
            empresa_id=empresa_id,
            sector=sector,
            entidad=CAMPO_ENTIDAD_ACTIVO,
            clave=clave,
            nombre=nombre,
            seccion=SECTOR_CUSTOM_FIELD_SECTIONS.get(clave, "tecnica"),
            tipo=tipo,
            texto_tamano="corto" if tipo == "text" else "",
            obligatorio=obligatorio,
            orden=orden,
            activo=True,
        )
        db.session.add(campo)
        creados.append(campo)
    db.session.flush()
    return creados


def crear_plantilla_sector(empresa_id: int, sector: str) -> dict[str, Any]:
    """
    Al registrar una empresa: categorías universales + plantilla de dashboard.
    Los campos personalizados los define el administrador en Configuración.
    """
    sector = normalizar_sector(sector)
    tipos = crear_categorias_universales(empresa_id, sector)
    crear_campos_hoja_vida_sector(empresa_id, sector)

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
    samples = SAMPLE_ASSETS_UNIVERSAL.get(sector, SAMPLE_ASSETS_UNIVERSAL["manufactura"])
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
            area="Producción",
            ubicacion="Línea 1",
            status=status,
            criticidad="alta" if n == 1 else "media",
            requiere_mantenimiento=True,
            tipos_mantenimiento=json.dumps(["preventivo"], ensure_ascii=False),
            frecuencia_mantenimiento="mensual",
        )
        m.sync_criticidad_critico()
        db.session.add(m)


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
    """Asegura categorías universales y plantilla de dashboard."""
    if not empresa or not empresa.id:
        return
    sector = normalizar_sector(empresa.sector or "manufactura")
    crear_categorias_universales(empresa.id, sector)
    crear_campos_hoja_vida_sector(empresa.id, sector)
    if not PlantillaDashboard.query.filter_by(empresa_id=empresa.id).first():
        config = dashboard_config_for_sector(sector)
        db.session.add(
            PlantillaDashboard(
                empresa_id=empresa.id,
                sector=sector,
                config_json=json.dumps(config, ensure_ascii=False),
            )
        )
    db.session.commit()


def campos_para_tipo(empresa_id: int, sector: str, machine_type_id: int | None) -> list[CampoPersonalizado]:
    """Campos personalizados de activos (configuración), filtrados por categoría."""
    sector = normalizar_sector(sector)
    q = CampoPersonalizado.query.filter(
        CampoPersonalizado.empresa_id == empresa_id,
        CampoPersonalizado.sector == sector,
        CampoPersonalizado.activo.is_(True),
        CampoPersonalizado.entidad == CAMPO_ENTIDAD_ACTIVO,
    )
    campos = q.order_by(CampoPersonalizado.seccion, CampoPersonalizado.orden, CampoPersonalizado.nombre).all()
    return [c for c in campos if campo_aplica_a_tipo(c, machine_type_id)]


def campos_por_seccion_estructurado(
    empresa_id: int, sector: str, machine_type_id: int | None
) -> tuple[dict[str, list], dict[str, list]]:
    """
    (campos_en_secciones_estandar, secciones_personalizadas_extra)
    Claves estándar: general, ubicacion, tecnica, …
    Personalizadas: nombre libre → bloque al final del formulario.
    """
    en_estandar: dict[str, list] = defaultdict(list)
    extra: dict[str, list] = defaultdict(list)
    for c in campos_para_tipo(empresa_id, sector, machine_type_id):
        key = normalizar_seccion_campo(c.seccion)
        if key in ACTIVO_SECCION_KEYS:
            en_estandar[key].append(c)
        else:
            extra[key].append(c)
    return dict(en_estandar), dict(extra)


def campos_por_seccion(empresa_id: int, sector: str, machine_type_id: int | None) -> dict[str, list]:
    """Compatibilidad: solo secciones extra (no estándar)."""
    _, extra = campos_por_seccion_estructurado(empresa_id, sector, machine_type_id)
    return extra


def categorias_de_seccion_personalizada(
    empresa_id: int, sector: str, nombre_seccion: str
) -> Optional[list[int]]:
    """
    Categorías de los campos ya existentes en la sección personalizada.
    None = sin campos previos; [] = al menos uno aplica a todas; [ids] = unión restringida.
    """
    sector = normalizar_sector(sector)
    nombre = (nombre_seccion or "").strip()
    if not nombre or es_seccion_estandar(nombre):
        return None
    rows = CampoPersonalizado.query.filter_by(
        empresa_id=empresa_id,
        sector=sector,
        entidad=CAMPO_ENTIDAD_ACTIVO,
        seccion=nombre,
    ).all()
    if not rows:
        return None
    union: set[int] = set()
    for c in rows:
        ids = categorias_ids_desde_campo(c)
        if ids:
            union.update(ids)
    if not union:
        return []
    return sorted(union)


def secciones_personalizadas_empresa(empresa_id: int, sector: str) -> list[dict]:
    """Nombres de secciones custom ya creadas (para agregar más campos a la misma sección)."""
    sector = normalizar_sector(sector)
    por_nombre: dict[str, str] = {}
    q = CampoPersonalizado.query.filter_by(
        empresa_id=empresa_id,
        sector=sector,
        entidad=CAMPO_ENTIDAD_ACTIVO,
    )
    labels = dict(ACTIVO_SECCIONES)
    for c in q.all():
        raw = (c.seccion or "").strip()
        if not raw or es_seccion_estandar(raw):
            continue
        if raw not in por_nombre:
            ancla = normalizar_seccion_ancla(c.seccion_ancla)
            por_nombre[raw] = ancla
    return [
        {
            "nombre": nombre,
            "ancla": por_nombre[nombre],
            "ancla_label": labels.get(por_nombre[nombre], "Al final del formulario"),
            "categorias_ids": categorias_de_seccion_personalizada(empresa_id, sector, nombre) or [],
        }
        for nombre in sorted(por_nombre.keys(), key=lambda x: x.casefold())
    ]


def ancla_de_seccion_personalizada(empresa_id: int, sector: str, nombre_seccion: str) -> str:
    sector = normalizar_sector(sector)
    nombre = (nombre_seccion or "").strip()
    if not nombre:
        return ""
    row = (
        CampoPersonalizado.query.filter_by(
            empresa_id=empresa_id,
            sector=sector,
            entidad=CAMPO_ENTIDAD_ACTIVO,
            seccion=nombre,
        )
        .first()
    )
    return normalizar_seccion_ancla(row.seccion_ancla) if row else ""


def secciones_custom_por_ancla(
    empresa_id: int, sector: str, machine_type_id: int | None
) -> tuple[dict[str, list[dict]], list[dict]]:
    """
    Secciones personalizadas agrupadas por ancla (clave estándar) y bloques al final.
    Cada bloque: {"titulo": str, "campos": list[CampoPersonalizado]}.
    """
    _, extra = campos_por_seccion_estructurado(empresa_id, sector, machine_type_id)
    por_ancla: dict[str, list[dict]] = defaultdict(list)
    al_final: list[dict] = []
    for nombre in sorted(extra.keys(), key=lambda n: (extra[n][0].orden if extra[n] else 0, n)):
        campos = extra[nombre]
        ancla = ""
        for c in campos:
            raw = (getattr(c, "seccion_ancla", None) or "").strip()
            if raw:
                ancla = normalizar_seccion_ancla(raw)
                break
        bloque = {"titulo": nombre, "campos": campos}
        if ancla in ACTIVO_SECCION_KEYS:
            por_ancla[ancla].append(bloque)
        else:
            al_final.append(bloque)
    return dict(por_ancla), al_final


def campos_para_equipo(empresa_id: int, sector: str) -> list[CampoPersonalizado]:
    sector = normalizar_sector(sector)
    return (
        CampoPersonalizado.query.filter_by(
            empresa_id=empresa_id, sector=sector, activo=True, entidad=CAMPO_ENTIDAD_EQUIPO
        )
        .order_by(CampoPersonalizado.orden, CampoPersonalizado.nombre)
        .all()
    )


def valores_campos_map(machine: Machine) -> dict[int, str]:
    return {v.campo_id: (v.valor or "") for v in machine.valores_campos}


_SECCION_PRIORIDAD_RESPONSABLE: tuple[str, ...] = (
    "general",
    "ubicacion",
    "tecnica",
    "operativa",
    "financiera",
    "documentacion",
    "observaciones",
    "mantenimiento",
)


def _prioridad_seccion_responsable(seccion: Optional[str]) -> int:
    key = normalizar_seccion_campo(seccion)
    try:
        return _SECCION_PRIORIDAD_RESPONSABLE.index(key)
    except ValueError:
        return len(_SECCION_PRIORIDAD_RESPONSABLE)


def _campo_personalizado_responsable(
    empresa_id: int, sector: str
) -> Optional[CampoPersonalizado]:
    """Campo personalizado «Responsable» del activo (prioriza información general)."""
    from app.sector_templates import normalizar_sector

    sector = normalizar_sector(sector)
    campos = (
        CampoPersonalizado.query.filter(
            CampoPersonalizado.empresa_id == empresa_id,
            CampoPersonalizado.sector == sector,
            CampoPersonalizado.activo.is_(True),
            db.func.lower(CampoPersonalizado.nombre) == "responsable",
            or_(
                CampoPersonalizado.entidad == CAMPO_ENTIDAD_ACTIVO,
                CampoPersonalizado.entidad == CAMPO_ENTIDAD_EQUIPO,
                CampoPersonalizado.entidad.is_(None),
            ),
        )
        .all()
    )
    if not campos:
        return None
    return min(campos, key=lambda c: _prioridad_seccion_responsable(c.seccion))


def valor_campo_personalizado_display(campo: CampoPersonalizado, valor: Optional[str]) -> str:
    """Texto legible de un valor guardado (lista múltiple, booleano, etc.)."""
    raw = (valor or "").strip()
    if not raw:
        return ""
    tipo = (campo.tipo or "text").lower()
    if tipo == "list_multi":
        try:
            items = json.loads(raw)
            if isinstance(items, list):
                return ", ".join(str(x).strip() for x in items if str(x).strip())
        except json.JSONDecodeError:
            pass
    if tipo == "boolean":
        if raw.lower() in ("1", "true", "yes", "si", "sí"):
            return "Sí"
        if raw.lower() in ("0", "false", "no"):
            return "No"
        return ""
    return raw


def responsables_display_por_maquinas(
    machines: list, empresa_id: Optional[int], sector: Optional[str]
) -> dict[int, str]:
    """
    Responsable del activo para OT: solo el campo personalizado «Responsable» del activo.
    Si está vacío en el activo, queda vacío (no usa datos de la OT ni de mantenimiento).
    """
    if not machines:
        return {}
    from app.sector_templates import normalizar_sector

    resultado: dict[int, str] = {}
    custom: dict[int, str] = {}
    if empresa_id and sector:
        sector = normalizar_sector(sector)
        campo = _campo_personalizado_responsable(empresa_id, sector)
        if campo:
            ids = [m.id for m in machines]
            filas = ActivoCampoValor.query.filter(
                ActivoCampoValor.machine_id.in_(ids),
                ActivoCampoValor.campo_id == campo.id,
            ).all()
            for fila in filas:
                texto = valor_campo_personalizado_display(campo, fila.valor)
                if texto:
                    custom[fila.machine_id] = texto
    for m in machines:
        resultado[m.id] = custom.get(m.id, "") or m.responsable_nombre
    return resultado


def responsable_display_maquina(
    machine: Machine, empresa_id: Optional[int], sector: Optional[str]
) -> str:
    return responsables_display_por_maquinas([machine], empresa_id, sector).get(machine.id, "")


def valores_campos_usuario_map(user) -> dict[int, str]:
    return {v.campo_id: (v.valor or "") for v in user.valores_campos}
