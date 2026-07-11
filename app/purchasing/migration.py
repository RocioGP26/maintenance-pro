"""Migración idempotente de compras Inventory a trazabilidad Purchasing."""

from __future__ import annotations

from app import db
from app.models import InvCompra, InvProveedor, PurEvento, PurOrdenCompra, PurOrdenEvento, PurOrdenLinea, PurRecepcion, PurRecepcionLinea, PurSolicitud, PurSolicitudLinea, User

LEGACY_PROVIDER_NAME = "Proveedor histórico sin identificar"


def _actor(empresa_id):
    return User.query.filter_by(empresa_id=empresa_id, activo=True).order_by(User.id).first()


def _provider(compra):
    if compra.proveedor:
        return compra.proveedor
    provider = InvProveedor.query.filter_by(empresa_id=compra.empresa_id, nombre=LEGACY_PROVIDER_NAME).first()
    if not provider:
        provider = InvProveedor(empresa_id=compra.empresa_id, nombre=LEGACY_PROVIDER_NAME, observaciones="Creado por migración Sprint 16.5", activo=True)
        db.session.add(provider); db.session.flush()
    return provider


def migrate_legacy_purchases(*, dry_run=True):
    purchases = InvCompra.query.order_by(InvCompra.id).all()
    stats = {"total": len(purchases), "linked": 0, "migrated": 0, "skipped_no_user": 0}
    for compra in purchases:
        if PurRecepcion.query.filter_by(inv_compra_id=compra.id).first():
            stats["linked"] += 1; continue
        actor = _actor(compra.empresa_id)
        if not actor:
            stats["skipped_no_user"] += 1; continue
        if dry_run:
            stats["migrated"] += 1; continue
        provider = _provider(compra)
        request = PurSolicitud(empresa_id=compra.empresa_id, numero=f"SC-LEGACY-{compra.id}", solicitante_id=actor.id, estado="convertida", prioridad="media", justificacion=f"Migración de compra histórica {compra.numero or compra.id}", requerida_para=compra.fecha)
        db.session.add(request); db.session.flush()
        source_lines = list(compra.lineas)
        if not source_lines:
            request.lineas.append(PurSolicitudLinea(descripcion_libre=f"Compra histórica {compra.numero or compra.id}", cantidad=1, unidad="registro", costo_estimado=compra.total))
        else:
            for line in source_lines:
                request.lineas.append(PurSolicitudLinea(producto=line.producto, descripcion_libre="", cantidad=line.cantidad, unidad=line.producto.unidad if line.producto else "pza", costo_estimado=line.precio_unitario))
        db.session.flush()
        order = PurOrdenCompra(empresa_id=compra.empresa_id, numero=f"OC-LEGACY-{compra.id}", solicitud=request, proveedor=provider, creador_id=actor.id, estado="cerrada", moneda=compra.moneda_factura or "COP", subtotal=compra.subtotal or compra.total, monto_iva=compra.monto_iva or 0, total=compra.total or 0, entrega_prevista=compra.fecha, notas="Migrada desde InvCompra; no recalcular stock.", emitida_en=compra.created_at, enviada_en=compra.created_at)
        db.session.add(order); db.session.flush()
        for idx, req_line in enumerate(request.lineas):
            src = source_lines[idx] if idx < len(source_lines) else None
            subtotal = float(src.subtotal or 0) if src else float(compra.subtotal or compra.total or 0)
            iva = float(src.monto_iva or 0) if src else float(compra.monto_iva or 0)
            order.lineas.append(PurOrdenLinea(solicitud_linea=req_line, producto=req_line.producto, descripcion_snapshot=f"{req_line.producto.sku} · {req_line.producto.nombre}" if req_line.producto else req_line.descripcion_libre, unidad=req_line.unidad, cantidad_ordenada=req_line.cantidad, precio_unitario=float(src.precio_unitario or 0) if src else float(compra.total or 0), tasa_iva=float(src.tasa_iva_pct) if src else 0, subtotal=subtotal, monto_iva=iva, total=subtotal + iva))
        db.session.flush()
        receipt = PurRecepcion(empresa_id=compra.empresa_id, numero=f"RC-LEGACY-{compra.id}", orden=order, estado="confirmada", recibido_por_id=actor.id, fecha=compra.fecha, idempotency_key=f"legacy-inv-compra-{compra.id}", documento_proveedor=compra.numero or "", observaciones="Migración histórica sin movimiento de stock.", compra=compra)
        db.session.add(receipt)
        for line in order.lineas:
            receipt.lineas.append(PurRecepcionLinea(orden_linea=line, cantidad_recibida=line.cantidad_ordenada, cantidad_rechazada=0))
        db.session.add_all([
            PurEvento(empresa_id=compra.empresa_id, solicitud=request, evento="legacy_migrated", actor_id=actor.id, estado_anterior=None, estado_nuevo="convertida", detalle=f"InvCompra {compra.id}"),
            PurOrdenEvento(empresa_id=compra.empresa_id, orden=order, evento="legacy_migrated", actor_id=actor.id, estado_anterior=None, estado_nuevo="cerrada", detalle=f"InvCompra {compra.id}"),
        ])
        stats["migrated"] += 1
    if not dry_run:
        db.session.commit()
    return stats
