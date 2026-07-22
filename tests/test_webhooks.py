"""Sprint 22.3 · webhooks: outbox, HMAC, SSRF y reintentos."""

from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import unittest

from app import create_app, db
from app.integrations.emitters import (
    emit_incident_created,
    emit_work_order_status_changed,
)
from app.integrations.webhooks import (
    WebhookError,
    create_endpoint,
    process_pending_deliveries,
    sign_payload,
    unseal_secret,
    validate_webhook_url,
)
from app.models import (
    Empresa,
    Incident,
    IntegrationEvent,
    Machine,
    MachineType,
    PlanSuscripcion,
    User,
    WebhookDelivery,
    WorkOrder,
    WorkOrderStatus,
)


class _CaptureHandler(BaseHTTPRequestHandler):
    requests = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        type(self).requests.append({"headers": dict(self.headers), "body": body})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        return


class TestWebhooks(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.company = Empresa(
            razon_social="Webhooks SAS", slug="webhooks-tenant", email_verified_at=datetime.utcnow()
        )
        db.session.add(self.company)
        db.session.flush()
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.company.id,
                plan="enterprise",
                fecha_inicio=date.today(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        self.admin = User(
            empresa_id=self.company.id,
            username="wh-admin",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        self.admin.set_password(self.PASSWORD)
        mtype = MachineType(
            empresa_id=self.company.id, clave="wh", nombre="Equipo WH", prefijo="WH"
        )
        db.session.add_all([self.admin, mtype])
        db.session.flush()
        self.machine = Machine(
            empresa_id=self.company.id,
            machine_type_id=mtype.id,
            codigo="WH-001",
            nombre="Activo WH",
        )
        db.session.add(self.machine)
        db.session.commit()
        _CaptureHandler.requests = []

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _server(self):
        server = HTTPServer(("127.0.0.1", 0), _CaptureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_address[1]
        return server, f"http://127.0.0.1:{port}/hook"

    def test_ssrf_blocks_private_and_localhost_for_live(self):
        with self.assertRaises(WebhookError):
            validate_webhook_url("http://127.0.0.1/hook", allow_http=False)
        with self.assertRaises(WebhookError):
            validate_webhook_url("https://127.0.0.1/hook", allow_http=False)

    def test_outbox_hmac_delivery_and_signature(self):
        server, url = self._server()
        try:
            endpoint, secret = create_endpoint(
                empresa_id=self.company.id,
                name="Receptor local",
                url=url,
                events=["incident.created", "work_order.completed"],
                environment="test",
                created_by_id=self.admin.id,
            )
            db.session.commit()
            self.assertTrue(secret.startswith("whsec_"))
            self.assertEqual(unseal_secret(endpoint.secret_sealed), secret)

            incident = Incident(
                empresa_id=self.company.id,
                numero="INC-WH-1",
                titulo="Fuga",
                descripcion="Detalle",
                machine_id=self.machine.id,
                user_id=self.admin.id,
                area_responsable="Mantenimiento",
                tipo="falla",
                prioridad="alta",
                estado="reportado",
            )
            db.session.add(incident)
            db.session.flush()
            emit_incident_created(incident)
            db.session.commit()

            event = IntegrationEvent.query.filter_by(
                empresa_id=self.company.id, event_type="incident.created"
            ).one()
            delivery = WebhookDelivery.query.filter_by(event_id=event.id).one()
            self.assertEqual(delivery.status, "pending")

            stats = process_pending_deliveries(limit=10)
            self.assertEqual(stats["delivered"], 1)
            self.assertEqual(len(_CaptureHandler.requests), 1)
            captured = _CaptureHandler.requests[0]
            body = captured["body"]
            ts = int(captured["headers"]["X-Roustix-Timestamp"])
            expected = sign_payload(secret, ts, body)
            self.assertEqual(captured["headers"]["X-Roustix-Signature"], expected)
            self.assertEqual(captured["headers"]["X-Roustix-Event-Id"], event.public_id)
            payload = json.loads(body.decode("utf-8"))
            self.assertEqual(payload["type"], "incident.created")
            self.assertEqual(payload["data"]["object"]["incident_id"], incident.id)
        finally:
            server.shutdown()

    def test_work_order_completed_emits_specific_event(self):
        order = WorkOrder(
            empresa_id=self.company.id,
            machine_id=self.machine.id,
            titulo="OT webhook",
            tipo="correctivo",
            status=WorkOrderStatus.ABIERTA.value,
            numero="OT-WH-1",
        )
        db.session.add(order)
        db.session.flush()
        emit_work_order_status_changed(order, previous_status=WorkOrderStatus.ABIERTA.value)
        order.status = WorkOrderStatus.COMPLETADO.value
        emit_work_order_status_changed(order, previous_status=WorkOrderStatus.ABIERTA.value)
        db.session.commit()
        types = {
            row.event_type
            for row in IntegrationEvent.query.filter_by(empresa_id=self.company.id).all()
        }
        self.assertIn("work_order.status_changed", types)
        self.assertIn("work_order.completed", types)

    def test_admin_api_creates_endpoint_session_only(self):
        client = self.app.test_client()
        denied = client.post(
            "/api/v1/admin/webhooks",
            json={"name": "x", "url": "https://example.com/hook", "events": ["incident.created"]},
        )
        self.assertEqual(denied.status_code, 403)
        login = client.post(
            "/login",
            data={
                "username": self.admin.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(login.status_code, 302)
        created = client.post(
            "/api/v1/admin/webhooks",
            json={
                "name": "ERP",
                "url": "https://example.com/hooks/roustix",
                "events": ["incident.created", "work_order.closed"],
                "environment": "live",
            },
        )
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.json["data"]["secret"].startswith("whsec_"))
        listed = client.get("/api/v1/admin/webhooks")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json["data"]), 1)
        self.assertNotIn("secret", listed.json["data"][0])


if __name__ == "__main__":
    unittest.main()
