"""Gestión histórica de motores asociados a activos.

Revision ID: b5s0u26z49c7
Revises: su0v5w17x29z_test_company_flag
"""

from alembic import op
import sqlalchemy as sa


revision = "b5s0u26z49c7"
down_revision = "su0v5w17x29z_test_company_flag"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    machine_columns = {column["name"] for column in inspector.get_columns("machines")}
    if "tiene_motores" not in machine_columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "tiene_motores",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )

    inspector = sa.inspect(op.get_bind())
    if "asset_motor_assignments" not in inspector.get_table_names():
        op.create_table(
            "asset_motor_assignments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "empresa_id",
                sa.Integer(),
                sa.ForeignKey("empresas.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "asset_id",
                sa.Integer(),
                sa.ForeignKey("machines.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "motor_machine_id",
                sa.Integer(),
                sa.ForeignKey("machines.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "spare_part_id",
                sa.Integer(),
                sa.ForeignKey("spare_parts.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "reemplaza_asignacion_id",
                sa.Integer(),
                sa.ForeignKey("asset_motor_assignments.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("nombre_funcion", sa.String(160), nullable=False),
            sa.Column("identificador", sa.String(80), nullable=False, server_default=""),
            sa.Column("marca", sa.String(120), nullable=False, server_default=""),
            sa.Column("modelo", sa.String(120), nullable=False, server_default=""),
            sa.Column("numero_serie", sa.String(120), nullable=False, server_default=""),
            sa.Column("potencia", sa.Float(), nullable=True),
            sa.Column("potencia_unidad", sa.String(8), nullable=False, server_default="kW"),
            sa.Column("rpm", sa.Integer(), nullable=True),
            sa.Column("voltaje", sa.String(40), nullable=False, server_default=""),
            sa.Column("amperaje", sa.String(40), nullable=False, server_default=""),
            sa.Column("fecha_instalacion", sa.Date(), nullable=True),
            sa.Column("fecha_retiro", sa.Date(), nullable=True),
            sa.Column("estado", sa.String(24), nullable=False, server_default="instalado"),
            sa.Column("notas", sa.Text(), nullable=False, server_default=""),
            sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.CheckConstraint("asset_id <> motor_machine_id", name="ck_asset_motor_not_self"),
        )
        for column in (
            "empresa_id",
            "asset_id",
            "motor_machine_id",
            "spare_part_id",
            "reemplaza_asignacion_id",
            "estado",
        ):
            op.create_index(
                f"ix_asset_motor_assignments_{column}",
                "asset_motor_assignments",
                [column],
            )


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if "asset_motor_assignments" in inspector.get_table_names():
        op.drop_table("asset_motor_assignments")
    machine_columns = {column["name"] for column in inspector.get_columns("machines")}
    if "tiene_motores" in machine_columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.drop_column("tiene_motores")
