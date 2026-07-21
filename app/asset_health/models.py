"""Persistencia histórica de Asset Health."""

from datetime import datetime
import json

from app import db


class AssetHealthSnapshot(db.Model):
    __tablename__ = "asset_health_snapshots"
    __table_args__ = (
        db.CheckConstraint("score >= 0 and score <= 100", name="ck_asset_health_score"),
        db.CheckConstraint("confidence >= 0 and confidence <= 100", name="ck_asset_health_confidence"),
        db.CheckConstraint(
            "band in ('healthy','watch','at_risk','critical','unknown')",
            name="ck_asset_health_band",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Integer, nullable=False)
    band = db.Column(db.String(16), nullable=False, index=True)
    factors_json = db.Column(db.Text, nullable=False, default="[]")
    reasons_json = db.Column(db.Text, nullable=False, default="[]")
    trigger = db.Column(db.String(48), nullable=False, default="manual")
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    calculated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    machine = db.relationship("Machine", backref=db.backref("health_snapshots", lazy="dynamic", cascade="all, delete-orphan"))
    actor = db.relationship("User")

    @property
    def factors(self):
        try:
            value = json.loads(self.factors_json or "[]")
            return value if isinstance(value, list) else []
        except (TypeError, ValueError):
            return []

    @property
    def reasons(self):
        try:
            value = json.loads(self.reasons_json or "[]")
            return value if isinstance(value, list) else []
        except (TypeError, ValueError):
            return []

