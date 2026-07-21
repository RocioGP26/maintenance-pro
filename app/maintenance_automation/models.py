"""Modelos de automatización de mantenimiento · Sprint 20."""

from datetime import datetime
import json

from app import db


class MaintenanceAutomationRule(db.Model):
    __tablename__ = "maintenance_automation_rules"
    __table_args__ = (
        db.UniqueConstraint("empresa_id", "name", name="uq_maintenance_automation_tenant_name"),
        db.CheckConstraint("trigger_type in ('meter_threshold')", name="ck_maintenance_automation_trigger"),
        db.CheckConstraint("operator in ('gt','gte','lt','lte')", name="ck_maintenance_automation_operator"),
        db.CheckConstraint("action_type in ('notify','create_work_order')", name="ck_maintenance_automation_action"),
        db.CheckConstraint("cooldown_minutes >= 0", name="ck_maintenance_automation_cooldown"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.String(500), nullable=False, default="")
    trigger_type = db.Column(db.String(32), nullable=False, default="meter_threshold")
    meter_id = db.Column(db.Integer, db.ForeignKey("asset_meters.id", ondelete="CASCADE"), nullable=False, index=True)
    operator = db.Column(db.String(8), nullable=False)
    threshold = db.Column(db.Numeric(20, 6), nullable=False)
    crossing_only = db.Column(db.Boolean, nullable=False, default=True)
    cooldown_minutes = db.Column(db.Integer, nullable=False, default=0)
    action_type = db.Column(db.String(32), nullable=False)
    action_json = db.Column(db.Text, nullable=False, default="{}")
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    meter = db.relationship("AssetMeter")
    created_by = db.relationship("User")
    executions = db.relationship(
        "MaintenanceAutomationExecution", back_populates="rule", cascade="all, delete-orphan",
        order_by="MaintenanceAutomationExecution.evaluated_at.desc()",
    )
    events = db.relationship("MaintenanceAutomationEvent", back_populates="rule", cascade="all, delete-orphan")

    @property
    def action_config(self):
        try:
            value = json.loads(self.action_json or "{}")
            return value if isinstance(value, dict) else {}
        except (TypeError, ValueError):
            return {}


class MaintenanceAutomationExecution(db.Model):
    __tablename__ = "maintenance_automation_executions"
    __table_args__ = (
        db.UniqueConstraint("rule_id", "reading_id", name="uq_maintenance_automation_rule_reading"),
        db.CheckConstraint("status in ('succeeded','skipped','failed')", name="ck_maintenance_automation_execution_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("maintenance_automation_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    reading_id = db.Column(db.Integer, db.ForeignKey("meter_readings.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False)
    matched = db.Column(db.Boolean, nullable=False, default=False)
    reason = db.Column(db.String(120), nullable=False, default="")
    condition_snapshot = db.Column(db.String(500), nullable=False, default="")
    action_snapshot = db.Column(db.String(500), nullable=False, default="")
    work_order_id = db.Column(db.Integer, db.ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    error = db.Column(db.String(500), nullable=False, default="")
    evaluated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    rule = db.relationship("MaintenanceAutomationRule", back_populates="executions")
    reading = db.relationship("MeterReading")
    work_order = db.relationship("WorkOrder")
    notifications = db.relationship("MaintenanceAutomationNotification", back_populates="execution", cascade="all, delete-orphan")


class MaintenanceAutomationNotification(db.Model):
    __tablename__ = "maintenance_automation_notifications"
    __table_args__ = (
        db.UniqueConstraint("execution_id", "user_id", name="uq_maintenance_automation_notification_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = db.Column(db.Integer, db.ForeignKey("maintenance_automation_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    read_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    execution = db.relationship("MaintenanceAutomationExecution", back_populates="notifications")
    user = db.relationship("User")


class MaintenanceAutomationEvent(db.Model):
    __tablename__ = "maintenance_automation_events"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("maintenance_automation_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = db.Column(db.Integer, db.ForeignKey("maintenance_automation_executions.id", ondelete="SET NULL"), nullable=True, index=True)
    event = db.Column(db.String(64), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    detail = db.Column(db.String(500), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    rule = db.relationship("MaintenanceAutomationRule", back_populates="events")
    execution = db.relationship("MaintenanceAutomationExecution")
    actor = db.relationship("User")
