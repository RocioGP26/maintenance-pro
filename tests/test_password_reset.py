"""Restablecimiento self-service de contraseña por correo."""

from __future__ import annotations

import re
import unittest
from datetime import datetime, timedelta
from urllib.parse import urlparse

from app import create_app, db
from app.models import Empresa, PasswordReset, User
from app.password_reset_service import (
    GENERIC_REQUEST_MESSAGE,
    consume_password_reset,
    get_valid_reset,
    request_password_reset,
)


class TestPasswordReset(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Empresa Demo",
            slug="empresa-demo",
            email="ops@example.com",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(self.empresa)
        db.session.flush()
        self.user = User(
            empresa_id=self.empresa.id,
            username="operador",
            email="ops@example.com",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        self.user.set_password("Clave-Antigua-123!")
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _raw_token_from_outbox(self) -> str:
        message = self.app.extensions["mail_outbox"][-1]
        body = message.get_body(preferencelist=("plain",)).get_content()
        match = re.search(r"/restablecer-contrasena/([A-Za-z0-9_\-]+)", body)
        self.assertIsNotNone(match, body)
        return match.group(1)

    def test_login_shows_forgot_password_link(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("¿Olvidaste tu contraseña?", body)
        self.assertIn("/recuperar-contrasena", body)
        self.assertIn("Ingresar", body)

    def test_request_is_anti_enumeration_and_sends_mail(self):
        msg_ok = request_password_reset("ops@example.com", empresa_slug="empresa-demo")
        self.assertEqual(msg_ok, GENERIC_REQUEST_MESSAGE)
        self.assertEqual(len(self.app.extensions["mail_outbox"]), 1)
        self.assertEqual(PasswordReset.query.count(), 1)
        item = PasswordReset.query.one()
        raw = self._raw_token_from_outbox()
        self.assertNotEqual(item.token_hash, raw)
        self.assertNotIn(raw, item.token_hash)

        msg_unknown = request_password_reset("nadie@example.com")
        self.assertEqual(msg_unknown, GENERIC_REQUEST_MESSAGE)
        self.assertEqual(len(self.app.extensions["mail_outbox"]), 1)

    def test_http_flow_resets_password_and_revokes_old(self):
        response = self.client.post(
            "/recuperar-contrasena",
            data={"email": "ops@example.com", "empresa_slug": "empresa-demo"},
        )
        self.assertIn(response.status_code, (302, 303))
        self.assertTrue(response.location.endswith("/login"))
        raw = self._raw_token_from_outbox()

        page = self.client.get(f"/restablecer-contrasena/{raw}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Nueva contraseña", page.get_data(as_text=True))

        done = self.client.post(
            f"/restablecer-contrasena/{raw}",
            data={
                "password": "Clave-Nueva-456!",
                "password_confirm": "Clave-Nueva-456!",
            },
        )
        self.assertIn(done.status_code, (302, 303))
        self.assertIn("/login", urlparse(done.location).path)

        db.session.refresh(self.user)
        self.assertTrue(self.user.check_password("Clave-Nueva-456!"))
        self.assertFalse(self.user.check_password("Clave-Antigua-123!"))
        self.assertEqual(self.user.auth_version, 2)
        self.assertIsNotNone(PasswordReset.query.one().used_at)
        self.assertIsNone(get_valid_reset(raw))

        # Tras el reset, el login debe aceptar correo o username.
        login_email = self.client.post(
            "/login",
            data={
                "username": "ops@example.com",
                "empresa_slug": "empresa-demo",
                "password": "Clave-Nueva-456!",
            },
        )
        self.assertIn(login_email.status_code, (302, 303))

    def test_expired_token_rejected(self):
        request_password_reset("ops@example.com")
        raw = self._raw_token_from_outbox()
        item = PasswordReset.query.one()
        item.expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        self.assertIsNone(get_valid_reset(raw))
        err = consume_password_reset(raw, "Clave-Nueva-456!")
        self.assertIn("no es válido", err.lower())

    def test_faq_mentions_forgot_password(self):
        response = self.client.get("/faq")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("¿Olvidaste tu contraseña?", body)
        self.assertIn("correo corporativo", body)


if __name__ == "__main__":
    unittest.main()
