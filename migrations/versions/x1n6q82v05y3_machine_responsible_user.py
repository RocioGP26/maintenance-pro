"""Permite asignar cualquier usuario de la empresa como responsable del activo.

Revision ID: x1n6q82v05y3
Revises: w0m5p71u94x2
"""
from alembic import op
import sqlalchemy as sa


revision = "x1n6q82v05y3"
down_revision = "w0m5p71u94x2"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("machines")}
    if "responsable_user_id" not in columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.add_column(sa.Column("responsable_user_id", sa.Integer(), nullable=True))
            batch_op.create_index("ix_machines_responsable_user_id", ["responsable_user_id"])
            batch_op.create_foreign_key(
                "fk_machine_responsable_user", "users", ["responsable_user_id"], ["id"]
            )


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("machines")}
    if "responsable_user_id" in columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.drop_constraint("fk_machine_responsable_user", type_="foreignkey")
            batch_op.drop_index("ix_machines_responsable_user_id")
            batch_op.drop_column("responsable_user_id")
