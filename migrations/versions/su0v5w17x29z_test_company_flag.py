"""Classify internal test companies.

Revision ID: su0v5w17x29z_test_company_flag
Revises: rt9u4v06w18y_email_outbox
"""

from alembic import op
import sqlalchemy as sa


revision = "su0v5w17x29z_test_company_flag"
down_revision = "rt9u4v06w18y_email_outbox"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.add_column(
            sa.Column("es_prueba", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade():
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.drop_column("es_prueba")
