"""Restablecimiento self-service de contraseña por correo."""

from __future__ import annotations

import re
import unittest
from datetime import datetime, timedelta
from urllib.parse import urlparse

from app import create_app, db, limiter
from app.models import ActiveSession, Empresa, PasswordReset, User
from app.password_reset_service import (
    GENERIC_REQUEST_MESSAGE,
    consume_password_reset,
    get_valid_reset,
    request_password_reset,
)


class TestPasswordReset(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        limiter.reset()
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
        limiter.reset()
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

    def test_new_request_invalidates_previous_token(self):
        request_password_reset("ops@example.com")
        first_raw = self._raw_token_from_outbox()

        request_password_reset("ops@example.com")
        second_raw = self._raw_token_from_outbox()

        self.assertIsNone(get_valid_reset(first_raw))
        self.assertIsNotNone(get_valid_reset(second_raw))
        first, second = PasswordReset.query.order_by(PasswordReset.id).all()
        self.assertIsNotNone(first.used_at)
        self.assertIsNone(second.used_at)

    def test_consumed_token_cannot_be_reused(self):
        request_password_reset("ops@example.com")
        raw = self._raw_token_from_outbox()

        self.assertIsNone(consume_password_reset(raw, "Clave-Nueva-456!"))
        second_attempt = consume_password_reset(raw, "Otra-Clave-789!")

        self.assertIsNotNone(second_attempt)
        self.assertIn("enlace", second_attempt.lower())
        db.session.refresh(self.user)
        self.assertTrue(self.user.check_password("Clave-Nueva-456!"))

    def test_consumed_link_is_rejected_even_after_new_login(self):
        request_password_reset("ops@example.com")
        raw = self._raw_token_from_outbox()
        self.assertIsNone(consume_password_reset(raw, "Clave-Nueva-456!"))

        login = self.client.post(
            "/login",
            data={
                "username": "operador",
                "empresa_slug": "empresa-demo",
                "password": "Clave-Nueva-456!",
            },
        )
        self.assertIn(login.status_code, (302, 303))

        reused = self.client.get(f"/restablecer-contrasena/{raw}")
        self.assertEqual(reused.status_code, 200)
        body = reused.get_data(as_text=True)
        self.assertIn("Solicitar un enlace nuevo", body)
        self.assertNotIn("/dashboard", reused.request.path)

        request_page = self.client.get("/recuperar-contrasena")
        self.assertEqual(request_page.status_code, 200)
        self.assertIn("Enviar enlace", request_page.get_data(as_text=True))

        requested = self.client.post(
            "/recuperar-contrasena",
            data={"email": "ops@example.com", "empresa_slug": "empresa-demo"},
        )
        self.assertIn(requested.status_code, (302, 303))
        self.assertTrue(requested.location.endswith("/recuperar-contrasena"))

    def test_reset_revokes_existing_managed_session(self):
        active_client = self.app.test_client()
        login = active_client.post(
            "/login",
            data={
                "username": "operador",
                "empresa_slug": "empresa-demo",
                "password": "Clave-Antigua-123!",
            },
        )
        self.assertIn(login.status_code, (302, 303))
        managed_session = ActiveSession.query.one()
        self.assertIsNone(managed_session.revoked_at)

        # setUp conserva el app context para la BD. Limpia el usuario cacheado
        # antes de simular un segundo navegador anonimo.
        from flask import g

        g.pop("_login_user", None)
        reset_client = self.app.test_client()
        reset_client.post(
            "/recuperar-contrasena",
            data={"email": "ops@example.com", "empresa_slug": "empresa-demo"},
        )
        raw = self._raw_token_from_outbox()
        done = reset_client.post(
            f"/restablecer-contrasena/{raw}",
            data={
                "password": "Clave-Nueva-456!",
                "password_confirm": "Clave-Nueva-456!",
            },
        )
        self.assertIn(done.status_code, (302, 303))

        db.session.refresh(managed_session)
        self.assertIsNotNone(managed_session.revoked_at)
        self.assertEqual(managed_session.revoked_reason, "password_reset")
        g.pop("_login_user", None)
        blocked = active_client.get("/dashboard")
        self.assertIn(blocked.status_code, (302, 303))
        self.assertIn("/login", blocked.location)

    def test_request_endpoint_hides_account_existence(self):
        known = self.client.post(
            "/recuperar-contrasena",
            data={"email": "ops@example.com", "empresa_slug": "empresa-demo"},
            follow_redirects=True,
        )
        unknown = self.client.post(
            "/recuperar-contrasena",
            data={"email": "nadie@example.com", "empresa_slug": "empresa-demo"},
            follow_redirects=True,
        )

        self.assertEqual(known.status_code, 200)
        self.assertEqual(unknown.status_code, 200)
        self.assertIn(GENERIC_REQUEST_MESSAGE, known.get_data(as_text=True))
        self.assertIn(GENERIC_REQUEST_MESSAGE, unknown.get_data(as_text=True))

    def test_request_endpoint_rate_limits_sixth_attempt(self):
        responses = [
            self.client.post(
                "/recuperar-contrasena",
                data={"email": "nadie@example.com", "empresa_slug": "empresa-demo"},
            )
            for _ in range(6)
        ]

        self.assertTrue(
            all(response.status_code in (302, 303) for response in responses[:5])
        )
        self.assertEqual(responses[5].status_code, 429)

    def test_faq_mentions_forgot_password(self):
        response = self.client.get("/faq")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("¿Olvidaste tu contraseña?", body)
        self.assertIn("correo corporativo", body)


if __name__ == "__main__":
    unittest.main()
