"""UI Purchasing · solicitudes Sprint 16.1."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app import db
from app.models import InvProducto, PurSolicitud
from app.module_guard import require_module
from app.modules import MODULO_INVENTARIO
from app.permissions import can_approve_purchase_request
from app.purchasing.service import PRIORIDADES, guardar_solicitud, transicionar

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

