"""Observabilidad de entregas webhook (excerpt de respuesta).

Revision ID: sa7p3r59w82h
Revises: rz6o2q48v71g
"""

from alembic import op
import sqlalchemy as sa


revision = "sa7p3r59w82h"
down_revision = "rz6o2q48v71g"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("webhook_deliveries")}
    if "response_excerpt" not in columns:
        with op.batch_alter_table("webhook_deliveries") as batch_op:
            batch_op.add_column(sa.Column("response_excerpt", sa.String(length=255), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("webhook_deliveries")}
    if "response_excerpt" in columns:
        with op.batch_alter_table("webhook_deliveries") as batch_op:
            batch_op.drop_column("response_excerpt")
