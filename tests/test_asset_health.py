"""Sprint 21 · Asset Health avanzado."""

from datetime import date, datetime

from app import db
from app.asset_health.models import AssetHealthSnapshot
from app.asset_health.service import (
    calculate_asset_health,
    health_band,
    latest_attention_count,
    save_health_snapshot,
)
from app.maintenance_execution.meter_service import create_meter, record_reading
from app.models import Incident, Machine, MachineType, WorkOrder
from tests import test_work_order_checklists as checklist_base


class TestAssetHealth(checklist_base.TestWorkOrderChecklists):
    def test_score_is_explainable_and_confidence_exposes_missing_condition_data(self):
        result = calculate_asset_health(self.order.machine)
        self.assertEqual([item["key"] for item in result["factors"]], [
            "operational", "maintenance", "reliability", "condition",
        ])
        self.assertEqual(result["confidence"], 75)
        condition = next(item for item in result["factors"] if item["key"] == "condition")
        self.assertFalse(condition["observed"])
        self.assertIn("Sin medidores", condition["evidence"])

    def test_out_of_range_reading_degrades_health_and_creates_snapshot(self):
        meter = create_meter(self.order.machine, self.admin, {
            "code":"TEMP", "name":"Temperatura", "meter_type":"gauge", "unit":"°C",
            "decimals":"1", "min_value":"10", "max_value":"80",
        })
        db.session.commit()
        record_reading(meter, self.admin, {
            "value":"95", "measured_at":datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "anomaly_type":"out_of_range", "justification":"Temperatura confirmada fuera del límite",
        })
        db.session.commit()
        result = calculate_asset_health(self.order.machine)
        condition = next(item for item in result["factors"] if item["key"] == "condition")
        self.assertEqual(condition["score"], 0)
        self.assertEqual(result["confidence"], 100)
        self.assertIn("Temperatura fuera de rango", result["reasons"])
        self.assertTrue(AssetHealthSnapshot.query.filter_by(
            machine_id=self.order.machine_id, trigger="meter_reading"
        ).first())

    def test_overdue_work_and_open_incidents_are_visible_reasons(self):
        self.order.status = "vencida"
        db.session.add(Incident(
            empresa_id=self.company.id, machine_id=self.order.machine_id,
            titulo="Vibración", estado="reportado",
        ))
        db.session.commit()
        result = calculate_asset_health(self.order.machine)
        self.assertIn("1 OT vencida(s)", result["reasons"])
        self.assertIn("1 incidencia(s) abierta(s)", result["reasons"])
        self.assertLess(result["score"], 85)

    def test_snapshots_are_deduplicated_and_attention_is_tenant_safe(self):
        self.order.machine.status = "falla"
        first = save_health_snapshot(self.order.machine, trigger="manual", actor_id=self.admin.id)
        db.session.commit()
        second = save_health_snapshot(self.order.machine, trigger="manual", actor_id=self.admin.id)
        db.session.commit()
        self.assertEqual(first.id, second.id)
        self.assertEqual(AssetHealthSnapshot.query.filter_by(machine_id=self.order.machine_id).count(), 1)
        self.assertEqual(latest_attention_count(self.admin), 1)
        self.assertEqual(latest_attention_count(self.other_user), 0)

    def test_portfolio_and_detail_respect_technician_scope(self):
        other_type = MachineType(
            empresa_id=self.other_company.id, clave="otro", nombre="Otro", prefijo="AH2"
        )
        db.session.add(other_type); db.session.flush()
        other_machine = Machine(
            empresa_id=self.other_company.id, machine_type_id=other_type.id,
            codigo="AH2-001", nombre="Activo de otro tenant",
        )
        db.session.add(other_machine); db.session.commit()

        client = self.app.test_client()
        client.post("/login", data={
            "username":self.tech_user.username, "empresa_slug":self.company.slug,
            "password":"Clave-Segura-123!",
        })
        page = client.get("/maintenance/asset-health/")
        self.assertEqual(page.status_code, 200)
        html = page.get_data(as_text=True)
        self.assertIn(self.order.machine.codigo, html)
        self.assertNotIn(other_machine.codigo, html)
        self.assertEqual(
            client.get(f"/maintenance/asset-health/assets/{other_machine.id}").status_code,
            404,
        )
        self.assertIn(client.post("/maintenance/asset-health/refresh").status_code, (302, 403))

    def test_band_contract(self):
        self.assertEqual(health_band(90, 100), "healthy")
        self.assertEqual(health_band(75, 100), "watch")
        self.assertEqual(health_band(55, 100), "at_risk")
        self.assertEqual(health_band(40, 100), "critical")
        self.assertEqual(health_band(90, 20), "unknown")

    def test_snapshot_history_converts_utc_to_company_timezone(self):
        self.company.zona_horaria = "America/Bogota"
        db.session.add(AssetHealthSnapshot(
            empresa_id=self.company.id,
            machine_id=self.order.machine_id,
            score=70,
            confidence=100,
            band="watch",
            factors_json="[]",
            reasons_json="[]",
            trigger="test",
            calculated_at=datetime(2026, 7, 21, 19, 49),
        ))
        db.session.commit()
        client = self.app.test_client()
        client.post("/login", data={
            "username":self.admin.username,
            "empresa_slug":self.company.slug,
            "password":"Clave-Segura-123!",
        })
        html = client.get(
            f"/maintenance/asset-health/assets/{self.order.machine_id}"
        ).get_data(as_text=True)
        self.assertIn("21/07/2026 14:49", html)
        self.assertNotIn("21/07/2026 19:49", html)
