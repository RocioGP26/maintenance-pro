"""Monedas activas por empresa y precios multi-divisa."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from app.money import MONEDAS_CODIGOS, normalizar_moneda

if TYPE_CHECKING:
    from app.models import Empresa, InvProducto

# Paquete habitual en Venezuela
MONEDAS_VENEZUELA: tuple[str, ...] = ("USD", "VES", "COP")


def normalizar_monedas_activas(raw, moneda_principal: str | None = None) -> list[str]:
    if raw is None:
        ref = normalizar_moneda(moneda_principal)
        return [ref]
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            raw = [m.strip() for m in raw.split(",") if m.strip()]
    if not isinstance(raw, (list, tuple)):
        ref = normalizar_moneda(moneda_principal)
        return [ref]
    seen: set[str] = set()
    out: list[str] = []
    for item in raw:
        raw_cod = (item or "").strip().upper()
        if raw_cod not in MONEDAS_CODIGOS:
            continue
        if raw_cod not in seen:
            seen.add(raw_cod)
            out.append(raw_cod)
    if out:
        return out
    return [normalizar_moneda(moneda_principal)]


def monedas_activas_de(empresa: "Empresa | None") -> list[str]:
    if empresa is None:
        return ["COP"]
    principal = normalizar_moneda(getattr(empresa, "moneda", None))
    return normalizar_monedas_activas(
        getattr(empresa, "monedas_activas_json", None), principal
    )


def empresa_multimoneda(empresa: "Empresa | None") -> bool:
    return len(monedas_activas_de(empresa)) > 1


def set_monedas_empresa(
    empresa: "Empresa",
    monedas: list[str] | None,
    moneda_referencia: str | None = None,
) -> None:
    ref = normalizar_moneda(moneda_referencia or getattr(empresa, "moneda", None))
    activas = normalizar_monedas_activas(monedas, ref)
    if ref not in activas:
        activas.insert(0, ref)
    empresa.moneda = ref
    empresa.monedas_activas_json = json.dumps(activas, ensure_ascii=False)


def monedas_desde_modo_venezuela(modo: str, moneda_elegida: str) -> list[str]:
    """modo: 'una' | 'tres'."""
    if (modo or "").strip().lower() == "tres":
        return list(MONEDAS_VENEZUELA)
    return [normalizar_moneda(moneda_elegida)]


def parse_precios_json(texto: str | None) -> dict[str, float]:
    try:
        data = json.loads(texto or "{}")
        if not isinstance(data, dict):
            return {}
        out: dict[str, float] = {}
        for k, v in data.items():
            cod = (k or "").strip().upper()
            if cod in MONEDAS_CODIGOS:
                try:
                    out[cod] = float(v)
                except (TypeError, ValueError):
                    continue
        return out
    except (json.JSONDecodeError, TypeError):
        return {}


def precios_producto(producto: "InvProducto", moneda_referencia: str) -> dict[str, float]:
    """Mapa moneda → precio venta; completa con precio_venta legacy si falta la ref."""
    precios = parse_precios_json(getattr(producto, "precios_json", None))
    ref = normalizar_moneda(moneda_referencia)
    if ref not in precios and getattr(producto, "precio_venta", None):
        precios.setdefault(ref, float(producto.precio_venta or 0))
    return precios


def precio_producto_en(producto: "InvProducto", moneda: str, moneda_referencia: str) -> float:
    return precios_producto(producto, moneda_referencia).get(
        normalizar_moneda(moneda), float(getattr(producto, "precio_venta", 0) or 0)
    )


def set_precios_producto(producto: "InvProducto", precios: dict[str, float], moneda_referencia: str) -> None:
    ref = normalizar_moneda(moneda_referencia)
    limpio = {k: float(v) for k, v in precios.items() if k in MONEDAS_CODIGOS}
    producto.precios_json = json.dumps(limpio, ensure_ascii=False)
    producto.precio_venta = float(limpio.get(ref, producto.precio_venta or 0))
