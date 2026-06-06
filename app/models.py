import os
import re
from datetime import date, datetime
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


# Roles definidos en app.permissions (re-export para compatibilidad)
from app.permissions import USER_ROLE_LABELS, UserRole  # noqa: E402


class PlanTipo(str, Enum):
    TRIAL = "trial"
    BASICO = "basico"
    PROFESIONAL = "profesional"
    ENTERPRISE = "enterprise"


PLAN_CATALOG = {
    PlanTipo.TRIAL.value: {
        "label": "Prueba gratuita 30 días",
        "descripcion": "Ideal para evaluar la plataforma",
        "max_activos": 100,
        "dias": 30,
    },
    PlanTipo.BASICO.value: {
        "label": "Plan Básico",
        "descripcion": "Hasta 100 activos",
        "max_activos": 100,
        "dias": None,
    },
    PlanTipo.PROFESIONAL.value: {
        "label": "Plan Profesional",
        "descripcion": "Hasta 1.000 activos",
        "max_activos": 1000,
        "dias": None,
    },
    PlanTipo.ENTERPRISE.value: {
        "label": "Plan Enterprise",
        "descripcion": "Activos ilimitados",
        "max_activos": None,
        "dias": None,
    },
}

WORK_ORDER_PRIORITIES = (
    ("baja", "Baja"),
    ("media", "Media"),
    ("alta", "Alta"),
    ("critica", "Crítica"),
)

WORK_ORDER_STATUS_META = {
    "abierta": {
        "label": "Abierta",
        "badge_class": "badge-wo-estado badge-wo-abierta",
        "color": "#f59e0b",
    },
    "en_proceso": {
        "label": "En proceso",
        "badge_class": "badge-wo-estado badge-wo-en-proceso",
        "color": "#2563eb",
    },
    "cerrada": {
        "label": "Cerrada",
        "badge_class": "badge-wo-estado badge-wo-cerrada",
        "color": "#16a34a",
    },
    "completado": {
        "label": "Completado",
        "badge_class": "badge-wo-estado badge-wo-completado",
        "color": "#0d9488",
    },
    "vencida": {
        "label": "Vencida",
        "badge_class": "badge-wo-estado badge-wo-vencida",
        "color": "#dc2626",
    },
    "programada": {
        "label": "Programada",
        "badge_class": "badge-wo-estado badge-wo-programada",
        "color": "#6366f1",
    },
}


def wo_status_meta(status: str) -> dict:
    """Etiqueta, clase CSS y color para el estado de una OT."""
    key = (status or "").strip().lower()
    default = {
        "label": status or "—",
        "badge_class": "badge-wo-estado badge-wo-desconocido",
        "color": "#6c757d",
    }
    return {**default, **WORK_ORDER_STATUS_META.get(key, {})}


WORK_ORDER_TYPE_META = {
    "preventivo": {
        "label": "Preventivo",
        "short": "Prev",
        "badge_class": "badge-wo-tipo badge-wo-tipo-preventivo",
        "color": "#0284c7",
    },
    "correctivo": {
        "label": "Correctivo",
        "short": "Corr",
        "badge_class": "badge-wo-tipo badge-wo-tipo-correctivo",
        "color": "#ea580c",
    },
    "emergencia": {
        "label": "Emergencia",
        "short": "Emer",
        "badge_class": "badge-wo-tipo badge-wo-tipo-emergencia",
        "color": "#dc2626",
    },
}


def wo_tipo_meta(tipo: str) -> dict:
    """Etiqueta, abreviatura, clase CSS y color para el tipo de mantenimiento."""
    key = (tipo or "").strip().lower()
    default = {
        "label": tipo or "—",
        "short": (tipo or "—")[:4],
        "badge_class": "badge-wo-tipo badge-wo-tipo-desconocido",
        "color": "#6c757d",
    }
    return {**default, **WORK_ORDER_TYPE_META.get(key, {})}


def wo_es_editable(status: str) -> bool:
    """False solo si la OT está cerrada (cierre definitivo, sin edición)."""
    return (status or "").strip().lower() != WorkOrderStatus.CERRADA.value


class Empresa(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(32), default="")
    direccion = db.Column(db.String(255), default="")
    ciudad = db.Column(db.String(120), default="")
    pais = db.Column(db.String(120), default="Colombia")
    sector = db.Column(db.String(32), default="manufactura")
    slug = db.Column(db.String(48), unique=True, nullable=True, index=True)
    logo = db.Column(db.String(255), default="")
    telefono = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    moneda = db.Column(db.String(8), default="COP")
    zona_horaria = db.Column(db.String(64), default="America/Bogota")
    jornada_habilitada = db.Column(db.Boolean, default=False)
    jornada_hora_inicio = db.Column(db.String(5), default="08:00")
    jornada_hora_fin = db.Column(db.String(5), default="17:00")
    jornada_dias = db.Column(db.String(32), default="0,1,2,3,4")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    sedes = db.relationship("Sede", back_populates="empresa", lazy="dynamic")
    usuarios = db.relationship("User", back_populates="empresa", lazy="dynamic")
    planes = db.relationship("PlanSuscripcion", back_populates="empresa", lazy="dynamic")

    @property
    def sector_label(self) -> str:
        return SECTOR_LABELS.get(self.sector or "", self.sector or "—")


class Sede(db.Model):
    __tablename__ = "sedes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="sedes")


class PlanSuscripcion(db.Model):
    __tablename__ = "planes_suscripcion"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    plan = db.Column(db.String(32), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="planes")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), default="", index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_visible = db.Column(db.String(120), default="")
    telefono = db.Column(db.String(40), default="")
    area = db.Column(db.String(120), default="")
    sede_id = db.Column(db.Integer, db.ForeignKey("sedes.id"), nullable=True, index=True)
    rol = db.Column(db.String(32), default=UserRole.ADMIN.value)
    activo = db.Column(db.Boolean, default=True)
    onboarding_completado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="usuarios")
    sede = db.relationship("Sede", backref="usuarios")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):  # noqa: D102
        return self.activo

    def etiqueta(self) -> str:
        return (self.nombre_visible or self.username).strip() or self.username

    @property
    def rol_label(self) -> str:
        from app.permissions import normalize_rol

        return USER_ROLE_LABELS.get(normalize_rol(self.rol), self.rol or "—")

    valores_campos = db.relationship(
        "UsuarioCampoValor", back_populates="user", lazy="dynamic", cascade="all, delete-orphan"
    )


class MachineStatus(str, Enum):
    OPERATIVO = "operativo"
    MANTENIMIENTO = "mantenimiento"
    FALLA = "falla"


MACHINE_STATUS_META = {
    MachineStatus.OPERATIVO.value: {
        "label": "Operativo",
        "short": "OPERATIVO",
        "slug": "operativo",
    },
    MachineStatus.MANTENIMIENTO.value: {
        "label": "En mantenimiento",
        "short": "MANTENIMIENTO",
        "slug": "mantenimiento",
    },
    MachineStatus.FALLA.value: {
        "label": "En falla",
        "short": "FALLA",
        "slug": "falla",
    },
}


def machine_status_meta(status: str) -> dict:
    """Etiqueta y slug CSS para el estado operativo del activo."""
    key = (status or "").strip().lower()
    default = {
        "label": status or "—",
        "short": (status or "—").upper()[:14],
        "slug": "desconocido",
    }
    return {**default, **MACHINE_STATUS_META.get(key, {})}


class WorkOrderType(str, Enum):
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"
    EMERGENCIA = "emergencia"


class WorkOrderStatus(str, Enum):
    PROGRAMADA = "programada"
    ABIERTA = "abierta"
    EN_PROCESO = "en_proceso"
    VENCIDA = "vencida"
    CERRADA = "cerrada"
    COMPLETADO = "completado"


WORK_ORDER_TERMINAL_STATUSES = (
    WorkOrderStatus.CERRADA.value,
    WorkOrderStatus.COMPLETADO.value,
)

WORK_ORDER_PENDING_STATUSES = (
    WorkOrderStatus.PROGRAMADA.value,
    WorkOrderStatus.ABIERTA.value,
    WorkOrderStatus.EN_PROCESO.value,
    WorkOrderStatus.VENCIDA.value,
)


class IndustrialSector(str, Enum):
    MANUFACTURA = "manufactura"
    LOGISTICA = "logistica"
    SALUD = "salud"
    MINERIA = "mineria"
    ALIMENTOS = "alimentos"
    CONSTRUCCION = "construccion"
    EDUCACION = "educacion"


from app.sector_templates import (  # noqa: E402
    SECTOR_DASHBOARD_CATEGORIES,
    SECTOR_LABELS,
    normalizar_sector,
)

TYPE_SECTOR_BY_CLAVE = {
    "bomba_agua": IndustrialSector.MANUFACTURA.value,
    "compresor": IndustrialSector.MANUFACTURA.value,
    "linea": IndustrialSector.MANUFACTURA.value,
    "motor": IndustrialSector.MANUFACTURA.value,
    "valvula": IndustrialSector.MANUFACTURA.value,
    "general": IndustrialSector.MANUFACTURA.value,
    "transporte": IndustrialSector.LOGISTICA.value,
    "vehiculo": IndustrialSector.LOGISTICA.value,
    "montacargas": IndustrialSector.LOGISTICA.value,
    "equipo_carga": IndustrialSector.LOGISTICA.value,
    "intercambiador": IndustrialSector.ALIMENTOS.value,
    "cuarto_frio": IndustrialSector.ALIMENTOS.value,
    "horno": IndustrialSector.ALIMENTOS.value,
    "mezcladora": IndustrialSector.ALIMENTOS.value,
}

EXTRA_MACHINE_TYPES_SEED = (
    ("vehiculo", "Vehículo", "VH", IndustrialSector.LOGISTICA.value, 20),
    ("montacargas", "Montacargas", "MC", IndustrialSector.LOGISTICA.value, 21),
    ("equipo_carga", "Equipo de carga", "EC", IndustrialSector.LOGISTICA.value, 22),
    ("cuarto_frio", "Cuarto frío", "CF", IndustrialSector.ALIMENTOS.value, 30),
    ("horno", "Horno", "HN", IndustrialSector.ALIMENTOS.value, 31),
    ("mezcladora", "Mezcladora", "MZ", IndustrialSector.ALIMENTOS.value, 32),
)

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
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    clave = db.Column(db.String(48), nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    prefijo = db.Column(db.String(8), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    sector_industrial = db.Column(
        db.String(32),
        default=IndustrialSector.MANUFACTURA.value,
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    machines = db.relationship("Machine", back_populates="machine_type", lazy="dynamic")

    @property
    def sector_etiqueta(self) -> str:
        return SECTOR_LABELS.get(self.sector_industrial or "", "—")


class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    sede_id = db.Column(db.Integer, db.ForeignKey("sedes.id"), nullable=True)
    parent_machine_id = db.Column(
        db.Integer, db.ForeignKey("machines.id"), nullable=True, index=True
    )
    codigo = db.Column(db.String(64), unique=True, nullable=False)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    registro_tipo = db.Column(db.String(32), default="")
    checklist_registro = db.Column(db.Text, default="[]")
    etiquetas = db.Column(db.Text, default="[]")
    ubicacion = db.Column(db.String(200), default="")
    area = db.Column(db.String(120), default="")
    marca = db.Column(db.String(120), default="")
    modelo = db.Column(db.String(120), default="")
    fabricante = db.Column(db.String(120), default="")
    numero_serie = db.Column(db.String(120), default="")
    fecha_fabricacion = db.Column(db.Date, nullable=True)
    fecha_ingreso = db.Column(db.Date, nullable=True)
    criticidad = db.Column(db.String(32), default="media")
    fecha_instalacion = db.Column(db.Date, nullable=True)
    fecha_puesta_marcha = db.Column(db.Date, nullable=True)
    vida_util_anios = db.Column(db.Integer, nullable=True)
    horas_operacion = db.Column(db.Float, nullable=True)
    fecha_compra = db.Column(db.Date, nullable=True)
    valor_compra = db.Column(db.Float, nullable=True)
    moneda_compra = db.Column(db.String(8), default="")
    proveedor = db.Column(db.String(200), default="")
    tiempo_garantia_meses = db.Column(db.Integer, nullable=True)
    garantia_hasta = db.Column(db.Date, nullable=True)
    manual_url = db.Column(db.String(500), default="")
    ficha_tecnica_url = db.Column(db.String(500), default="")
    foto_url = db.Column(db.String(500), default="")
    requiere_mantenimiento = db.Column(db.Boolean, default=True)
    tipos_mantenimiento = db.Column(db.Text, default="[]")
    frecuencia_mantenimiento = db.Column(db.String(32), default="")
    responsable_technician_id = db.Column(
        db.Integer, db.ForeignKey("technicians.id"), nullable=True, index=True
    )
    status = db.Column(db.String(32), default=MachineStatus.OPERATIVO.value)
    es_critico = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sede = db.relationship("Sede", backref="machines")
    parent = db.relationship("Machine", remote_side=[id], backref="hijos")
    responsable = db.relationship(
        "Technician",
        foreign_keys=[responsable_technician_id],
        backref="activos_responsable",
    )

    @property
    def responsable_nombre(self) -> str:
        """Nombre del técnico responsable en ficha de mantenimiento (respaldo si no hay campo personalizado)."""
        if self.responsable and self.responsable.nombre:
            return self.responsable.nombre
        if not self.responsable_technician_id:
            return ""
        from sqlalchemy import inspect

        sess = inspect(self).session
        if sess is None:
            return ""
        tech = sess.get(Technician, self.responsable_technician_id)
        return (tech.nombre or "") if tech else ""
    machine_type = db.relationship("MachineType", back_populates="machines", lazy="joined")
    work_orders = db.relationship("WorkOrder", backref="machine", lazy="dynamic")
    planificaciones_mensuales = db.relationship(
        "MachineMonthlyPlan",
        back_populates="machine",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    valores_campos = db.relationship(
        "ActivoCampoValor",
        back_populates="machine",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @property
    def tipo_etiqueta(self) -> str:
        return self.machine_type.nombre if self.machine_type else "—"

    @property
    def estado_garantia_etiqueta(self) -> str:
        from app.asset_standard import estado_garantia_etiqueta

        return estado_garantia_etiqueta(self.garantia_hasta)

    @property
    def estado_garantia_badge(self) -> str:
        from app.asset_standard import estado_garantia_badge_class, estado_garantia_etiqueta

        return estado_garantia_badge_class(estado_garantia_etiqueta(self.garantia_hasta))

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

    def sync_criticidad_critico(self) -> None:
        self.es_critico = (self.criticidad or "media") in ("alta", "critica")


class MachineMonthlyPlan(db.Model):
    """Meta de horas mensuales programadas por activo (planeación OT)."""

    __tablename__ = "machine_monthly_plans"
    __table_args__ = (
        db.UniqueConstraint("machine_id", "anio", "mes", name="uq_machine_plan_mes"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    machine_id = db.Column(
        db.Integer, db.ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    anio = db.Column(db.Integer, nullable=False, index=True)
    mes = db.Column(db.Integer, nullable=False, index=True)
    horas_meta = db.Column(db.Float, nullable=True)
    guardado_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = db.relationship("Machine", back_populates="planificaciones_mensuales")

    @property
    def configurado(self) -> bool:
        return self.guardado_at is not None and self.horas_meta is not None

    @property
    def solo_lectura(self) -> bool:
        return self.guardado_at is not None


class CampoPersonalizado(db.Model):
    """Definición de campo dinámico por sector (activos o equipo técnico)."""

    __tablename__ = "campos_personalizados"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    sector = db.Column(db.String(32), nullable=False, index=True)
    entidad = db.Column(db.String(16), default="activo", nullable=False, index=True)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"), nullable=True)
    categorias_ids = db.Column(db.Text, default="")
    clave = db.Column(db.String(64), nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    seccion = db.Column(db.String(80), default="", index=True)
    seccion_ancla = db.Column(db.String(32), default="")
    tipo = db.Column(db.String(16), default="text")
    texto_tamano = db.Column(db.String(16), default="mediano")
    opciones = db.Column(db.Text, default="")
    obligatorio = db.Column(db.Boolean, default=False)
    orden = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    machine_type = db.relationship("MachineType", backref="campos_personalizados")
    valores = db.relationship("ActivoCampoValor", back_populates="campo", lazy="dynamic")
    valores_usuario = db.relationship("UsuarioCampoValor", back_populates="campo", lazy="dynamic")

    @property
    def entidad_label(self) -> str:
        from app.custom_fields import CAMPO_ENTIDAD_LABEL

        key = (self.entidad or "activo").strip().lower()
        return CAMPO_ENTIDAD_LABEL.get(key, key)

    @property
    def tipo_label(self) -> str:
        from app.custom_fields import CAMPO_TIPOS_LABEL, TEXTO_TAMANO_LABEL, normalizar_texto_tamano

        key = (self.tipo or "text").lower()
        base = CAMPO_TIPOS_LABEL.get(key, self.tipo or "—")
        if key == "text":
            tam = TEXTO_TAMANO_LABEL.get(normalizar_texto_tamano(self.texto_tamano), "")
            if tam:
                return f"{base} — {tam}"
        return base

    @property
    def texto_tamano_efectivo(self) -> str:
        from app.custom_fields import TEXTO_TAMANO_DEFAULT, normalizar_texto_tamano

        if (self.tipo or "").lower() != "text":
            return ""
        return normalizar_texto_tamano(self.texto_tamano or TEXTO_TAMANO_DEFAULT)

    @property
    def columna_grid(self) -> str:
        from app.custom_fields import columna_grid_para_campo

        return columna_grid_para_campo(self.tipo, self.texto_tamano)

    def opciones_lista(self) -> list[str]:
        from app.custom_fields import opciones_desde_campo

        return opciones_desde_campo(self)

    def multi_seleccion_desde_valor(self, valor: str | None = "") -> set[str]:
        from app.custom_fields import multi_seleccion_desde_valor

        return multi_seleccion_desde_valor(self, valor)

    def categorias_aplicables(self) -> list[int]:
        from app.custom_fields import categorias_ids_desde_campo

        return categorias_ids_desde_campo(self)

    def aplica_a_tipo(self, machine_type_id: int | None) -> bool:
        from app.custom_fields import campo_aplica_a_tipo

        return campo_aplica_a_tipo(self, machine_type_id)


class ActivoCampoValor(db.Model):
    __tablename__ = "activo_campo_valores"
    __table_args__ = (
        db.UniqueConstraint("machine_id", "campo_id", name="uq_activo_campo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False, index=True)
    campo_id = db.Column(
        db.Integer, db.ForeignKey("campos_personalizados.id"), nullable=False, index=True
    )
    valor = db.Column(db.Text, default="")

    machine = db.relationship("Machine", back_populates="valores_campos")
    campo = db.relationship("CampoPersonalizado", back_populates="valores")


class UsuarioCampoValor(db.Model):
    __tablename__ = "usuario_campo_valores"
    __table_args__ = (
        db.UniqueConstraint("user_id", "campo_id", name="uq_usuario_campo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    campo_id = db.Column(
        db.Integer, db.ForeignKey("campos_personalizados.id"), nullable=False, index=True
    )
    valor = db.Column(db.Text, default="")

    user = db.relationship("User", back_populates="valores_campos")
    campo = db.relationship("CampoPersonalizado", back_populates="valores_usuario")


class PlantillaDashboard(db.Model):
    __tablename__ = "plantillas_dashboard"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, unique=True)
    sector = db.Column(db.String(32), nullable=False)
    config_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    empresa = db.relationship("Empresa", backref=db.backref("plantilla_dashboard", uselist=False))


class Technician(db.Model):
    __tablename__ = "technicians"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    especialidad = db.Column(db.String(120), default="")
    telefono = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    work_orders = db.relationship("WorkOrder", backref="technician", lazy="dynamic")
    user = db.relationship("User", backref=db.backref("technician", uselist=False))


class ProveedorTipo(str, Enum):
    SERVICIO = "servicio"
    INSUMOS = "insumos"
    AMBOS = "ambos"


PROVEEDOR_TIPOS_VALIDOS = frozenset(t.value for t in ProveedorTipo)

PROVEEDOR_TIPO_META = {
    ProveedorTipo.SERVICIO.value: {
        "label": "Servicio",
        "hint": "Hace el mantenimiento",
        "badge_class": "badge-prov-tipo badge-prov-servicio",
        "avatar_class": "prov-avatar prov-avatar--servicio",
        "kpi_class": "prov-kpi-card--servicio",
        "icon": "bi-wrench",
        "color": "#2563eb",
    },
    ProveedorTipo.INSUMOS.value: {
        "label": "Insumos",
        "hint": "Repuestos y materiales",
        "badge_class": "badge-prov-tipo badge-prov-insumos",
        "avatar_class": "prov-avatar prov-avatar--insumos",
        "kpi_class": "prov-kpi-card--insumos",
        "icon": "bi-box-seam",
        "color": "#16a34a",
    },
    ProveedorTipo.AMBOS.value: {
        "label": "Ambos",
        "hint": "Servicio e insumos",
        "badge_class": "badge-prov-tipo badge-prov-ambos",
        "avatar_class": "prov-avatar prov-avatar--ambos",
        "kpi_class": "prov-kpi-card--ambos",
        "icon": "bi-arrow-left-right",
        "color": "#7c3aed",
    },
}


def proveedor_tipo_meta(tipo: str) -> dict:
    key = (tipo or "").strip().lower()
    default = {
        "label": tipo or "—",
        "hint": "",
        "badge_class": "badge-prov-tipo badge-prov-desconocido",
        "avatar_class": "prov-avatar",
        "kpi_class": "",
        "icon": "bi-building",
        "color": "#6c757d",
    }
    return {**default, **PROVEEDOR_TIPO_META.get(key, {})}


def proveedor_iniciales(nombre: str) -> str:
    palabras = [p for p in (nombre or "").split() if p.strip()]
    if not palabras:
        return "?"
    if len(palabras) == 1:
        return palabras[0][:2].upper()
    return (palabras[0][0] + palabras[1][0]).upper()


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(32), default="")
    direccion = db.Column(db.String(255), default="")
    contacto_nombre = db.Column(db.String(200), default="")
    contacto_cargo = db.Column(db.String(120), default="")
    contacto_email = db.Column(db.String(120), default="")
    contacto_telefono = db.Column(db.String(40), default="")
    tipo = db.Column(db.String(16), default=ProveedorTipo.SERVICIO.value, nullable=False)
    observaciones = db.Column(db.Text, default="")
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def iniciales(self) -> str:
        return proveedor_iniciales(self.nombre)

    @property
    def tipo_meta(self) -> dict:
        return proveedor_tipo_meta(self.tipo)


class PreventiveMaintenancePlan(db.Model):
    """Programa de mantenimiento preventivo: una actividad por activo (sin repetir)."""

    __tablename__ = "preventive_maintenance_plans"
    __table_args__ = (
        db.UniqueConstraint("machine_id", "actividad_key", name="uq_prev_plan_machine_actividad"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    machine_id = db.Column(
        db.Integer, db.ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actividad = db.Column(db.String(200), nullable=False)
    actividad_key = db.Column(db.String(220), nullable=False, index=True)
    frecuencia_valor = db.Column(db.Integer, default=1, nullable=False)
    frecuencia_unidad = db.Column(db.String(16), default="meses", nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = db.relationship("Machine", backref=db.backref("planes_preventivos", lazy="dynamic"))
    work_orders = db.relationship("WorkOrder", back_populates="preventive_plan", lazy="dynamic")


class WorkOrder(db.Model):
    __tablename__ = "work_orders"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    numero = db.Column(db.String(32), nullable=True, index=True)
    folio_anio = db.Column(db.Integer, nullable=True)
    folio_seq = db.Column(db.Integer, nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    tipo = db.Column(db.String(32), default=WorkOrderType.CORRECTIVO.value)
    status = db.Column(db.String(32), default=WorkOrderStatus.ABIERTA.value)
    prioridad = db.Column(db.String(32), default="media")
    fecha_programada = db.Column(db.Date, nullable=True)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    tiempo_gastado_minutos = db.Column(db.Integer, nullable=True)
    usar_jornada_laboral = db.Column(db.Boolean, default=False)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=True)
    preventive_plan_id = db.Column(
        db.Integer, db.ForeignKey("preventive_maintenance_plans.id"), nullable=True, index=True
    )
    frecuencia_valor = db.Column(db.Integer, nullable=True)
    frecuencia_unidad = db.Column(db.String(16), nullable=True)
    ubicacion = db.Column(db.String(200), default="")
    area = db.Column(db.String(120), default="")
    autorizado_por = db.Column(db.String(120), default="")
    recibido_por = db.Column(db.String(120), default="")
    empresa_tercerizada = db.Column(db.String(200), default="")
    maquina_requirio_paro = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    preventive_plan = db.relationship(
        "PreventiveMaintenancePlan", back_populates="work_orders"
    )
    jornadas = db.relationship(
        "WorkOrderJornada",
        back_populates="work_order",
        cascade="all, delete-orphan",
        order_by="WorkOrderJornada.orden",
    )
    repuestos = db.relationship(
        "WorkOrderRepuesto",
        back_populates="work_order",
        cascade="all, delete-orphan",
    )

    @property
    def usa_repuestos(self) -> bool:
        return len(self.repuestos) > 0

    @property
    def tiempo_gastado_label(self) -> str:
        from app.work_time import formatear_duracion, wo_tiempo_gastado_minutos

        return formatear_duracion(wo_tiempo_gastado_minutos(self))

    @property
    def num_jornadas(self) -> int:
        return len(self.jornadas)

    @property
    def status_meta(self) -> dict:
        return wo_status_meta(self.status)

    @property
    def es_editable(self) -> bool:
        return wo_es_editable(self.status)


class WorkOrderJornada(db.Model):
    """Sesión de trabajo en una OT (ej. 3:30–4:30 y luego 17:00–18:30 el mismo día)."""

    __tablename__ = "work_order_jornadas"

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(
        db.Integer, db.ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    orden = db.Column(db.Integer, default=1)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=True)
    tecnico_nombre = db.Column(db.String(200), default="")
    descripcion_avance = db.Column(db.Text, default="")

    work_order = db.relationship("WorkOrder", back_populates="jornadas")
    technician = db.relationship("Technician", backref="jornadas_orden")

    @property
    def duracion_minutos(self) -> int:
        from app.work_time import minutos_entre

        return minutos_entre(self.fecha_inicio, self.fecha_fin)

    @property
    def tecnico_label(self) -> str:
        if self.technician_id and self.technician:
            return self.technician.nombre
        return self.tecnico_nombre or "—"


class WorkOrderRepuesto(db.Model):
    """Repuesto consumido en una OT correctiva."""

    __tablename__ = "work_order_repuestos"

    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(
        db.Integer, db.ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    spare_part_id = db.Column(db.Integer, db.ForeignKey("spare_parts.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    notas = db.Column(db.String(255), default="")

    work_order = db.relationship("WorkOrder", back_populates="repuestos")
    spare_part = db.relationship("SparePart", backref="usos_en_ordenes")

    @property
    def costo_unitario_linea(self) -> float:
        if self.spare_part:
            return float(self.spare_part.costo_unitario or 0)
        return 0.0

    @property
    def costo_total_linea(self) -> float:
        return round(self.costo_unitario_linea * int(self.cantidad or 0), 2)


class SparePart(db.Model):
    __tablename__ = "spare_parts"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    sku = db.Column(db.String(64), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(120), default="")
    unidad = db.Column(db.String(32), default="pza")
    cantidad = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    ubicacion_almacen = db.Column(db.String(120), default="")
    costo_unitario = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def costo_total(self) -> float:
        return round(float(self.costo_unitario or 0) * int(self.cantidad or 0), 2)


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    reportado_en = db.Column(db.DateTime, default=datetime.utcnow)
    resuelto = db.Column(db.Boolean, default=False)

    machine = db.relationship("Machine", backref="incidents")
    empresa = db.relationship("Empresa", backref="incidents")


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
            MachineType(
                clave=clave,
                nombre=nombre,
                prefijo=prefijo.upper(),
                orden=i,
                activo=True,
                sector_industrial=TYPE_SECTOR_BY_CLAVE.get(
                    clave, IndustrialSector.MANUFACTURA.value
                ),
            )
        )
    db.session.commit()


def ensure_machine_types_sector_column():
    """SQLite: columna sector_industrial, valores por clave y tipos extra por sector."""
    from sqlalchemy import func, inspect, text

    try:
        insp = inspect(db.engine)
        if "machine_types" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("machine_types")}
        if "sector_industrial" not in cols:
            with db.engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE machine_types ADD COLUMN sector_industrial VARCHAR(32)"
                    )
                )
            db.session.execute(
                text(
                    "UPDATE machine_types SET sector_industrial = :m WHERE sector_industrial IS NULL"
                ),
                {"m": IndustrialSector.MANUFACTURA.value},
            )
            db.session.commit()

        for clave, sector in TYPE_SECTOR_BY_CLAVE.items():
            db.session.execute(
                text(
                    "UPDATE machine_types SET sector_industrial = :s WHERE clave = :c"
                ),
                {"s": sector, "c": clave},
            )
        db.session.commit()

        max_orden = db.session.query(func.max(MachineType.orden)).scalar() or 0
        for clave, nombre, prefijo, sector, orden in EXTRA_MACHINE_TYPES_SEED:
            if MachineType.query.filter_by(clave=clave).first() is not None:
                continue
            db.session.add(
                MachineType(
                    clave=clave,
                    nombre=nombre,
                    prefijo=prefijo.upper(),
                    sector_industrial=sector,
                    orden=orden if orden else max_orden + 1,
                    activo=True,
                )
            )
            max_orden += 1
        db.session.commit()
    except Exception:
        db.session.rollback()


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


def _add_column_if_missing(table: str, column: str, ddl: str) -> None:
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if table not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns(table)}
    if column not in cols:
        with db.engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))


def _backfill_empresa_slugs() -> None:
    """Asigna slug a empresas existentes sin slug (JWT / identificación)."""
    from sqlalchemy import or_

    from app.tenancy.slug import slug_unico_empresa

    pendientes = Empresa.query.filter(or_(Empresa.slug.is_(None), Empresa.slug == "")).all()
    if not pendientes:
        return
    for emp in pendientes:
        emp.slug = slug_unico_empresa(emp.razon_social or f"empresa-{emp.id}", excluir_id=emp.id)
        db.session.add(emp)
    db.session.commit()


def ensure_saas_schema():
    """Columnas multi-empresa, prioridad en OT y tablas de onboarding."""
    from sqlalchemy import inspect, text

    try:
        db.create_all()
        _add_column_if_missing("users", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("users", "email", "email VARCHAR(120)")
        _add_column_if_missing("users", "telefono", "telefono VARCHAR(40)")
        _add_column_if_missing("users", "rol", "rol VARCHAR(32)")
        _add_column_if_missing("users", "area", "area VARCHAR(120)")
        _add_column_if_missing("users", "sede_id", "sede_id INTEGER")
        _add_column_if_missing(
            "users", "onboarding_completado", "onboarding_completado BOOLEAN DEFAULT 0"
        )
        _add_column_if_missing("machine_types", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("machines", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("machines", "sede_id", "sede_id INTEGER")
        _add_column_if_missing("machines", "parent_machine_id", "parent_machine_id INTEGER")
        _add_column_if_missing("machines", "etiquetas", "etiquetas TEXT")
        _add_column_if_missing("machines", "area", "area VARCHAR(120)")
        _add_column_if_missing("machines", "fabricante", "fabricante VARCHAR(120)")
        _add_column_if_missing("machines", "anio_fabricacion", "anio_fabricacion INTEGER")
        _add_column_if_missing("machines", "fecha_instalacion", "fecha_instalacion DATE")
        _add_column_if_missing("machines", "fecha_puesta_marcha", "fecha_puesta_marcha DATE")
        _add_column_if_missing("machines", "vida_util_anios", "vida_util_anios INTEGER")
        _add_column_if_missing("machines", "horas_operacion", "horas_operacion REAL")
        _add_column_if_missing("machines", "valor_compra", "valor_compra REAL")
        _add_column_if_missing("machines", "garantia_hasta", "garantia_hasta DATE")
        _add_column_if_missing("machines", "ficha_tecnica_url", "ficha_tecnica_url VARCHAR(500)")
        _add_column_if_missing(
            "machines", "requiere_mantenimiento", "requiere_mantenimiento BOOLEAN DEFAULT 1"
        )
        _add_column_if_missing("machines", "tipos_mantenimiento", "tipos_mantenimiento TEXT")
        _add_column_if_missing(
            "machines", "frecuencia_mantenimiento", "frecuencia_mantenimiento VARCHAR(32)"
        )
        _add_column_if_missing(
            "machines", "responsable_technician_id", "responsable_technician_id INTEGER"
        )
        _add_column_if_missing("campos_personalizados", "seccion", "seccion VARCHAR(80)")
        _add_column_if_missing("campos_personalizados", "seccion_ancla", "seccion_ancla VARCHAR(32)")
        _add_column_if_missing("technicians", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("technicians", "user_id", "user_id INTEGER")
        _add_column_if_missing("work_orders", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("work_orders", "numero", "numero VARCHAR(32)")
        _add_column_if_missing("work_orders", "folio_anio", "folio_anio INTEGER")
        _add_column_if_missing("work_orders", "folio_seq", "folio_seq INTEGER")
        _add_column_if_missing("work_orders", "prioridad", "prioridad VARCHAR(32) DEFAULT 'media'")
        _add_column_if_missing(
            "work_orders", "tiempo_gastado_minutos", "tiempo_gastado_minutos INTEGER"
        )
        _add_column_if_missing(
            "work_orders",
            "usar_jornada_laboral",
            "usar_jornada_laboral BOOLEAN DEFAULT 0",
        )
        _add_column_if_missing(
            "work_order_jornadas", "technician_id", "technician_id INTEGER"
        )
        _add_column_if_missing(
            "work_order_jornadas", "tecnico_nombre", "tecnico_nombre VARCHAR(200)"
        )
        _add_column_if_missing(
            "work_order_jornadas", "descripcion_avance", "descripcion_avance TEXT"
        )
        _add_column_if_missing(
            "empresas", "jornada_habilitada", "jornada_habilitada BOOLEAN DEFAULT 0"
        )
        _add_column_if_missing(
            "empresas", "jornada_hora_inicio", "jornada_hora_inicio VARCHAR(5) DEFAULT '08:00'"
        )
        _add_column_if_missing(
            "empresas", "jornada_hora_fin", "jornada_hora_fin VARCHAR(5) DEFAULT '17:00'"
        )
        _add_column_if_missing(
            "empresas", "jornada_dias", "jornada_dias VARCHAR(32) DEFAULT '0,1,2,3,4'"
        )
        _add_column_if_missing("spare_parts", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing(
            "spare_parts", "costo_unitario", "costo_unitario REAL DEFAULT 0"
        )
        _add_column_if_missing(
            "work_orders", "preventive_plan_id", "preventive_plan_id INTEGER"
        )
        _add_column_if_missing(
            "work_orders", "frecuencia_valor", "frecuencia_valor INTEGER"
        )
        _add_column_if_missing(
            "work_orders", "frecuencia_unidad", "frecuencia_unidad VARCHAR(16)"
        )
        _add_column_if_missing("work_orders", "ubicacion", "ubicacion VARCHAR(200)")
        _add_column_if_missing("work_orders", "area", "area VARCHAR(120)")
        _add_column_if_missing("work_orders", "autorizado_por", "autorizado_por VARCHAR(120)")
        _add_column_if_missing("work_orders", "recibido_por", "recibido_por VARCHAR(120)")
        _add_column_if_missing(
            "work_orders", "empresa_tercerizada", "empresa_tercerizada VARCHAR(200)"
        )
        _add_column_if_missing(
            "work_orders",
            "maquina_requirio_paro",
            "maquina_requirio_paro BOOLEAN DEFAULT 0",
        )
        _add_column_if_missing("campos_personalizados", "opciones", "opciones TEXT")
        _add_column_if_missing("campos_personalizados", "categorias_ids", "categorias_ids TEXT")
        _add_column_if_missing(
            "campos_personalizados", "entidad", "entidad VARCHAR(16) DEFAULT 'activo'"
        )
        _add_column_if_missing(
            "campos_personalizados",
            "texto_tamano",
            "texto_tamano VARCHAR(16) DEFAULT 'mediano'",
        )
        _add_column_if_missing("empresas", "telefono", "telefono VARCHAR(40)")
        _add_column_if_missing("empresas", "email", "email VARCHAR(120)")
        _add_column_if_missing("empresas", "slug", "slug VARCHAR(48)")
        _add_column_if_missing("incidents", "empresa_id", "empresa_id INTEGER")
        ensure_asset_base_columns()
        _backfill_empresa_slugs()
        ensure_sector_plantilla_schema()
        migrate_legacy_tenant()
        from app.wo_numbering import backfill_work_order_numeros

        backfill_work_order_numeros()
    except Exception:
        db.session.rollback()


def ensure_asset_base_columns():
    """Campos base unificados del activo (todos los sectores)."""
    _add_column_if_missing("machines", "descripcion", "descripcion TEXT")
    _add_column_if_missing("machines", "numero_serie", "numero_serie VARCHAR(120)")
    _add_column_if_missing("machines", "criticidad", "criticidad VARCHAR(32) DEFAULT 'media'")
    _add_column_if_missing("machines", "fecha_compra", "fecha_compra DATE")
    _add_column_if_missing("machines", "proveedor", "proveedor VARCHAR(200)")
    _add_column_if_missing("machines", "manual_url", "manual_url VARCHAR(500)")
    _add_column_if_missing("machines", "foto_url", "foto_url VARCHAR(500)")
    _add_column_if_missing("machines", "registro_tipo", "registro_tipo VARCHAR(32)")
    _add_column_if_missing("machines", "checklist_registro", "checklist_registro TEXT")
    _add_column_if_missing("machines", "fecha_fabricacion", "fecha_fabricacion DATE")
    _add_column_if_missing("machines", "fecha_ingreso", "fecha_ingreso DATE")
    _add_column_if_missing("machines", "tiempo_garantia_meses", "tiempo_garantia_meses INTEGER")
    _add_column_if_missing("machines", "moneda_compra", "moneda_compra VARCHAR(8)")
    _migrate_anio_fabricacion_a_fecha()


def _migrate_anio_fabricacion_a_fecha() -> None:
    """Convierte anio_fabricacion (entero) legado a fecha_fabricacion."""
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if "machines" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("machines")}
    if "anio_fabricacion" not in cols or "fecha_fabricacion" not in cols:
        return
    with db.engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE machines SET fecha_fabricacion = "
                "printf('%04d-01-01', anio_fabricacion) "
                "WHERE anio_fabricacion IS NOT NULL AND fecha_fabricacion IS NULL"
            )
        )


def ensure_sector_plantilla_schema():
    db.create_all()


def migrate_legacy_tenant():
    """Usuarios y datos existentes → empresa por defecto con onboarding ya completado."""
    from sqlalchemy import text

    if Empresa.query.first() is not None:
        return
    users = User.query.all()
    if not users:
        return
    emp = Empresa(
        razon_social="Organización existente",
        nit="",
        ciudad="",
        sector=IndustrialSector.MANUFACTURA.value,
    )
    db.session.add(emp)
    db.session.flush()
    sede = Sede(empresa_id=emp.id, nombre="Sede principal", es_principal=True)
    db.session.add(sede)
    db.session.flush()
    hoy = date.today()
    db.session.add(
        PlanSuscripcion(
            empresa_id=emp.id,
            plan=PlanTipo.PROFESIONAL.value,
            fecha_inicio=hoy,
            fecha_fin=None,
            activo=True,
        )
    )
    for u in users:
        u.empresa_id = emp.id
        u.onboarding_completado = True
        if not u.rol:
            u.rol = UserRole.ADMIN.value
    for table in ("machines", "technicians", "work_orders", "spare_parts", "incidents", "proveedores"):
        try:
            db.session.execute(
                text(f"UPDATE {table} SET empresa_id = :e WHERE empresa_id IS NULL"),
                {"e": emp.id},
            )
        except Exception:
            pass
    try:
        db.session.execute(
            text(
                """
                UPDATE incidents
                SET empresa_id = (
                    SELECT machines.empresa_id FROM machines
                    WHERE machines.id = incidents.machine_id
                )
                WHERE empresa_id IS NULL AND machine_id IS NOT NULL
                """
            )
        )
    except Exception:
        pass
    db.session.commit()


def ensure_default_user():
    if User.query.first() is not None:
        return
    u = User(
        username="admin",
        nombre_visible="Administrador",
        activo=True,
        onboarding_completado=False,
        rol=UserRole.SUPERADMIN.value,
    )
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

    emp = Empresa.query.first()
    eid = emp.id if emp else None
    m1 = Machine(
        codigo="CP-001",
        empresa_id=eid,
        machine_type_id=mt_cp.id,
        nombre="Compresor principal",
        ubicacion="Planta A",
        status=MachineStatus.OPERATIVO.value,
        es_critico=True,
    )
    m2 = Machine(
        codigo="LP-001",
        empresa_id=eid,
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
            costo_unitario=45000.0,
        )
    )
    wo_seed = WorkOrder(
        empresa_id=eid,
        titulo="Inspección mensual compresor",
        tipo=WorkOrderType.PREVENTIVO.value,
        status=WorkOrderStatus.CERRADA.value,
        prioridad="media",
        machine_id=m1.id,
        technician_id=t1.id,
        fecha_programada=date.today(),
        fecha_cierre=datetime.utcnow(),
    )
    db.session.add(wo_seed)
    db.session.flush()
    from app.wo_numbering import asignar_numero_ot

    asignar_numero_ot(wo_seed)
    db.session.commit()
