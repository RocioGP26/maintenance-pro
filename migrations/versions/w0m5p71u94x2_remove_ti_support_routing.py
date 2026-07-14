"""Retira la integración de áreas TI y restaura el enfoque original de mantenimiento.

Revision ID: w0m5p71u94x2
Revises: v9l4n60t83w1
"""
from alembic import op
import sqlalchemy as sa


revision = "w0m5p71u94x2"
down_revision = "v9l4n60t83w1"
branch_labels = None
depends_on = None


def _columns(table):
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _indexes(table):
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table)}


def upgrade():
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "incidents" in tables and "support_area_id" in _columns("incidents"):
        if "ix_incidents_support_area_id" in _indexes("incidents"):
            op.drop_index("ix_incidents_support_area_id", table_name="incidents")
        with op.batch_alter_table("incidents") as batch_op:
            batch_op.drop_column("support_area_id")
    if "machines" in tables:
        machine_columns = _columns("machines")
        machine_indexes = _indexes("machines")
        if "ix_machines_support_area_id" in machine_indexes:
            op.drop_index("ix_machines_support_area_id", table_name="machines")
        if "ix_machines_custodio_user_id" in machine_indexes:
            op.drop_index("ix_machines_custodio_user_id", table_name="machines")
        with op.batch_alter_table("machines") as batch_op:
            if "support_area_id" in machine_columns:
                batch_op.drop_column("support_area_id")
            if "custodio_user_id" in machine_columns:
                batch_op.drop_column("custodio_user_id")
    if "user_support_areas" in tables:
        op.drop_table("user_support_areas")
    if "support_areas" in tables:
        op.drop_table("support_areas")


def downgrade():
    op.create_table(
        "support_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_support_area_empresa_nombre"),
    )
    op.create_table(
        "user_support_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("support_area_id", sa.Integer(), sa.ForeignKey("support_areas.id"), nullable=False),
        sa.Column("puede_recibir", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_asignar", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_atender", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_diagnosticar", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("user_id", "support_area_id", name="uq_user_support_area"),
    )
    with op.batch_alter_table("machines") as batch_op:
        batch_op.add_column(sa.Column("custodio_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("support_area_id", sa.Integer(), nullable=True))
    with op.batch_alter_table("incidents") as batch_op:
        batch_op.add_column(sa.Column("support_area_id", sa.Integer(), nullable=True))
