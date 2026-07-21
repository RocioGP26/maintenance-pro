"""Sprint 20 · disparadores y automatizaciones configurables."""

from app import db
from app.maintenance_automation.models import (
    MaintenanceAutomationExecution,
    MaintenanceAutomationNotification,
    MaintenanceAutomationRule,
)
from app.maintenance_automation.service import create_rule, evaluate_reading
from app.maintenance_execution.meter_service import record_reading
from app.models import WorkOrder
from tests.test_asset_meters import TestAssetMeters


class TestMaintenanceAutomation(TestAssetMeters):
    def _rule(self, meter, **values):
        data = {
            "name": "Temperatura alta", "description": "Protección del activo",
            "meter_id": str(meter.id), "operator": "gte", "threshold": "90",
            "crossing_only": "1", "cooldown_minutes": "0",
            "action_type": "create_work_order", "notify_roles": ["admin", "supervisor"],
            "work_order_title": "Inspeccionar condición crítica", "work_order_type": "correctivo",
            "priority": "alta", "technician_id": str(self.tech.id),
            "work_order_description": "Generada por lectura de condición.",
        }
        data.update(values)
        rule = create_rule(self.company.id, self.admin, data)
        db.session.commit()
        return rule

    def test_threshold_crossing_creates_one_work_order_and_notifications(self):
        meter = self._meter(code="AUTO_TEMP", name="Temperatura", meter_type="gauge", unit="°C")
        rule = self._rule(meter)
        low = record_reading(meter, self.admin, {"value": "80", "measured_at": "2026-07-21T08:00"})
        db.session.commit()
        self.assertEqual(rule.executions[-1].reason, "condition_not_met")
        high = record_reading(meter, self.admin, {"value": "95", "measured_at": "2026-07-21T09:00"})
        db.session.commit()
        execution = MaintenanceAutomationExecution.query.filter_by(rule_id=rule.id, reading_id=high.id).one()
        self.assertEqual(execution.status, "succeeded")
        self.assertIsNotNone(execution.work_order_id)
        order = db.session.get(WorkOrder, execution.work_order_id)
        self.assertEqual(order.machine_id, self.order.machine_id)
        self.assertEqual(order.technician_id, self.tech.id)
        self.assertTrue(order.numero.startswith("OT-"))
        self.assertGreater(MaintenanceAutomationNotification.query.filter_by(execution_id=execution.id).count(), 0)

        record_reading(meter, self.admin, {"value": "100", "measured_at": "2026-07-21T10:00"})
        db.session.commit()
        self.assertEqual(WorkOrder.query.filter(WorkOrder.id != self.order.id).count(), 1)
        self.assertTrue(MaintenanceAutomationExecution.query.filter_by(
            rule_id=rule.id, reason="no_threshold_crossing"
        ).first())

    def test_evaluation_is_idempotent_per_rule_and_reading(self):
        meter = self._meter(code="AUTO_H", name="Horas automáticas")
        rule = self._rule(meter, name="Avisar horas", action_type="notify", threshold="10")
        reading = record_reading(meter, self.admin, {"value": "12", "measured_at": "2026-07-21T08:00"})
        db.session.commit()
        first = evaluate_reading(reading); db.session.commit()
        second = evaluate_reading(reading); db.session.commit()
        self.assertEqual(first[0].id, second[0].id)
        self.assertEqual(MaintenanceAutomationExecution.query.filter_by(rule_id=rule.id, reading_id=reading.id).count(), 1)

    def test_cooldown_skips_repeated_matches(self):
        meter = self._meter(code="AUTO_P", name="Presión", meter_type="gauge", unit="bar")
        rule = self._rule(
            meter, name="Avisar presión", action_type="notify", threshold="5",
            crossing_only="0", cooldown_minutes="60",
        )
        record_reading(meter, self.admin, {"value": "6", "measured_at": "2026-07-21T08:00"})
        record_reading(meter, self.admin, {"value": "7", "measured_at": "2026-07-21T08:05"})
        db.session.commit()
        self.assertEqual(MaintenanceAutomationExecution.query.filter_by(rule_id=rule.id, status="succeeded").count(), 1)
        self.assertEqual(MaintenanceAutomationExecution.query.filter_by(rule_id=rule.id, reason="cooldown_active").count(), 1)

    def test_rule_rejects_cross_tenant_meter_and_actor(self):
        meter = self._meter(code="AUTO_SAFE", name="Seguro")
        with self.assertRaisesRegex(ValueError, "permiso"):
            create_rule(self.company.id, self.other_user, {
                "name": "Cruce", "meter_id": str(meter.id), "operator": "gte", "threshold": "1",
                "action_type": "notify",
            })
        with self.assertRaisesRegex(ValueError, "medidor activo"):
            create_rule(self.other_company.id, self.other_user, {
                "name": "Cruce", "meter_id": str(meter.id), "operator": "gte", "threshold": "1",
                "action_type": "notify",
            })

    def test_routes_are_manager_only_and_notification_is_user_scoped(self):
        meter = self._meter(code="AUTO_ROUTE", name="Ruta")
        rule = self._rule(meter, name="Ruta automática", action_type="notify", threshold="1")
        record_reading(meter, self.admin, {"value": "2", "measured_at": "2026-07-21T08:00"})
        db.session.commit()
        client = self.app.test_client()
        client.post("/login", data={"username": self.admin.username, "empresa_slug": self.company.slug, "password": "Clave-Segura-123!"})
        self.assertEqual(client.get("/maintenance/automation/").status_code, 200)
        self.assertEqual(client.get(f"/maintenance/automation/{rule.id}").status_code, 200)
        self.assertEqual(client.get("/maintenance/automation/notifications").status_code, 200)
        client.post("/logout")
        client.post("/login", data={"username": self.tech_user.username, "empresa_slug": self.company.slug, "password": "Clave-Segura-123!"})
        self.assertEqual(client.get("/maintenance/automation/").status_code, 403)
        self.assertEqual(client.get("/maintenance/automation/notifications").status_code, 200)
