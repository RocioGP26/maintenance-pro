"""Sprint 23.2 · hardening de identidad y plataforma."""

from __future__ import annotations

from datetime import date, datetime
import time
import unittest
from unittest.mock import patch

import pyotp
from flask import Flask

from app import create_app, db
from app.models import Empresa, PlanSuscripcion, PlatformAuditLog, User
from app.password_policy import validar_password
from app.security_hardening import (
    production_configuration_errors,
    register_runtime_hardening,
)
from app.tenancy.jwt_auth import generar_token


class TestProductionConfiguration(unittest.TestCase):
    def _valid_config(self) -> dict:
        return {
            "SECRET_KEY": "prod-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg://user:pwd@db/roustix",
            "STORAGE_BACKEND": "s3",
            "STORAGE_BUCKET": "roustix-production",
            "STORAGE_ENDPOINT_URL": "https://account.r2.cloudflarestorage.com",
            "STORAGE_ACCESS_KEY_ID": "access",
            "STORAGE_SECRET_ACCESS_KEY": "secret",
            "MAIL_SUPPRESS_SEND": False,
            "MAIL_SERVER": "smtp.example.com",
            "MAIL_USERNAME": "mailer",
            "MAIL_PASSWORD": "mail-secret",
            "MAIL_DEFAULT_SENDER": "Roustix <mail@example.com>",
            "PLATFORM_ADMIN_KEY": "platform-key-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "PLATFORM_MFA_REQUIRED": True,
            "PLATFORM_ADMIN_TOTP_SECRET": pyotp.random_base32(),
            "DISTRIBUTED_RATE_LIMITS_REQUIRED": True,
            "REDIS_URL": "redis://roustix-keyvalue:6379/0",
        }

    def test_valid_production_configuration_has_no_errors(self):
        self.assertEqual(production_configuration_errors(self._valid_config()), [])

    def test_insecure_fallbacks_and_privileged_mfa_are_rejected(self):
        config = self._valid_config()
        config.update(
            SECRET_KEY="short",
            SQLALCHEMY_DATABASE_URI="sqlite:///local.db",
            STORAGE_BACKEND="local",
            STORAGE_ENDPOINT_URL="http://storage.internal",
            PLATFORM_ADMIN_TOTP_SECRET="",
        )
        errors = " ".join(production_configuration_errors(config))
        self.assertIn("SECRET_KEY", errors)
        self.assertIn("PostgreSQL", errors)
        self.assertIn("STORAGE_BACKEND", errors)
        self.assertIn("HTTPS", errors)
        self.assertIn("PLATFORM_ADMIN_TOTP_SECRET", errors)

    def test_production_rejects_in_memory_rate_limiting(self):
        config = self._valid_config()
        config["REDIS_URL"] = ""
        errors = " ".join(production_configuration_errors(config))
        self.assertIn("REDIS_URL", errors)

    def test_password_policy_has_safe_length_bounds(self):
        self.assertIn("12", validar_password("Abcdef12345") or "")
        self.assertIn("128", validar_password("A1" + ("x" * 127)) or "")
        self.assertIsNone(validar_password("Clave-Segura-123!"))

    def test_host_allowlist_rejects_untrusted_host(self):
        app = Flask(__name__)
        with patch.dict(
            "os.environ",
            {"TRUSTED_HOSTS": "roustix.example", "RENDER_EXTERNAL_HOSTNAME": ""},
            clear=False,
        ):
            register_runtime_hardening(app, production=True)

        @app.get("/")
        def index():
            return "ok"

        client = app.test_client()
        self.assertEqual(client.get("/", headers={"Host": "roustix.example"}).status_code, 200)
        self.assertEqual(client.get("/", headers={"Host": "evil.example"}).status_code, 400)


class TestSecurityHeaders(unittest.TestCase):
    def test_auth_pages_disable_cache_and_add_defensive_headers(self):
        app = create_app("testing")
        app.config["RATELIMIT_ENABLED"] = False
        response = app.test_client().get("/login")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("camera=()", response.headers["Permissions-Policy"])


class SecurityAppTestCase(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.app.config.update(RATELIMIT_ENABLED=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.company = Empresa(
            razon_social="Tenant seguro",
            slug="tenant-seguro",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(self.company)
        db.session.flush()
        self.user = User(
            empresa_id=self.company.id,
            username="admin",
            email="admin@example.com",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        self.user.set_password(self.PASSWORD)
        db.session.add(self.user)
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.company.id,
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


class TestPlatformHardening(SecurityAppTestCase):
    def setUp(self):
        super().setUp()
        self.totp_secret = pyotp.random_base32()
        self.app.config.update(
            PLATFORM_ADMIN_KEY="K" * 48,
            PLATFORM_ADMIN_TOTP_SECRET=self.totp_secret,
            PLATFORM_MFA_REQUIRED=True,
            PLATFORM_SESSION_IDLE_MINUTES=15,
            PLATFORM_SESSION_ABSOLUTE_MINUTES=120,
            PLATFORM_MFA_PENDING_MINUTES=5,
        )

    def _platform_login(self):
        first = self.client.post("/platform/login", data={"clave": "K" * 48})
        self.assertEqual(first.status_code, 200)
        second = self.client.post(
            "/platform/login",
            data={"action": "totp", "totp": pyotp.TOTP(self.totp_secret).now()},
        )
        self.assertEqual(second.status_code, 302)
        return second

    def test_mfa_is_required_when_platform_is_enabled(self):
        self.app.config["PLATFORM_ADMIN_TOTP_SECRET"] = ""
        response = self.client.get("/platform/login")
        self.assertEqual(response.status_code, 503)
        self.assertIn("PLATFORM_ADMIN_TOTP_SECRET", response.get_data(as_text=True))

    def test_totp_creates_short_non_permanent_audited_session(self):
        self._platform_login()
        with self.client.session_transaction() as browser_session:
            self.assertTrue(browser_session["platform_admin"])
            self.assertFalse(browser_session.permanent)
            self.assertIn("platform_started_at", browser_session)
            self.assertIn("platform_last_activity_at", browser_session)
        self.assertEqual(PlatformAuditLog.query.filter_by(accion="platform_login").count(), 1)

    def test_expired_platform_session_is_closed_and_audited(self):
        self._platform_login()
        with self.client.session_transaction() as browser_session:
            browser_session["platform_last_activity_at"] = int(time.time()) - (16 * 60)
        response = self.client.get("/platform/empresas")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/platform/login", response.location)
        with self.client.session_transaction() as browser_session:
            self.assertNotIn("platform_admin", browser_session)
        self.assertEqual(
            PlatformAuditLog.query.filter_by(accion="platform_session_expired").count(),
            1,
        )

    def test_failed_key_is_audited_without_granting_access(self):
        response = self.client.post("/platform/login", data={"clave": "incorrecta"})
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as browser_session:
            self.assertNotIn("platform_admin", browser_session)
        self.assertEqual(
            PlatformAuditLog.query.filter_by(accion="platform_login_failed").count(),
            1,
        )


class TestJwtHardening(SecurityAppTestCase):
    def _api_login(self) -> str:
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": self.user.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        return response.get_json()["token"]

    def _me(self, token: str):
        return self.client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_password_change_revokes_existing_jwt(self):
        token = self._api_login()
        self.assertEqual(self._me(token).status_code, 200)
        self.user.set_password("Otra-Clave-456!")
        self.user.auth_version += 1
        db.session.commit()
        revoked = self._me(token)
        self.assertEqual(revoked.status_code, 401)
        self.assertIn("TOKEN_REVOKED", revoked.get_data(as_text=True))

    def test_blocked_user_cannot_continue_with_existing_jwt(self):
        token = self._api_login()
        self.user.bloqueado = True
        db.session.commit()
        self.assertEqual(self._me(token).status_code, 401)

    def test_token_with_stale_tenant_or_role_is_rejected(self):
        token = generar_token(
            user_id=self.user.id,
            empresa_id=self.company.id + 999,
            empresa_slug=self.company.slug,
            rol="superadmin",
            secret=self.app.config["SECRET_KEY"],
            auth_version=self.user.auth_version,
        )
        self.assertEqual(self._me(token).status_code, 401)


if __name__ == "__main__":
    unittest.main()
