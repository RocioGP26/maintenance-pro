"""Modelos del catálogo de procedimientos · Sprint 19.1."""

from __future__ import annotations

from datetime import datetime
import json

from app import db


PROCEDURE_VERSION_DRAFT = "draft"
PROCEDURE_VERSION_PUBLISHED = "published"
PROCEDURE_VERSION_RETIRED = "retired"
PROCEDURE_VERSION_STATUSES = frozenset(
    {
        PROCEDURE_VERSION_DRAFT,
        PROCEDURE_VERSION_PUBLISHED,
        PROCEDURE_VERSION_RETIRED,
    }
)

PROCEDURE_RESPONSE_TYPES = (
    ("confirmation", "Confirmación"),
    ("text", "Texto"),
    ("number", "Número"),
    ("choice", "Selección"),
    ("measurement", "Medición"),
    ("evidence", "Evidencia"),
    ("signature", "Firma"),
)


class MaintenanceProcedure(db.Model):
    __tablename__ = "maintenance_procedures"
    __table_args__ = (
        db.UniqueConstraint(
            "empresa_id", "code", name="uq_maintenance_procedure_tenant_code"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code = db.Column(db.String(48), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    machine_type_id = db.Column(
        db.Integer,
        db.ForeignKey("machine_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    machine_type = db.relationship("MachineType")
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    versions = db.relationship(
        "MaintenanceProcedureVersion",
        back_populates="procedure",
        cascade="all, delete-orphan",
    )
    events = db.relationship(
        "MaintenanceProcedureEvent",
        back_populates="procedure",
        cascade="all, delete-orphan",
    )

    @property
    def published_version(self):
        return next((item for item in self.versions if item.status == "published"), None)

    @property
    def draft_version(self):
        return next((item for item in self.versions if item.status == "draft"), None)


class MaintenanceProcedureVersion(db.Model):
    __tablename__ = "maintenance_procedure_versions"
    __table_args__ = (
        db.UniqueConstraint(
            "procedure_id", "version", name="uq_maintenance_procedure_version"
        ),
        db.CheckConstraint("version > 0", name="ck_maintenance_procedure_version_positive"),
        db.CheckConstraint(
            "status in ('draft', 'published', 'retired')",
            name="ck_maintenance_procedure_version_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_procedures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=PROCEDURE_VERSION_DRAFT)
    change_notes = db.Column(db.String(500), nullable=False, default="")
    created_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    published_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    published_at = db.Column(db.DateTime, nullable=True)
    retired_at = db.Column(db.DateTime, nullable=True)

    procedure = db.relationship("MaintenanceProcedure", back_populates="versions")
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    published_by = db.relationship("User", foreign_keys=[published_by_id])
    steps = db.relationship(
        "MaintenanceProcedureStep",
        back_populates="version_record",
        cascade="all, delete-orphan",
        order_by="MaintenanceProcedureStep.position",
    )

    @property
    def editable(self) -> bool:
        return self.status == PROCEDURE_VERSION_DRAFT


class MaintenanceProcedureStep(db.Model):
    __tablename__ = "maintenance_procedure_steps"
    __table_args__ = (
        db.UniqueConstraint(
            "version_id", "position", name="uq_maintenance_procedure_step_position"
        ),
        db.UniqueConstraint(
            "version_id", "code", name="uq_maintenance_procedure_step_code"
        ),
        db.CheckConstraint("position > 0", name="ck_maintenance_procedure_step_position_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_procedure_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position = db.Column(db.Integer, nullable=False)
    code = db.Column(db.String(48), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    instructions = db.Column(db.Text, nullable=False, default="")
    response_type = db.Column(db.String(24), nullable=False, default="confirmation")
    required = db.Column(db.Boolean, nullable=False, default=True)
    config_json = db.Column(db.Text, nullable=False, default="{}")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    version_record = db.relationship(
        "MaintenanceProcedureVersion", back_populates="steps"
    )


class MaintenanceProcedureEvent(db.Model):
    __tablename__ = "maintenance_procedure_events"

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(
        db.Integer,
        db.ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    procedure_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_procedures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id = db.Column(
        db.Integer,
        db.ForeignKey("maintenance_procedure_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event = db.Column(db.String(48), nullable=False, index=True)
    actor_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    previous_status = db.Column(db.String(20), nullable=False, default="")
    new_status = db.Column(db.String(20), nullable=False, default="")
    detail = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    procedure = db.relationship("MaintenanceProcedure", back_populates="events")
    version_record = db.relationship("MaintenanceProcedureVersion")
    actor = db.relationship("User")


CHECKLIST_PENDING = "pending"
CHECKLIST_IN_PROGRESS = "in_progress"
CHECKLIST_COMPLETED = "completed"
CHECKLIST_BLOCKED = "blocked"
CHECKLIST_REVIEWED = "reviewed"
CHECKLIST_VOID = "void"


class WorkOrderChecklist(db.Model):
    __tablename__ = "work_order_checklists"
    __table_args__ = (
        db.UniqueConstraint("work_order_id", name="uq_work_order_checklist_order"),
        db.CheckConstraint(
            "status in ('pending','in_progress','blocked','completed','reviewed','void')",
            name="ck_work_order_checklist_status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    procedure_version_id = db.Column(db.Integer, db.ForeignKey("maintenance_procedure_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey("technicians.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default=CHECKLIST_PENDING)
    procedure_code_snapshot = db.Column(db.String(48), nullable=False)
    procedure_name_snapshot = db.Column(db.String(160), nullable=False)
    version_snapshot = db.Column(db.Integer, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.String(500), nullable=False, default="")
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    work_order = db.relationship("WorkOrder", backref=db.backref("execution_checklist", uselist=False))
    procedure_version = db.relationship("MaintenanceProcedureVersion")
    assigned_technician = db.relationship("Technician")
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id])
    responses = db.relationship("WorkOrderChecklistResponse", back_populates="checklist", cascade="all, delete-orphan")
    events = db.relationship("WorkOrderChecklistEvent", back_populates="checklist", cascade="all, delete-orphan")

    @property
    def required_total(self):
        return sum(1 for step in self.procedure_version.steps if step.required)

    @property
    def required_completed(self):
        valid = {item.step_id for item in self.responses if item.is_valid}
        return sum(1 for step in self.procedure_version.steps if step.required and step.id in valid)

    @property
    def progress_percent(self):
        total = self.required_total
        return 100 if total == 0 else round(self.required_completed * 100 / total)


class WorkOrderChecklistResponse(db.Model):
    __tablename__ = "work_order_checklist_responses"
    __table_args__ = (
        db.UniqueConstraint("checklist_id", "step_id", name="uq_checklist_response_step"),
        db.CheckConstraint(
            "conformity in ('conforming','nonconforming','not_applicable','pending_review')",
            name="ck_checklist_response_conformity",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("work_order_checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = db.Column(db.Integer, db.ForeignKey("maintenance_procedure_steps.id", ondelete="RESTRICT"), nullable=False, index=True)
    value_json = db.Column(db.Text, nullable=False, default="{}")
    is_valid = db.Column(db.Boolean, nullable=False, default=False)
    conformity = db.Column(db.String(24), nullable=False, default="pending_review")
    justification = db.Column(db.String(500), nullable=False, default="")
    resolution_note = db.Column(db.String(500), nullable=False, default="")
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    signed_at = db.Column(db.DateTime, nullable=True)
    signature_name_snapshot = db.Column(db.String(160), nullable=False, default="")
    signature_purpose = db.Column(db.String(255), nullable=False, default="")
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    recorded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    checklist = db.relationship("WorkOrderChecklist", back_populates="responses")
    step = db.relationship("MaintenanceProcedureStep")
    performed_by = db.relationship("User", foreign_keys=[performed_by_user_id])
    recorded_by = db.relationship("User", foreign_keys=[recorded_by_user_id])
    resolved_by = db.relationship("User", foreign_keys=[resolved_by_id])
    evidences = db.relationship("WorkOrderChecklistEvidence", back_populates="response", cascade="all, delete-orphan")


class WorkOrderChecklistEvidence(db.Model):
    __tablename__ = "work_order_checklist_evidences"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("work_order_checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = db.Column(db.Integer, db.ForeignKey("work_order_checklist_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = db.Column(db.Integer, db.ForeignKey("maintenance_procedure_steps.id", ondelete="RESTRICT"), nullable=False, index=True)
    storage_key = db.Column(db.String(500), nullable=False, unique=True)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    checksum_sha256 = db.Column(db.String(64), nullable=False, index=True)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    checklist = db.relationship("WorkOrderChecklist")
    response = db.relationship("WorkOrderChecklistResponse", back_populates="evidences")
    step = db.relationship("MaintenanceProcedureStep")
    uploaded_by = db.relationship("User")


class WorkOrderChecklistEvent(db.Model):
    __tablename__ = "work_order_checklist_events"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey("work_order_checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    event = db.Column(db.String(48), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    detail = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    checklist = db.relationship("WorkOrderChecklist", back_populates="events")
    actor = db.relationship("User")


class MaintenanceLogEntry(db.Model):
    __tablename__ = "maintenance_log_entries"
    __table_args__ = (
        db.CheckConstraint(
            "(case when work_order_id is not null then 1 else 0 end + "
            "case when incident_id is not null then 1 else 0 end + "
            "case when machine_id is not null then 1 else 0 end) = 1",
            name="ck_maintenance_log_single_context",
        ),
        db.CheckConstraint("visibility in ('internal','requester','system')", name="ck_maintenance_log_visibility"),
    )
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id", ondelete="CASCADE"), nullable=True, index=True)
    entry_type = db.Column(db.String(32), nullable=False, default="comment")
    visibility = db.Column(db.String(16), nullable=False, default="internal")
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    correction_of_id = db.Column(db.Integer, db.ForeignKey("maintenance_log_entries.id", ondelete="RESTRICT"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    work_order = db.relationship("WorkOrder")
    incident = db.relationship("Incident")
    machine = db.relationship("Machine")
    author = db.relationship("User", foreign_keys=[author_id])
    performed_by = db.relationship("User", foreign_keys=[performed_by_user_id])
    correction_of = db.relationship("MaintenanceLogEntry", remote_side=[id])
    attachments = db.relationship("MaintenanceLogAttachment", back_populates="entry", cascade="all, delete-orphan")


class MaintenanceLogAttachment(db.Model):
    __tablename__ = "maintenance_log_attachments"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("maintenance_log_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_key = db.Column(db.String(500), nullable=False, unique=True)
    original_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    checksum_sha256 = db.Column(db.String(64), nullable=False, index=True)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    entry = db.relationship("MaintenanceLogEntry", back_populates="attachments")
    uploaded_by = db.relationship("User")


class MaintenanceLogEvent(db.Model):
    __tablename__ = "maintenance_log_events"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("maintenance_log_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    event = db.Column(db.String(48), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    detail = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    entry = db.relationship("MaintenanceLogEntry")
    actor = db.relationship("User")


class MaintenanceLogNotification(db.Model):
    """Entrega personal de una novedad de bitácora a un participante autorizado."""

    __tablename__ = "maintenance_log_notifications"
    __table_args__ = (
        db.UniqueConstraint("entry_id", "user_id", name="uq_maintenance_log_notification_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("maintenance_log_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    entry = db.relationship("MaintenanceLogEntry")
    user = db.relationship("User")


METER_CUMULATIVE = "cumulative"
METER_GAUGE = "gauge"
METER_TYPES = ((METER_CUMULATIVE, "Acumulativo"), (METER_GAUGE, "Instantáneo"))


class AssetMeter(db.Model):
    __tablename__ = "asset_meters"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "machine_id", "code", name="uq_asset_meter_tenant_machine_code"),
        db.CheckConstraint("meter_type in ('cumulative','gauge')", name="ck_asset_meter_type"),
        db.CheckConstraint("decimals >= 0 and decimals <= 6", name="ck_asset_meter_decimals"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    code = db.Column(db.String(48), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    meter_type = db.Column(db.String(20), nullable=False, default=METER_CUMULATIVE)
    unit = db.Column(db.String(24), nullable=False)
    decimals = db.Column(db.Integer, nullable=False, default=2)
    active = db.Column(db.Boolean, nullable=False, default=True)
    rules_json = db.Column(db.Text, nullable=False, default="{}")
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    machine = db.relationship("Machine", backref=db.backref("asset_meters", lazy="dynamic", cascade="all, delete-orphan"))
    created_by = db.relationship("User")
    readings = db.relationship(
        "MeterReading", back_populates="meter", cascade="all, delete-orphan",
        order_by="MeterReading.measured_at.desc(), MeterReading.id.desc()",
    )
    events = db.relationship("MeterEvent", back_populates="meter", cascade="all, delete-orphan")

    @property
    def rules(self):
        try:
            value = json.loads(self.rules_json or "{}")
            return value if isinstance(value, dict) else {}
        except (TypeError, ValueError):
            return {}

    @property
    def latest_reading(self):
        return self.readings[0] if self.readings else None


class MeterReading(db.Model):
    __tablename__ = "meter_readings"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "idempotency_key", name="uq_meter_reading_tenant_idempotency"),
        db.CheckConstraint("source in ('manual','legacy_migration','correction')", name="ck_meter_reading_source"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    meter_id = db.Column(db.Integer, db.ForeignKey("asset_meters.id", ondelete="CASCADE"), nullable=False, index=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    value = db.Column(db.Numeric(20, 6), nullable=False)
    measured_at = db.Column(db.DateTime, nullable=False, index=True)
    source = db.Column(db.String(24), nullable=False, default="manual")
    performed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    recorded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    idempotency_key = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.String(500), nullable=False, default="")
    flagged = db.Column(db.Boolean, nullable=False, default=False)
    anomaly_type = db.Column(db.String(32), nullable=False, default="")
    justification = db.Column(db.String(500), nullable=False, default="")
    correction_of_id = db.Column(db.Integer, db.ForeignKey("meter_readings.id", ondelete="RESTRICT"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    meter = db.relationship("AssetMeter", back_populates="readings")
    work_order = db.relationship("WorkOrder")
    performed_by = db.relationship("User", foreign_keys=[performed_by_user_id])
    recorded_by = db.relationship("User", foreign_keys=[recorded_by_user_id])
    correction_of = db.relationship("MeterReading", remote_side=[id])


class MeterEvent(db.Model):
    __tablename__ = "meter_events"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    meter_id = db.Column(db.Integer, db.ForeignKey("asset_meters.id", ondelete="CASCADE"), nullable=False, index=True)
    reading_id = db.Column(db.Integer, db.ForeignKey("meter_readings.id", ondelete="SET NULL"), nullable=True, index=True)
    event = db.Column(db.String(64), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    detail = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    meter = db.relationship("AssetMeter", back_populates="events")
    reading = db.relationship("MeterReading")
    actor = db.relationship("User")
