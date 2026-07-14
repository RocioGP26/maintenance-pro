from datetime import date, datetime, timedelta
import unittest

from app import create_app, db
from app.models import ActiveSession, Empresa, PlanSuscripcion, TenantActivityLog, User


class TestSessionManagement(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Empresa segura",
            slug="segura",
            email_verified_at=datetime.utcnow(),
            session_idle_minutes=30,
            session_absolute_minutes=480,
            session_remember_enabled=False,
        )
        db.session.add(self.empresa)
        db.session.flush()
        self.user = User(
            empresa_id=self.empresa.id,
            username="admin",
            email="admin@example.com",
            rol="superadmin",
            activo=True,
            onboarding_completado=True,
        )
        self.user.set_password("Clave-Segura-123!")
        db.session.add(self.user)
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.empresa.id,
                plan="professional",
                fecha_inicio=date.today(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self, remember=False):
        data = {
            "username": "admin",
            "empresa_slug": "segura",
            "password": "Clave-Segura-123!",
        }
        if remember:
            data["remember"] = "1"
        return self.client.post("/login", data=data)

    def test_login_creates_server_managed_session(self):
        response = self._login()
        self.assertEqual(response.status_code, 302)
        item = ActiveSession.query.one()
        self.assertEqual(item.user_id, self.user.id)
        self.assertFalse(item.remember)
        with self.client.session_transaction() as browser_session:
            self.assertEqual(browser_session["managed_session_key"], item.session_key)
            self.assertEqual(browser_session["_user_id"], self.user.get_id())
            self.assertFalse(browser_session.permanent)

    def test_remember_is_ignored_when_company_disables_it(self):
        self._login(remember=True)
        self.assertFalse(ActiveSession.query.one().remember)
        with self.client.session_transaction() as browser_session:
            self.assertNotIn("_remember", browser_session)

    def test_idle_timeout_revokes_and_audits(self):
        self._login()
        item = ActiveSession.query.one()
        item.last_activity_at = datetime.utcnow() - timedelta(minutes=31)
        db.session.commit()

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        db.session.refresh(item)
        self.assertEqual(item.revoked_reason, "idle_timeout")
        self.assertIsNotNone(item.revoked_at)
        self.assertEqual(TenantActivityLog.query.filter_by(tipo="session_expired").count(), 1)

    def test_absolute_timeout_requires_login_again(self):
        self._login()
        item = ActiveSession.query.one()
        item.absolute_expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)
        db.session.refresh(item)
        self.assertEqual(item.revoked_reason, "absolute_timeout")

    def test_admin_can_open_security_panel(self):
        self._login()
        response = self.client.get("/administracion/seguridad")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sesiones activas", response.data)

    def test_revoked_session_cannot_continue(self):
        self._login()
        item = ActiveSession.query.one()
        item.revoked_at = datetime.utcnow()
        item.revoked_reason = "revocacion_admin"
        db.session.commit()

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_auth_version_invalidates_signed_identity(self):
        self._login()
        self.user.auth_version += 1
        db.session.commit()
        # setUp mantiene un app_context para la BD; limpia el caché que en producción
        # desaparece naturalmente al finalizar cada petición.
        from flask import g

        g.pop("_login_user", None)

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)


if __name__ == "__main__":
    unittest.main()
