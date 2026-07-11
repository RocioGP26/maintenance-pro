"""UI Purchasing · solicitudes Sprint 16.1."""

from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app import db
from app.models import InvProducto, InvProveedor, PurOrdenCompra, PurRecepcion, PurSolicitud
from app.module_guard import require_module
from app.modules import MODULO_INVENTARIO
from app.permissions import can_approve_purchase_request, can_receive_purchasing
from app.purchasing.service import PRIORIDADES, crear_orden_desde_solicitud, guardar_solicitud, registrar_recepcion, transicionar, transicionar_orden

purchasing_bp = Blueprint("purchasing", __name__, url_prefix="/purchasing")


def _empresa_id():
    return getattr(current_user, "empresa_id", None)


def _query():
    return PurSolicitud.query.filter_by(empresa_id=_empresa_id())


def _get_or_404(id):
    return _query().options(joinedload(PurSolicitud.lineas), joinedload(PurSolicitud.solicitante), joinedload(PurSolicitud.aprobador), joinedload(PurSolicitud.eventos)).filter_by(id=id).first_or_404()


def _lineas_form():
    productos = request.form.getlist("producto_id")
    descripciones = request.form.getlist("descripcion_libre")
    cantidades = request.form.getlist("cantidad")
    unidades = request.form.getlist("unidad")
    costos = request.form.getlist("costo_estimado")
    width = max(len(productos), len(descripciones), len(cantidades), 0)
    return [{"producto_id": productos[i] if i < len(productos) else "", "descripcion_libre": descripciones[i] if i < len(descripciones) else "", "cantidad": cantidades[i] if i < len(cantidades) else "", "unidad": unidades[i] if i < len(unidades) else "pza", "costo_estimado": costos[i] if i < len(costos) else ""} for i in range(width)]


def _fecha(raw):
    try:
        return datetime.strptime((raw or "").strip(), "%Y-%m-%d").date() if raw else None
    except ValueError:
        raise ValueError("La fecha requerida no es válida.")


@purchasing_bp.route("/solicitudes")
@login_required
@require_module(MODULO_INVENTARIO)
def solicitudes_list():
    estado = (request.args.get("estado") or "").strip().lower()
    query = _query().options(joinedload(PurSolicitud.solicitante))
    if estado:
        query = query.filter_by(estado=estado)
    items = query.order_by(PurSolicitud.created_at.desc()).all()
    return render_template("purchasing/solicitudes_list.html", items=items, estado=estado)


@purchasing_bp.route("/solicitudes/nueva", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def solicitudes_new():
    if request.method == "POST":
        try:
            datos = dict(request.form)
            datos["requerida_para"] = _fecha(request.form.get("requerida_para"))
            item = guardar_solicitud(_empresa_id(), current_user.id, datos, _lineas_form())
            db.session.commit()
            flash(f"Solicitud {item.numero} guardada como borrador.", "success")
            return redirect(url_for("purchasing.solicitudes_detail", id=item.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    productos = InvProducto.query.filter_by(empresa_id=_empresa_id(), activo=True).order_by(InvProducto.nombre).all()
    return render_template("purchasing/solicitud_form.html", solicitud=None, productos=productos, prioridades=PRIORIDADES)


@purchasing_bp.route("/solicitudes/<int:id>/editar", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def solicitudes_edit(id):
    item = _get_or_404(id)
    if item.solicitante_id != current_user.id and not can_approve_purchase_request(current_user):
        flash("Solo el solicitante puede editar este borrador.", "warning")
        return redirect(url_for("purchasing.solicitudes_detail", id=id))
    if request.method == "POST":
        try:
            datos = dict(request.form)
            datos["requerida_para"] = _fecha(request.form.get("requerida_para"))
            guardar_solicitud(_empresa_id(), current_user.id, datos, _lineas_form(), item)
            db.session.commit()
            flash("Solicitud actualizada.", "success")
            return redirect(url_for("purchasing.solicitudes_detail", id=id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    productos = InvProducto.query.filter_by(empresa_id=_empresa_id(), activo=True).order_by(InvProducto.nombre).all()
    return render_template("purchasing/solicitud_form.html", solicitud=item, productos=productos, prioridades=PRIORIDADES)


@purchasing_bp.route("/solicitudes/<int:id>")
@login_required
@require_module(MODULO_INVENTARIO)
def solicitudes_detail(id):
    return render_template("purchasing/solicitud_detail.html", solicitud=_get_or_404(id), puede_aprobar=can_approve_purchase_request(current_user))


@purchasing_bp.route("/solicitudes/<int:id>/<accion>", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def solicitudes_transition(id, accion):
    item = _get_or_404(id)
    targets = {"enviar": "enviada", "aprobar": "aprobada", "rechazar": "rechazada", "cancelar": "cancelada"}
    nuevo = targets.get(accion)
    if not nuevo:
        return redirect(url_for("purchasing.solicitudes_detail", id=id))
    if nuevo in ("aprobada", "rechazada") and not can_approve_purchase_request(current_user):
        flash("No tienes permiso para decidir solicitudes.", "danger")
        return redirect(url_for("purchasing.solicitudes_detail", id=id))
    if nuevo in ("enviada", "cancelada") and item.solicitante_id != current_user.id and not can_approve_purchase_request(current_user):
        flash("No tienes permiso para cambiar esta solicitud.", "danger")
        return redirect(url_for("purchasing.solicitudes_detail", id=id))
    try:
        transicionar(item, current_user.id, nuevo, detalle=request.form.get("motivo", ""))
        db.session.commit()
        flash(f"Solicitud {nuevo}.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("purchasing.solicitudes_detail", id=id))


def _orden_query():
    return PurOrdenCompra.query.filter_by(empresa_id=_empresa_id())


def _orden_or_404(id):
    return _orden_query().options(joinedload(PurOrdenCompra.lineas), joinedload(PurOrdenCompra.proveedor), joinedload(PurOrdenCompra.solicitud), joinedload(PurOrdenCompra.eventos), joinedload(PurOrdenCompra.recepciones).joinedload(PurRecepcion.lineas)).filter_by(id=id).first_or_404()


@purchasing_bp.route("/ordenes")
@login_required
@require_module(MODULO_INVENTARIO)
def ordenes_list():
    items = _orden_query().options(joinedload(PurOrdenCompra.proveedor)).order_by(PurOrdenCompra.created_at.desc()).all()
    return render_template("purchasing/ordenes_list.html", items=items)


@purchasing_bp.route("/solicitudes/<int:id>/convertir", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def ordenes_from_request(id):
    if not can_approve_purchase_request(current_user):
        flash("Solo un administrador puede crear órdenes de compra.", "danger")
        return redirect(url_for("purchasing.solicitudes_detail", id=id))
    solicitud = _get_or_404(id)
    if request.method == "POST":
        try:
            datos = dict(request.form)
            datos["entrega_prevista"] = _fecha(request.form.get("entrega_prevista"))
            line_ids = request.form.getlist("linea_id"); prices = request.form.getlist("precio_unitario"); rates = request.form.getlist("tasa_iva")
            pricing = {int(line_id): (prices[i] if i < len(prices) else "", rates[i] if i < len(rates) else "0") for i, line_id in enumerate(line_ids)}
            orden = crear_orden_desde_solicitud(_empresa_id(), current_user.id, solicitud, datos, pricing)
            db.session.commit(); flash(f"Orden {orden.numero} creada como borrador.", "success")
            return redirect(url_for("purchasing.ordenes_detail", id=orden.id))
        except ValueError as exc:
            db.session.rollback(); flash(str(exc), "danger")
    proveedores = InvProveedor.query.filter_by(empresa_id=_empresa_id(), activo=True).order_by(InvProveedor.nombre).all()
    return render_template("purchasing/orden_form.html", solicitud=solicitud, proveedores=proveedores)


@purchasing_bp.route("/ordenes/<int:id>")
@login_required
@require_module(MODULO_INVENTARIO)
def ordenes_detail(id):
    return render_template("purchasing/orden_detail.html", orden=_orden_or_404(id), puede_gestionar=can_approve_purchase_request(current_user))


@purchasing_bp.route("/ordenes/<int:id>/<accion>", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def ordenes_transition(id, accion):
    if not can_approve_purchase_request(current_user):
        flash("No tienes permiso para cambiar la OC.", "danger")
        return redirect(url_for("purchasing.ordenes_detail", id=id))
    orden = _orden_or_404(id); target = {"emitir": "emitida", "enviar": "enviada", "cancelar": "cancelada"}.get(accion)
    try:
        if not target: raise ValueError("Acción no válida.")
        transicionar_orden(orden, current_user.id, target); db.session.commit(); flash(f"Orden {target}.", "success")
    except ValueError as exc:
        db.session.rollback(); flash(str(exc), "danger")
    return redirect(url_for("purchasing.ordenes_detail", id=id))


@purchasing_bp.route("/ordenes/<int:id>/pdf")
@login_required
@require_module(MODULO_INVENTARIO)
def ordenes_pdf(id):
    from io import BytesIO
    from app.purchasing.mrl_exports import export_orden_compra_pdf
    content, name = export_orden_compra_pdf(current_user.empresa, _orden_or_404(id), usuario=current_user)
    return send_file(BytesIO(content), mimetype="application/pdf", as_attachment=True, download_name=name)


@purchasing_bp.route("/ordenes/<int:id>/recibir", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def recepciones_new(id):
    orden = _orden_or_404(id)
    if not can_receive_purchasing(current_user):
        flash("No tienes permiso para registrar recepciones.", "danger")
        return redirect(url_for("purchasing.ordenes_detail", id=id))
    if request.method == "POST":
        try:
            line_ids = request.form.getlist("linea_id"); accepted = request.form.getlist("cantidad_recibida"); rejected = request.form.getlist("cantidad_rechazada"); reasons = request.form.getlist("motivo_rechazo")
            quantities = {int(line_id): (accepted[i] if i < len(accepted) else 0, rejected[i] if i < len(rejected) else 0, reasons[i] if i < len(reasons) else "") for i, line_id in enumerate(line_ids)}
            datos = dict(request.form); datos["fecha"] = _fecha(request.form.get("fecha")) or date.today()
            receipt = registrar_recepcion(_empresa_id(), current_user.id, orden, datos, quantities)
            db.session.commit(); flash(f"Recepción {receipt.numero} registrada. El stock fue actualizado.", "success")
            return redirect(url_for("purchasing.ordenes_detail", id=id))
        except ValueError as exc:
            db.session.rollback(); flash(str(exc), "danger")
    received = {line.id: sum(float(r.cantidad_recibida or 0) for r in line.lineas_recepcion) for line in orden.lineas}
    return render_template("purchasing/recepcion_form.html", orden=orden, recibido=received, idempotency_key=str(uuid4()), hoy=date.today())
