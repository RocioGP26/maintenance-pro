"""Catálogo de marca, modelo, fabricante, área, ubicación y planta (campo personalizado)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func

from app import db
from app.models import (
    MACHINE_CATALOG_CAMPOS,
    MACHINE_CATALOG_COLUMN_CAMPOS,
    MACHINE_CATALOG_CUSTOM_CLAVES,
    MACHINE_CATALOG_LABELS,
    ActivoCampoValor,
    CampoPersonalizado,
    Machine,
    MachineCatalogValue,
)


def normalizar_valor_catalogo(valor: str) -> str:
    return " ".join((valor or "").strip().split()).casefold()


def campo_catalogo_valido(campo: str) -> bool:
    return (campo or "").strip().lower() in MACHINE_CATALOG_CAMPOS


def _columna_maquina(campo: str):
    return getattr(Machine, campo)


def _valores_campo_personalizado(empresa_id: int, clave: str) -> list[str]:
    rows = (
        db.session.query(ActivoCampoValor.valor)
        .join(CampoPersonalizado, CampoPersonalizado.id == ActivoCampoValor.campo_id)
        .filter(
            CampoPersonalizado.empresa_id == empresa_id,
            CampoPersonalizado.clave == clave,
            ActivoCampoValor.valor.isnot(None),
            ActivoCampoValor.valor != "",
        )
        .distinct()
        .all()
    )
    return [raw for (raw,) in rows if (raw or "").strip()]


def seed_catalogo_desde_activos(empresa_id: int, campo: str) -> int:
    """Copia valores distintos al catálogo si aún no hay filas para el campo."""
    campo = (campo or "").strip().lower()
    if not campo_catalogo_valido(campo) or not empresa_id:
        return 0
    existentes = MachineCatalogValue.query.filter_by(empresa_id=empresa_id, campo=campo).count()
    if existentes:
        return 0
    creados = 0
    if campo in MACHINE_CATALOG_CUSTOM_CLAVES:
        valores = _valores_campo_personalizado(empresa_id, campo)
    else:
        col = _columna_maquina(campo)
        valores = [
            raw
            for (raw,) in db.session.query(col)
            .filter(Machine.empresa_id == empresa_id, col.isnot(None), col != "")
            .distinct()
            .all()
        ]
    for raw in valores:
        if upsert_valor_catalogo(empresa_id, campo, raw):
            creados += 1
    return creados


def listar_valores_catalogo(
    empresa_id: int, campo: str, *, q: str = "", limit: int = 50
) -> list[dict]:
    campo = (campo or "").strip().lower()
    if not campo_catalogo_valido(campo) or not empresa_id:
        return []
    seed_catalogo_desde_activos(empresa_id, campo)
    query = MachineCatalogValue.query.filter_by(empresa_id=empresa_id, campo=campo)
    term = (q or "").strip()
    if term:
        like = f"%{term}%"
        query = query.filter(MachineCatalogValue.valor.ilike(like))
    rows = query.order_by(func.lower(MachineCatalogValue.valor)).limit(max(1, min(limit, 100))).all()
    return [{"id": row.id, "valor": row.valor} for row in rows]


def upsert_valor_catalogo(empresa_id: int, campo: str, valor: str) -> Optional[MachineCatalogValue]:
    campo = (campo or "").strip().lower()
    texto = " ".join((valor or "").strip().split())
    if not empresa_id or not campo_catalogo_valido(campo) or not texto:
        return None
    if len(texto) > 120:
        texto = texto[:120].strip()
    norm = normalizar_valor_catalogo(texto)
    row = MachineCatalogValue.query.filter_by(
        empresa_id=empresa_id, campo=campo, valor_norm=norm
    ).first()
    if row:
        if row.valor != texto:
            row.valor = texto
        return row
    row = MachineCatalogValue(
        empresa_id=empresa_id,
        campo=campo,
        valor=texto,
        valor_norm=norm,
    )
    db.session.add(row)
    return row


def _usos_valor(empresa_id: int, campo: str, norm: str) -> int:
    if campo in MACHINE_CATALOG_CUSTOM_CLAVES:
        rows = (
            db.session.query(ActivoCampoValor.valor)
            .join(CampoPersonalizado, CampoPersonalizado.id == ActivoCampoValor.campo_id)
            .filter(
                CampoPersonalizado.empresa_id == empresa_id,
                CampoPersonalizado.clave == campo,
                ActivoCampoValor.valor.isnot(None),
                ActivoCampoValor.valor != "",
            )
            .all()
        )
        return sum(1 for (raw,) in rows if normalizar_valor_catalogo(raw or "") == norm)
    col = _columna_maquina(campo)
    return sum(
        1
        for (raw,) in db.session.query(col)
        .filter(Machine.empresa_id == empresa_id, col.isnot(None), col != "")
        .all()
        if normalizar_valor_catalogo(raw or "") == norm
    )


def eliminar_valor_catalogo(empresa_id: int, campo: str, valor: str) -> tuple[bool, str, int]:
    """Elimina del catálogo. Devuelve (ok, mensaje, usos en activos)."""
    campo = (campo or "").strip().lower()
    texto = " ".join((valor or "").strip().split())
    if not empresa_id or not campo_catalogo_valido(campo) or not texto:
        return False, "Indica un valor válido para eliminar.", 0
    norm = normalizar_valor_catalogo(texto)
    row = MachineCatalogValue.query.filter_by(
        empresa_id=empresa_id, campo=campo, valor_norm=norm
    ).first()
    if row is None:
        return False, "Ese valor no está en el catálogo.", 0

    usos = _usos_valor(empresa_id, campo, norm)
    db.session.delete(row)
    label = MACHINE_CATALOG_LABELS.get(campo, campo)
    return True, f"{label} «{row.valor}» eliminada del catálogo.", usos


def sincronizar_catalogo_desde_maquina(machine: Machine) -> None:
    eid = getattr(machine, "empresa_id", None)
    if not eid:
        return
    for campo in MACHINE_CATALOG_COLUMN_CAMPOS:
        upsert_valor_catalogo(eid, campo, getattr(machine, campo, "") or "")


def sincronizar_catalogo_campos_personalizados(
    empresa_id: int, campos_valores: dict[str, str]
) -> None:
    """Upsert de claves personalizadas creatable (p. ej. planta)."""
    if not empresa_id:
        return
    for clave in MACHINE_CATALOG_CUSTOM_CLAVES:
        upsert_valor_catalogo(empresa_id, clave, campos_valores.get(clave, "") or "")


def catalogo_contexto_formulario(empresa_id: Optional[int]) -> dict:
    if not empresa_id:
        return {campo: [] for campo in MACHINE_CATALOG_CAMPOS}
    data = {}
    for campo in MACHINE_CATALOG_CAMPOS:
        data[campo] = [item["valor"] for item in listar_valores_catalogo(empresa_id, campo, limit=100)]
    return data


__all__ = [
    "MACHINE_CATALOG_CAMPOS",
    "MACHINE_CATALOG_COLUMN_CAMPOS",
    "MACHINE_CATALOG_CUSTOM_CLAVES",
    "MACHINE_CATALOG_LABELS",
    "campo_catalogo_valido",
    "catalogo_contexto_formulario",
    "eliminar_valor_catalogo",
    "listar_valores_catalogo",
    "normalizar_valor_catalogo",
    "seed_catalogo_desde_activos",
    "sincronizar_catalogo_campos_personalizados",
    "sincronizar_catalogo_desde_maquina",
    "upsert_valor_catalogo",
]
