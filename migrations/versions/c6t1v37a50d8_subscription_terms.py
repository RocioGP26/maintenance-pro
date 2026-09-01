"""Add versioned commercial terms acceptance to subscriptions.

Revision ID: c6t1v37a50d8
Revises: a4r9t15y38b6, t7j0l48r51u9, b5s0u26z49c7
"""

from alembic import op
import sqlalchemy as sa


revision = "c6t1v37a50d8"
down_revision = ("a4r9t15y38b6", "t7j0l48r51u9", "b5s0u26z49c7")
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("planes_suscripcion") as batch_op:
        batch_op.add_column(sa.Column("terminos_version", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("terminos_aceptados_en", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("terminos_aceptados_por_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("terminos_aceptados_ip", sa.String(length=45), nullable=True))
        batch_op.create_foreign_key(
            "fk_planes_suscripcion_terminos_usuario",
            "users",
            ["terminos_aceptados_por_id"],
            ["id"],
        )
    # La etapa comercial aprobada conserva consulta durante los días 16–30.
    op.execute(
        "UPDATE reglas_plataforma SET valor = '15' "
        "WHERE clave = 'dias_gracia_mora' AND valor = '5'"
    )


def downgrade():
    with op.batch_alter_table("planes_suscripcion") as batch_op:
        batch_op.drop_constraint("fk_planes_suscripcion_terminos_usuario", type_="foreignkey")
        batch_op.drop_column("terminos_aceptados_ip")
        batch_op.drop_column("terminos_aceptados_por_id")
        batch_op.drop_column("terminos_aceptados_en")
        batch_op.drop_column("terminos_version")
