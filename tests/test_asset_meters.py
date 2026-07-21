"""Sprint 19.5 · medidores, lecturas, integración y cierre."""

from datetime import datetime, timedelta

from app import db
from app.maintenance_execution.meter_service import (
    can_view_meters,
    create_meter,
    record_reading,
    seed_legacy_runtime_meters,
)
from app.maintenance_execution.models import AssetMeter, MeterEvent, MeterReading
from tests import test_work_order_checklists as checklist_base


class TestAssetMeters(checklist_base.TestWorkOrderChecklists):
    def _meter(self, **values):
        data = {
            "code": "HOURS", "name": "Horómetro", "meter_type": "cumulative",
            "unit": "h", "decimals": "1", "min_value": "", "max_value": "",
        }
        data.update(values)
        meter = create_meter(self.order.machine, self.admin, data)
        db.session.commit()
        return meter

    def test_cumulative_regression_requires_explicit_justification(self):
        meter = self._meter()
        first = record_reading(meter, self.tech_user, {
            "value": "100", "measured_at": "2026-07-21T08:00",
        })
        db.session.commit()
        self.assertFalse(first.flagged)
        with self.assertRaisesRegex(ValueError, "altera la secuencia"):
            record_reading(meter, self.tech_user, {
                "value": "20", "measured_at": "2026-07-21T09:00",
            })
        flagged = record_reading(meter, self.admin, {
            "value": "20", "measured_at": "2026-07-21T09:00", "anomaly_type": "replacement",
            "justification": "Se reemplazó físicamente el horómetro", "performed_by_user_id": str(self.tech_user.id),
        })
        db.session.commit()
        self.assertTrue(flagged.flagged)
        self.assertEqual(flagged.performed_by_user_id, self.tech_user.id)
        self.assertEqual(flagged.recorded_by_user_id, self.admin.id)
        self.assertTrue(MeterEvent.query.filter_by(
            reading_id=flagged.id, event="maintenance.meter.reading_flagged"
        ).first())

    def test_gauge_out_of_range_and_correction_are_audited_without_overwrite(self):
        meter = self._meter(
            code="TEMP", name="Temperatura", meter_type="gauge", unit="°C",
            min_value="10", max_value="80", decimals="1",
        )
        original = record_reading(meter, self.admin, {
            "value": "40", "measured_at": "2026-07-21T08:00",
        })
        db.session.commit()
        with self.assertRaisesRegex(ValueError, "fuera del rango"):
            record_reading(meter, self.admin, {
                "value": "95", "measured_at": "2026-07-21T09:00",
            })
        correction = record_reading(meter, self.admin, {
            "value": "42", "measured_at": "2026-07-21T08:00",
            "correction_of_id": str(original.id), "justification": "Corrección de digitación",
        })
        db.session.commit()
        self.assertEqual(correction.source, "correction")
        self.assertEqual(correction.correction_of_id, original.id)
        self.assertEqual(float(original.value), 40.0)

    def test_tenant_and_operational_relationship_protect_meter_access(self):
        meter = self._meter()
        self.assertTrue(can_view_meters(self.admin, self.order.machine))
        self.assertTrue(can_view_meters(self.tech_user, self.order.machine))
        self.assertFalse(can_view_meters(self.other_user, self.order.machine))
        with self.assertRaisesRegex(ValueError, "permiso"):
            record_reading(meter, self.other_user, {"value": "5"})

    def test_legacy_runtime_seed_is_idempotent(self):
        self.order.machine.horas_operacion = 321.5
        db.session.commit()
        self.assertEqual(seed_legacy_runtime_meters(self.company.id), 1)
        db.session.commit()
        self.assertEqual(seed_legacy_runtime_meters(self.company.id), 0)
        db.session.commit()
        meter = AssetMeter.query.filter_by(
            empresa_id=self.company.id, machine_id=self.order.machine_id, code="RUNTIME_HOURS"
        ).one()
        readings = MeterReading.query.filter_by(meter_id=meter.id).all()
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0].source, "legacy_migration")
        self.assertEqual(float(readings[0].value), 321.5)

    def test_routes_render_and_technician_records_related_reading(self):
        meter = self._meter()
        client = self.app.test_client()
        client.post("/login", data={
            "username": self.tech_user.username, "empresa_slug": self.company.slug,
            "password": "Clave-Segura-123!",
        })
        page = client.get(
            f"/maintenance/procedures/assets/{self.order.machine_id}/meters?work_order_id={self.order.id}"
        )
        self.assertEqual(page.status_code, 200)
        self.assertIn("Horómetro", page.get_data(as_text=True))
        response = client.post(
            f"/maintenance/procedures/assets/{self.order.machine_id}/meters/{meter.id}/reading",
            data={
                "value": "44.5", "measured_at": "2026-07-21T10:30",
                "work_order_id": str(self.order.id),
            },
        )
        self.assertEqual(response.status_code, 302)
        reading = MeterReading.query.filter_by(meter_id=meter.id).one()
        self.assertEqual(reading.work_order_id, self.order.id)
        self.assertEqual(reading.performed_by_user_id, self.tech_user.id)

