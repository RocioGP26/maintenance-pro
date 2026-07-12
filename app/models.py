import os
import re
import json
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
        "label": "Prueba gratuita 15 días",
        "short_label": "Trial",
        "descripcion": "Ideal para evaluar la plataforma",
        "max_activos": 100,
        "dias": 15,
        "precio_mensual": 0,
    },
    PlanTipo.BASICO.value: {
        "label": "Plan Start",
        "short_label": "Start",
        "descripcion": "Digitaliza tu operación en menos de una semana",
        "max_activos": 100,
        "dias": None,
        "precio_mensual": 490_000,
    },
    PlanTipo.PROFESIONAL.value: {
        "label": "Plan Scale",
        "short_label": "Scale",
        "descripcion": "Control multisede y mayor volumen",
        "max_activos": 1000,
        "dias": None,
        "precio_mensual": 1_290_000,
    },
    PlanTipo.ENTERPRISE.value: {
        "label": "Plan Enterprise",
        "short_label": "Enterprise",
        "descripcion": "Activos ilimitados",
        "max_activos": None,
        "dias": None,
        "precio_mensual": 3_490_000,
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
        "label": "Completada",
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
    monedas_activas_json = db.Column(db.Text, default='["COP"]')
    zona_horaria = db.Column(db.String(64), default="America/Bogota")
    jornada_habilitada = db.Column(db.Boolean, default=False)
    jornada_hora_inicio = db.Column(db.String(5), default="08:00")
    jornada_hora_fin = db.Column(db.String(5), default="17:00")
    jornada_dias = db.Column(db.String(32), default="0,1,2,3,4")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    suspendida = db.Column(db.Boolean, default=False, nullable=False)
    modulos_activos_json = db.Column(db.Text, default='["mantenimiento"]')

    sedes = db.relationship("Sede", back_populates="empresa", lazy="dynamic")
    usuarios = db.relationship("User", back_populates="empresa", lazy="dynamic")
    planes = db.relationship("PlanSuscripcion", back_populates="empresa", lazy="dynamic")

    @property
    def sector_label(self) -> str:
        from app.platform_config_service import etiqueta_sector

        return etiqueta_sector(self.sector or "")

    @property
    def modulos_activos(self) -> list[str]:
        from app.modules import modulos_activos_de

        return modulos_activos_de(self)

    def tiene_modulo(self, modulo: str) -> bool:
        from app.modules import empresa_tiene_modulo

        return empresa_tiene_modulo(self, modulo)

    @property
    def monedas_activas(self) -> list[str]:
        from app.currency import monedas_activas_de

        return monedas_activas_de(self)

    @property
    def multimoneda(self) -> bool:
        from app.currency import empresa_multimoneda

        return empresa_multimoneda(self)

    @property
    def plan_activo(self) -> "PlanSuscripcion | None":
        return (
            PlanSuscripcion.query.filter_by(empresa_id=self.id, activo=True)
            .order_by(PlanSuscripcion.created_at.desc())
            .first()
        )

    def iniciales(self) -> str:
        partes = [p for p in re.split(r"\s+", (self.razon_social or "").strip()) if p]
        if not partes:
            return "?"
        if len(partes) == 1:
            return partes[0][:2].upper()
        return (partes[0][0] + partes[1][0]).upper()


class Sede(db.Model):
    __tablename__ = "sedes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="sedes")


class SuscripcionEstado(str, Enum):
    TRIAL = "trial"
    ACTIVA = "activa"
    MORA = "mora"
    SUSPENDIDA = "suspendida"


class PlanSuscripcion(db.Model):
    __tablename__ = "planes_suscripcion"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False)
    plan = db.Column(db.String(32), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    estado_ciclo = db.Column(db.String(16), default=SuscripcionEstado.TRIAL.value)
    pasarela_customer_id = db.Column(db.String(120), default="")
    pasarela_subscription_id = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", back_populates="planes")
    facturas = db.relationship("FacturaEmpresa", back_populates="suscripcion", lazy="dynamic")


class FacturaEstado(str, Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    VENCIDA = "vencida"
    ANULADA = "anulada"


FACTURA_ESTADO_LABELS = {
    FacturaEstado.PENDIENTE.value: "Pendiente",
    FacturaEstado.PAGADA.value: "Pagada",
    FacturaEstado.VENCIDA.value: "Vencida",
    FacturaEstado.ANULADA.value: "Anulada",
}


class FacturaEmpresa(db.Model):
    """Factura de suscripción SaaS por tenant."""

    __tablename__ = "facturas_empresa"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    suscripcion_id = db.Column(
        db.Integer, db.ForeignKey("planes_suscripcion.id"), nullable=True, index=True
    )
    numero = db.Column(db.String(32), nullable=False)
    concepto = db.Column(db.String(200), default="Suscripción mensual")
    monto = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(8), default="COP")
    periodo = db.Column(db.String(7), nullable=True, index=True)  # YYYY-MM
    estado = db.Column(db.String(16), default=FacturaEstado.PENDIENTE.value)
    fecha_emision = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    fecha_pago = db.Column(db.Date, nullable=True)
    metodo_pago = db.Column(db.String(64), default="")
    referencia_pago = db.Column(db.String(120), default="")
    pasarela_payment_id = db.Column(db.String(120), default="")
    notas = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    empresa = db.relationship("Empresa", backref=db.backref("facturas", lazy="dynamic"))
    suscripcion = db.relationship("PlanSuscripcion", back_populates="facturas")


class TenantActivityLog(db.Model):
    """Auditoría de actividad por tenant (logins, impersonación, etc.)."""

    __tablename__ = "tenant_activity_log"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    username = db.Column(db.String(80), default="")
    tipo = db.Column(db.String(32), nullable=False, index=True)
    detalle = db.Column(db.String(500), default="")
    ip_address = db.Column(db.String(45), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    empresa = db.relationship("Empresa", backref=db.backref("actividad_logs", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("actividad_logs", lazy="dynamic"))


class PlatformAuditLog(db.Model):
    """Auditoría de acciones del superadmin de plataforma (visible al cliente)."""

    __tablename__ = "platform_audit_log"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    accion = db.Column(db.String(32), nullable=False, index=True)
    actor_label = db.Column(db.String(120), nullable=False, default="Soporte Maintix")
    detalle = db.Column(db.String(500), default="")
    ip_address = db.Column(db.String(45), default="")
    visible_cliente = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    empresa = db.relationship("Empresa", backref=db.backref("auditoria_plataforma", lazy="dynamic"))
    user = db.relationship("User", backref=db.backref("auditoria_plataforma", lazy="dynamic"))


class CatalogoPlan(db.Model):
    """Plan comercial editable desde el panel de plataforma."""

    __tablename__ = "catalogo_planes"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(32), unique=True, nullable=False, index=True)
    label = db.Column(db.String(120), nullable=False, default="")
    short_label = db.Column(db.String(32), nullable=False, default="")
    descripcion = db.Column(db.String(255), default="")
    precio_mensual = db.Column(db.Float, default=0, nullable=False)
    precio_anual = db.Column(db.Float, nullable=True)
    max_usuarios = db.Column(db.Integer, nullable=True)
    max_activos = db.Column(db.Integer, nullable=True)
    storage_mb = db.Column(db.Integer, nullable=True)
    soporte = db.Column(db.String(40), default="Email")
    visible_registro = db.Column(db.Boolean, default=True, nullable=False)
    destacado = db.Column(db.Boolean, default=False, nullable=False)
    orden = db.Column(db.Integer, default=0, nullable=False)
    caracteristicas_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def caracteristicas(self) -> list[dict]:
        try:
            data = json.loads(self.caracteristicas_json or "[]")
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_caracteristicas(self, items: list[dict]) -> None:
        self.caracteristicas_json = json.dumps(items, ensure_ascii=False)


class ReglaPlataforma(db.Model):
    """Reglas globales (trial, mora, etc.) — una fila por clave."""

    __tablename__ = "reglas_plataforma"

    clave = db.Column(db.String(64), primary_key=True)
    valor = db.Column(db.String(255), nullable=False, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SectorCatalogo(db.Model):
    """Sectores industriales visibles en registro y filtros."""

    __tablename__ = "sectores_catalogo"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(32), unique=True, nullable=False, index=True)
    etiqueta = db.Column(db.String(120), nullable=False)
    visible_registro = db.Column(db.Boolean, default=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    orden = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "username", name="uq_user_empresa_username"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    email = db.Column(db.String(120), default="", index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre_visible = db.Column(db.String(120), default="")
    telefono = db.Column(db.String(40), default="")
    area = db.Column(db.String(120), default="")
    cargo = db.Column(db.String(120), default="")
    sede_id = db.Column(db.Integer, db.ForeignKey("sedes.id"), nullable=True, index=True)
    rol = db.Column(db.String(32), default=UserRole.ADMIN.value)
    activo = db.Column(db.Boolean, default=True)
    bloqueado = db.Column(db.Boolean, default=False, nullable=False)
    bloqueado_en = db.Column(db.DateTime, nullable=True)
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
        return bool(self.activo) and not bool(self.bloqueado)

    def etiqueta(self) -> str:
        return (self.nombre_visible or self.username).strip() or self.username

    @property
    def rol_label(self) -> str:
        from app.permissions import role_display_label

        return role_display_label(self.rol, empresa=self.empresa)

    valores_campos = db.relationship(
        "UsuarioCampoValor", back_populates="user", lazy="dynamic", cascade="all, delete-orphan"
    )


class SupportArea(db.Model):
    """Cola de atención de incidentes dentro de una empresa."""

    __tablename__ = "support_areas"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "nombre", name="uq_support_area_empresa_nombre"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    membresias = db.relationship("UserSupportArea", back_populates="area_soporte", cascade="all, delete-orphan")


class UserSupportArea(db.Model):
    """Membresía y capacidades de un usuario en una cola de soporte."""

    __tablename__ = "user_support_areas"
    __table_args__ = (
        db.UniqueConstraint("user_id", "support_area_id", name="uq_user_support_area"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    support_area_id = db.Column(db.Integer, db.ForeignKey("support_areas.id"), nullable=False, index=True)
    puede_recibir = db.Column(db.Boolean, default=False, nullable=False)
    puede_asignar = db.Column(db.Boolean, default=False, nullable=False)
    puede_atender = db.Column(db.Boolean, default=False, nullable=False)
    puede_diagnosticar = db.Column(db.Boolean, default=False, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship("User", backref=db.backref("membresias_soporte", cascade="all, delete-orphan"))
    area_soporte = db.relationship("SupportArea", back_populates="membresias")


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


class WorkOrderEjecucionTipo(str, Enum):
    INTERNO = "interno"
    EXTERNO = "externo"


WORK_ORDER_EJECUCION_LABELS = {
    WorkOrderEjecucionTipo.INTERNO.value: "Interno",
    WorkOrderEjecucionTipo.EXTERNO.value: "Externo",
}


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
    numero_factura = db.Column(db.String(80), default="")
    valor_compra = db.Column(db.Float, nullable=True)
    moneda_compra = db.Column(db.String(8), default="")
    proveedor = db.Column(db.String(200), default="")
    proveedor_id = db.Column(
        db.Integer, db.ForeignKey("proveedores.id"), nullable=True, index=True
    )
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
    custodio_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    support_area_id = db.Column(db.Integer, db.ForeignKey("support_areas.id"), nullable=True, index=True)
    responsable_area = db.Column(db.String(120), default="")
    responsable_cargo = db.Column(db.String(120), default="")
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
    custodio = db.relationship("User", foreign_keys=[custodio_user_id])
    area_tecnica = db.relationship("SupportArea", foreign_keys=[support_area_id])
    proveedor_relacionado = db.relationship(
        "Proveedor",
        foreign_keys=[proveedor_id],
        backref="activos",
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

    work_orders = db.relationship(
        "WorkOrder",
        foreign_keys="WorkOrder.technician_id",
        backref=db.backref("technician"),
        lazy="dynamic",
    )
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
    ejecucion_tipo = db.Column(
        db.String(16), default=WorkOrderEjecucionTipo.INTERNO.value, nullable=False
    )
    proveedor_id = db.Column(
        db.Integer, db.ForeignKey("proveedores.id"), nullable=True, index=True
    )
    supervisor_technician_id = db.Column(
        db.Integer, db.ForeignKey("technicians.id"), nullable=True, index=True
    )
    contacto_proveedor = db.Column(db.String(200), default="")
    numero_cotizacion = db.Column(db.String(64), default="")
    costo_estimado = db.Column(db.Float, nullable=True)
    costo_real = db.Column(db.Float, nullable=True)
    proveedor_incluye_insumos = db.Column(db.Boolean, default=False)
    fecha_limite = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    proveedor = db.relationship("Proveedor", backref=db.backref("work_orders", lazy="dynamic"))
    supervisor = db.relationship(
        "Technician",
        foreign_keys=[supervisor_technician_id],
        backref=db.backref("ordenes_supervisadas", lazy="dynamic"),
    )

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

    @property
    def es_ejecucion_externa(self) -> bool:
        return (self.ejecucion_tipo or "").strip().lower() == WorkOrderEjecucionTipo.EXTERNO.value

    @property
    def ejecucion_label(self) -> str:
        key = (self.ejecucion_tipo or WorkOrderEjecucionTipo.INTERNO.value).strip().lower()
        return WORK_ORDER_EJECUCION_LABELS.get(key, key)


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


# --- Módulo inventario comercial (prefijo inv_, sin FK cruzadas a mantenimiento) ---


class InvCliente(db.Model):
    """Cliente del módulo inventario comercial (comprador final)."""

    __tablename__ = "inv_clientes"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    documento = db.Column(db.String(32), default="")
    telefono = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    direccion = db.Column(db.String(255), default="")
    notas = db.Column(db.Text, default="")
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ventas = db.relationship("InvVenta", back_populates="cliente", lazy="dynamic")


class InvProveedor(db.Model):
    """Proveedor comercial: a quién le compro para revender (≠ proveedor de servicio OT)."""

    __tablename__ = "inv_proveedores"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(32), default="")
    contacto_nombre = db.Column(db.String(200), default="")
    contacto_email = db.Column(db.String(120), default="")
    contacto_telefono = db.Column(db.String(40), default="")
    direccion = db.Column(db.String(255), default="")
    observaciones = db.Column(db.Text, default="")
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InvProducto(db.Model):
    __tablename__ = "inv_productos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    sku = db.Column(db.String(64), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    marca = db.Column(db.String(120), default="")
    categoria = db.Column(db.String(120), default="")
    subcategoria = db.Column(db.String(120), default="")
    ubicacion = db.Column(db.String(120), default="")
    imagen = db.Column(db.String(255), default="")
    unidad = db.Column(db.String(32), default="pza")
    stock = db.Column(db.Integer, default=0, nullable=False)
    stock_minimo = db.Column(db.Integer, default=0, nullable=False)
    precio_compra = db.Column(db.Float, default=0.0)
    precio_venta = db.Column(db.Float, default=0.0)
    precios_json = db.Column(db.Text, default="{}")
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("empresa_id", "sku", name="uq_inv_producto_empresa_sku"),
    )

    @property
    def bajo_stock(self) -> bool:
        return int(self.stock or 0) <= int(self.stock_minimo or 0)

    @property
    def imagen_publica(self) -> str | None:
        from app.inventario_comercial.media import producto_imagen_url_or_none

        return producto_imagen_url_or_none(self)

    def precios_venta(self, moneda_referencia: str = "USD") -> dict[str, float]:
        from app.currency import precios_producto

        return precios_producto(self, moneda_referencia)

    def precio_venta_en(self, moneda: str, moneda_referencia: str = "USD") -> float:
        from app.currency import precio_producto_en

        return precio_producto_en(self, moneda, moneda_referencia)


class InvCompra(db.Model):
    __tablename__ = "inv_compras"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("inv_proveedores.id"), nullable=True, index=True)
    numero = db.Column(db.String(32), default="")
    moneda_factura = db.Column(db.String(8), default="COP")
    tasa_cambio = db.Column(db.Float, default=1.0)
    tipo_iva = db.Column(db.String(16), default="exento")
    subtotal = db.Column(db.Float, default=0.0)
    monto_iva = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    notas = db.Column(db.Text, default="")
    fecha = db.Column(db.Date, nullable=False)
    fecha_factura = db.Column(db.Date, nullable=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    estado_pago = db.Column(db.String(16), default="pendiente")
    monto_pagado = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    proveedor = db.relationship("InvProveedor", backref="compras")
    pagos = db.relationship(
        "InvCompraPago",
        back_populates="compra",
        lazy="joined",
        cascade="all, delete-orphan",
        order_by="InvCompraPago.fecha.desc()",
    )
    lineas = db.relationship(
        "InvCompraLinea",
        back_populates="compra",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    @property
    def dias_hasta_vencimiento(self) -> int | None:
        if not self.fecha_vencimiento:
            return None
        from datetime import date as _date

        return (self.fecha_vencimiento - _date.today()).days

    @property
    def cxp_vencida(self) -> bool:
        d = self.dias_hasta_vencimiento
        return d is not None and d < 0

    @property
    def cxp_por_vencer(self) -> bool:
        d = self.dias_hasta_vencimiento
        return d is not None and 0 <= d <= 7

    @property
    def saldo_pendiente(self) -> float:
        return max(0.0, round(float(self.total or 0) - float(self.monto_pagado or 0), 2))

    @property
    def estado_pago_label(self) -> str:
        labels = {"pagada": "Pagada", "pendiente": "Pendiente", "parcial": "Abono parcial"}
        return labels.get((self.estado_pago or "").strip().lower(), self.estado_pago or "—")

    @property
    def cxp_activa(self) -> bool:
        return self.saldo_pendiente > 0 and float(self.total or 0) > 0


class InvCompraPago(db.Model):
    """Pago o abono registrado sobre una compra / cuenta por pagar."""

    __tablename__ = "inv_compra_pagos"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("inv_compras.id"), nullable=False, index=True)
    monto = db.Column(db.Float, default=0.0, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cuenta_origen = db.Column(db.String(120), default="")
    numero_comprobante = db.Column(db.String(64), default="")
    notas = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    compra = db.relationship("InvCompra", back_populates="pagos")


class InvCompraLinea(db.Model):
    """Detalle de compra / entrada de mercancía."""

    __tablename__ = "inv_compra_lineas"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("inv_compras.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("inv_productos.id"), nullable=False, index=True)
    marca = db.Column(db.String(120), default="")
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, default=0.0)
    tasa_iva = db.Column(db.Float, default=0.0)
    monto_iva = db.Column(db.Float, default=0.0)

    @property
    def tasa_iva_pct(self) -> float:
        tasa = float(self.tasa_iva or 0)
        if tasa > 0:
            return round(tasa, 2)
        sub = float(self.subtotal or 0)
        iva = float(self.monto_iva or 0)
        if sub > 0 and iva > 0:
            return round(iva / sub * 100, 2)
        return 0.0

    @property
    def iva_linea(self) -> float:
        compra = self.compra
        if compra and (compra.tipo_iva or "").strip().lower() == "con_iva":
            return round(float(self.monto_iva or 0), 2)
        return 0.0

    @property
    def total_linea(self) -> float:
        return round(float(self.subtotal or 0) + self.iva_linea, 2)

    compra = db.relationship("InvCompra", back_populates="lineas")
    producto = db.relationship("InvProducto", backref="lineas_compra")


class PurSolicitud(db.Model):
    """Solicitud interna de compra · Sprint 16.1."""

    __tablename__ = "pur_solicitudes"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "numero", name="uq_pur_solicitud_empresa_numero"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    numero = db.Column(db.String(32), nullable=False, index=True)
    solicitante_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    estado = db.Column(db.String(16), nullable=False, default="borrador", index=True)
    prioridad = db.Column(db.String(16), nullable=False, default="media")
    justificacion = db.Column(db.Text, nullable=False, default="")
    requerida_para = db.Column(db.Date, nullable=True)
    aprobador_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    decision_en = db.Column(db.DateTime, nullable=True)
    motivo_decision = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    solicitante = db.relationship("User", foreign_keys=[solicitante_id])
    aprobador = db.relationship("User", foreign_keys=[aprobador_id])
    lineas = db.relationship("PurSolicitudLinea", back_populates="solicitud", cascade="all, delete-orphan", order_by="PurSolicitudLinea.id")
    eventos = db.relationship("PurEvento", back_populates="solicitud", cascade="all, delete-orphan", order_by="PurEvento.created_at")


class PurSolicitudLinea(db.Model):
    __tablename__ = "pur_solicitud_lineas"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("pur_solicitudes.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("inv_productos.id"), nullable=True, index=True)
    descripcion_libre = db.Column(db.String(255), nullable=False, default="")
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(32), nullable=False, default="pza")
    costo_estimado = db.Column(db.Float, nullable=True)

    solicitud = db.relationship("PurSolicitud", back_populates="lineas")
    producto = db.relationship("InvProducto")


class PurEvento(db.Model):
    __tablename__ = "pur_eventos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("pur_solicitudes.id", ondelete="CASCADE"), nullable=False, index=True)
    evento = db.Column(db.String(32), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    estado_anterior = db.Column(db.String(16), nullable=True)
    estado_nuevo = db.Column(db.String(16), nullable=False)
    detalle = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    solicitud = db.relationship("PurSolicitud", back_populates="eventos")
    actor = db.relationship("User")


class PurOrdenCompra(db.Model):
    """Orden de compra formal · Sprint 16.2."""

    __tablename__ = "pur_ordenes"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "numero", name="uq_pur_orden_empresa_numero"),
        db.UniqueConstraint("solicitud_id", name="uq_pur_orden_solicitud"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    numero = db.Column(db.String(32), nullable=False, index=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("pur_solicitudes.id"), nullable=False, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("inv_proveedores.id"), nullable=False, index=True)
    creador_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    estado = db.Column(db.String(16), nullable=False, default="borrador", index=True)
    moneda = db.Column(db.String(8), nullable=False, default="COP")
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    monto_iva = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    entrega_prevista = db.Column(db.Date, nullable=True)
    direccion_entrega = db.Column(db.String(255), nullable=False, default="")
    condiciones_pago = db.Column(db.String(255), nullable=False, default="")
    notas = db.Column(db.Text, nullable=False, default="")
    emitida_en = db.Column(db.DateTime, nullable=True)
    enviada_en = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    solicitud = db.relationship("PurSolicitud", backref=db.backref("orden_compra", uselist=False))
    proveedor = db.relationship("InvProveedor")
    creador = db.relationship("User")
    lineas = db.relationship("PurOrdenLinea", back_populates="orden", cascade="all, delete-orphan", order_by="PurOrdenLinea.id")
    eventos = db.relationship("PurOrdenEvento", back_populates="orden", cascade="all, delete-orphan", order_by="PurOrdenEvento.created_at")


class PurOrdenLinea(db.Model):
    __tablename__ = "pur_orden_lineas"

    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("pur_ordenes.id", ondelete="CASCADE"), nullable=False, index=True)
    solicitud_linea_id = db.Column(db.Integer, db.ForeignKey("pur_solicitud_lineas.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("inv_productos.id"), nullable=True)
    descripcion_snapshot = db.Column(db.String(255), nullable=False)
    unidad = db.Column(db.String(32), nullable=False)
    cantidad_ordenada = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False, default=0.0)
    tasa_iva = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    monto_iva = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)

    orden = db.relationship("PurOrdenCompra", back_populates="lineas")
    solicitud_linea = db.relationship("PurSolicitudLinea")
    producto = db.relationship("InvProducto")


class PurOrdenEvento(db.Model):
    __tablename__ = "pur_orden_eventos"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("pur_ordenes.id", ondelete="CASCADE"), nullable=False, index=True)
    evento = db.Column(db.String(32), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    estado_anterior = db.Column(db.String(16), nullable=True)
    estado_nuevo = db.Column(db.String(16), nullable=False)
    detalle = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    orden = db.relationship("PurOrdenCompra", back_populates="eventos")
    actor = db.relationship("User")


class PurRecepcion(db.Model):
    """Recepción inmutable de una orden de compra · Sprint 16.3."""

    __tablename__ = "pur_recepciones"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "numero", name="uq_pur_recepcion_empresa_numero"),
        db.UniqueConstraint("empresa_id", "idempotency_key", name="uq_pur_recepcion_empresa_idempotency"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    numero = db.Column(db.String(32), nullable=False, index=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("pur_ordenes.id"), nullable=False, index=True)
    estado = db.Column(db.String(16), nullable=False, default="confirmada", index=True)
    recibido_por_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    idempotency_key = db.Column(db.String(64), nullable=False)
    documento_proveedor = db.Column(db.String(64), nullable=False, default="")
    observaciones = db.Column(db.Text, nullable=False, default="")
    inv_compra_id = db.Column(db.Integer, db.ForeignKey("inv_compras.id"), nullable=True, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    orden = db.relationship("PurOrdenCompra", backref=db.backref("recepciones", order_by="PurRecepcion.created_at"))
    recibido_por = db.relationship("User")
    compra = db.relationship("InvCompra", backref=db.backref("recepcion", uselist=False))
    lineas = db.relationship("PurRecepcionLinea", back_populates="recepcion", cascade="all, delete-orphan", order_by="PurRecepcionLinea.id")


class PurRecepcionLinea(db.Model):
    __tablename__ = "pur_recepcion_lineas"

    id = db.Column(db.Integer, primary_key=True)
    recepcion_id = db.Column(db.Integer, db.ForeignKey("pur_recepciones.id", ondelete="CASCADE"), nullable=False, index=True)
    orden_linea_id = db.Column(db.Integer, db.ForeignKey("pur_orden_lineas.id"), nullable=False, index=True)
    cantidad_recibida = db.Column(db.Float, nullable=False, default=0.0)
    cantidad_rechazada = db.Column(db.Float, nullable=False, default=0.0)
    motivo_rechazo = db.Column(db.String(255), nullable=False, default="")

    recepcion = db.relationship("PurRecepcion", back_populates="lineas")
    orden_linea = db.relationship("PurOrdenLinea", backref="lineas_recepcion")


class InvVenta(db.Model):
    __tablename__ = "inv_ventas"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("inv_clientes.id"), nullable=True, index=True)
    numero = db.Column(db.String(32), default="")
    moneda = db.Column(db.String(8), default="USD")
    total = db.Column(db.Float, default=0.0)
    notas = db.Column(db.Text, default="")
    fecha = db.Column(db.Date, nullable=False)
    forma_pago = db.Column(db.String(16), default="contado")
    estado_cobro = db.Column(db.String(16), default="pagada")
    monto_cobrado = db.Column(db.Float, default=0.0)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cliente = db.relationship("InvCliente", back_populates="ventas")
    cobros = db.relationship(
        "InvVentaCobro",
        back_populates="venta",
        lazy="joined",
        cascade="all, delete-orphan",
        order_by="InvVentaCobro.fecha.desc()",
    )
    lineas = db.relationship(
        "InvVentaLinea",
        back_populates="venta",
        lazy="joined",
        cascade="all, delete-orphan",
    )

    @property
    def es_credito(self) -> bool:
        return (self.forma_pago or "contado").strip().lower() == "credito"

    @property
    def saldo_pendiente(self) -> float:
        return max(0.0, round(float(self.total or 0) - float(self.monto_cobrado or 0), 2))

    @property
    def estado_cobro_label(self) -> str:
        labels = {"pagada": "Pagada", "pendiente": "Pendiente", "parcial": "Abono parcial"}
        return labels.get((self.estado_cobro or "").strip().lower(), self.estado_cobro or "—")


class InvVentaCobro(db.Model):
    """Abono o pago recibido sobre una venta."""

    __tablename__ = "inv_venta_cobros"

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("inv_ventas.id"), nullable=False, index=True)
    monto = db.Column(db.Float, default=0.0, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    notas = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    venta = db.relationship("InvVenta", back_populates="cobros")


class InvVentaLinea(db.Model):
    """Detalle de venta — solo FK dentro del módulo inventario."""

    __tablename__ = "inv_venta_lineas"

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("inv_ventas.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("inv_productos.id"), nullable=False, index=True)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Float, default=0.0)
    subtotal = db.Column(db.Float, default=0.0)

    venta = db.relationship("InvVenta", back_populates="lineas")
    producto = db.relationship("InvProducto", backref="lineas_venta")


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    idempotency_key = db.Column(db.String(36), nullable=True, unique=True, index=True)
    numero = db.Column(db.String(32), nullable=True, index=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, default="")
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    reportado_por = db.Column(db.String(200), default="")
    cargo_reportante = db.Column(db.String(120), default="")
    telefono_contacto = db.Column(db.String(40), default="")
    area = db.Column(db.String(120), default="")
    area_responsable = db.Column(db.String(120), default="", nullable=False)
    support_area_id = db.Column(db.Integer, db.ForeignKey("support_areas.id"), nullable=True, index=True)
    ubicacion = db.Column(db.String(200), default="")
    tipo = db.Column(db.String(32), default="")
    prioridad = db.Column(db.String(32), default="media")
    prioridad_confirmada = db.Column(db.String(32), default="")
    estado = db.Column(db.String(32), default="reportado", nullable=False, index=True)
    responsable_area_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    tecnico_asignado_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=True)
    recibido_en = db.Column(db.DateTime, nullable=True)
    asignado_en = db.Column(db.DateTime, nullable=True)
    iniciado_en = db.Column(db.DateTime, nullable=True)
    diagnosticado_en = db.Column(db.DateTime, nullable=True)
    cerrado_en = db.Column(db.DateTime, nullable=True)
    motivo_cierre = db.Column(db.Text, default="")
    equipo_detenido = db.Column(db.Boolean, default=False, nullable=False)
    fecha_evento = db.Column(db.Date, nullable=True)
    hora_evento = db.Column(db.String(5), default="")
    reportado_en = db.Column(db.DateTime, default=datetime.utcnow)
    resuelto = db.Column(db.Boolean, default=False)
    resuelto_en = db.Column(db.DateTime, nullable=True)
    resuelto_por_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    notas_resolucion = db.Column(db.Text, default="")
    work_order_id = db.Column(
        db.Integer, db.ForeignKey("work_orders.id"), nullable=True, index=True
    )

    machine = db.relationship("Machine", backref="incidents")
    empresa = db.relationship("Empresa", backref="incidents")
    usuario = db.relationship("User", foreign_keys=[user_id], backref="incidentes_reportados")
    resuelto_por = db.relationship("User", foreign_keys=[resuelto_por_id])
    responsable_area = db.relationship("User", foreign_keys=[responsable_area_id])
    area_soporte = db.relationship("SupportArea", foreign_keys=[support_area_id])
    tecnico_asignado = db.relationship("Technician", foreign_keys=[tecnico_asignado_id])
    work_order = db.relationship("WorkOrder", backref=db.backref("incidencia_origen", uselist=False))

    @property
    def prioridad_label(self) -> str:
        return INCIDENT_PRIORIDAD_LABELS.get((self.prioridad or "").strip().lower(), self.prioridad or "—")

    @property
    def prioridad_meta(self) -> dict:
        return incident_prioridad_meta(self.prioridad)

    @property
    def tipo_label(self) -> str:
        return INCIDENT_TIPO_LABELS.get((self.tipo or "").strip().lower(), self.tipo or "—")

    @property
    def estado_label(self) -> str:
        return INCIDENT_ESTADO_LABELS.get(self.estado or "", self.estado or "—")

    @property
    def estado_slug(self) -> str:
        return self.estado or "reportado"


class IncidentEstado(str, Enum):
    REPORTADO = "reportado"
    RECIBIDO = "recibido"
    ASIGNADO = "asignado"
    EN_ATENCION = "en_atencion"
    DIAGNOSTICADO = "diagnosticado"
    SOLUCIONADO_VISITA = "solucionado_visita"
    PENDIENTE_OT = "pendiente_ot"
    PENDIENTE_REEMPLAZO = "pendiente_reemplazo"
    PENDIENTE_USUARIO = "pendiente_usuario"
    REASIGNADO = "reasignado"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"
    CANCELADO = "cancelado"


INCIDENT_ESTADO_LABELS = {
    "reportado": "Reportado", "recibido": "Recibido", "asignado": "Asignado",
    "en_atencion": "En atención", "diagnosticado": "Diagnosticado",
    "solucionado_visita": "Solucionado en visita", "pendiente_ot": "Pendiente de OT",
    "pendiente_reemplazo": "Pendiente de reemplazo", "pendiente_usuario": "Pendiente de usuario/acceso",
    "reasignado": "Reasignado", "resuelto": "Resuelto", "cerrado": "Cerrado", "cancelado": "Cancelado",
}


class IncidentDiagnosis(db.Model):
    __tablename__ = "incident_diagnoses"
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    hallazgo = db.Column(db.Text, nullable=False)
    causa = db.Column(db.Text, default="")
    pruebas = db.Column(db.Text, default="")
    recomendacion = db.Column(db.Text, default="")
    resultado = db.Column(db.String(32), nullable=False)
    evidencia = db.Column(db.Text, default="")
    incident = db.relationship("Incident", backref=db.backref("diagnosticos", lazy="dynamic", order_by="IncidentDiagnosis.created_at"))
    technician = db.relationship("Technician")


class IncidentHistory(db.Model):
    __tablename__ = "incident_history"
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    accion = db.Column(db.String(80), nullable=False)
    estado_anterior = db.Column(db.String(32), default="")
    estado_nuevo = db.Column(db.String(32), default="")
    comentario = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    incident = db.relationship("Incident", backref=db.backref("historial", lazy="dynamic", order_by="IncidentHistory.created_at"))
    user = db.relationship("User")


class IncidentPrioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class IncidentTipo(str, Enum):
    MECANICA = "mecanica"
    ELECTRICA = "electrica"
    HIDRAULICA = "hidraulica"
    SEGURIDAD = "seguridad"
    AMBIENTAL = "ambiental"
    OTRO = "otro"


INCIDENT_PRIORIDADES = (
    (IncidentPrioridad.BAJA.value, "Baja"),
    (IncidentPrioridad.MEDIA.value, "Media"),
    (IncidentPrioridad.ALTA.value, "Alta"),
    (IncidentPrioridad.CRITICA.value, "Crítica"),
)

INCIDENT_PRIORIDAD_LABELS = dict(INCIDENT_PRIORIDADES)

INCIDENT_TIPOS = (
    (IncidentTipo.MECANICA.value, "Mecánica / falla de equipo"),
    (IncidentTipo.ELECTRICA.value, "Eléctrica"),
    (IncidentTipo.HIDRAULICA.value, "Hidráulica / neumática"),
    (IncidentTipo.SEGURIDAD.value, "Seguridad"),
    (IncidentTipo.AMBIENTAL.value, "Ambiental"),
    (IncidentTipo.OTRO.value, "Otra"),
)

INCIDENT_TIPO_LABELS = dict(INCIDENT_TIPOS)

INCIDENT_AREAS_BASE = (
    "Producción",
    "Mantenimiento",
    "TIC / Sistemas",
    "Calidad",
    "Logística",
    "Administración",
    "Seguridad industrial",
    "Almacén",
    "Servicios generales",
)

INCIDENT_PRIORIDAD_META = {
    IncidentPrioridad.BAJA.value: {
        "label": "Baja",
        "badge_class": "badge-inc-prio badge-inc-baja",
    },
    IncidentPrioridad.MEDIA.value: {
        "label": "Media",
        "badge_class": "badge-inc-prio badge-inc-media",
    },
    IncidentPrioridad.ALTA.value: {
        "label": "Alta",
        "badge_class": "badge-inc-prio badge-inc-alta",
    },
    IncidentPrioridad.CRITICA.value: {
        "label": "Crítica",
        "badge_class": "badge-inc-prio badge-inc-critica",
    },
}


def incident_prioridad_meta(prioridad: str) -> dict:
    key = (prioridad or "").strip().lower()
    default = {
        "label": prioridad or "—",
        "badge_class": "badge-inc-prio badge-inc-desconocido",
    }
    return {**default, **INCIDENT_PRIORIDAD_META.get(key, {})}


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


def _backfill_modulos_activos() -> None:
    """Empresas existentes conservan solo mantenimiento hasta que activen inventario."""
    from sqlalchemy import or_

    pendientes = Empresa.query.filter(
        or_(Empresa.modulos_activos_json.is_(None), Empresa.modulos_activos_json == "")
    ).all()
    if not pendientes:
        return
    for emp in pendientes:
        emp.modulos_activos_json = '["mantenimiento"]'
        db.session.add(emp)
    db.session.commit()


def _backfill_monedas_activas() -> None:
    """Empresas existentes: una sola moneda activa = moneda actual."""
    from sqlalchemy import or_

    import json

    pendientes = Empresa.query.filter(
        or_(Empresa.monedas_activas_json.is_(None), Empresa.monedas_activas_json == "")
    ).all()
    if not pendientes:
        return
    for emp in pendientes:
        ref = (emp.moneda or "COP").strip().upper() or "COP"
        emp.monedas_activas_json = json.dumps([ref], ensure_ascii=False)
        db.session.add(emp)
    db.session.commit()


def _backfill_ventas_cobro_legacy() -> None:
    """Ventas existentes: contado y cobradas por el total."""
    from sqlalchemy import or_, text, inspect

    if "inv_ventas" not in inspect(db.engine).get_table_names():
        return
    with db.engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE inv_ventas SET forma_pago = 'contado' "
                "WHERE forma_pago IS NULL OR forma_pago = ''"
            )
        )
        conn.execute(
            text(
                "UPDATE inv_ventas SET estado_cobro = 'pagada' "
                "WHERE estado_cobro IS NULL OR estado_cobro = ''"
            )
        )
        conn.execute(
            text(
                "UPDATE inv_ventas SET monto_cobrado = total "
                "WHERE monto_cobrado IS NULL OR monto_cobrado = 0"
            )
        )


def ensure_users_username_por_empresa() -> None:
    """Unicidad (empresa_id, username) en lugar de username global."""
    from sqlalchemy import inspect, text

    insp = inspect(db.engine)
    if "users" not in insp.get_table_names():
        return
    indexes = {idx["name"] for idx in insp.get_indexes("users")}
    if "uq_user_empresa_username" in indexes:
        return
    with db.engine.begin() as conn:
        for name in indexes:
            if name and "username" in name.lower() and name != "uq_user_empresa_username":
                try:
                    conn.execute(text(f'DROP INDEX IF EXISTS "{name}"'))
                except Exception:
                    pass
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_empresa_username "
                "ON users (empresa_id, username)"
            )
        )


def ensure_saas_schema():
    """Columnas multi-empresa, prioridad en OT y tablas de onboarding.

    DEPRECADO: usar Flask-Migrate (`flask db migrate` / `flask db upgrade`).
    Solo se ejecuta con RUN_LEGACY_SCHEMA_MIGRATIONS=true durante la transición.
    """
    from sqlalchemy import inspect, text

    try:
        _add_column_if_missing("users", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("users", "email", "email VARCHAR(120)")
        _add_column_if_missing("users", "telefono", "telefono VARCHAR(40)")
        _add_column_if_missing("users", "rol", "rol VARCHAR(32)")
        _add_column_if_missing("users", "area", "area VARCHAR(120)")
        _add_column_if_missing("users", "cargo", "cargo VARCHAR(120)")
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
        _add_column_if_missing("machines", "numero_factura", "numero_factura VARCHAR(80)")
        _add_column_if_missing("machines", "proveedor_id", "proveedor_id INTEGER")
        _add_column_if_missing("machines", "responsable_area", "responsable_area VARCHAR(120)")
        _add_column_if_missing("machines", "responsable_cargo", "responsable_cargo VARCHAR(120)")
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
        _add_column_if_missing(
            "work_orders", "ejecucion_tipo", "ejecucion_tipo VARCHAR(16) DEFAULT 'interno'"
        )
        _add_column_if_missing("work_orders", "proveedor_id", "proveedor_id INTEGER")
        _add_column_if_missing(
            "work_orders", "supervisor_technician_id", "supervisor_technician_id INTEGER"
        )
        _add_column_if_missing(
            "work_orders", "contacto_proveedor", "contacto_proveedor VARCHAR(200)"
        )
        _add_column_if_missing(
            "work_orders", "numero_cotizacion", "numero_cotizacion VARCHAR(64)"
        )
        _add_column_if_missing("work_orders", "costo_estimado", "costo_estimado REAL")
        _add_column_if_missing("work_orders", "costo_real", "costo_real REAL")
        _add_column_if_missing(
            "work_orders",
            "proveedor_incluye_insumos",
            "proveedor_incluye_insumos BOOLEAN DEFAULT 0",
        )
        _add_column_if_missing("work_orders", "fecha_limite", "fecha_limite DATE")
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
        _add_column_if_missing("empresas", "suspendida", "suspendida BOOLEAN DEFAULT 0")
        _add_column_if_missing(
            "empresas",
            "modulos_activos_json",
            'modulos_activos_json TEXT DEFAULT \'["mantenimiento"]\'',
        )
        _add_column_if_missing(
            "empresas",
            "monedas_activas_json",
            'monedas_activas_json TEXT DEFAULT \'["COP"]\'',
        )
        _add_column_if_missing("inv_productos", "precios_json", "precios_json TEXT DEFAULT '{}'")
        _add_column_if_missing("inv_productos", "marca", "marca VARCHAR(120) DEFAULT ''")
        _add_column_if_missing("inv_productos", "subcategoria", "subcategoria VARCHAR(120) DEFAULT ''")
        _add_column_if_missing("inv_productos", "imagen", "imagen VARCHAR(255) DEFAULT ''")
        _add_column_if_missing("inv_productos", "ubicacion", "ubicacion VARCHAR(120) DEFAULT ''")
        _add_column_if_missing("inv_compra_lineas", "marca", "marca VARCHAR(120) DEFAULT ''")
        _add_column_if_missing("inv_compras", "moneda_factura", "moneda_factura VARCHAR(8) DEFAULT 'COP'")
        _add_column_if_missing("inv_compras", "tasa_cambio", "tasa_cambio REAL DEFAULT 1")
        _add_column_if_missing("inv_compras", "tipo_iva", "tipo_iva VARCHAR(16) DEFAULT 'exento'")
        _add_column_if_missing("inv_compras", "subtotal", "subtotal REAL DEFAULT 0")
        _add_column_if_missing("inv_compras", "monto_iva", "monto_iva REAL DEFAULT 0")
        _add_column_if_missing("inv_compras", "fecha_factura", "fecha_factura DATE")
        _add_column_if_missing("inv_compras", "fecha_vencimiento", "fecha_vencimiento DATE")
        _add_column_if_missing("inv_compras", "estado_pago", "estado_pago VARCHAR(16) DEFAULT 'pendiente'")
        _add_column_if_missing("inv_compras", "monto_pagado", "monto_pagado REAL DEFAULT 0")
        _add_column_if_missing("inv_ventas", "moneda", "moneda VARCHAR(8) DEFAULT 'USD'")
        _add_column_if_missing("inv_ventas", "cliente_id", "cliente_id INTEGER")
        _add_column_if_missing("inv_ventas", "forma_pago", "forma_pago VARCHAR(16) DEFAULT 'contado'")
        _add_column_if_missing("inv_ventas", "estado_cobro", "estado_cobro VARCHAR(16) DEFAULT 'pagada'")
        _add_column_if_missing("inv_ventas", "monto_cobrado", "monto_cobrado REAL DEFAULT 0")
        _add_column_if_missing("inv_ventas", "fecha_vencimiento", "fecha_vencimiento DATE")
        _backfill_ventas_cobro_legacy()
        _backfill_modulos_activos()
        _backfill_monedas_activas()
        ensure_users_username_por_empresa()
        _add_column_if_missing("planes_suscripcion", "estado_ciclo", "estado_ciclo VARCHAR(16) DEFAULT 'trial'")
        _add_column_if_missing(
            "planes_suscripcion", "pasarela_customer_id", "pasarela_customer_id VARCHAR(120)"
        )
        _add_column_if_missing(
            "planes_suscripcion", "pasarela_subscription_id", "pasarela_subscription_id VARCHAR(120)"
        )
        _add_column_if_missing("facturas_empresa", "suscripcion_id", "suscripcion_id INTEGER")
        _add_column_if_missing(
            "facturas_empresa", "pasarela_payment_id", "pasarela_payment_id VARCHAR(120)"
        )
        _add_column_if_missing("users", "bloqueado", "bloqueado BOOLEAN DEFAULT 0")
        _add_column_if_missing("users", "bloqueado_en", "bloqueado_en DATETIME")
        _add_column_if_missing("incidents", "empresa_id", "empresa_id INTEGER")
        _add_column_if_missing("incidents", "idempotency_key", "idempotency_key VARCHAR(36)")
        with db.engine.begin() as conn:
            conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_incidents_idempotency_key "
                "ON incidents (idempotency_key)"
            ))
        _add_column_if_missing("incidents", "numero", "numero VARCHAR(32)")
        _add_column_if_missing("incidents", "user_id", "user_id INTEGER")
        _add_column_if_missing("incidents", "reportado_por", "reportado_por VARCHAR(200)")
        _add_column_if_missing("incidents", "cargo_reportante", "cargo_reportante VARCHAR(120)")
        _add_column_if_missing("incidents", "telefono_contacto", "telefono_contacto VARCHAR(40)")
        _add_column_if_missing("incidents", "area", "area VARCHAR(120)")
        _add_column_if_missing("incidents", "ubicacion", "ubicacion VARCHAR(200)")
        _add_column_if_missing("incidents", "tipo", "tipo VARCHAR(32)")
        _add_column_if_missing("incidents", "prioridad", "prioridad VARCHAR(32) DEFAULT 'media'")
        _add_column_if_missing(
            "incidents", "equipo_detenido", "equipo_detenido BOOLEAN DEFAULT 0"
        )
        _add_column_if_missing("incidents", "fecha_evento", "fecha_evento DATE")
        _add_column_if_missing("incidents", "hora_evento", "hora_evento VARCHAR(5)")
        _add_column_if_missing("incidents", "resuelto_en", "resuelto_en DATETIME")
        _add_column_if_missing("incidents", "resuelto_por_id", "resuelto_por_id INTEGER")
        _add_column_if_missing("incidents", "notas_resolucion", "notas_resolucion TEXT")
        _add_column_if_missing("incidents", "work_order_id", "work_order_id INTEGER")
        ensure_asset_base_columns()
        _backfill_empresa_slugs()
        ensure_sector_plantilla_schema()
        migrate_legacy_tenant()
        from app.wo_numbering import backfill_work_order_numeros

        backfill_work_order_numeros()
    except Exception:
        import logging

        logging.getLogger(__name__).exception("ensure_saas_schema falló")
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

    dialect = db.engine.dialect.name

    with db.engine.begin() as conn:

        if dialect == "postgresql":
            conn.execute(
                text("""
                    UPDATE machines
                    SET fecha_fabricacion = make_date(anio_fabricacion, 1, 1)
                    WHERE anio_fabricacion IS NOT NULL
                    AND fecha_fabricacion IS NULL
                """)
            )
        else:
            conn.execute(
                text("""
                    UPDATE machines
                    SET fecha_fabricacion = printf('%04d-01-01', anio_fabricacion)
                    WHERE anio_fabricacion IS NOT NULL
                    AND fecha_fabricacion IS NULL
                """)
            )

def ensure_sector_plantilla_schema():
    """DEPRECADO: tablas de plantilla gestionadas por Flask-Migrate."""
    pass


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


def _is_production_env() -> bool:
    env = (os.environ.get("FLASK_ENV") or os.environ.get("ENV") or "").strip().lower()
    return env == "production"


def ensure_default_user():
    if User.query.first() is not None:
        return
    if _is_production_env():
        return
    password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "").strip()
    if not password:
        return
    u = User(
        username="admin",
        nombre_visible="Administrador",
        activo=True,
        onboarding_completado=False,
        rol=UserRole.SUPERADMIN.value,
    )
    u.set_password(password)
    db.session.add(u)
    db.session.commit()


def seed_if_empty():
    if _is_production_env():
        return
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
