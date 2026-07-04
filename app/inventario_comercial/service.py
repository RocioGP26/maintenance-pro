"""Datos de ejemplo y KPIs del módulo inventario comercial."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.currency import MONEDAS_VENEZUELA, empresa_multimoneda, monedas_activas_de, set_precios_producto
from app.money import normalizar_moneda
from app.models import (
    Empresa,
    InvCompra,
    InvCompraLinea,
    InvCompraPago,
    InvCliente,
    InvProducto,
    InvProveedor,
    InvVenta,
    InvVentaCobro,
    InvVentaLinea,
)

FORMA_PAGO_CONTADO = "contado"
FORMA_PAGO_CREDITO = "credito"
ESTADO_COBRO_PAGADA = "pagada"
ESTADO_COBRO_PENDIENTE = "pendiente"
ESTADO_COBRO_PARCIAL = "parcial"
ESTADO_PAGO_PAGADA = "pagada"
ESTADO_PAGO_PENDIENTE = "pendiente"
ESTADO_PAGO_PARCIAL = "parcial"


def crear_datos_ejemplo_inventario(empresa_id: int) -> None:
    """Productos, proveedor y ventas de bienvenida (sin FK a mantenimiento)."""
    if InvProducto.query.filter_by(empresa_id=empresa_id).first():
        return

    empresa = Empresa.query.get(empresa_id)
    multimoneda = empresa_multimoneda(empresa)
    moneda_ref = (empresa.moneda if empresa else "USD") or "USD"

    prov = InvProveedor(
        empresa_id=empresa_id,
        nombre="Distribuidora El Surtidor",
        nit="900123456-1",
        contacto_nombre="Ana Mercado",
        contacto_email="compras@elsurtidor.example",
        contacto_telefono="3001234567",
        activo=True,
    )
    db.session.add(prov)
    db.session.flush()

    productos: list[InvProducto] = []
    if multimoneda:
        ejemplos = [
            (
                "SKU-001",
                "Aceite motor 1L",
                "Lubricantes",
                24,
                5,
                {"USD": 8.0, "VES": 290.0, "COP": 32000.0},
                {"USD": 12.0, "VES": 435.0, "COP": 48000.0},
            ),
            (
                "SKU-002",
                "Filtro de aire universal",
                "Repuestos",
                8,
                10,
                {"USD": 15.0, "VES": 545.0, "COP": 60000.0},
                {"USD": 22.0, "VES": 800.0, "COP": 88000.0},
            ),
            (
                "SKU-003",
                "Líquido refrigerante 500ml",
                "Fluidos",
                3,
                8,
                {"USD": 6.0, "VES": 218.0, "COP": 24000.0},
                {"USD": 9.5, "VES": 345.0, "COP": 38000.0},
            ),
        ]
        for sku, nombre, cat, stock, minimo, compra_map, venta_map in ejemplos:
            p = InvProducto(
                empresa_id=empresa_id,
                sku=sku,
                nombre=nombre,
                categoria=cat,
                stock=stock,
                stock_minimo=minimo,
                precio_compra=float(compra_map.get(moneda_ref, 0)),
                precio_venta=float(venta_map.get(moneda_ref, 0)),
                precios_json=json.dumps(venta_map, ensure_ascii=False),
                activo=True,
            )
            db.session.add(p)
            productos.append(p)
    else:
        ejemplos = [
            ("SKU-001", "Aceite motor 1L", "Lubricantes", 24, 5, 8500, 12000),
            ("SKU-002", "Filtro de aire universal", "Repuestos", 8, 10, 15000, 22000),
            ("SKU-003", "Líquido refrigerante 500ml", "Fluidos", 3, 8, 6000, 9500),
        ]
        for sku, nombre, cat, stock, minimo, compra, venta in ejemplos:
            p = InvProducto(
                empresa_id=empresa_id,
                sku=sku,
                nombre=nombre,
                categoria=cat,
                stock=stock,
                stock_minimo=minimo,
                precio_compra=compra,
                precio_venta=venta,
                activo=True,
            )
            db.session.add(p)
            productos.append(p)
    db.session.flush()

    hoy = date.today()
    if multimoneda:
        ventas_demo = [
            (hoy, "USD", [(0, 3), (1, 2)], "V-001"),
            (hoy, "VES", [(0, 2), (2, 1)], "V-002"),
            (hoy - timedelta(days=1), "COP", [(0, 5), (2, 4)], "V-003"),
            (hoy - timedelta(days=2), "USD", [(1, 6), (2, 2)], "V-004"),
        ]
    else:
        ventas_demo = [
            (hoy, moneda_ref, [(0, 3), (1, 2)], "V-001"),
            (hoy - timedelta(days=1), moneda_ref, [(0, 5), (2, 4)], "V-002"),
            (hoy - timedelta(days=2), moneda_ref, [(1, 6), (2, 2)], "V-003"),
        ]

    for fecha, moneda_venta, lineas, numero in ventas_demo:
        total = 0.0
        venta = InvVenta(
            empresa_id=empresa_id,
            numero=numero,
            fecha=fecha,
            moneda=moneda_venta,
            total=0,
        )
        db.session.add(venta)
        db.session.flush()
        for prod_idx, cantidad in lineas:
            prod = productos[prod_idx]
            precio = prod.precio_venta_en(moneda_venta, moneda_ref)
            subtotal = round(precio * cantidad, 2)
            total += subtotal
            db.session.add(
                InvVentaLinea(
                    venta_id=venta.id,
                    producto_id=prod.id,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal,
                )
            )
        venta.total = round(total, 2)


def kpis_dashboard_inventario(empresa_id: int, hoy: date | None = None) -> dict:
    hoy = hoy or date.today()
    inicio_mes = hoy.replace(day=1)

    empresa = Empresa.query.get(empresa_id)
    moneda_ref = (empresa.moneda if empresa else "USD") or "USD"
    multimoneda = empresa_multimoneda(empresa)

    ventas_hoy_rows = (
        db.session.query(
            InvVenta.moneda,
            func.coalesce(func.sum(InvVenta.total), 0),
            func.count(InvVenta.id),
        )
        .filter(InvVenta.empresa_id == empresa_id, InvVenta.fecha == hoy)
        .group_by(InvVenta.moneda)
        .all()
    )
    ventas_hoy_por_moneda = [
        {"moneda": (r[0] or moneda_ref), "total": float(r[1] or 0), "count": int(r[2] or 0)}
        for r in ventas_hoy_rows
    ]
    ventas_hoy_total = sum(v["total"] for v in ventas_hoy_por_moneda if v["moneda"] == moneda_ref)
    ventas_count_hoy = sum(v["count"] for v in ventas_hoy_por_moneda)

    unidades_hoy = (
        db.session.query(func.coalesce(func.sum(InvVentaLinea.cantidad), 0))
        .join(InvVenta, InvVentaLinea.venta_id == InvVenta.id)
        .filter(InvVenta.empresa_id == empresa_id, InvVenta.fecha == hoy)
        .scalar()
    )

    bajo_stock_q = query_productos_bajo_stock(empresa_id)
    bajo_stock_count = bajo_stock_q.count()
    bajo_stock = bajo_stock_q.limit(8).all()

    total_productos = InvProducto.query.filter_by(empresa_id=empresa_id, activo=True).count()

    valor_inventario = (
        db.session.query(
            func.coalesce(func.sum(InvProducto.stock * InvProducto.precio_compra), 0)
        )
        .filter(InvProducto.empresa_id == empresa_id, InvProducto.activo.is_(True))
        .scalar()
    )
    unidades_en_stock = (
        db.session.query(func.coalesce(func.sum(InvProducto.stock), 0))
        .filter(InvProducto.empresa_id == empresa_id, InvProducto.activo.is_(True))
        .scalar()
    )

    top_rows = (
        db.session.query(
            InvProducto.nombre,
            InvProducto.sku,
            func.coalesce(func.sum(InvVentaLinea.cantidad), 0).label("unidades"),
            func.coalesce(func.sum(InvVentaLinea.subtotal), 0).label("ingresos"),
        )
        .join(InvVentaLinea, InvVentaLinea.producto_id == InvProducto.id)
        .join(InvVenta, InvVentaLinea.venta_id == InvVenta.id)
        .filter(
            InvProducto.empresa_id == empresa_id,
            InvVenta.empresa_id == empresa_id,
            InvVenta.fecha >= inicio_mes,
            InvVenta.fecha <= hoy,
        )
        .group_by(InvProducto.id, InvProducto.nombre, InvProducto.sku)
        .order_by(func.sum(InvVentaLinea.cantidad).desc())
        .limit(5)
        .all()
    )
    top_productos = [
        {
            "nombre": r[0],
            "sku": r[1],
            "unidades": int(r[2] or 0),
            "ingresos": float(r[3] or 0),
        }
        for r in top_rows
    ]

    return {
        "ventas_hoy_total": float(ventas_hoy_total or 0),
        "ventas_hoy_count": ventas_count_hoy,
        "ventas_hoy_por_moneda": ventas_hoy_por_moneda,
        "moneda_referencia": moneda_ref,
        "multimoneda": multimoneda,
        "unidades_vendidas_hoy": int(unidades_hoy or 0),
        "bajo_stock": bajo_stock,
        "bajo_stock_count": bajo_stock_count,
        "total_productos": total_productos,
        "valor_inventario": float(valor_inventario or 0),
        "unidades_en_stock": int(unidades_en_stock or 0),
        "top_productos": top_productos,
        "cxp": alertas_cxp_compras(empresa_id, hoy),
    }


CXP_DIAS_ALERTA = 7


def filtro_compras_cxp_alerta(q, alerta: str, hoy: date | None = None):
    """Filtra entradas con vencimiento de cuentas por pagar (misma lógica que la campana)."""
    hoy = hoy or date.today()
    key = (alerta or "").strip().lower()
    if key not in ("por_vencer", "vencidas"):
        return q
    q = q.filter(
        InvCompra.fecha_vencimiento.isnot(None),
        InvCompra.total > 0,
        InvCompra.estado_pago.in_([ESTADO_PAGO_PENDIENTE, ESTADO_PAGO_PARCIAL]),
    )
    if key == "vencidas":
        return q.filter(InvCompra.fecha_vencimiento < hoy)
    limite = hoy + timedelta(days=CXP_DIAS_ALERTA)
    return q.filter(InvCompra.fecha_vencimiento >= hoy, InvCompra.fecha_vencimiento <= limite)


def query_compras_cxp_pendientes(empresa_id: int):
    return InvCompra.query.filter(
        InvCompra.empresa_id == empresa_id,
        InvCompra.total > 0,
        InvCompra.estado_pago.in_([ESTADO_PAGO_PENDIENTE, ESTADO_PAGO_PARCIAL]),
    )


def filtro_cxp_vista(q, *, alerta: str = "", proveedor_id: int | None = None, hoy: date | None = None):
    hoy = hoy or date.today()
    q = q.filter(
        InvCompra.total > 0,
        InvCompra.estado_pago.in_([ESTADO_PAGO_PENDIENTE, ESTADO_PAGO_PARCIAL]),
    )
    if proveedor_id:
        q = q.filter(InvCompra.proveedor_id == proveedor_id)
    key = (alerta or "").strip().lower()
    if key == "vencidas":
        q = q.filter(InvCompra.fecha_vencimiento.isnot(None), InvCompra.fecha_vencimiento < hoy)
    elif key == "por_vencer":
        limite = hoy + timedelta(days=CXP_DIAS_ALERTA)
        q = q.filter(
            InvCompra.fecha_vencimiento.isnot(None),
            InvCompra.fecha_vencimiento >= hoy,
            InvCompra.fecha_vencimiento <= limite,
        )
    return q


def kpis_cxp(empresa_id: int, hoy: date | None = None) -> dict:
    hoy = hoy or date.today()
    base = query_compras_cxp_pendientes(empresa_id)
    pendientes = base.all()
    saldo_total = sum(c.saldo_pendiente for c in pendientes)
    vencidas = [c for c in pendientes if c.fecha_vencimiento and c.fecha_vencimiento < hoy]
    limite = hoy + timedelta(days=CXP_DIAS_ALERTA)
    por_vencer = [
        c
        for c in pendientes
        if c.fecha_vencimiento and hoy <= c.fecha_vencimiento <= limite
    ]
    return {
        "saldo_total": round(saldo_total, 2),
        "facturas_pendientes": len(pendientes),
        "vencidas_count": len(vencidas),
        "por_vencer_count": len(por_vencer),
        "dias_alerta": CXP_DIAS_ALERTA,
    }


def resumen_cxp_por_proveedor(empresa_id: int) -> list[dict]:
    rows = (
        db.session.query(
            InvProveedor.id,
            InvProveedor.nombre,
            func.count(InvCompra.id),
            func.coalesce(func.sum(InvCompra.total - InvCompra.monto_pagado), 0),
        )
        .join(InvCompra, InvCompra.proveedor_id == InvProveedor.id)
        .filter(
            InvProveedor.empresa_id == empresa_id,
            InvCompra.empresa_id == empresa_id,
            InvCompra.estado_pago.in_([ESTADO_PAGO_PENDIENTE, ESTADO_PAGO_PARCIAL]),
            InvCompra.total > 0,
        )
        .group_by(InvProveedor.id, InvProveedor.nombre)
        .order_by(func.sum(InvCompra.total - InvCompra.monto_pagado).desc())
        .all()
    )
    return [
        {
            "proveedor_id": r[0],
            "nombre": r[1],
            "facturas": int(r[2] or 0),
            "saldo": round(float(r[3] or 0), 2),
        }
        for r in rows
    ]


def alertas_cxp_compras(empresa_id: int, hoy: date | None = None) -> dict:
    """Facturas de proveedor con fecha de vencimiento para cuentas por pagar."""
    hoy = hoy or date.today()
    limite = hoy + timedelta(days=CXP_DIAS_ALERTA)
    todas = (
        query_compras_cxp_pendientes(empresa_id)
        .options(joinedload(InvCompra.proveedor))
        .filter(InvCompra.fecha_vencimiento.isnot(None))
        .order_by(InvCompra.fecha_vencimiento.asc())
        .all()
    )
    vencidas = [c for c in todas if c.fecha_vencimiento < hoy]
    por_vencer = [c for c in todas if hoy <= c.fecha_vencimiento <= limite]

    vencidas_por_proveedor: dict[str, int] = {}
    for c in vencidas:
        nombre = c.proveedor.nombre if c.proveedor else "Sin proveedor"
        vencidas_por_proveedor[nombre] = vencidas_por_proveedor.get(nombre, 0) + 1

    return {
        "vencidas": vencidas[:8],
        "por_vencer": por_vencer[:8],
        "vencidas_count": len(vencidas),
        "por_vencer_count": len(por_vencer),
        "vencidas_por_proveedor": sorted(
            vencidas_por_proveedor.items(), key=lambda x: (-x[1], x[0])
        ),
        "dias_alerta": CXP_DIAS_ALERTA,
    }


def query_productos_bajo_stock(empresa_id: int):
    """Productos activos cuyo stock actual es menor o igual al mínimo configurado."""
    return (
        InvProducto.query.filter_by(empresa_id=empresa_id, activo=True)
        .filter(InvProducto.stock <= InvProducto.stock_minimo)
        .order_by(InvProducto.stock.asc(), InvProducto.nombre.asc())
    )


def modulos_desde_preset(preset: str) -> list[str]:
    """Convierte selección del onboarding (mantenimiento / inventario / ambos)."""
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO

    key = (preset or "").strip().lower()
    if key == "ambos":
        return [MODULO_MANTENIMIENTO, MODULO_INVENTARIO]
    if key == "inventario":
        return [MODULO_INVENTARIO]
    return [MODULO_MANTENIMIENTO]


def _parse_float(val, default: float = 0.0) -> float:
    try:
        return float(str(val or "").replace(",", ".").strip() or default)
    except (TypeError, ValueError):
        return default


def _parse_int(val, default: int = 0) -> int:
    try:
        return int(float(str(val or "").strip() or default))
    except (TypeError, ValueError):
        return default


def siguiente_numero_entrada(empresa_id: int) -> str:
    anio = date.today().year
    prefijo = f"ENT-{anio}-"
    ultima = (
        InvCompra.query.filter(
            InvCompra.empresa_id == empresa_id,
            InvCompra.numero.like(f"{prefijo}%"),
        )
        .order_by(InvCompra.id.desc())
        .first()
    )
    if not ultima or not ultima.numero:
        return f"{prefijo}001"
    try:
        seq = int(ultima.numero.rsplit("-", 1)[-1]) + 1
    except ValueError:
        seq = 1
    return f"{prefijo}{seq:03d}"


def ultimo_costo_entrada_producto(empresa_id: int, producto_id: int) -> dict | None:
    """Último costo unitario registrado en una entrada de mercancía para el producto."""
    linea = (
        db.session.query(InvCompraLinea)
        .join(InvCompra, InvCompraLinea.compra_id == InvCompra.id)
        .filter(
            InvCompra.empresa_id == empresa_id,
            InvCompraLinea.producto_id == producto_id,
            InvCompraLinea.precio_unitario > 0,
        )
        .order_by(
            InvCompra.fecha.desc(),
            InvCompra.id.desc(),
            InvCompraLinea.id.desc(),
        )
        .first()
    )
    if not linea:
        return None
    compra = linea.compra
    return {
        "costo": round(float(linea.precio_unitario), 2),
        "fecha": compra.fecha.isoformat() if compra and compra.fecha else None,
        "numero": (compra.numero or "").strip() if compra else "",
    }


def guardar_producto_comercial(
    empresa_id: int,
    datos: dict,
    *,
    producto: InvProducto | None = None,
    permitir_stock_inicial: bool = False,
) -> InvProducto:
    sku = (datos.get("sku") or "").strip()
    nombre = (datos.get("nombre") or "").strip()
    if not sku or not nombre:
        raise ValueError("Referencia y nombre son obligatorios.")

    empresa = Empresa.query.get(empresa_id)
    moneda_ref = (empresa.moneda if empresa else "COP") or "COP"

    if producto is None:
        producto = InvProducto(empresa_id=empresa_id, activo=True)
        if permitir_stock_inicial:
            producto.stock = max(0, _parse_int(datos.get("stock")))
    else:
        if producto.empresa_id != empresa_id:
            raise ValueError("Producto no pertenece a esta empresa.")

    producto.sku = sku
    producto.nombre = nombre
    producto.marca = (datos.get("marca") or "").strip()
    producto.categoria = (datos.get("categoria") or "").strip()
    producto.subcategoria = (datos.get("subcategoria") or "").strip()
    producto.ubicacion = (datos.get("ubicacion") or "").strip()
    producto.unidad = (datos.get("unidad") or "pza").strip() or "pza"
    producto.stock_minimo = max(0, _parse_int(datos.get("stock_minimo")))
    producto.precio_compra = max(0.0, _parse_float(datos.get("precio_compra")))
    producto.activo = datos.get("activo", True) is not False

    if empresa_multimoneda(empresa):
        precios: dict[str, float] = {}
        for moneda in monedas_activas_de(empresa):
            precios[moneda] = max(0.0, _parse_float(datos.get(f"precio_venta_{moneda}")))
        set_precios_producto(producto, precios, moneda_ref)
    else:
        producto.precio_venta = max(0.0, _parse_float(datos.get("precio_venta")))

    db.session.add(producto)
    return producto


def guardar_proveedor_comercial(
    empresa_id: int,
    datos: dict,
    *,
    proveedor: InvProveedor | None = None,
) -> InvProveedor:
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        raise ValueError("El nombre del proveedor es obligatorio.")
    if proveedor is None:
        proveedor = InvProveedor(empresa_id=empresa_id, activo=True)
    elif proveedor.empresa_id != empresa_id:
        raise ValueError("Proveedor no pertenece a esta empresa.")

    proveedor.nombre = nombre
    proveedor.nit = (datos.get("nit") or "").strip()
    proveedor.contacto_nombre = (datos.get("contacto_nombre") or "").strip()
    proveedor.contacto_email = (datos.get("contacto_email") or "").strip()
    proveedor.contacto_telefono = (datos.get("contacto_telefono") or "").strip()
    proveedor.direccion = (datos.get("direccion") or "").strip()
    proveedor.observaciones = (datos.get("observaciones") or "").strip()
    proveedor.activo = datos.get("activo", True) is not False
    db.session.add(proveedor)
    return proveedor


def proveedores_para_entrada(
    empresa_id: int,
    seleccionado_id: int | None = None,
) -> list[InvProveedor]:
    """Proveedores activos; incluye el seleccionado aunque esté inactivo (edición)."""
    items = (
        InvProveedor.query.filter_by(empresa_id=empresa_id, activo=True)
        .order_by(InvProveedor.nombre)
        .all()
    )
    if seleccionado_id and not any(p.id == seleccionado_id for p in items):
        extra = InvProveedor.query.filter_by(id=seleccionado_id, empresa_id=empresa_id).first()
        if extra:
            items = sorted(items + [extra], key=lambda p: (p.nombre or "").lower())
    return items


def guardar_cliente_comercial(
    empresa_id: int,
    datos: dict,
    *,
    cliente: InvCliente | None = None,
) -> InvCliente:
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")
    if cliente is None:
        cliente = InvCliente(empresa_id=empresa_id, activo=True)
    elif cliente.empresa_id != empresa_id:
        raise ValueError("Cliente no pertenece a esta empresa.")

    cliente.nombre = nombre
    cliente.documento = (datos.get("documento") or "").strip()
    cliente.telefono = (datos.get("telefono") or "").strip()
    cliente.email = (datos.get("email") or "").strip()
    cliente.direccion = (datos.get("direccion") or "").strip()
    cliente.notas = (datos.get("notas") or "").strip()
    cliente.activo = datos.get("activo", True) is not False
    db.session.add(cliente)
    return cliente


def clientes_para_select(empresa_id: int) -> list[InvCliente]:
    return (
        InvCliente.query.filter_by(empresa_id=empresa_id, activo=True)
        .order_by(InvCliente.nombre)
        .all()
    )


def moneda_base_empresa(empresa_id: int) -> str:
    empresa = Empresa.query.get(empresa_id)
    return normalizar_moneda((empresa.moneda if empresa else None) or "COP")


def monedas_opciones_factura(empresa_id: int, *, incluir: str | None = None) -> list[str]:
    """Monedas para factura de proveedor: activas de la empresa + USD/VES/COP habituales."""
    empresa = Empresa.query.get(empresa_id)
    base = moneda_base_empresa(empresa_id)
    opciones: list[str] = []
    for m in list(dict.fromkeys(monedas_activas_de(empresa))) + list(MONEDAS_VENEZUELA):
        cod = normalizar_moneda(m, base)
        if cod not in opciones:
            opciones.append(cod)
    if incluir:
        extra = normalizar_moneda(incluir, base)
        if extra not in opciones:
            opciones.append(extra)
    if base in opciones:
        opciones.remove(base)
    orden_pref = {"USD": 1, "VES": 2, "COP": 3}
    opciones.sort(key=lambda x: orden_pref.get(x, 50))
    opciones.insert(0, base)
    return opciones


def parse_moneda_factura_entrada(form, moneda_base: str) -> tuple[str, float]:
    moneda = normalizar_moneda((form.get("moneda_factura") if hasattr(form, "get") else "") or moneda_base)
    tasa = max(0.0, _parse_float(form.get("tasa_cambio") if hasattr(form, "get") else 1, 1.0))
    if moneda == moneda_base:
        return moneda, 1.0
    if tasa <= 0:
        raise ValueError(
            f"Indica la tasa de cambio (1 {moneda} = cuántos {moneda_base}) cuando la factura no está en {moneda_base}."
        )
    return moneda, tasa


def precio_factura_a_base(
    precio_factura: float,
    *,
    moneda_factura: str,
    moneda_base: str,
    tasa: float,
) -> float:
    if moneda_factura == moneda_base:
        return round(float(precio_factura), 2)
    return round(float(precio_factura) * float(tasa), 2)


def precio_base_a_factura(
    precio_base: float,
    *,
    moneda_factura: str,
    moneda_base: str,
    tasa: float,
) -> float:
    if moneda_factura == moneda_base or tasa <= 0:
        return round(float(precio_base), 4)
    return round(float(precio_base) / float(tasa), 4)


def parse_lineas_entrada_form(
    form,
    *,
    moneda_factura: str,
    moneda_base: str,
    tasa: float,
) -> list[dict]:
    producto_ids = form.getlist("linea_producto_id")
    cantidades = form.getlist("linea_cantidad")
    precios = form.getlist("linea_precio")
    marcas = form.getlist("linea_marca")
    lineas: list[dict] = []
    for i, pid in enumerate(producto_ids):
        pid_str = (pid or "").strip()
        if not pid_str:
            continue
        cantidad = _parse_int(cantidades[i] if i < len(cantidades) else 0)
        if cantidad <= 0:
            continue
        precio_factura = max(0.0, _parse_float(precios[i] if i < len(precios) else 0))
        precio_base = precio_factura_a_base(
            precio_factura,
            moneda_factura=moneda_factura,
            moneda_base=moneda_base,
            tasa=tasa,
        )
        lineas.append(
            {
                "producto_id": int(pid_str),
                "cantidad": cantidad,
                "precio_unitario": precio_base,
                "marca": (marcas[i] if i < len(marcas) else "").strip(),
            }
        )
    return lineas


def _lineas_iniciales_entrada_json(compra: InvCompra | None, moneda_base: str) -> list[dict]:
    if not compra:
        return []
    moneda_f = normalizar_moneda(compra.moneda_factura or moneda_base)
    tasa = float(compra.tasa_cambio or 1.0)
    filas: list[dict] = []
    for l in compra.lineas:
        precio_base = float(l.precio_unitario or 0)
        filas.append(
            {
                "producto_id": l.producto_id,
                "cantidad": int(l.cantidad or 0),
                "precio_unitario": precio_base_a_factura(
                    precio_base,
                    moneda_factura=moneda_f,
                    moneda_base=moneda_base,
                    tasa=tasa,
                ),
                "marca": l.marca or "",
            }
        )
    return filas


IVA_ENTRADA_TASA = 0.19


def parse_tipo_iva_entrada(form) -> str:
    raw = (form.get("tipo_iva") if hasattr(form, "get") else "exento") or "exento"
    return "con_iva" if str(raw).strip().lower() == "con_iva" else "exento"


def calcular_totales_entrada(subtotal_lineas: float, tipo_iva: str) -> tuple[float, float, float]:
    sub = round(float(subtotal_lineas), 2)
    if tipo_iva == "con_iva":
        iva = round(sub * IVA_ENTRADA_TASA, 2)
    else:
        iva = 0.0
    return sub, iva, round(sub + iva, 2)


def _asignar_totales_compra(compra: InvCompra, subtotal_lineas: float, tipo_iva: str) -> None:
    sub, iva, total = calcular_totales_entrada(subtotal_lineas, tipo_iva)
    compra.tipo_iva = tipo_iva
    compra.subtotal = sub
    compra.monto_iva = iva
    compra.total = total
    compra.estado_pago = _calcular_estado_pago(total, float(compra.monto_pagado or 0))


def registrar_entrada_mercancia(
    empresa_id: int,
    *,
    proveedor_id: int | None,
    fecha: date,
    numero: str,
    notas: str,
    lineas: list[dict],
    moneda_factura: str,
    moneda_base: str,
    tasa_cambio: float,
    tipo_iva: str = "exento",
    fecha_factura: date | None = None,
    fecha_vencimiento: date | None = None,
) -> InvCompra:
    if not lineas:
        raise ValueError("Agrega al menos un producto con cantidad mayor a cero.")

    if proveedor_id:
        prov = InvProveedor.query.filter_by(id=proveedor_id, empresa_id=empresa_id).first()
        if not prov:
            raise ValueError("Proveedor no válido.")

    compra = InvCompra(
        empresa_id=empresa_id,
        proveedor_id=proveedor_id,
        numero=(numero or "").strip() or siguiente_numero_entrada(empresa_id),
        fecha=fecha,
        fecha_factura=fecha_factura,
        fecha_vencimiento=fecha_vencimiento,
        notas=(notas or "").strip(),
        moneda_factura=normalizar_moneda(moneda_factura),
        tasa_cambio=float(tasa_cambio) if moneda_factura != moneda_base else 1.0,
        total=0.0,
        estado_pago=ESTADO_PAGO_PENDIENTE,
        monto_pagado=0.0,
    )
    db.session.add(compra)
    db.session.flush()

    total = 0.0
    for linea in lineas:
        producto = InvProducto.query.filter_by(
            id=linea["producto_id"], empresa_id=empresa_id, activo=True
        ).first()
        if not producto:
            raise ValueError("Uno de los productos seleccionados no existe.")
        cantidad = int(linea["cantidad"])
        precio = float(linea["precio_unitario"])
        marca = (linea.get("marca") or "").strip()
        subtotal = round(cantidad * precio, 2)
        total += subtotal
        db.session.add(
            InvCompraLinea(
                compra_id=compra.id,
                producto_id=producto.id,
                marca=marca,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )
        )
        producto.stock = int(producto.stock or 0) + cantidad
        if precio > 0:
            producto.precio_compra = precio
        if marca:
            producto.marca = marca

    _asignar_totales_compra(compra, total, tipo_iva)
    return compra


def actualizar_entrada_mercancia(
    empresa_id: int,
    compra_id: int,
    *,
    proveedor_id: int | None,
    fecha: date,
    numero: str,
    notas: str,
    lineas: list[dict],
    moneda_factura: str,
    moneda_base: str,
    tasa_cambio: float,
    tipo_iva: str = "exento",
    fecha_factura: date | None = None,
    fecha_vencimiento: date | None = None,
) -> InvCompra:
    compra = InvCompra.query.filter_by(id=compra_id, empresa_id=empresa_id).first()
    if not compra:
        raise ValueError("Entrada no encontrada.")
    if not lineas:
        raise ValueError("Agrega al menos un producto con cantidad mayor a cero.")

    if proveedor_id:
        prov = InvProveedor.query.filter_by(id=proveedor_id, empresa_id=empresa_id).first()
        if not prov:
            raise ValueError("Proveedor no válido.")

    for linea_old in list(compra.lineas):
        producto = InvProducto.query.filter_by(
            id=linea_old.producto_id, empresa_id=empresa_id
        ).first()
        if producto:
            producto.stock = max(0, int(producto.stock or 0) - int(linea_old.cantidad or 0))
        db.session.delete(linea_old)
    db.session.flush()

    compra.proveedor_id = proveedor_id
    compra.fecha = fecha
    compra.fecha_factura = fecha_factura
    compra.fecha_vencimiento = fecha_vencimiento
    compra.moneda_factura = normalizar_moneda(moneda_factura)
    compra.tasa_cambio = float(tasa_cambio) if moneda_factura != moneda_base else 1.0
    if (numero or "").strip():
        compra.numero = (numero or "").strip()
    compra.notas = (notas or "").strip()

    total = 0.0
    for linea in lineas:
        producto = InvProducto.query.filter_by(id=linea["producto_id"], empresa_id=empresa_id).first()
        if not producto:
            raise ValueError("Uno de los productos seleccionados no existe.")
        if not producto.activo:
            raise ValueError(f"El producto «{producto.nombre}» está inactivo.")
        cantidad = int(linea["cantidad"])
        precio = float(linea["precio_unitario"])
        marca = (linea.get("marca") or "").strip()
        subtotal = round(cantidad * precio, 2)
        total += subtotal
        db.session.add(
            InvCompraLinea(
                compra_id=compra.id,
                producto_id=producto.id,
                marca=marca,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )
        )
        producto.stock = int(producto.stock or 0) + cantidad
        if precio > 0:
            producto.precio_compra = precio
        if marca:
            producto.marca = marca

    _asignar_totales_compra(compra, total, tipo_iva)
    return compra


def productos_para_select(empresa_id: int) -> list[InvProducto]:
    return (
        InvProducto.query.filter_by(empresa_id=empresa_id, activo=True)
        .order_by(InvProducto.nombre)
        .all()
    )


def siguiente_numero_venta(empresa_id: int) -> str:
    anio = date.today().year
    prefijo = f"VTA-{anio}-"
    ultima = (
        InvVenta.query.filter(
            InvVenta.empresa_id == empresa_id,
            InvVenta.numero.like(f"{prefijo}%"),
        )
        .order_by(InvVenta.id.desc())
        .first()
    )
    if not ultima or not ultima.numero:
        return f"{prefijo}001"
    try:
        seq = int(ultima.numero.rsplit("-", 1)[-1]) + 1
    except ValueError:
        seq = 1
    return f"{prefijo}{seq:03d}"


def productos_pos_json(empresa_id: int) -> list[dict]:
    empresa = Empresa.query.get(empresa_id)
    moneda_ref = (empresa.moneda if empresa else "COP") or "COP"
    monedas = monedas_activas_de(empresa)
    items: list[dict] = []
    for p in productos_para_select(empresa_id):
        precios = {m: float(p.precio_venta_en(m, moneda_ref)) for m in monedas}
        items.append(
            {
                "id": p.id,
                "sku": p.sku,
                "nombre": p.nombre,
                "marca": p.marca or "",
                "stock": int(p.stock or 0),
                "precios": precios,
                "precio": float(p.precio_venta_en(moneda_ref, moneda_ref)),
            }
        )
    return items


def productos_entrada_json(
    empresa_id: int,
    incluir_ids: list[int] | None = None,
) -> list[dict]:
    """Catálogo para búsqueda en registrar entrada (referencia / nombre)."""
    vistos: set[int] = set()
    items: list[dict] = []

    def _append(p: InvProducto) -> None:
        if p.id in vistos:
            return
        vistos.add(p.id)
        items.append(
            {
                "id": p.id,
                "sku": p.sku,
                "nombre": p.nombre,
                "marca": p.marca or "",
                "stock": int(p.stock or 0),
                "precio_compra": float(p.precio_compra or 0),
            }
        )

    for p in productos_para_select(empresa_id):
        _append(p)
    for pid in incluir_ids or []:
        if pid in vistos:
            continue
        p = InvProducto.query.filter_by(id=pid, empresa_id=empresa_id).first()
        if p:
            _append(p)
    return items


def parse_lineas_venta_form(form) -> list[dict]:
    producto_ids = form.getlist("linea_producto_id")
    cantidades = form.getlist("linea_cantidad")
    precios = form.getlist("linea_precio")
    lineas: list[dict] = []
    for i, pid in enumerate(producto_ids):
        pid_str = (pid or "").strip()
        if not pid_str:
            continue
        cantidad = _parse_int(cantidades[i] if i < len(cantidades) else 0)
        if cantidad <= 0:
            continue
        lineas.append(
            {
                "producto_id": int(pid_str),
                "cantidad": cantidad,
                "precio_unitario": max(0.0, _parse_float(precios[i] if i < len(precios) else 0)),
            }
        )
    return lineas


def _calcular_estado_cobro(total: float, monto_cobrado: float) -> str:
    total = round(float(total or 0), 2)
    cobrado = round(float(monto_cobrado or 0), 2)
    if total <= 0 or cobrado >= total:
        return ESTADO_COBRO_PAGADA
    if cobrado <= 0:
        return ESTADO_COBRO_PENDIENTE
    return ESTADO_COBRO_PARCIAL


def _parse_fecha_opcional(val) -> date | None:
    raw = (val or "").strip() if isinstance(val, str) else val
    if not raw:
        return None
    if isinstance(raw, date):
        return raw
    try:
        return datetime.strptime(str(raw), "%Y-%m-%d").date()
    except ValueError:
        return None


def _calcular_estado_pago(total: float, monto_pagado: float) -> str:
    return _calcular_estado_cobro(total, monto_pagado)


def registrar_pago_compra(
    compra: InvCompra,
    *,
    monto: float,
    fecha: date,
    cuenta_origen: str = "",
    numero_comprobante: str = "",
    notas: str = "",
) -> InvCompraPago:
    if compra.estado_pago == ESTADO_PAGO_PAGADA:
        raise ValueError("Esta factura ya está pagada.")
    monto = round(float(monto), 2)
    if monto <= 0:
        raise ValueError("Indica un monto de pago mayor a cero.")
    saldo = compra.saldo_pendiente
    if monto > saldo + 0.01:
        raise ValueError(f"El pago ({monto}) supera el saldo pendiente ({saldo}).")
    pago = InvCompraPago(
        compra_id=compra.id,
        monto=monto,
        fecha=fecha,
        cuenta_origen=(cuenta_origen or "").strip(),
        numero_comprobante=(numero_comprobante or "").strip(),
        notas=(notas or "").strip(),
    )
    db.session.add(pago)
    compra.monto_pagado = round(float(compra.monto_pagado or 0) + monto, 2)
    compra.estado_pago = _calcular_estado_pago(compra.total, compra.monto_pagado)
    return pago


def registrar_abono_venta(
    venta: InvVenta,
    *,
    monto: float,
    fecha: date,
    notas: str = "",
) -> InvVentaCobro:
    if not venta.es_credito and venta.estado_cobro == ESTADO_COBRO_PAGADA:
        raise ValueError("Esta venta ya está pagada.")
    monto = round(float(monto), 2)
    if monto <= 0:
        raise ValueError("Indica un monto de abono mayor a cero.")
    saldo = venta.saldo_pendiente
    if monto > saldo + 0.01:
        raise ValueError(
            f"El abono ({monto}) supera el saldo pendiente ({saldo})."
        )
    cobro = InvVentaCobro(
        venta_id=venta.id,
        monto=monto,
        fecha=fecha,
        notas=(notas or "").strip(),
    )
    db.session.add(cobro)
    venta.monto_cobrado = round(float(venta.monto_cobrado or 0) + monto, 2)
    venta.estado_cobro = _calcular_estado_cobro(venta.total, venta.monto_cobrado)
    return cobro


def registrar_venta(
    empresa_id: int,
    *,
    fecha: date,
    numero: str,
    moneda: str,
    notas: str,
    lineas: list[dict],
    cliente_id: int | None = None,
    forma_pago: str = FORMA_PAGO_CONTADO,
    monto_abono_inicial: float = 0.0,
    fecha_vencimiento: date | None = None,
) -> InvVenta:
    from app.money import normalizar_moneda

    if not lineas:
        raise ValueError("Agrega al menos un producto con cantidad mayor a cero.")

    empresa = Empresa.query.get(empresa_id)
    moneda_ref = normalizar_moneda(empresa.moneda if empresa else "COP")
    moneda_venta = normalizar_moneda(moneda or moneda_ref, moneda_ref)
    if empresa_multimoneda(empresa):
        activas = monedas_activas_de(empresa)
        if moneda_venta not in activas:
            raise ValueError("Selecciona una moneda válida para la venta.")
    else:
        moneda_venta = moneda_ref

    if cliente_id:
        cliente = InvCliente.query.filter_by(
            id=cliente_id, empresa_id=empresa_id, activo=True
        ).first()
        if not cliente:
            raise ValueError("Cliente no válido.")

    fp = (forma_pago or FORMA_PAGO_CONTADO).strip().lower()
    if fp not in (FORMA_PAGO_CONTADO, FORMA_PAGO_CREDITO):
        fp = FORMA_PAGO_CONTADO
    if fp == FORMA_PAGO_CREDITO and not cliente_id:
        raise ValueError("La venta a crédito requiere seleccionar un cliente.")

    venta = InvVenta(
        empresa_id=empresa_id,
        cliente_id=cliente_id,
        numero=(numero or "").strip() or siguiente_numero_venta(empresa_id),
        fecha=fecha,
        moneda=moneda_venta,
        notas=(notas or "").strip(),
        forma_pago=fp,
        fecha_vencimiento=fecha_vencimiento if fp == FORMA_PAGO_CREDITO else None,
        total=0.0,
        monto_cobrado=0.0,
        estado_cobro=ESTADO_COBRO_PENDIENTE,
    )
    db.session.add(venta)
    db.session.flush()

    total = 0.0
    for linea in lineas:
        producto = InvProducto.query.filter_by(
            id=linea["producto_id"], empresa_id=empresa_id, activo=True
        ).first()
        if not producto:
            raise ValueError("Uno de los productos seleccionados no existe o está inactivo.")
        cantidad = int(linea["cantidad"])
        stock_actual = int(producto.stock or 0)
        if cantidad > stock_actual:
            raise ValueError(
                f"Stock insuficiente para «{producto.nombre}»: hay {stock_actual}, "
                f"se intentaron vender {cantidad}."
            )
        precio = float(linea["precio_unitario"])
        if precio <= 0:
            precio = float(producto.precio_venta_en(moneda_venta, moneda_ref))
        if precio <= 0:
            raise ValueError(f"Indica el precio de venta para «{producto.nombre}».")
        subtotal = round(cantidad * precio, 2)
        total += subtotal
        db.session.add(
            InvVentaLinea(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal,
            )
        )
        producto.stock = stock_actual - cantidad

    venta.total = round(total, 2)
    if fp == FORMA_PAGO_CONTADO:
        venta.monto_cobrado = venta.total
        venta.estado_cobro = ESTADO_COBRO_PAGADA
    else:
        abono = max(0.0, min(round(float(monto_abono_inicial or 0), 2), venta.total))
        venta.monto_cobrado = abono
        venta.estado_cobro = _calcular_estado_cobro(venta.total, abono)
        if abono > 0:
            db.session.add(
                InvVentaCobro(
                    venta_id=venta.id,
                    monto=abono,
                    fecha=fecha,
                    notas="Abono inicial",
                )
            )
    return venta
