"""Adaptadores MRL del módulo de inventario comercial."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from app.currency import empresa_multimoneda, monedas_activas_de
from app.inventario_comercial.service import query_productos_bajo_stock
from app.models import Empresa
from app.mrl.excel.exporter import BaseExcelExporter, ColumnFormat
from app.mrl.metadata import MRLDocumentMeta
from app.timezone_utils import resolve_timezone_name


def _usuario_label(usuario) -> str:
    if usuario is None:
        return "Sistema · Roustix"
    return str(getattr(usuario, "username", usuario) or "Usuario")


def _meta(empresa: Empresa, title: str, code: str, usuario=None) -> MRLDocumentMeta:
    return MRLDocumentMeta(
        doc_code="DOC-010", instance_code=code, module="Inventory",
        title=title, empresa_id=empresa.id,
        empresa_nombre=(empresa.razon_social or "Empresa").strip(),
        empresa_nit=(empresa.nit or "").strip() or None,
        generated_at=datetime.now(timezone.utc),
        timezone_name=resolve_timezone_name(empresa), usuario=_usuario_label(usuario),
    )


def _save(empresa, title, code, sheet, headers, rows, formats=None, usuario=None):
    exporter = BaseExcelExporter(_meta(empresa, title, code, usuario))
    exporter.add_sheet(sheet).write_table(headers, rows, column_formats=formats)
    return exporter.save()


def _producto_columns(empresa: Empresa):
    ref = (empresa.moneda or "COP").upper()
    monedas = monedas_activas_de(empresa) if empresa_multimoneda(empresa) else [ref]
    headers = ["Referencia", "Nombre", "Marca", "Categoría", "Subcategoría", "Unidad", "Stock", "Stock mínimo", f"Precio compra ({ref})"]
    headers.extend(f"Precio venta ({m})" for m in monedas)
    headers.append("Activo")
    formats = [None] * 6 + ["integer", "integer"] + ["currency"] * (1 + len(monedas)) + [None]
    return ref, monedas, headers, formats


def _producto_row(producto, empresa, ref, monedas):
    prices = producto.precios_venta(ref) if empresa_multimoneda(empresa) else {ref: producto.precio_venta}
    return [producto.sku, producto.nombre, producto.marca or "", producto.categoria or "", producto.subcategoria or "", producto.unidad or "pza", int(producto.stock or 0), int(producto.stock_minimo or 0), float(producto.precio_compra or 0), *[float(prices.get(m, 0) or 0) for m in monedas], "Sí" if producto.activo else "No"]


def excel_productos_catalogo_mrl(empresa: Empresa, productos: Iterable, *, usuario=None):
    ref, monedas, headers, formats = _producto_columns(empresa)
    rows = [_producto_row(p, empresa, ref, monedas) for p in productos]
    return _save(empresa, "Catálogo de productos", f"PRODUCTOS-{datetime.now():%Y%m%d}", "Productos", headers, rows, formats, usuario)


def excel_productos_bajo_stock(empresa_id: int, *, usuario=None):
    empresa = Empresa.query.get(empresa_id)
    productos = query_productos_bajo_stock(empresa_id).all()
    ref, monedas, headers, formats = _producto_columns(empresa)
    headers.insert(8, "Faltante")
    formats.insert(8, "integer")
    rows = []
    for p in productos:
        row = _producto_row(p, empresa, ref, monedas)
        row.insert(8, max(0, int(p.stock_minimo or 0) - int(p.stock or 0)))
        rows.append(row)
    return _save(empresa, "Productos con bajo stock", f"BAJO-STOCK-{datetime.now():%Y%m%d}", "Bajo stock", headers, rows, formats, usuario)


def excel_compras_mrl(empresa: Empresa, compras: Iterable, *, usuario=None):
    headers = ["Número", "Recepción", "Factura", "Vencimiento", "Proveedor", "Moneda", "Subtotal", "IVA", "Total", "Pagado", "Saldo", "Estado", "Registros", "Unidades"]
    rows = [[c.numero or f"#{c.id}", c.fecha, c.fecha_factura, c.fecha_vencimiento, c.proveedor.nombre if c.proveedor else "—", c.moneda_factura, float(c.subtotal or 0), float(c.monto_iva or 0), float(c.total or 0), float(c.monto_pagado or 0), c.saldo_pendiente, c.estado_pago_label, len(c.lineas), sum(int(l.cantidad or 0) for l in c.lineas)] for c in compras]
    formats = [None, "date", "date", "date", None, None] + ["currency"] * 5 + [None, "integer", "integer"]
    return _save(empresa, "Historial de compras", f"COMPRAS-{datetime.now():%Y%m%d}", "Compras", headers, rows, formats, usuario)


def excel_ventas_mrl(empresa: Empresa, ventas: Iterable, *, usuario=None):
    headers = ["Número", "Fecha", "Cliente", "Forma de pago", "Estado cobro", "Moneda", "Total", "Cobrado", "Saldo", "Vencimiento", "Registros", "Unidades"]
    rows = [[v.numero or f"#{v.id}", v.fecha, v.cliente.nombre if v.cliente else "—", "Crédito" if v.es_credito else "Contado", v.estado_cobro_label, v.moneda, float(v.total or 0), float(v.monto_cobrado or 0), v.saldo_pendiente, v.fecha_vencimiento, len(v.lineas), sum(int(l.cantidad or 0) for l in v.lineas)] for v in ventas]
    formats = [None, "date", None, None, None, None, "currency", "currency", "currency", "date", "integer", "integer"]
    return _save(empresa, "Historial de ventas", f"VENTAS-{datetime.now():%Y%m%d}", "Ventas", headers, rows, formats, usuario)


__all__ = ["excel_productos_catalogo_mrl", "excel_productos_bajo_stock", "excel_compras_mrl", "excel_ventas_mrl"]
