"""Comandos de solicitudes Purchasing · Sprint 16.1."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from sqlalchemy import func

from app import db
from app.models import InvProducto, InvProveedor, PurEvento, PurOrdenCompra, PurOrdenEvento, PurOrdenLinea, PurSolicitud, PurSolicitudLinea

ESTADOS = ("borrador", "enviada", "aprobada", "rechazada", "cancelada", "convertida")
PRIORIDADES = (("baja", "Baja"), ("media", "Media"), ("alta", "Alta"), ("critica", "Crítica"))


def siguiente_numero(empresa_id: int) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"SC-{year}-"
    last = db.session.query(func.max(PurSolicitud.numero)).filter(
        PurSolicitud.empresa_id == empresa_id, PurSolicitud.numero.like(f"{prefix}%")
    ).scalar()
    seq = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


def _evento(solicitud, actor_id, evento, anterior, nuevo, detalle=""):
    db.session.add(PurEvento(empresa_id=solicitud.empresa_id, solicitud=solicitud, evento=evento, actor_id=actor_id, estado_anterior=anterior, estado_nuevo=nuevo, detalle=(detalle or "").strip()))


def guardar_solicitud(empresa_id: int, actor_id: int, datos, lineas: list[dict], solicitud=None):
    if solicitud and solicitud.empresa_id != empresa_id:
        raise ValueError("Solicitud no disponible.")
    if solicitud and solicitud.estado != "borrador":
        raise ValueError("Solo se puede editar una solicitud en borrador.")
    justificacion = (datos.get("justificacion") or "").strip()
    if not justificacion:
        raise ValueError("Explica por qué se necesita la compra.")
    parsed = []
    for item in lineas:
        producto_id = item.get("producto_id") or None
        descripcion = (item.get("descripcion_libre") or "").strip()
        try:
            cantidad = float(item.get("cantidad") or 0)
            costo = float(item["costo_estimado"]) if item.get("costo_estimado") not in (None, "") else None
        except (TypeError, ValueError):
            raise ValueError("Cantidad o costo estimado inválido.")
        producto = None
        if producto_id:
            producto = InvProducto.query.filter_by(id=int(producto_id), empresa_id=empresa_id).first()
            if not producto:
                raise ValueError("Uno de los productos no pertenece a tu empresa.")
        if not producto and not descripcion:
            continue
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        parsed.append((producto, descripcion, cantidad, (item.get("unidad") or getattr(producto, "unidad", None) or "pza").strip(), costo))
    if not parsed:
        raise ValueError("Agrega al menos una línea válida.")
    if solicitud is None:
        solicitud = PurSolicitud(empresa_id=empresa_id, numero=siguiente_numero(empresa_id), solicitante_id=actor_id)
        db.session.add(solicitud)
        _evento(solicitud, actor_id, "creada", None, "borrador")
    else:
        solicitud.lineas.clear()
    solicitud.justificacion = justificacion
    solicitud.prioridad = datos.get("prioridad") if datos.get("prioridad") in dict(PRIORIDADES) else "media"
    solicitud.requerida_para = datos.get("requerida_para") or None
    for producto, descripcion, cantidad, unidad, costo in parsed:
        solicitud.lineas.append(PurSolicitudLinea(producto=producto, descripcion_libre=descripcion, cantidad=cantidad, unidad=unidad, costo_estimado=costo))
    return solicitud


def transicionar(solicitud, actor_id: int, nuevo: str, *, detalle=""):
    allowed = {("borrador", "enviada"), ("enviada", "aprobada"), ("enviada", "rechazada"), ("borrador", "cancelada"), ("enviada", "cancelada")}
    anterior = solicitud.estado
    if (anterior, nuevo) not in allowed:
        raise ValueError(f"No se puede cambiar de {anterior} a {nuevo}.")
    if nuevo == "rechazada" and not (detalle or "").strip():
        raise ValueError("Indica el motivo del rechazo.")
    solicitud.estado = nuevo
    if nuevo in ("aprobada", "rechazada"):
        solicitud.aprobador_id = actor_id
        solicitud.decision_en = datetime.now(timezone.utc).replace(tzinfo=None)
        solicitud.motivo_decision = (detalle or "").strip()
    _evento(solicitud, actor_id, nuevo, anterior, nuevo, detalle)
    return solicitud


def siguiente_numero_oc(empresa_id: int) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"OC-{year}-"
    last = db.session.query(func.max(PurOrdenCompra.numero)).filter(PurOrdenCompra.empresa_id == empresa_id, PurOrdenCompra.numero.like(f"{prefix}%")).scalar()
    seq = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


def _decimal(value, label):
    try:
        result = Decimal(str(value or 0))
    except InvalidOperation:
        raise ValueError(f"{label} inválido.")
    if result < 0:
        raise ValueError(f"{label} no puede ser negativo.")
    return result


def _orden_evento(orden, actor_id, evento, anterior, nuevo, detalle=""):
    db.session.add(PurOrdenEvento(empresa_id=orden.empresa_id, orden=orden, evento=evento, actor_id=actor_id, estado_anterior=anterior, estado_nuevo=nuevo, detalle=(detalle or "").strip()))


def crear_orden_desde_solicitud(empresa_id: int, actor_id: int, solicitud, datos, precios: dict[int, tuple]):
    if solicitud.empresa_id != empresa_id or solicitud.estado != "aprobada":
        raise ValueError("Solo una solicitud aprobada puede convertirse en orden.")
    if solicitud.orden_compra:
        raise ValueError("La solicitud ya tiene una orden de compra.")
    proveedor = InvProveedor.query.filter_by(id=int(datos.get("proveedor_id") or 0), empresa_id=empresa_id, activo=True).first()
    if not proveedor:
        raise ValueError("Selecciona un proveedor válido.")
    orden = PurOrdenCompra(empresa_id=empresa_id, numero=siguiente_numero_oc(empresa_id), solicitud=solicitud, proveedor=proveedor, creador_id=actor_id, moneda=(datos.get("moneda") or "COP").strip().upper()[:8], entrega_prevista=datos.get("entrega_prevista") or None, direccion_entrega=(datos.get("direccion_entrega") or "").strip(), condiciones_pago=(datos.get("condiciones_pago") or "").strip(), notas=(datos.get("notas") or "").strip())
    db.session.add(orden)
    total_sub = Decimal("0"); total_iva = Decimal("0")
    for line in solicitud.lineas:
        precio_raw, tasa_raw = precios.get(line.id, (None, None))
        precio = _decimal(precio_raw, "Precio unitario")
        tasa = _decimal(tasa_raw, "Tasa IVA")
        if tasa > 100:
            raise ValueError("La tasa IVA no puede superar 100%.")
        cantidad = Decimal(str(line.cantidad))
        subtotal = (cantidad * precio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        iva = (subtotal * tasa / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_sub += subtotal; total_iva += iva
        descripcion = f"{line.producto.sku} · {line.producto.nombre}" if line.producto else line.descripcion_libre
        orden.lineas.append(PurOrdenLinea(solicitud_linea=line, producto=line.producto, descripcion_snapshot=descripcion, unidad=line.unidad, cantidad_ordenada=float(cantidad), precio_unitario=float(precio), tasa_iva=float(tasa), subtotal=float(subtotal), monto_iva=float(iva), total=float(subtotal + iva)))
    orden.subtotal = float(total_sub); orden.monto_iva = float(total_iva); orden.total = float(total_sub + total_iva)
    solicitud.estado = "convertida"
    _evento(solicitud, actor_id, "convertida", "aprobada", "convertida", orden.numero)
    _orden_evento(orden, actor_id, "creada", None, "borrador", solicitud.numero)
    return orden


def transicionar_orden(orden, actor_id: int, nuevo: str):
    allowed = {("borrador", "emitida"), ("emitida", "enviada"), ("borrador", "cancelada"), ("emitida", "cancelada")}
    anterior = orden.estado
    if (anterior, nuevo) not in allowed:
        raise ValueError(f"No se puede cambiar la OC de {anterior} a {nuevo}.")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    orden.estado = nuevo
    if nuevo == "emitida": orden.emitida_en = now
    if nuevo == "enviada": orden.enviada_en = now
    _orden_evento(orden, actor_id, nuevo, anterior, nuevo)
    return orden
