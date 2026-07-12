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
    # SQLite y PostgreSQL usan funciones diferentes para extraer fecha y hora.
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        fecha_expr = "CAST(({} ) AS DATE)"
        hora_inicio_expr = "to_char(({}), 'HH24:MI')"
        hora_fin_expr = "to_char(({}), 'HH24:MI')"
    else:
        fecha_expr = "date(({}))"
        hora_inicio_expr = "strftime('%H:%M', ({}))"
        hora_fin_expr = "strftime('%H:%M', ({}))"

    inicio_query = """
        SELECT j.fecha_inicio FROM work_order_jornadas j
        WHERE j.work_order_id = work_order_repuestos.work_order_id
        ORDER BY j.orden DESC, j.id DESC LIMIT 1
    """
    fin_query = """
        SELECT j.fecha_fin FROM work_order_jornadas j
        WHERE j.work_order_id = work_order_repuestos.work_order_id
        ORDER BY j.orden DESC, j.id DESC LIMIT 1
    """
    backfill_sql = """
        UPDATE work_order_repuestos
        SET jornada_fecha = {fecha},
            jornada_hora_inicio = {hora_inicio},
            jornada_hora_fin = {hora_fin},
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
    """.format(
        fecha=fecha_expr.format(inicio_query),
        hora_inicio=hora_inicio_expr.format(inicio_query),
        hora_fin=hora_fin_expr.format(fin_query),
    )
    op.execute(sa.text(backfill_sql))


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
