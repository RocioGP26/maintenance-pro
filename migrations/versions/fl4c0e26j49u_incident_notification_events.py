"""Eventos de estado para notificaciones de incidencias.

Revision ID: fl4c0e26j49u
Revises: ek4b9d15i38t
"""

from alembic import op
import sqlalchemy as sa


revision = "fl4c0e26j49u"
down_revision = "ek4b9d15i38t"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incident_notifications") as batch_op:
        batch_op.add_column(
            sa.Column("audience", sa.String(20), nullable=False, server_default="area")
        )
        batch_op.add_column(
            sa.Column(
                "event_key", sa.String(80), nullable=False, server_default="area_reported"
            )
        )
        batch_op.add_column(
            sa.Column("event_type", sa.String(40), nullable=False, server_default="reported")
        )
        batch_op.add_column(
            sa.Column(
                "title",
                sa.String(160),
                nullable=False,
                server_default="Nueva incidencia reportada",
            )
        )
        batch_op.add_column(
            sa.Column("message", sa.String(500), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("status_snapshot", sa.String(32), nullable=False, server_default="")
        )
        batch_op.drop_constraint("uq_incident_notification_user", type_="unique")
        batch_op.create_unique_constraint(
            "uq_incident_notification_user_event",
            ["incident_id", "user_id", "event_key"],
        )
        batch_op.create_index("ix_incident_notifications_audience", ["audience"])


def downgrade():
    op.execute(
        "DELETE FROM incident_notifications "
        "WHERE audience <> 'area' OR event_key <> 'area_reported'"
    )
    with op.batch_alter_table("incident_notifications") as batch_op:
        batch_op.drop_index("ix_incident_notifications_audience")
        batch_op.drop_constraint("uq_incident_notification_user_event", type_="unique")
        batch_op.create_unique_constraint(
            "uq_incident_notification_user", ["incident_id", "user_id"]
        )
        batch_op.drop_column("status_snapshot")
        batch_op.drop_column("message")
        batch_op.drop_column("title")
        batch_op.drop_column("event_type")
        batch_op.drop_column("event_key")
        batch_op.drop_column("audience")
