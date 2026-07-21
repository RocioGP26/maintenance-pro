"""Medidores, lecturas y migración idempotente de horas.

Revision ID: kr9h5j71o04z
Revises: jq8g4i60n93y
"""
from alembic import op
import sqlalchemy as sa


revision = "kr9h5j71o04z"
down_revision = "jq8g4i60n93y"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "asset_meters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(48), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("meter_type", sa.String(20), nullable=False, server_default="cumulative"),
        sa.Column("unit", sa.String(24), nullable=False),
        sa.Column("decimals", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("rules_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("meter_type in ('cumulative','gauge')", name="ck_asset_meter_type"),
        sa.CheckConstraint("decimals >= 0 and decimals <= 6", name="ck_asset_meter_decimals"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "machine_id", "code", name="uq_asset_meter_tenant_machine_code"),
    )
    for column in ("empresa_id", "machine_id"):
        op.create_index(f"ix_asset_meters_{column}", "asset_meters", [column])

    op.create_table(
        "meter_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("meter_id", sa.Integer(), nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=True),
        sa.Column("value", sa.Numeric(20, 6), nullable=False),
        sa.Column("measured_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.String(24), nullable=False, server_default="manual"),
        sa.Column("performed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(120), nullable=True),
        sa.Column("notes", sa.String(500), nullable=False, server_default=""),
        sa.Column("flagged", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("anomaly_type", sa.String(32), nullable=False, server_default=""),
        sa.Column("justification", sa.String(500), nullable=False, server_default=""),
        sa.Column("correction_of_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("source in ('manual','legacy_migration','correction')", name="ck_meter_reading_source"),
        sa.ForeignKeyConstraint(["correction_of_id"], ["meter_readings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meter_id"], ["asset_meters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "idempotency_key", name="uq_meter_reading_tenant_idempotency"),
    )
    for column in ("empresa_id", "meter_id", "work_order_id", "measured_at"):
        op.create_index(f"ix_meter_readings_{column}", "meter_readings", [column])

    op.create_table(
        "meter_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("meter_id", sa.Integer(), nullable=False),
        sa.Column("reading_id", sa.Integer(), nullable=True),
        sa.Column("event", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meter_id"], ["asset_meters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reading_id"], ["meter_readings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("empresa_id", "meter_id", "reading_id", "event", "created_at"):
        op.create_index(f"ix_meter_events_{column}", "meter_events", [column])

    _seed_legacy_hours()


def _seed_legacy_hours():
    bind = op.get_bind()
    bind.execute(sa.text(
        "INSERT INTO asset_meters "
        "(empresa_id,machine_id,code,name,meter_type,unit,decimals,active,rules_json,created_by_id,created_at,updated_at) "
        "SELECT m.empresa_id,m.id,'RUNTIME_HOURS','Horómetro','cumulative','h',2,:active,'{}',NULL,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP "
        "FROM machines m WHERE m.empresa_id IS NOT NULL AND m.horas_operacion IS NOT NULL "
        "AND NOT EXISTS (SELECT 1 FROM asset_meters am WHERE am.empresa_id=m.empresa_id AND am.machine_id=m.id AND am.code='RUNTIME_HOURS')"
    ), {"active": True})
    bind.execute(sa.text(
        "INSERT INTO meter_events (empresa_id,meter_id,reading_id,event,actor_id,detail,created_at) "
        "SELECT am.empresa_id,am.id,NULL,'meter_created_from_legacy',NULL,'Machine.horas_operacion',CURRENT_TIMESTAMP "
        "FROM asset_meters am WHERE am.code='RUNTIME_HOURS' "
        "AND NOT EXISTS (SELECT 1 FROM meter_events me WHERE me.meter_id=am.id AND me.event='meter_created_from_legacy')"
    ))
    bind.execute(sa.text(
        "INSERT INTO meter_readings "
        "(empresa_id,meter_id,work_order_id,value,measured_at,source,performed_by_user_id,recorded_by_user_id,idempotency_key,notes,flagged,anomaly_type,justification,correction_of_id,created_at) "
        "SELECT m.empresa_id,am.id,NULL,m.horas_operacion,CURRENT_TIMESTAMP,'legacy_migration',NULL,NULL,"
        "'legacy-runtime-hours-machine-' || CAST(m.id AS VARCHAR(32)),"
        "'Lectura inicial importada desde Machine.horas_operacion.',:flagged,'','',NULL,CURRENT_TIMESTAMP "
        "FROM machines m JOIN asset_meters am ON am.empresa_id=m.empresa_id AND am.machine_id=m.id AND am.code='RUNTIME_HOURS' "
        "WHERE m.horas_operacion IS NOT NULL AND NOT EXISTS (SELECT 1 FROM meter_readings mr WHERE mr.empresa_id=m.empresa_id "
        "AND mr.idempotency_key='legacy-runtime-hours-machine-' || CAST(m.id AS VARCHAR(32)))"
    ), {"flagged": False})
    bind.execute(sa.text(
        "INSERT INTO meter_events (empresa_id,meter_id,reading_id,event,actor_id,detail,created_at) "
        "SELECT mr.empresa_id,mr.meter_id,mr.id,'maintenance.meter.reading_created',NULL,'legacy_migration',CURRENT_TIMESTAMP "
        "FROM meter_readings mr WHERE mr.source='legacy_migration' "
        "AND NOT EXISTS (SELECT 1 FROM meter_events me WHERE me.reading_id=mr.id AND me.event='maintenance.meter.reading_created')"
    ))


def downgrade():
    op.drop_table("meter_events")
    op.drop_table("meter_readings")
    op.drop_table("asset_meters")
