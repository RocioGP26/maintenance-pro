"""Agrega cargo al perfil del usuario.

Revision ID: l9b2d60j73i1
Revises: k8a1c59i62h0
"""
from alembic import op
import sqlalchemy as sa


revision = "l9b2d60j73i1"
down_revision = "k8a1c59i62h0"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("cargo", sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("cargo")
