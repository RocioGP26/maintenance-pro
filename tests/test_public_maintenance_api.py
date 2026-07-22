"""Sprint 22.2 · contrato público Maintenance."""

from datetime import date, datetime, timedelta
import unittest

from app import create_app, db
from app.integrations.credentials import issue_credential
from app.maintenance_execution.models import AssetMeter, MeterReading
from app.models import (
    ApiIdempotencyRecord,
    Empresa,
    Incident,
    IncidentNotification,
    Machine,
    MachineType,
    PlanSuscripcion,
    User,
    WorkOrder,
)


class TestPublicMaintenanceApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        now = datetime.utcnow()
        self.company = Empresa(
            razon_social="Maintenance API SAS",
            slug="maintenance-api",
            email_verified_at=now,
        )
        self.other_company = Empresa(
            razon_social="Tenant Externo SAS",
            slug="tenant-externo-api",
            email_verified_at=now,
        )
        db.session.add_all([self.company, self.other_company])
        db.session.flush()
        db.session.add_all(
            [
                PlanSuscripcion(
                    empresa_id=self.company.id,
                    plan="enterprise",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=self.other_company.id,
                    plan="enterprise",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        self.admin = User(
            empresa_id=self.company.id,
            username="api-owner",
            rol="admin",
            area="Mantenimiento",
            activo=True,
            onboarding_completado=True,
        )
        self.admin.set_password("Clave-Segura-123!")
        self.receiver = User(
            empresa_id=self.company.id,
            username="api-receiver",
            rol="supervisor",
            area="Mantenimiento",
            activo=True,
            onboarding_completado=True,
        )
        self.receiver.set_password("Clave-Segura-123!")
        own_type = MachineType(
            empresa_id=self.company.id, clave="api-machine", nombre="Equipo", prefijo="PM"
        )
        other_type = MachineType(
            empresa_id=self.other_company.id, clave="other-machine", nombre="Otro", prefijo="PX"
        )
        db.session.add_all([self.admin, self.receiver, own_type, other_type])
        db.session.flush()
        self.asset = Machine(
            empresa_id=self.company.id,
            machine_type_id=own_type.id,
            codigo="PM-001",
            nombre="Compresor API",
            area="Producción",
            ubicacion="Planta 1",
            criticidad="alta",
            status="operativo",
            updated_at=now,
        )
        self.other_asset = Machine(
            empresa_id=self.other_company.id,
            machine_type_id=other_type.id,
            codigo="PX-001",
            nombre="Activo externo",
            updated_at=now,
        )
        db.session.add_all([self.asset, self.other_asset])
        db.session.flush()
        self.order = WorkOrder(
            empresa_id=self.company.id,
            machine_id=self.asset.id,
            numero="OT-API-001",
            titulo="Inspección API",
            tipo="preventivo",
            prioridad="alta",
            status="abierta",
            fecha_programada=date.today(),
            updated_at=now,
        )
        self.meter = AssetMeter(
            empresa_id=self.company.id,
            machine_id=self.asset.id,
            code="RUNTIME",
            name="Horómetro",
            meter_type="cumulative",
            unit="h",
            decimals=2,
            active=True,
            rules_json="{}",
            created_by_id=self.admin.id,
        )
        db.session.add_all([self.order, self.meter])
        db.session.flush()
        issued = issue_credential(
            empresa_id=self.company.id,
            name="API Maintenance tests",
            environment="test",
            scopes=[
                "maintenance.assets:read",
                "maintenance.incidents:read",
                "maintenance.incidents:write",
                "maintenance.work_orders:read",
                "maintenance.meters:read",
                "maintenance.meters:write",
            ],
            created_by_id=self.admin.id,
        )
        db.session.commit()
        self.secret = issued.secret
        self.headers = {"Authorization": f"Bearer {self.secret}"}
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_assets_use_canonical_envelope_filters_and_request_id(self):
        response = self.client.get(
            "/api/v1/maintenance/assets?status=operational&criticality=alta&page_size=10",
            headers={**self.headers, "X-Request-Id": "request-test-2202"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Request-Id"], "request-test-2202")
        self.assertEqual(response.json["meta"]["api_version"], "v1")
        self.assertEqual(response.json["meta"]["pagination"]["total"], 1)
        self.assertEqual(response.json["data"][0]["asset_code"], self.asset.codigo)
        self.assertNotIn(self.other_asset.codigo, str(response.json))

        invalid = self.client.get(
            "/api/v1/maintenance/assets?unknown=true", headers=self.headers
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.json["error"]["code"], "INVALID_PARAMETER")

    def test_incremental_assets_and_work_order_filters(self):
        future = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
        empty = self.client.get(
            f"/api/v1/maintenance/assets?updated_since={future}", headers=self.headers
        )
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.json["data"], [])

        orders = self.client.get(
            f"/api/v1/maintenance/work-orders?status=open&priority=alta&asset_id={self.asset.id}",
            headers=self.headers,
        )
        self.assertEqual(orders.status_code, 200)
        self.assertEqual(orders.json["data"][0]["number"], self.order.numero)
        detail = self.client.get(
            f"/api/v1/maintenance/work-orders/{self.order.id}", headers=self.headers
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json["data"]["asset_id"], self.asset.id)

    def test_incident_creation_is_idempotent_and_notifies_responsible_area(self):
        payload = {
            "title": "Vibración anormal",
            "description": "Se detecta vibración continua en el compresor.",
            "responsible_area": "Mantenimiento",
            "reporter_area": "Producción",
            "type": "mecanica",
            "priority": "alta",
            "asset_id": self.asset.id,
            "equipment_stopped": True,
        }
        headers = {**self.headers, "Idempotency-Key": "incident-api-0001"}
        created = self.client.post(
            "/api/v1/maintenance/incidents", json=payload, headers=headers
        )
        self.assertEqual(created.status_code, 201)
        incident_id = created.json["data"]["incident_id"]
        repeated = self.client.post(
            "/api/v1/maintenance/incidents", json=payload, headers=headers
        )
        self.assertEqual(repeated.status_code, 201)
        self.assertEqual(repeated.json["data"]["incident_id"], incident_id)
        self.assertEqual(Incident.query.filter_by(empresa_id=self.company.id).count(), 1)
        self.assertEqual(ApiIdempotencyRecord.query.count(), 1)
        self.assertTrue(
            IncidentNotification.query.filter_by(
                incident_id=incident_id, user_id=self.receiver.id
            ).first()
        )

        conflict_payload = dict(payload, title="Cuerpo diferente")
        conflict = self.client.post(
            "/api/v1/maintenance/incidents", json=conflict_payload, headers=headers
        )
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.json["error"]["code"], "IDEMPOTENCY_CONFLICT")

    def test_incident_read_endpoints_are_tenant_safe(self):
        own = Incident(
            empresa_id=self.company.id,
            numero="INC-26-9001",
            titulo="Propia",
            descripcion="Detalle",
            area_responsable="Mantenimiento",
            tipo="mecanica",
            updated_at=datetime.utcnow(),
        )
        foreign = Incident(
            empresa_id=self.other_company.id,
            numero="INC-26-9002",
            titulo="Ajena",
            descripcion="No visible",
            area_responsable="Mantenimiento",
            tipo="mecanica",
            updated_at=datetime.utcnow(),
        )
        db.session.add_all([own, foreign])
        db.session.commit()
        listed = self.client.get("/api/v1/maintenance/incidents", headers=self.headers)
        self.assertEqual(listed.status_code, 200)
        self.assertIn(own.numero, str(listed.json))
        self.assertNotIn(foreign.numero, str(listed.json))
        hidden = self.client.get(
            f"/api/v1/maintenance/incidents/{foreign.id}", headers=self.headers
        )
        self.assertEqual(hidden.status_code, 404)

    def test_meter_reading_is_idempotent_and_updates_domain_services(self):
        meters = self.client.get(
            f"/api/v1/maintenance/assets/{self.asset.id}/meters", headers=self.headers
        )
        self.assertEqual(meters.status_code, 200)
        self.assertEqual(meters.json["data"][0]["code"], "RUNTIME")
        payload = {
            "value": "125.50",
            "measured_at": "2026-07-22T14:30:00Z",
            "notes": "Lectura desde integración",
        }
        headers = {**self.headers, "Idempotency-Key": "meter-reading-0001"}
        created = self.client.post(
            f"/api/v1/maintenance/meters/{self.meter.id}/readings",
            json=payload,
            headers=headers,
        )
        self.assertEqual(created.status_code, 201)
        repeated = self.client.post(
            f"/api/v1/maintenance/meters/{self.meter.id}/readings",
            json=payload,
            headers=headers,
        )
        self.assertEqual(repeated.status_code, 201)
        self.assertEqual(
            repeated.json["data"]["reading_id"], created.json["data"]["reading_id"]
        )
        self.assertEqual(MeterReading.query.filter_by(meter_id=self.meter.id).count(), 1)
        listed = self.client.get(
            f"/api/v1/maintenance/meters/{self.meter.id}/readings",
            headers=self.headers,
        )
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json["data"][0]["value"], "125.500000")

    def test_writes_require_idempotency_key(self):
        response = self.client.post(
            "/api/v1/maintenance/incidents",
            json={"title": "x"},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"]["code"], "IDEMPOTENCY_KEY_REQUIRED")


if __name__ == "__main__":
    unittest.main()
