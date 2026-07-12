"""Repara instalaciones marcadas al día sin idempotency_key en incidents.

Revision ID: u8k3m59s72v0
Revises: t7j2k48r61u9
"""
from alembic import op
import sqlalchemy as sa


revision = "u8k3m59s72v0"
down_revision = "t7j2k48r61u9"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("incidents")}
    indexes = {index["name"] for index in inspector.get_indexes("incidents")}

    if "idempotency_key" not in columns:
        with op.batch_alter_table("incidents") as batch_op:
            batch_op.add_column(sa.Column("idempotency_key", sa.String(length=36), nullable=True))

    if "ix_incidents_idempotency_key" not in indexes:
        op.create_index(
            "ix_incidents_idempotency_key",
            "incidents",
            ["idempotency_key"],
            unique=True,
        )


def downgrade():
    # Migración de reparación: no elimina datos ni una columna que podría
    # haber sido creada originalmente por p3f6h04n17q5.
    pass
