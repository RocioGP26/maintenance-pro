import re
import unicodedata
from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import Optional, Tuple
from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func, or_

from app import db
from app.models import (
    Incident,
    Machine,
    MachineStatus,
    MachineType,
    SparePart,
    Technician,
    User,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderType,
)

bp = Blueprint("main", __name__)


def _is_safe_url(target: str) -> bool:
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


@bp.before_request
def _require_login():
    if request.endpoint == "main.login":
        return
    if not current_user.is_authenticated:
        return redirect(url_for("main.login", next=request.url))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))
        user = User.query.filter_by(username=username).first()
        if user is not None and user.activo and user.check_password(password):
            login_user(user, remember=remember)
            flash("Sesión iniciada correctamente.", "success")
            nxt = request.form.get("next") or request.args.get("next")
            if nxt and _is_safe_url(nxt):
                return redirect(nxt)
            return redirect(url_for("main.dashboard"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.login"))


def _period_bounds(period: str, ref: Optional[date] = None) -> Tuple[date, date, str]:
    ref = ref or date.today()
    period = (period or "mes").lower()
    if period == "dia":
        start = ref
        end = ref
    elif period == "semana":
        start = ref - timedelta(days=ref.weekday())
        end = start + timedelta(days=6)
    elif period == "año":
        start = date(ref.year, 1, 1)
        end = date(ref.year, 12, 31)
    else:
        start = date(ref.year, ref.month, 1)
        _, last = monthrange(ref.year, ref.month)
        end = date(ref.year, ref.month, last)
    return start, end, period


def _wo_in_period_query(start: date, end: date):
    return WorkOrder.query.filter(
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada >= start,
        WorkOrder.fecha_programada <= end,
    )


@bp.route("/")
def dashboard():
    period = request.args.get("periodo", "mes")
    start, end, period = _period_bounds(period)

    total_m = Machine.query.count()
    op = Machine.query.filter_by(status=MachineStatus.OPERATIVO.value).count()
    mant = Machine.query.filter_by(status=MachineStatus.MANTENIMIENTO.value).count()
    falla = Machine.query.filter_by(status=MachineStatus.FALLA.value).count()

    if total_m == 0:
        pct_op = pct_mant = pct_falla = 0.0
    else:
        pct_op = round(100.0 * op / total_m, 1)
        pct_mant = round(100.0 * mant / total_m, 1)
        pct_falla = round(100.0 * falla / total_m, 1)

    wo_period = _wo_in_period_query(start, end)
    preventivas = wo_period.filter(WorkOrder.tipo == WorkOrderType.PREVENTIVO.value)
    total_prev = preventivas.count()
    prev_cerradas = preventivas.filter(WorkOrder.status == WorkOrderStatus.CERRADA.value).count()
    if total_prev == 0:
        cumplimiento = 100.0
        prev_msg = "Sin órdenes preventivas en el período"
    else:
        cumplimiento = round(100.0 * prev_cerradas / total_prev, 1)
        prev_msg = f"{prev_cerradas} de {total_prev} preventivas cerradas"

    criticos = (
        Machine.query.filter_by(es_critico=True)
        .order_by(Machine.nombre)
        .limit(5)
        .all()
    )

    techs = Technician.query.filter_by(activo=True).order_by(Technician.nombre).all()
    workload_labels = []
    workload_values = []
    for t in techs:
        n = (
            WorkOrder.query.filter(
                WorkOrder.technician_id == t.id,
                WorkOrder.fecha_programada.isnot(None),
                WorkOrder.fecha_programada >= start,
                WorkOrder.fecha_programada <= end,
                WorkOrder.status.in_(
                    [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
                ),
            ).count()
        )
        workload_labels.append(t.nombre)
        workload_values.append(n)

    workload_empty = sum(workload_values) == 0

    return render_template(
        "dashboard.html",
        periodo=period,
        health={
            "operativos": pct_op,
            "mantenimiento": pct_mant,
            "falla": pct_falla,
            "counts": {"op": op, "mant": mant, "falla": falla, "total": total_m},
        },
        cumplimiento=cumplimiento,
        prev_msg=prev_msg,
        criticos=criticos,
        workload_labels=workload_labels,
        workload_values=workload_values,
        workload_empty=workload_empty,
    )


# --- Activos ---
def _machine_types_activos():
    return MachineType.query.filter_by(activo=True).order_by(MachineType.orden, MachineType.nombre).all()


def _machine_types_para_formulario(machine: Optional[Machine] = None):
    base = _machine_types_activos()
    if machine is None or not machine.machine_type_id:
        return base
    if any(mt.id == machine.machine_type_id for mt in base):
        return base
    cur = MachineType.query.get(machine.machine_type_id)
    return [cur] + base if cur else base


def _default_machine_type_id() -> Optional[int]:
    g = MachineType.query.filter_by(clave="general", activo=True).first()
    if g:
        return g.id
    first = MachineType.query.filter_by(activo=True).order_by(MachineType.orden, MachineType.nombre).first()
    return first.id if first else None


def _machine_type_id_validado(form) -> Optional[int]:
    raw = form.get("machine_type_id")
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        return None
    mt = MachineType.query.filter_by(id=tid, activo=True).first()
    return mt.id if mt else None


def _slugify_clave(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return (s or "tipo")[:48]


def _clave_tipo_unica(base: str) -> str:
    c = base[:48]
    n = 2
    while MachineType.query.filter_by(clave=c).first():
        suffix = f"_{n}"
        c = (base[: 48 - len(suffix)] + suffix)[:48]
        n += 1
    return c


@bp.route("/activos")
def activos_list():
    q = request.args.get("q", "").strip()
    query = Machine.query.order_by(Machine.codigo)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Machine.codigo.ilike(like),
                Machine.nombre.ilike(like),
                Machine.ubicacion.ilike(like),
            )
        )
    return render_template("activos/list.html", machines=query.all(), q=q)


@bp.route("/activos/api/sugerir-codigo")
def activos_api_sugerir_codigo():
    raw = request.args.get("type_id", "").strip()
    try:
        tid = int(raw)
    except (TypeError, ValueError):
        tid = None
    mt = MachineType.query.filter_by(id=tid, activo=True).first() if tid else None
    if mt is None:
        mt = MachineType.query.filter_by(clave="general", activo=True).first()
    pref = (mt.prefijo if mt else "EQ").strip().upper() or "EQ"
    return jsonify(
        {
            "codigo": Machine.sugerir_codigo_siguiente(pref),
            "prefijo": pref,
        }
    )


@bp.route("/activos/nuevo", methods=["GET", "POST"])
def activos_new():
    tipos = _machine_types_activos()
    if not tipos:
        flash("Primero debes crear al menos un tipo de máquina en Activos → Tipos de máquina.", "warning")
        return redirect(url_for("main.activos_tipo_list"))

    if request.method == "POST":
        mt_id = _machine_type_id_validado(request.form)
        nombre = request.form.get("nombre", "").strip()
        auto_codigo = request.form.get("generar_codigo") == "1"
        mt = MachineType.query.get(mt_id) if mt_id else None
        if auto_codigo and mt:
            codigo = Machine.sugerir_codigo_siguiente(mt.prefijo)
        else:
            codigo = request.form.get("codigo", "").strip()
        if not mt_id:
            flash("Selecciona un tipo de máquina válido.", "danger")
        elif not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not codigo:
            flash("Indica un código manual o activa la generación automática.", "danger")
        else:
            m = Machine(
                codigo=codigo,
                machine_type_id=mt_id,
                nombre=nombre,
                ubicacion=request.form.get("ubicacion", "").strip(),
                marca=request.form.get("marca", "").strip(),
                modelo=request.form.get("modelo", "").strip(),
                status=request.form.get("status") or MachineStatus.OPERATIVO.value,
                es_critico=bool(request.form.get("es_critico")),
                notas=request.form.get("notas", "").strip(),
            )
            db.session.add(m)
            try:
                db.session.commit()
                flash(f"Activo registrado con código {m.codigo}.", "success")
                return redirect(url_for("main.activos_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿código duplicado?).", "danger")

    preview_id = _default_machine_type_id()
    if request.method == "POST":
        raw = request.form.get("machine_type_id")
        try:
            tid = int(raw)
            if MachineType.query.filter_by(id=tid, activo=True).first():
                preview_id = tid
        except (TypeError, ValueError):
            pass
    mt_sel = MachineType.query.get(preview_id) if preview_id else None
    pref = (mt_sel.prefijo if mt_sel else "EQ").upper()
    return render_template(
        "activos/form.html",
        machine=None,
        machine_types=tipos,
        default_machine_type_id=preview_id,
        codigo_sugerido=Machine.sugerir_codigo_siguiente(pref),
    )


@bp.route("/activos/<int:id>/editar", methods=["GET", "POST"])
def activos_edit(id):
    m = Machine.query.get_or_404(id)
    tipos = _machine_types_para_formulario(m)
    if not tipos:
        flash("No hay tipos de máquina activos.", "warning")
        return redirect(url_for("main.activos_tipo_list"))

    if request.method == "POST":
        mt_id = _machine_type_id_validado(request.form)
        m.codigo = request.form.get("codigo", "").strip()
        if mt_id:
            m.machine_type_id = mt_id
        m.nombre = request.form.get("nombre", "").strip()
        m.ubicacion = request.form.get("ubicacion", "").strip()
        m.marca = request.form.get("marca", "").strip()
        m.modelo = request.form.get("modelo", "").strip()
        m.status = request.form.get("status") or m.status
        m.es_critico = bool(request.form.get("es_critico"))
        m.notas = request.form.get("notas", "").strip()
        if not m.codigo or not m.nombre:
            flash("Código y nombre son obligatorios.", "danger")
        elif not mt_id:
            flash("Selecciona un tipo de máquina válido.", "danger")
        else:
            try:
                db.session.commit()
                flash("Activo actualizado.", "success")
                return redirect(url_for("main.activos_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar.", "danger")
    return render_template(
        "activos/form.html",
        machine=m,
        machine_types=tipos,
        default_machine_type_id=m.machine_type_id,
        codigo_sugerido=Machine.sugerir_codigo_siguiente(
            (m.machine_type.prefijo if m.machine_type else "EQ").upper()
        ),
    )


@bp.route("/activos/<int:id>/eliminar", methods=["POST"])
def activos_delete(id):
    m = Machine.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("Activo eliminado.", "info")
    return redirect(url_for("main.activos_list"))


# --- Tipos de máquina (catálogo) ---
@bp.route("/activos/tipos")
def activos_tipo_list():
    tipos = MachineType.query.order_by(MachineType.orden, MachineType.nombre).all()
    return render_template("activos/tipos_list.html", tipos=tipos)


@bp.route("/activos/tipos/nuevo", methods=["GET", "POST"])
def activos_tipo_new():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        prefijo = (request.form.get("prefijo", "").strip() or "").upper()
        try:
            orden = int(request.form.get("orden") or 0)
        except ValueError:
            orden = 0
        if not nombre:
            flash("El nombre del tipo es obligatorio.", "danger")
        elif not re.match(r"^[A-Z0-9]{2,8}$", prefijo):
            flash("El prefijo debe tener entre 2 y 8 letras o números (ej. BM, CP12).", "danger")
        else:
            base_clave = _slugify_clave(nombre)
            clave = _clave_tipo_unica(base_clave)
            db.session.add(
                MachineType(
                    clave=clave,
                    nombre=nombre,
                    prefijo=prefijo,
                    orden=orden,
                    activo=True,
                )
            )
            try:
                db.session.commit()
                flash("Tipo de máquina creado.", "success")
                return redirect(url_for("main.activos_tipo_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿prefijo o clave duplicado?).", "danger")
    siguiente_orden = db.session.query(func.max(MachineType.orden)).scalar()
    siguiente_orden = (siguiente_orden or 0) + 1
    return render_template("activos/tipo_form.html", tipo=None, siguiente_orden=siguiente_orden)


@bp.route("/activos/tipos/<int:id>/editar", methods=["GET", "POST"])
def activos_tipo_edit(id):
    t = MachineType.query.get_or_404(id)
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        prefijo = (request.form.get("prefijo", "").strip() or "").upper()
        try:
            orden = int(request.form.get("orden") or 0)
        except ValueError:
            orden = t.orden
        activo = bool(request.form.get("activo"))
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
        elif not re.match(r"^[A-Z0-9]{2,8}$", prefijo):
            flash("El prefijo debe tener entre 2 y 8 letras o números.", "danger")
        else:
            other = MachineType.query.filter(MachineType.prefijo == prefijo, MachineType.id != t.id).first()
            if other:
                flash("Ese prefijo ya lo usa otro tipo.", "danger")
            else:
                t.nombre = nombre
                t.prefijo = prefijo
                t.orden = orden
                t.activo = activo
                try:
                    db.session.commit()
                    flash("Tipo actualizado.", "success")
                    return redirect(url_for("main.activos_tipo_list"))
                except Exception:
                    db.session.rollback()
                    flash("No se pudo guardar.", "danger")
    return render_template("activos/tipo_form.html", tipo=t, siguiente_orden=t.orden)


@bp.route("/activos/tipos/<int:id>/eliminar", methods=["POST"])
def activos_tipo_delete(id):
    t = MachineType.query.get_or_404(id)
    if t.machines.count() > 0:
        flash("No se puede eliminar: hay equipos asignados a este tipo. Desactívalo en su lugar.", "danger")
        return redirect(url_for("main.activos_tipo_list"))
    db.session.delete(t)
    db.session.commit()
    flash("Tipo eliminado.", "info")
    return redirect(url_for("main.activos_tipo_list"))


# --- Órdenes ---
@bp.route("/ordenes")
def ordenes_list():
    status = request.args.get("status", "")
    q = WorkOrder.query.order_by(WorkOrder.fecha_programada.desc(), WorkOrder.id.desc())
    if status:
        q = q.filter_by(status=status)
    return render_template("ordenes/list.html", orders=q.all(), status_filter=status)


@bp.route("/ordenes/nueva", methods=["GET", "POST"])
def ordenes_new():
    machines = Machine.query.order_by(Machine.nombre).all()
    technicians = Technician.query.filter_by(activo=True).order_by(Technician.nombre).all()
    if request.method == "POST":
        fp = request.form.get("fecha_programada")
        fecha_prog = datetime.strptime(fp, "%Y-%m-%d").date() if fp else None
        wo = WorkOrder(
            titulo=request.form.get("titulo", "").strip(),
            descripcion=request.form.get("descripcion", "").strip(),
            tipo=request.form.get("tipo") or WorkOrderType.CORRECTIVO.value,
            status=request.form.get("status") or WorkOrderStatus.ABIERTA.value,
            fecha_programada=fecha_prog,
            machine_id=int(request.form.get("machine_id", 0)),
            technician_id=int(request.form["technician_id"])
            if request.form.get("technician_id")
            else None,
        )
        if not wo.titulo or not wo.machine_id:
            flash("Título y equipo son obligatorios.", "danger")
        else:
            db.session.add(wo)
            db.session.commit()
            flash("Orden creada.", "success")
            return redirect(url_for("main.ordenes_list"))
    return render_template(
        "ordenes/form.html",
        order=None,
        machines=machines,
        technicians=technicians,
    )


@bp.route("/ordenes/<int:id>/editar", methods=["GET", "POST"])
def ordenes_edit(id):
    wo = WorkOrder.query.get_or_404(id)
    machines = Machine.query.order_by(Machine.nombre).all()
    technicians = Technician.query.filter_by(activo=True).order_by(Technician.nombre).all()
    if request.method == "POST":
        wo.titulo = request.form.get("titulo", "").strip()
        wo.descripcion = request.form.get("descripcion", "").strip()
        wo.tipo = request.form.get("tipo") or wo.tipo
        wo.status = request.form.get("status") or wo.status
        fp = request.form.get("fecha_programada")
        wo.fecha_programada = datetime.strptime(fp, "%Y-%m-%d").date() if fp else None
        wo.machine_id = int(request.form.get("machine_id", wo.machine_id))
        wo.technician_id = (
            int(request.form["technician_id"]) if request.form.get("technician_id") else None
        )
        if not wo.titulo:
            flash("El título es obligatorio.", "danger")
        else:
            db.session.commit()
            flash("Orden actualizada.", "success")
            return redirect(url_for("main.ordenes_list"))
    return render_template(
        "ordenes/form.html",
        order=wo,
        machines=machines,
        technicians=technicians,
    )


# --- Calendario ---
@bp.route("/calendario")
def calendario():
    year = int(request.args.get("y", date.today().year))
    month = int(request.args.get("m", date.today().month))
    start = date(year, month, 1)
    _, last = monthrange(year, month)
    end = date(year, month, last)
    orders = (
        WorkOrder.query.filter(
            WorkOrder.fecha_programada.isnot(None),
            WorkOrder.fecha_programada >= start,
            WorkOrder.fecha_programada <= end,
        )
        .order_by(WorkOrder.fecha_programada)
        .all()
    )
    by_day = {}
    for o in orders:
        d = o.fecha_programada.isoformat()
        by_day.setdefault(d, []).append(o)

    first_weekday = start.weekday()
    cells = [None] * first_weekday
    for day in range(1, last + 1):
        cells.append(day)
    while len(cells) % 7 != 0:
        cells.append(None)
    weeks = [cells[i : i + 7] for i in range(0, len(cells), 7)]

    return render_template(
        "calendario.html",
        year=year,
        month=month,
        by_day=by_day,
        start=start,
        last_day=last,
        weeks=weeks,
    )


# --- Inventario ---
@bp.route("/inventario")
def inventario_list():
    q = request.args.get("q", "").strip()
    query = SparePart.query.order_by(SparePart.nombre)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                SparePart.sku.ilike(like),
                SparePart.nombre.ilike(like),
            )
        )
    return render_template("inventario/list.html", items=query.all(), q=q)


@bp.route("/inventario/nuevo", methods=["GET", "POST"])
def inventario_new():
    if request.method == "POST":
        p = SparePart(
            sku=request.form.get("sku", "").strip(),
            nombre=request.form.get("nombre", "").strip(),
            categoria=request.form.get("categoria", "").strip(),
            unidad=request.form.get("unidad", "pza").strip(),
            cantidad=int(request.form.get("cantidad") or 0),
            stock_minimo=int(request.form.get("stock_minimo") or 0),
            ubicacion_almacen=request.form.get("ubicacion_almacen", "").strip(),
        )
        if not p.sku or not p.nombre:
            flash("SKU y nombre son obligatorios.", "danger")
        else:
            db.session.add(p)
            try:
                db.session.commit()
                flash("Repuesto registrado.", "success")
                return redirect(url_for("main.inventario_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar (¿SKU duplicado?).", "danger")
    return render_template("inventario/form.html", item=None)


@bp.route("/inventario/<int:id>/editar", methods=["GET", "POST"])
def inventario_edit(id):
    p = SparePart.query.get_or_404(id)
    if request.method == "POST":
        p.sku = request.form.get("sku", "").strip()
        p.nombre = request.form.get("nombre", "").strip()
        p.categoria = request.form.get("categoria", "").strip()
        p.unidad = request.form.get("unidad", "pza").strip()
        p.cantidad = int(request.form.get("cantidad") or 0)
        p.stock_minimo = int(request.form.get("stock_minimo") or 0)
        p.ubicacion_almacen = request.form.get("ubicacion_almacen", "").strip()
        if not p.sku or not p.nombre:
            flash("SKU y nombre son obligatorios.", "danger")
        else:
            try:
                db.session.commit()
                flash("Repuesto actualizado.", "success")
                return redirect(url_for("main.inventario_list"))
            except Exception:
                db.session.rollback()
                flash("No se pudo guardar.", "danger")
    return render_template("inventario/form.html", item=p)


# --- Equipo técnico ---
@bp.route("/equipo")
def equipo_list():
    return render_template(
        "equipo/list.html",
        technicians=Technician.query.order_by(Technician.nombre).all(),
    )


@bp.route("/equipo/nuevo", methods=["GET", "POST"])
def equipo_new():
    if request.method == "POST":
        t = Technician(
            nombre=request.form.get("nombre", "").strip(),
            especialidad=request.form.get("especialidad", "").strip(),
            telefono=request.form.get("telefono", "").strip(),
            email=request.form.get("email", "").strip(),
            activo=bool(request.form.get("activo")),
        )
        if not t.nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            db.session.add(t)
            db.session.commit()
            flash("Técnico registrado.", "success")
            return redirect(url_for("main.equipo_list"))
    return render_template("equipo/form.html", tech=None)


@bp.route("/equipo/<int:id>/editar", methods=["GET", "POST"])
def equipo_edit(id):
    t = Technician.query.get_or_404(id)
    if request.method == "POST":
        t.nombre = request.form.get("nombre", "").strip()
        t.especialidad = request.form.get("especialidad", "").strip()
        t.telefono = request.form.get("telefono", "").strip()
        t.email = request.form.get("email", "").strip()
        t.activo = bool(request.form.get("activo"))
        if not t.nombre:
            flash("El nombre es obligatorio.", "danger")
        else:
            db.session.commit()
            flash("Técnico actualizado.", "success")
            return redirect(url_for("main.equipo_list"))
    return render_template("equipo/form.html", tech=t)


# --- Reportes ---
@bp.route("/reportes")
def reportes():
    total_m = Machine.query.count()
    by_status = (
        db.session.query(Machine.status, func.count(Machine.id))
        .group_by(Machine.status)
        .all()
    )
    wo_by_type = (
        db.session.query(WorkOrder.tipo, func.count(WorkOrder.id)).group_by(WorkOrder.tipo).all()
    )
    wo_by_status = (
        db.session.query(WorkOrder.status, func.count(WorkOrder.id))
        .group_by(WorkOrder.status)
        .all()
    )
    bajo_minimo = SparePart.query.filter(SparePart.cantidad < SparePart.stock_minimo).count()
    return render_template(
        "reportes.html",
        total_m=total_m,
        by_status=by_status,
        wo_by_type=wo_by_type,
        wo_by_status=wo_by_status,
        bajo_minimo=bajo_minimo,
        chart_estado_labels=[r[0] for r in by_status],
        chart_estado_data=[r[1] for r in by_status],
        chart_tipo_labels=[r[0] for r in wo_by_type],
        chart_tipo_data=[r[1] for r in wo_by_type],
        chart_wo_labels=[r[0] for r in wo_by_status],
        chart_wo_data=[r[1] for r in wo_by_status],
    )


# --- Incidencias ---
@bp.route("/incidencia", methods=["GET", "POST"])
def incidencia():
    machines = Machine.query.order_by(Machine.nombre).all()
    if request.method == "POST":
        mid = request.form.get("machine_id")
        inc = Incident(
            titulo=request.form.get("titulo", "").strip(),
            descripcion=request.form.get("descripcion", "").strip(),
            machine_id=int(mid) if mid else None,
        )
        if not inc.titulo:
            flash("Describe brevemente la incidencia.", "danger")
        else:
            db.session.add(inc)
            db.session.commit()
            flash("Incidencia registrada. El supervisor será notificado.", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("incidencia.html", machines=machines)
