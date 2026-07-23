"""Sprint 22.4 · seguridad y observabilidad de webhooks/API."""

from datetime import date, datetime
import unittest

from app import create_app, db
from app.integrations.entitlements import entitlement_int, entitlements_for_plan
from app.integrations.webhooks import (
    WebhookError,
    create_endpoint,
    delivery_stats,
    sign_payload,
    verify_signature,
)
from app.models import Empresa, PlanSuscripcion, PlanTipo, User, WebhookDelivery, WebhookEndpoint


class TestWebhookSecurityObservability(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.company = Empresa(
            razon_social="SecObs SAS", slug="secobs", email_verified_at=datetime.utcnow()
        )
        self.other = Empresa(
            razon_social="Otro SAS", slug="otro-sec", email_verified_at=datetime.utcnow()
        )
        db.session.add_all([self.company, self.other])
        db.session.flush()
        db.session.add_all(
            [
                PlanSuscripcion(
                    empresa_id=self.company.id,
                    plan=PlanTipo.ENTERPRISE.value,
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=self.other.id,
                    plan=PlanTipo.ENTERPRISE.value,
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        self.admin = User(
            empresa_id=self.company.id,
            username="sec-admin",
            rol="admin",
            area="Sistemas",
            activo=True,
            onboarding_completado=True,
        )
        self.admin.set_password(self.PASSWORD)
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_hmac_verify_rejects_skew_and_tampering(self):
        body = b'{"ok":true}'
        ts = 1_700_000_000
        secret = "whsec_test"
        signature = sign_payload(secret, ts, body)
        self.assertTrue(verify_signature(secret, ts, body, signature, now=ts))
        self.assertFalse(verify_signature(secret, ts, body, signature, now=ts + 301))
        self.assertFalse(verify_signature(secret, ts, b'{"ok":false}', signature, now=ts))

    def test_entitlement_matrix_and_endpoint_limit(self):
        start = entitlements_for_plan(PlanTipo.BASICO.value)
        enterprise = entitlements_for_plan(PlanTipo.ENTERPRISE.value)
        self.assertTrue(start["webhooks.enabled"])
        self.assertLess(start["webhooks.endpoints_max"], enterprise["webhooks.endpoints_max"])
        self.assertEqual(
            entitlement_int(self.company.id, "public_api.requests_per_minute"),
            300,
        )

        # Fuerza límite 1 para validar rechazo
        from app.integrations import entitlements as ent

        original = ent.ENTITLEMENT_MATRIX[PlanTipo.ENTERPRISE.value]["webhooks.endpoints_max"]
        ent.ENTITLEMENT_MATRIX[PlanTipo.ENTERPRISE.value]["webhooks.endpoints_max"] = 1
        try:
            create_endpoint(
                empresa_id=self.company.id,
                name="Uno",
                url="https://example.com/a",
                events=["incident.created"],
                environment="live",
                created_by_id=self.admin.id,
            )
            db.session.commit()
            with self.assertRaises(WebhookError):
                create_endpoint(
                    empresa_id=self.company.id,
                    name="Dos",
                    url="https://example.com/b",
                    events=["incident.created"],
                    environment="live",
                    created_by_id=self.admin.id,
                )
        finally:
            ent.ENTITLEMENT_MATRIX[PlanTipo.ENTERPRISE.value]["webhooks.endpoints_max"] = original

    def test_tenant_isolation_on_delivery_queries(self):
        from app.integrations.webhooks import emit_event

        own, _ = create_endpoint(
            empresa_id=self.company.id,
            name="Own",
            url="https://example.com/own",
            events=["incident.created"],
            environment="live",
            created_by_id=self.admin.id,
        )
        other, _ = create_endpoint(
            empresa_id=self.other.id,
            name="Other",
            url="https://example.com/other",
            events=["incident.created"],
            environment="live",
        )
        emit_event(
            empresa_id=self.other.id,
            event_type="incident.created",
            resource_type="incident",
            resource_id=99,
            data={"incident_id": 99},
        )
        db.session.commit()
        stats = delivery_stats(self.company.id)
        self.assertEqual(stats["endpoints_active"], 1)
        self.assertEqual(WebhookDelivery.query.filter_by(empresa_id=self.company.id).count(), 0)
        self.assertGreaterEqual(
            WebhookDelivery.query.filter_by(empresa_id=self.other.id).count(), 1
        )
        self.assertEqual(own.empresa_id, self.company.id)
        self.assertNotEqual(other.empresa_id, self.company.id)

    def test_admin_stats_endpoint(self):
        client = self.app.test_client()
        client.post(
            "/login",
            data={
                "username": self.admin.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        response = client.get("/api/v1/admin/webhook-stats")
        self.assertEqual(response.status_code, 200)
        self.assertIn("counts", response.json["data"])
        self.assertIn("webhooks.enabled", response.json["data"]["entitlements"])


if __name__ == "__main__":
    unittest.main()
