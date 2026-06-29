"""Datos de ejemplo y KPIs del módulo inventario comercial."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from sqlalchemy import func

from app import db
from app.currency import MONEDAS_VENEZUELA, empresa_multimoneda, monedas_activas_de, set_precios_producto
from app.models import (
    Empresa,
    InvCompra,
    InvCompraLinea,
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
        "top_productos": top_productos,
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


def parse_lineas_entrada_form(form) -> list[dict]:
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
        lineas.append(
            {
                "producto_id": int(pid_str),
                "cantidad": cantidad,
                "precio_unitario": max(0.0, _parse_float(precios[i] if i < len(precios) else 0)),
                "marca": (marcas[i] if i < len(marcas) else "").strip(),
            }
        )
    return lineas


def registrar_entrada_mercancia(
    empresa_id: int,
    *,
    proveedor_id: int | None,
    fecha: date,
    numero: str,
    notas: str,
    lineas: list[dict],
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
        notas=(notas or "").strip(),
        total=0.0,
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

    compra.total = round(total, 2)
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
