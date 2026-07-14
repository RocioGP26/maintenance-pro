"""Registro empresarial: verificación de correo y bloqueo de acceso."""

from __future__ import annotations

import re
import unittest
from datetime import datetime, timedelta

from app import create_app, db
from app.email_verification_service import (
    ResendCooldown,
    VerificationStatus,
    issue_verification,
    send_welcome_email,
    verify_code,
)
from app.models import EmailVerification, Empresa, User


class TestEmailVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Empresa pendiente",
            slug="empresa-pendiente",
            email="admin@example.com",
            email_verified_at=None,
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
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _issued_code(self) -> str:
        issue_verification(self.user)
        message = self.app.extensions["mail_outbox"][-1]
        body = message.get_body(preferencelist=("plain",)).get_content()
        match = re.search(r"\b(\d{6})\b", body)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_code_is_hashed_and_confirmation_enables_company(self):
        code = self._issued_code()
        item = EmailVerification.query.one()

        self.assertNotEqual(item.code_hash, code)
        self.assertNotIn(code, item.code_hash)
        self.assertIsNone(self.empresa.email_verified_at)
        self.assertEqual(verify_code(self.user, code), VerificationStatus.VERIFIED)
        self.assertIsNotNone(self.empresa.email_verified_at)
        self.assertIsNotNone(item.used_at)

        send_welcome_email(self.user)
        self.assertEqual(len(self.app.extensions["mail_outbox"]), 2)
        self.assertIn("bienvenida", self.app.extensions["mail_outbox"][-1]["Subject"].lower())

    def test_expired_code_is_rejected(self):
        code = self._issued_code()
        item = EmailVerification.query.one()
        item.expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()

        self.assertEqual(verify_code(self.user, code), VerificationStatus.EXPIRED)
        self.assertIsNone(self.empresa.email_verified_at)

    def test_attempt_limit_locks_the_challenge(self):
        self.app.config["EMAIL_VERIFICATION_MAX_ATTEMPTS"] = 2
        self._issued_code()

        self.assertEqual(verify_code(self.user, "111111"), VerificationStatus.INVALID)
        self.assertEqual(verify_code(self.user, "222222"), VerificationStatus.LOCKED)
        self.assertEqual(verify_code(self.user, "333333"), VerificationStatus.LOCKED)
        self.assertEqual(EmailVerification.query.one().attempts, 2)

    def test_resend_requires_cooldown_and_invalidates_previous_code(self):
        first_code = self._issued_code()
        with self.assertRaises(ResendCooldown):
            issue_verification(self.user, enforce_cooldown=True)

        first = EmailVerification.query.one()
        first.sent_at = datetime.utcnow() - timedelta(minutes=2)
        db.session.commit()
        second = issue_verification(self.user, enforce_cooldown=True)

        self.assertIsNotNone(first.used_at)
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(verify_code(self.user, first_code), VerificationStatus.INVALID)

    def test_login_and_authenticated_requests_are_blocked_until_confirmation(self):
        client = self.app.test_client()
        response = client.post(
            "/login",
            data={
                "username": "admin",
                "empresa_slug": "empresa-pendiente",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.location.endswith("/onboarding/verificar-correo"),
            response.location,
        )
        with client.session_transaction() as session:
            self.assertNotIn("_user_id", session)
            self.assertEqual(session["pending_email_verification_user_id"], self.user.id)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "empresa_slug": "empresa-pendiente",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["codigo"], "email_no_verificado")

        from app.tenant_activity import empresa_puede_operar

        with self.app.test_request_context("/dashboard"):
            allowed, code, _message = empresa_puede_operar(self.empresa)
        self.assertFalse(allowed)
        self.assertEqual(code, "email_no_verificado")

    def test_confirmation_route_logs_in_and_sends_welcome_email(self):
        code = self._issued_code()
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["pending_email_verification_user_id"] = self.user.id

        response = client.post(
            "/onboarding/verificar-correo",
            data={"code": code},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/dashboard?welcome=1"))
        with client.session_transaction() as session:
            self.assertEqual(session["_user_id"], self.user.get_id())
            self.assertIn("managed_session_key", session)
            self.assertNotIn("pending_email_verification_user_id", session)
        self.assertIsNotNone(self.empresa.email_verified_at)
        self.assertEqual(len(self.app.extensions["mail_outbox"]), 2)
        self.assertIn("bienvenida", self.app.extensions["mail_outbox"][-1]["Subject"].lower())


if __name__ == "__main__":
    unittest.main()
