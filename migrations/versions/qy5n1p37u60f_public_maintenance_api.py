"""API Maintenance incremental e idempotente.

Revision ID: qy5n1p37u60f
Revises: px4m0o26t59e
"""

from alembic import op
import sqlalchemy as sa


revision = "qy5n1p37u60f"
down_revision = "px4m0o26t59e"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _indexes(table: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table)}


def upgrade():
    # SQLite no permite DEFAULT CURRENT_TIMESTAMP en ALTER TABLE ADD COLUMN.
    # Se usa un default constante y luego se rellena con created_at / ahora.
    for table in ("machines", "work_orders", "incidents"):
        cols = _columns(table)
        if "updated_at" not in cols:
            op.add_column(
                table,
                sa.Column(
                    "updated_at",
                    sa.DateTime(),
                    nullable=False,
                    server_default="1970-01-01 00:00:00",
                ),
            )
            if "created_at" in cols:
                op.execute(
                    sa.text(
                        f"UPDATE {table} SET updated_at = COALESCE(created_at, CURRENT_TIMESTAMP)"
                    )
                )
            else:
                op.execute(
                    sa.text(f"UPDATE {table} SET updated_at = CURRENT_TIMESTAMP")
                )
        if f"ix_{table}_updated_at" not in _indexes(table):
            op.create_index(f"ix_{table}_updated_at", table, ["updated_at"])

    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "api_idempotency_records" not in tables:
        op.create_table(
            "api_idempotency_records",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("empresa_id", sa.Integer(), nullable=False),
            sa.Column("credential_id", sa.Integer(), nullable=True),
            sa.Column("actor_key", sa.String(length=80), nullable=False),
            sa.Column("operation", sa.String(length=80), nullable=False),
            sa.Column("idempotency_key", sa.String(length=120), nullable=False),
            sa.Column("request_hash", sa.String(length=64), nullable=False),
            sa.Column("resource_type", sa.String(length=40), nullable=False),
            sa.Column("resource_id", sa.Integer(), nullable=False),
            sa.Column("response_json", sa.Text(), nullable=False),
            sa.Column("status_code", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(
                ["credential_id"], ["integration_credentials.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "empresa_id",
                "actor_key",
                "operation",
                "idempotency_key",
                name="uq_api_idempotency_tenant_actor_operation_key",
            ),
        )
        op.create_index(
            "ix_api_idempotency_records_empresa_id",
            "api_idempotency_records",
            ["empresa_id"],
        )
        op.create_index(
            "ix_api_idempotency_records_credential_id",
            "api_idempotency_records",
            ["credential_id"],
        )
        op.create_index(
            "ix_api_idempotency_records_created_at",
            "api_idempotency_records",
            ["created_at"],
        )


def downgrade():
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "api_idempotency_records" in tables:
        op.drop_table("api_idempotency_records")
    for table in ("incidents", "work_orders", "machines"):
        idxs = _indexes(table)
        if f"ix_{table}_updated_at" in idxs:
            op.drop_index(f"ix_{table}_updated_at", table_name=table)
        if "updated_at" in _columns(table):
            op.drop_column(table, "updated_at")
