"""Rutas del módulo inventario comercial (productos, compras, ventas, proveedores)."""

from __future__ import annotations

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.inventario_comercial.exports import excel_productos_bajo_stock
from app.inventario_comercial.productos_excel import (
    excel_productos_catalogo,
    excel_productos_plantilla,
    importar_productos_desde_excel,
)
from app.inventario_comercial.media import aplicar_imagen_producto
from app.inventario_comercial.service import (
    guardar_cliente_comercial,
    guardar_producto_comercial,
    guardar_proveedor_comercial,
    clientes_para_select,
    kpis_dashboard_inventario,
    parse_lineas_entrada_form,
    parse_lineas_venta_form,
    productos_para_select,
    productos_pos_json,
    registrar_entrada_mercancia,
    registrar_abono_venta,
    registrar_venta,
    siguiente_numero_entrada,
    siguiente_numero_venta,
)
from app.models import InvCliente, InvCompra, InvProducto, InvProveedor, InvVenta
from app.module_guard import require_module
from app.modules import MODULO_INVENTARIO
from app.tenancy.queries import query_tenant

inv_comercial_bp = Blueprint("inv_comercial", __name__, url_prefix="/comercial")


def _empresa_id() -> int | None:
    from flask_login import current_user

    if not current_user.is_authenticated:
        return None
    return getattr(current_user, "empresa_id", None)


def _require_empresa_id() -> int:
    eid = _empresa_id()
    if not eid:
        raise RuntimeError("Sin empresa")
    return eid


def _producto_or_404(producto_id: int) -> InvProducto:
    return query_tenant(InvProducto).filter_by(id=producto_id).first_or_404()


def _proveedor_or_404(proveedor_id: int) -> InvProveedor:
    return query_tenant(InvProveedor).filter_by(id=proveedor_id).first_or_404()


def _cliente_or_404(cliente_id: int) -> InvCliente:
    return query_tenant(InvCliente).filter_by(id=cliente_id).first_or_404()


def _compra_or_404(compra_id: int) -> InvCompra:
    return query_tenant(InvCompra).filter_by(id=compra_id).first_or_404()


def _venta_or_404(venta_id: int) -> InvVenta:
    return query_tenant(InvVenta).filter_by(id=venta_id).first_or_404()


def _persistir_producto(eid: int, *, producto: InvProducto | None = None) -> InvProducto:
    item = guardar_producto_comercial(
        eid,
        request.form,
        producto=producto,
        permitir_stock_inicial=producto is None,
    )
    db.session.flush()
    aplicar_imagen_producto(item, request.form, request.files.get("imagen_archivo"))
    db.session.commit()
    return item


def _parse_fecha(val: str | None) -> date:
    raw = (val or "").strip()
    if not raw:
        return date.today()
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return date.today()


def _query_productos_lista(
    *,
    q: str = "",
    estado: str = "activo",
    alerta: str = "",
):
    estado = (estado or "activo").strip().lower()
    alerta = (alerta or "").strip().lower()
    q = (q or "").strip()
    query = query_tenant(InvProducto)
    if estado == "inactivo":
        query = query.filter_by(activo=False)
    elif estado != "todos":
        query = query.filter_by(activo=True)
        estado = "activo"
    if alerta == "bajo":
        query = query.filter_by(activo=True).filter(InvProducto.stock <= InvProducto.stock_minimo)
        estado = "activo"
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(InvProducto.nombre.ilike(like), InvProducto.sku.ilike(like))
        )
    return query.order_by(InvProducto.nombre), estado


@inv_comercial_bp.route("/dashboard")
@login_required
@require_module(MODULO_INVENTARIO)
def dashboard_inventario():
    from flask import session

    eid = _empresa_id()
    if not eid:
        return redirect(url_for("main.login"))
    show_welcome = request.args.get("welcome") == "1" or session.pop("show_welcome", False)
    session.pop("show_tour", False)
    kpis = kpis_dashboard_inventario(eid, date.today())
    return render_template(
        "inventario_comercial/dashboard.html",
        kpis=kpis,
        hoy=date.today(),
        show_welcome=show_welcome,
    )


@inv_comercial_bp.route("/productos")
@login_required
@require_module(MODULO_INVENTARIO)
def productos_list():
    q = (request.args.get("q") or "").strip()
    alerta = (request.args.get("alerta") or "").strip().lower()
    estado = (request.args.get("estado") or "activo").strip().lower()
    query, estado = _query_productos_lista(q=q, estado=estado, alerta=alerta)
    items = query.limit(200).all()
    return render_template(
        "inventario_comercial/productos_list.html",
        items=items,
        q=q,
        estado=estado,
        alerta=alerta,
    )


@inv_comercial_bp.route("/productos/export/bajo-stock")
@login_required
@require_module(MODULO_INVENTARIO)
def productos_export_bajo_stock():
    from io import BytesIO

    eid = _require_empresa_id()
    contenido, nombre = excel_productos_bajo_stock(eid)
    return send_file(
        BytesIO(contenido),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre,
    )


@inv_comercial_bp.route("/productos/export")
@login_required
@require_module(MODULO_INVENTARIO)
def productos_export_catalogo():
    from io import BytesIO

    eid = _require_empresa_id()
    q = (request.args.get("q") or "").strip()
    alerta = (request.args.get("alerta") or "").strip().lower()
    estado = (request.args.get("estado") or "activo").strip().lower()
    query, _ = _query_productos_lista(q=q, estado=estado, alerta=alerta)
    productos = query.all()
    contenido, nombre = excel_productos_catalogo(eid, productos)
    return send_file(
        BytesIO(contenido),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre,
    )


@inv_comercial_bp.route("/productos/export/plantilla")
@login_required
@require_module(MODULO_INVENTARIO)
def productos_export_plantilla():
    from io import BytesIO

    eid = _require_empresa_id()
    contenido, nombre = excel_productos_plantilla(eid)
    return send_file(
        BytesIO(contenido),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nombre,
    )


@inv_comercial_bp.route("/productos/import", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def productos_import_excel():
    eid = _require_empresa_id()
    archivo = request.files.get("archivo")
    if not archivo or not (archivo.filename or "").strip():
        flash("Selecciona un archivo Excel (.xlsx).", "warning")
        return redirect(url_for("inv_comercial.productos_list"))

    contenido = archivo.read()
    resultado = importar_productos_desde_excel(
        eid,
        contenido,
        nombre_archivo=archivo.filename or "",
    )

    if resultado.creados or resultado.actualizados:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar la importación.", "danger")
            return redirect(url_for("inv_comercial.productos_list"))

    partes = []
    if resultado.creados:
        partes.append(f"{resultado.creados} creado(s)")
    if resultado.actualizados:
        partes.append(f"{resultado.actualizados} actualizado(s)")
    if resultado.omitidos:
        partes.append(f"{resultado.omitidos} omitido(s)")

    if partes:
        flash(f"Importación completada: {', '.join(partes)}.", "success")
    elif not resultado.errores:
        flash("No se importó ningún producto.", "warning")

    for err in resultado.errores[:8]:
        flash(err, "danger" if not partes else "warning")
    if len(resultado.errores) > 8:
        flash(f"…y {len(resultado.errores) - 8} aviso(s) más.", "warning")

    return redirect(url_for("inv_comercial.productos_list"))


@inv_comercial_bp.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def productos_nuevo():
    eid = _require_empresa_id()
    if request.method == "POST":
        try:
            _persistir_producto(eid)
            flash("Producto registrado en el catálogo.", "success")
            return redirect(url_for("inv_comercial.productos_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Ya existe un producto con esa referencia en tu empresa.", "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el producto.", "danger")
    return render_template("inventario_comercial/productos_form.html", item=None)


@inv_comercial_bp.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def productos_editar(id):
    eid = _require_empresa_id()
    item = _producto_or_404(id)
    if request.method == "POST":
        try:
            _persistir_producto(eid, producto=item)
            flash("Producto actualizado.", "success")
            return redirect(url_for("inv_comercial.productos_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except IntegrityError:
            db.session.rollback()
            flash("Ya existe otro producto con esa referencia.", "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el producto.", "danger")
    return render_template("inventario_comercial/productos_form.html", item=item)


@inv_comercial_bp.route("/productos/<int:id>/estado", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def productos_cambiar_estado(id):
    item = _producto_or_404(id)
    accion = (request.form.get("accion") or "").strip().lower()
    if accion == "activar":
        item.activo = True
        msg = f"«{item.nombre}» activado en el catálogo."
    elif accion == "inactivar":
        item.activo = False
        msg = f"«{item.nombre}» inactivado. Ya no aparecerá en el listado ni en entradas."
    else:
        item.activo = not item.activo
        msg = (
            f"«{item.nombre}» activado en el catálogo."
            if item.activo
            else f"«{item.nombre}» inactivado. Ya no aparecerá en el listado ni en entradas."
        )
    try:
        db.session.commit()
        flash(msg, "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo cambiar el estado del producto.", "danger")
    estado_vista = (request.form.get("estado_vista") or "activo").strip().lower()
    q = (request.form.get("q") or "").strip()
    return redirect(url_for("inv_comercial.productos_list", estado=estado_vista, q=q or None))


@inv_comercial_bp.route("/proveedores")
@login_required
@require_module(MODULO_INVENTARIO)
def proveedores_list():
    q = (request.args.get("q") or "").strip()
    query = query_tenant(InvProveedor).filter_by(activo=True)
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(InvProveedor.nombre.ilike(like), InvProveedor.nit.ilike(like))
        )
    items = query.order_by(InvProveedor.nombre).limit(200).all()
    return render_template(
        "inventario_comercial/proveedores_list.html",
        items=items,
        q=q,
    )


@inv_comercial_bp.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def proveedores_nuevo():
    eid = _require_empresa_id()
    if request.method == "POST":
        try:
            guardar_proveedor_comercial(eid, request.form)
            db.session.commit()
            flash("Proveedor registrado.", "success")
            return redirect(url_for("inv_comercial.proveedores_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el proveedor.", "danger")
    return render_template("inventario_comercial/proveedores_form.html", item=None)


@inv_comercial_bp.route("/proveedores/<int:id>/editar", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def proveedores_editar(id):
    eid = _require_empresa_id()
    item = _proveedor_or_404(id)
    if request.method == "POST":
        try:
            guardar_proveedor_comercial(eid, request.form, proveedor=item)
            db.session.commit()
            flash("Proveedor actualizado.", "success")
            return redirect(url_for("inv_comercial.proveedores_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el proveedor.", "danger")
    return render_template("inventario_comercial/proveedores_form.html", item=item)


@inv_comercial_bp.route("/clientes")
@login_required
@require_module(MODULO_INVENTARIO)
def clientes_list():
    q = (request.args.get("q") or "").strip()
    estado = (request.args.get("estado") or "activo").strip().lower()
    query = query_tenant(InvCliente)
    if estado == "inactivo":
        query = query.filter_by(activo=False)
    elif estado != "todos":
        query = query.filter_by(activo=True)
        estado = "activo"
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                InvCliente.nombre.ilike(like),
                InvCliente.documento.ilike(like),
                InvCliente.telefono.ilike(like),
                InvCliente.email.ilike(like),
            )
        )
    items = query.order_by(InvCliente.nombre).limit(200).all()
    return render_template(
        "inventario_comercial/clientes_list.html",
        items=items,
        q=q,
        estado=estado,
    )


@inv_comercial_bp.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def clientes_nuevo():
    eid = _require_empresa_id()
    if request.method == "POST":
        try:
            guardar_cliente_comercial(eid, request.form)
            db.session.commit()
            flash("Cliente registrado.", "success")
            next_url = (request.form.get("next") or "").strip()
            if next_url and next_url.startswith("/comercial/"):
                return redirect(next_url)
            return redirect(url_for("inv_comercial.clientes_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el cliente.", "danger")
    return render_template(
        "inventario_comercial/clientes_form.html",
        item=None,
        next_url=request.args.get("next", ""),
    )


@inv_comercial_bp.route("/clientes/<int:id>/editar", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def clientes_editar(id):
    eid = _require_empresa_id()
    item = _cliente_or_404(id)
    if request.method == "POST":
        try:
            guardar_cliente_comercial(eid, request.form, cliente=item)
            db.session.commit()
            flash("Cliente actualizado.", "success")
            return redirect(url_for("inv_comercial.clientes_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo guardar el cliente.", "danger")
    return render_template("inventario_comercial/clientes_form.html", item=item, next_url="")


@inv_comercial_bp.route("/clientes/<int:id>/estado", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def clientes_cambiar_estado(id):
    item = _cliente_or_404(id)
    accion = (request.form.get("accion") or "").strip().lower()
    if accion == "activar":
        item.activo = True
        msg = f"«{item.nombre}» activado."
    elif accion == "inactivar":
        item.activo = False
        msg = f"«{item.nombre}» inactivado."
    else:
        item.activo = not item.activo
        msg = f"«{item.nombre}» {'activado' if item.activo else 'inactivado'}."
    try:
        db.session.commit()
        flash(msg, "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo cambiar el estado del cliente.", "danger")
    estado_vista = (request.form.get("estado_vista") or "activo").strip().lower()
    q = (request.form.get("q") or "").strip()
    return redirect(url_for("inv_comercial.clientes_list", estado=estado_vista, q=q or None))


@inv_comercial_bp.route("/compras")
@login_required
@require_module(MODULO_INVENTARIO)
def compras_list():
    items = (
        query_tenant(InvCompra)
        .order_by(InvCompra.fecha.desc(), InvCompra.id.desc())
        .limit(100)
        .all()
    )
    return render_template("inventario_comercial/compras_list.html", items=items)


@inv_comercial_bp.route("/compras/nueva", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def compras_nueva():
    eid = _require_empresa_id()
    productos = productos_para_select(eid)
    proveedores = (
        query_tenant(InvProveedor).filter_by(activo=True).order_by(InvProveedor.nombre).all()
    )

    if request.method == "POST":
        proveedor_raw = (request.form.get("proveedor_id") or "").strip()
        proveedor_id = int(proveedor_raw) if proveedor_raw.isdigit() else None
        try:
            registrar_entrada_mercancia(
                eid,
                proveedor_id=proveedor_id,
                fecha=_parse_fecha(request.form.get("fecha")),
                numero=(request.form.get("numero") or "").strip(),
                notas=(request.form.get("notas") or "").strip(),
                lineas=parse_lineas_entrada_form(request.form),
            )
            db.session.commit()
            flash("Entrada de mercancía registrada. El stock se actualizó.", "success")
            return redirect(url_for("inv_comercial.compras_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo registrar la entrada.", "danger")

    return render_template(
        "inventario_comercial/compras_form.html",
        productos=productos,
        proveedores=proveedores,
        numero_sugerido=siguiente_numero_entrada(eid),
        hoy=date.today(),
    )


@inv_comercial_bp.route("/compras/<int:id>")
@login_required
@require_module(MODULO_INVENTARIO)
def compras_detalle(id):
    compra = _compra_or_404(id)
    return render_template("inventario_comercial/compras_detalle.html", compra=compra)


@inv_comercial_bp.route("/ventas")
@login_required
@require_module(MODULO_INVENTARIO)
def ventas_list():
    cobro = (request.args.get("cobro") or "").strip().lower()
    query = query_tenant(InvVenta)
    if cobro == "pendiente":
        query = query.filter(InvVenta.estado_cobro.in_(["pendiente", "parcial"]))
    items = query.order_by(InvVenta.fecha.desc(), InvVenta.id.desc()).limit(100).all()
    return render_template(
        "inventario_comercial/ventas_list.html",
        items=items,
        cobro_filtro=cobro,
    )


@inv_comercial_bp.route("/ventas/nueva", methods=["GET", "POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def ventas_nueva():
    from app.models import Empresa

    eid = _require_empresa_id()
    empresa = Empresa.query.get(eid)
    productos = productos_para_select(eid)
    moneda_ref = (empresa.moneda if empresa else "COP") or "COP"

    if request.method == "POST":
        cliente_raw = (request.form.get("cliente_id") or "").strip()
        cliente_id = int(cliente_raw) if cliente_raw.isdigit() else None
        from app.inventario_comercial.service import _parse_float, _parse_fecha_opcional

        try:
            venta = registrar_venta(
                eid,
                fecha=_parse_fecha(request.form.get("fecha")),
                numero=(request.form.get("numero") or "").strip(),
                moneda=(request.form.get("moneda") or moneda_ref).strip(),
                notas=(request.form.get("notas") or "").strip(),
                lineas=parse_lineas_venta_form(request.form),
                cliente_id=cliente_id,
                forma_pago=(request.form.get("forma_pago") or "contado").strip(),
                monto_abono_inicial=_parse_float(request.form.get("monto_abono_inicial")),
                fecha_vencimiento=_parse_fecha_opcional(request.form.get("fecha_vencimiento")),
            )
            db.session.commit()
            if venta.es_credito and venta.saldo_pendiente > 0:
                flash(
                    f"Venta a crédito registrada. Saldo pendiente: {venta.saldo_pendiente} {venta.moneda}.",
                    "success",
                )
            else:
                flash("Venta registrada. El stock se actualizó.", "success")
            return redirect(url_for("inv_comercial.ventas_list"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo registrar la venta.", "danger")

    return render_template(
        "inventario_comercial/ventas_form.html",
        productos=productos,
        productos_json=productos_pos_json(eid),
        clientes=clientes_para_select(eid),
        numero_sugerido=siguiente_numero_venta(eid),
        hoy=date.today(),
        moneda_ref=moneda_ref,
    )


@inv_comercial_bp.route("/ventas/<int:id>")
@login_required
@require_module(MODULO_INVENTARIO)
def ventas_detalle(id):
    venta = _venta_or_404(id)
    return render_template(
        "inventario_comercial/ventas_detalle.html",
        venta=venta,
        hoy=date.today(),
    )


@inv_comercial_bp.route("/ventas/<int:id>/abono", methods=["POST"])
@login_required
@require_module(MODULO_INVENTARIO)
def ventas_registrar_abono(id):
    from app.inventario_comercial.service import _parse_float

    venta = _venta_or_404(id)
    try:
        registrar_abono_venta(
            venta,
            monto=_parse_float(request.form.get("monto")),
            fecha=_parse_fecha(request.form.get("fecha")),
            notas=(request.form.get("notas") or "").strip(),
        )
        db.session.commit()
        flash("Abono registrado correctamente.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    except Exception:
        db.session.rollback()
        flash("No se pudo registrar el abono.", "danger")
    return redirect(url_for("inv_comercial.ventas_detalle", id=id))
