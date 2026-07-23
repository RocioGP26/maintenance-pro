"""Sprint 22.5 · aislamiento entre empresas (API + webhooks + auditoría)."""

from datetime import date, datetime
import unittest

from app import create_app, db
from app.integrations.credentials import issue_credential
from app.integrations.webhooks import create_endpoint, emit_event
from app.models import (
    Empresa,
    IntegrationEvent,
    Machine,
    MachineType,
    PlanSuscripcion,
    PlanTipo,
    TenantActivityLog,
    User,
    WebhookDelivery,
)


class TestApiTenantIsolation(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.a = Empresa(
            razon_social="Tenant A", slug="tenant-a", email_verified_at=datetime.utcnow()
        )
        self.b = Empresa(
            razon_social="Tenant B", slug="tenant-b", email_verified_at=datetime.utcnow()
        )
        db.session.add_all([self.a, self.b])
        db.session.flush()
        db.session.add_all(
            [
                PlanSuscripcion(
                    empresa_id=self.a.id,
                    plan=PlanTipo.ENTERPRISE.value,
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=self.b.id,
                    plan=PlanTipo.ENTERPRISE.value,
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        self.admin_a = User(
            empresa_id=self.a.id,
            username="admin-a",
            rol="admin",
            area="TI",
            activo=True,
            onboarding_completado=True,
        )
        self.admin_a.set_password(self.PASSWORD)
        type_a = MachineType(
            empresa_id=self.a.id, clave="ta", nombre="Tipo A", prefijo="TA"
        )
        type_b = MachineType(
            empresa_id=self.b.id, clave="tb", nombre="Tipo B", prefijo="TB"
        )
        db.session.add_all([self.admin_a, type_a, type_b])
        db.session.flush()
        self.asset_a = Machine(
            empresa_id=self.a.id,
            machine_type_id=type_a.id,
            codigo="TA-001",
            nombre="Activo A",
        )
        self.asset_b = Machine(
            empresa_id=self.b.id,
            machine_type_id=type_b.id,
            codigo="TB-001",
            nombre="Activo B",
        )
        db.session.add_all([self.asset_a, self.asset_b])
        db.session.commit()
        self.key_a = issue_credential(
            empresa_id=self.a.id,
            name="Key A",
            environment="test",
            scopes=["maintenance.assets:read"],
            created_by_id=self.admin_a.id,
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_api_key_cannot_read_other_tenant_asset(self):
        client = self.app.test_client()
        headers = {"Authorization": f"Bearer {self.key_a.secret}"}
        own = client.get(f"/api/v1/maintenance/assets/{self.asset_a.id}", headers=headers)
        self.assertEqual(own.status_code, 200)
        foreign = client.get(
            f"/api/v1/maintenance/assets/{self.asset_b.id}", headers=headers
        )
        self.assertEqual(foreign.status_code, 404)
        listed = client.get("/api/v1/maintenance/assets", headers=headers)
        codes = [item["asset_code"] for item in listed.json["data"]]
        self.assertIn(self.asset_a.codigo, codes)
        self.assertNotIn(self.asset_b.codigo, codes)

    def test_webhook_events_do_not_cross_tenants(self):
        create_endpoint(
            empresa_id=self.a.id,
            name="Hook A",
            url="https://example.com/a",
            events=["incident.created"],
            environment="live",
            created_by_id=self.admin_a.id,
        )
        create_endpoint(
            empresa_id=self.b.id,
            name="Hook B",
            url="https://example.com/b",
            events=["incident.created"],
            environment="live",
        )
        emit_event(
            empresa_id=self.b.id,
            event_type="incident.created",
            resource_type="incident",
            resource_id=7,
            data={"incident_id": 7},
        )
        db.session.commit()
        self.assertEqual(
            IntegrationEvent.query.filter_by(empresa_id=self.a.id).count(), 0
        )
        self.assertEqual(
            WebhookDelivery.query.filter_by(empresa_id=self.a.id).count(), 0
        )
        self.assertGreaterEqual(
            IntegrationEvent.query.filter_by(empresa_id=self.b.id).count(), 1
        )
        for delivery in WebhookDelivery.query.filter_by(empresa_id=self.b.id).all():
            self.assertEqual(delivery.empresa_id, self.b.id)
            self.assertEqual(delivery.event.empresa_id, self.b.id)
            self.assertEqual(delivery.endpoint.empresa_id, self.b.id)

    def test_integration_audit_is_tenant_scoped(self):
        client = self.app.test_client()
        login = client.post(
            "/login",
            data={
                "username": self.admin_a.username,
                "empresa_slug": self.a.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(login.status_code, 302)
        created = client.post(
            "/api/v1/admin/webhooks",
            json={
                "name": "Audit Hook",
                "url": "https://example.com/audit",
                "environment": "live",
                "events": ["incident.created"],
            },
        )
        self.assertEqual(created.status_code, 201)
        audit = client.get("/api/v1/admin/integration-audit")
        self.assertEqual(audit.status_code, 200)
        tipos = {row["tipo"] for row in audit.json["data"]}
        self.assertIn("webhook_endpoint_created", tipos)
        # No debe filtrar filas de otro tenant aunque existan
        db.session.add(
            TenantActivityLog(
                empresa_id=self.b.id,
                tipo="webhook_endpoint_created",
                username="intruso",
                detalle="no debe verse",
            )
        )
        db.session.commit()
        audit2 = client.get("/api/v1/admin/integration-audit")
        detalles = [row["detalle"] for row in audit2.json["data"]]
        self.assertNotIn("no debe verse", detalles)


if __name__ == "__main__":
    unittest.main()
