"""Vincula cada repuesto consumido con su jornada de instalación.

Revision ID: ad7u2w48b61e9
Revises: ac6t1v37a50d8
"""
from alembic import op
import sqlalchemy as sa


revision = "ad7u2w48b61e9"
down_revision = "ac6t1v37a50d8"
branch_labels = None
depends_on = None


def upgrade():
    columns = {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("work_order_repuestos")
    }
    with op.batch_alter_table("work_order_repuestos") as batch_op:
        if "jornada_fecha" not in columns:
            batch_op.add_column(sa.Column("jornada_fecha", sa.Date(), nullable=True))
        if "jornada_hora_inicio" not in columns:
            batch_op.add_column(sa.Column("jornada_hora_inicio", sa.String(5), nullable=True))
        if "jornada_hora_fin" not in columns:
            batch_op.add_column(sa.Column("jornada_hora_fin", sa.String(5), nullable=True))
        if "jornada_tecnico" not in columns:
            batch_op.add_column(sa.Column("jornada_tecnico", sa.String(200), nullable=True))

    # Los consumos históricos se atribuyen a la última jornada conocida de su OT.
    op.execute(sa.text("""
        UPDATE work_order_repuestos
        SET jornada_fecha = date((
                SELECT j.fecha_inicio FROM work_order_jornadas j
                WHERE j.work_order_id = work_order_repuestos.work_order_id
                ORDER BY j.orden DESC, j.id DESC LIMIT 1
            )),
            jornada_hora_inicio = strftime('%H:%M', (
                SELECT j.fecha_inicio FROM work_order_jornadas j
                WHERE j.work_order_id = work_order_repuestos.work_order_id
                ORDER BY j.orden DESC, j.id DESC LIMIT 1
            )),
            jornada_hora_fin = strftime('%H:%M', (
                SELECT j.fecha_fin FROM work_order_jornadas j
                WHERE j.work_order_id = work_order_repuestos.work_order_id
                ORDER BY j.orden DESC, j.id DESC LIMIT 1
            )),
            jornada_tecnico = COALESCE((
                SELECT t.nombre FROM work_order_jornadas j
                JOIN technicians t ON t.id = j.technician_id
                WHERE j.work_order_id = work_order_repuestos.work_order_id
                ORDER BY j.orden DESC, j.id DESC LIMIT 1
            ), (
                SELECT j.tecnico_nombre FROM work_order_jornadas j
                WHERE j.work_order_id = work_order_repuestos.work_order_id
                ORDER BY j.orden DESC, j.id DESC LIMIT 1
            ), '')
    """))


def downgrade():
    columns = {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("work_order_repuestos")
    }
    with op.batch_alter_table("work_order_repuestos") as batch_op:
        for name in (
            "jornada_tecnico",
            "jornada_hora_fin",
            "jornada_hora_inicio",
            "jornada_fecha",
        ):
            if name in columns:
                batch_op.drop_column(name)
