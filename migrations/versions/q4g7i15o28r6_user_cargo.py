"""Agrega cargo al perfil del usuario.

Revision ID: q4g7i15o28r6
Revises: p3f6h04n17q5
"""
from alembic import op
import sqlalchemy as sa


revision = "q4g7i15o28r6"
down_revision = "p3f6h04n17q5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("cargo", sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("cargo")
