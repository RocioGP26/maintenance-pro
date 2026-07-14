"""Agrega cargo al perfil del usuario.

Revision ID: q4g7i15o28r6
Revises: s6i9k37q40t8
"""
from alembic import op
import sqlalchemy as sa


revision = "q4g7i15o28r6"
down_revision = "s6i9k37q40t8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("cargo", sa.String(length=120), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("cargo")
