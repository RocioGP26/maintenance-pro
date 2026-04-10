import os
import re
from datetime import date, datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_visible = db.Column(db.String(120), default="")
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):  # noqa: D102
        return self.activo

    def etiqueta(self) -> str:
        return (self.nombre_visible or self.username).strip() or self.username


class MachineStatus(str, Enum):
    OPERATIVO = "operativo"
    MANTENIMIENTO = "mantenimiento"
    FALLA = "falla"


class WorkOrderType(str, Enum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    EMERGENCIA = "emergencia"


class WorkOrderStatus(str, Enum):
    ABIERTA = "abierta"
    EN_PROCESO = "en_proceso"
    CERRADA = "cerrada"


# Datos iniciales si la tabla machine_types está vacía (clave, nombre, prefijo)
DEFAULT_MACHINE_TYPES_SEED = (
    ("bomba_agua", "Bomba de agua", "BM"),
    ("compresor", "Compresor", "CP"),
    ("linea", "Línea de producción / envasado", "LP"),
    ("motor", "Motor / accionamiento", "MT"),
    ("transporte", "Transporte / elevación", "TR"),
    ("intercambiador", "Intercambiador / torre de enfriamiento", "IC"),
    ("valvula", "Válvulas / instrumentación", "VA"),
    ("general", "Equipo general / otro", "EQ"),
)


class MachineType(db.Model):
    __tablename__ = "machine_types"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(48), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    prefijo = db.Column(db.String(8), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    machines = db.relationship("Machine", back_populates="machine_type", lazy="dynamic")


class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(64), unique=True, nullable=False)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    ubicacion = db.Column(db.String(200), default="")
    marca = db.Column(db.String(120), default="")
    modelo = db.Column(db.String(120), default="")
    status = db.Column(db.String(32), default=MachineStatus.OPERATIVO.value)
    es_critico = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    machine_type = db.relationship("MachineType", back_populates="machines", lazy="joined")
    work_orders = db.relationship("WorkOrder", backref="machine", lazy="dynamic")

    @property
    def tipo_etiqueta(self) -> str:
        return self.machine_type.nombre if self.machine_type else "—"

    @staticmethod
    def sugerir_codigo_siguiente(prefijo: str = "EQ") -> str:
        """Siguiente código libre PREF-001 según el máximo numérico existente con ese prefijo."""
        prefijo = (prefijo or "EQ").strip().upper()
        pat = re.compile(rf"^{re.escape(prefijo)}-(\d+)$", re.IGNORECASE)
        max_n = 0
        for (c,) in db.session.query(Machine.codigo).all():
            s = (c or "").strip()
            m = pat.match(s)
            if m:
                max_n = max(max_n, int(m.group(1)))
        n = max_n + 1
        while True:
            cand = f"{prefijo}-{n:03d}"
            if Machine.query.filter_by(codigo=cand).first() is None:
                return cand
            n += 1


class Technician(db.Model):
    __tablename__ = "technicians"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    especialidad = db.Column(db.String(120), default="")
    telefono = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_orders = db.relationship("WorkOrder", backref="technician", lazy="dynamic")


class WorkOrder(db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    tipo = db.Column(db.String(32), default=WorkOrderType.CORRECTIVO.value)
    status = db.Column(db.String(32), default=WorkOrderStatus.ABIERTA.value)
    fecha_programada = db.Column(db.Date, nullable=True)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SparePart(db.Model):
    __tablename__ = "spare_parts"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(120), default="")
    unidad = db.Column(db.String(32), default="pza")
    cantidad = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    ubicacion_almacen = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=True)
    reportado_en = db.Column(db.DateTime, default=datetime.utcnow)
    resuelto = db.Column(db.Boolean, default=False)

    machine = db.relationship("Machine", backref="incidents")


def ensure_machine_tipo_equipo_column():
    """SQLite legado: añade tipo_equipo si machines existía sin esa columna (antes del FK)."""
    from sqlalchemy import inspect, text

    try:
        insp = inspect(db.engine)
        if "machines" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("machines")}
        if "tipo_equipo" in cols:
            return
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE machines ADD COLUMN tipo_equipo VARCHAR(32)"))
            conn.execute(text("UPDATE machines SET tipo_equipo = 'general' WHERE tipo_equipo IS NULL"))
    except Exception:
        pass


def seed_machine_types_if_empty():
    if MachineType.query.first() is not None:
        return
    for i, (clave, nombre, prefijo) in enumerate(DEFAULT_MACHINE_TYPES_SEED):
        db.session.add(
            MachineType(clave=clave, nombre=nombre, prefijo=prefijo.upper(), orden=i, activo=True)
        )
    db.session.commit()


def ensure_machines_machine_type_fk():
    """Añade machine_type_id y rellena desde tipo_equipo (legado) o tipo 'general'."""
    from sqlalchemy import inspect, text

    try:
        insp = inspect(db.engine)
        if "machines" not in insp.get_table_names():
            return
        seed_machine_types_if_empty()
        cols = {c["name"] for c in insp.get_columns("machines")}
        if "machine_type_id" in cols:
            return
        with db.engine.begin() as conn:
            conn.execute(text("ALTER TABLE machines ADD COLUMN machine_type_id INTEGER"))
        if "tipo_equipo" in cols:
            db.session.execute(
                text(
                    """
                    UPDATE machines SET machine_type_id = (
                        SELECT id FROM machine_types WHERE machine_types.clave = machines.tipo_equipo LIMIT 1
                    )
                    WHERE EXISTS (
                        SELECT 1 FROM machine_types t WHERE t.clave = machines.tipo_equipo
                    )
                    """
                )
            )
            db.session.commit()
        db.session.execute(
            text(
                """
                UPDATE machines SET machine_type_id = (
                    SELECT id FROM machine_types WHERE machine_types.clave = 'general' LIMIT 1
                )
                WHERE machine_type_id IS NULL
                """
            )
        )
        db.session.commit()
    except Exception:
        db.session.rollback()


def ensure_default_user():
    if User.query.first() is not None:
        return
    u = User(username="admin", nombre_visible="Administrador", activo=True)
    u.set_password(os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123"))
    db.session.add(u)
    db.session.commit()


def seed_if_empty():
    ensure_default_user()
    if Machine.query.first() is not None:
        return

    t1 = Technician(
        nombre="Carlos Méndez",
        especialidad="Mecánica",
        telefono="555-0101",
        email="cmendez@empresa.com",
    )
    t2 = Technician(
        nombre="Ana Ruiz",
        especialidad="Electricidad",
        telefono="555-0102",
        email="aruiz@empresa.com",
    )
    db.session.add_all([t1, t2])
    db.session.flush()

    mt_cp = MachineType.query.filter_by(clave="compresor").first()
    mt_lp = MachineType.query.filter_by(clave="linea").first()
    if not mt_cp or not mt_lp:
        return

    m1 = Machine(
        codigo="CP-001",
        machine_type_id=mt_cp.id,
        nombre="Compresor principal",
        ubicacion="Planta A",
        status=MachineStatus.OPERATIVO.value,
        es_critico=True,
    )
    m2 = Machine(
        codigo="LP-001",
        machine_type_id=mt_lp.id,
        nombre="Línea de envasado 2",
        ubicacion="Planta B",
        status=MachineStatus.MANTENIMIENTO.value,
        es_critico=True,
    )
    db.session.add_all([m1, m2])
    db.session.flush()

    db.session.add(
        SparePart(
            sku="REP-100",
            nombre="Filtro de aceite",
            categoria="Lubricación",
            cantidad=12,
            stock_minimo=4,
        )
    )
    db.session.add(
        WorkOrder(
            titulo="Inspección mensual compresor",
            tipo=WorkOrderType.PREVENTIVO.value,
            status=WorkOrderStatus.CERRADA.value,
            machine_id=m1.id,
            technician_id=t1.id,
            fecha_programada=date.today(),
            fecha_cierre=datetime.utcnow(),
        )
    )
    db.session.commit()
