"""Cifrado, idempotencia, reintentos y aislamiento de la outbox de correo."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app import create_app, db
from app.email_service import (
    EmailDeliveryError,
    prune_email_outbox,
    process_pending_emails,
    send_templated_email,
)
from app.models import EmailOutbox, Empresa, User


class TestEmailOutbox(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app.config["EMAIL_OUTBOX_SYNC_IN_TESTS"] = False
        self.app.config["MAIL_DEFAULT_SENDER"] = "Roustix <mailer@example.com>"
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Tenant Uno", slug="tenant-uno", email="admin@example.com"
        )
        db.session.add(self.empresa)
        db.session.flush()
        self.user = User(
            empresa_id=self.empresa.id, username="admin", email="admin@example.com",
            rol="admin", activo=True,
        )
        self.user.set_password("Clave-Segura-123!")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _enqueue(self, *, key="verification:1", recipient="admin@example.com"):
        item = send_templated_email(
            empresa_id=self.empresa.id,
            recipient=recipient,
            subject="Código confidencial 654321",
            template_name="verification_code",
            context={
                "code": "654321", "user": self.user, "empresa": self.empresa,
                "ttl_minutes": 10,
            },
            idempotency_key=key,
        )
        db.session.commit()
        return item

    def test_sensitive_payload_is_encrypted_and_delivery_succeeds(self):
        item = self._enqueue()
        self.assertNotIn("654321", item.payload_sealed)
        self.assertNotIn("admin@example.com", item.payload_sealed)
        self.assertEqual(item.status, "pending")

        stats = process_pending_emails(limit=10)

        db.session.refresh(item)
        self.assertEqual(stats["email_sent"], 1)
        self.assertEqual(item.status, "sent")
        self.assertEqual(item.attempts, 1)
        self.assertEqual(len(self.app.extensions["mail_outbox"]), 1)

    def test_idempotency_is_scoped_by_tenant(self):
        first = self._enqueue(key="same-key")
        duplicate = self._enqueue(key="same-key")
        self.assertEqual(first.id, duplicate.id)

        other = Empresa(razon_social="Tenant Dos", slug="tenant-dos", email="dos@example.com")
        db.session.add(other)
        db.session.commit()
        second_tenant = send_templated_email(
            empresa_id=other.id, recipient="dos@example.com", subject="Bienvenida",
            template_name="welcome", context={"user": self.user, "empresa": other},
            idempotency_key="same-key",
        )
        db.session.commit()
        self.assertNotEqual(first.id, second_tenant.id)
        self.assertEqual(EmailOutbox.query.count(), 2)

    def test_failure_schedules_retry_without_persisting_provider_detail(self):
        item = self._enqueue()
        with patch(
            "app.email_service._deliver_message",
            side_effect=EmailDeliveryError("password=super-secret"),
        ):
            stats = process_pending_emails(limit=10)

        db.session.refresh(item)
        self.assertEqual(stats["email_retry"], 1)
        self.assertEqual(item.status, "pending")
        self.assertEqual(item.last_error, "EmailDeliveryError")
        self.assertNotIn("super-secret", item.last_error)
        self.assertGreater(item.next_attempt_at, datetime.utcnow())

        item.next_attempt_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        stats = process_pending_emails(limit=10)
        db.session.refresh(item)
        self.assertEqual(stats["email_sent"], 1)
        self.assertEqual(item.status, "sent")
        self.assertEqual(item.attempts, 2)

    def test_invalid_smtp_hostname_is_a_retryable_delivery_error(self):
        item = self._enqueue()
        self.app.config["MAIL_SUPPRESS_SEND"] = False
        self.app.config.update(
            MAIL_SERVER="x" * 80,
            MAIL_USERNAME="mailer@example.com",
            MAIL_PASSWORD="app-password",
            MAIL_DEFAULT_SENDER="Roustix <mailer@example.com>",
        )

        stats = process_pending_emails(limit=10)

        db.session.refresh(item)
        self.assertEqual(stats["email_retry"], 1)
        self.assertEqual(item.status, "pending")
        self.assertEqual(item.last_error, "EmailDeliveryError")

    def test_tampered_payload_fails_closed(self):
        item = self._enqueue()
        item.payload_sealed = item.payload_sealed[:-2] + "xx"
        db.session.commit()

        stats = process_pending_emails(limit=10)

        db.session.refresh(item)
        self.assertEqual(stats["email_failed"], 1)
        self.assertEqual(item.status, "failed")
        self.assertEqual(item.last_error, "EmailPayloadError")

    def test_dedicated_key_can_read_pending_legacy_envelope(self):
        self.app.config["OUTBOX_ENCRYPTION_KEY"] = ""
        item = self._enqueue()
        legacy_payload = item.payload_sealed

        self.app.config["OUTBOX_ENCRYPTION_KEY"] = "dedicated-key-0123456789-ABCDEFGHIJKLMN"
        stats = process_pending_emails(limit=10)

        db.session.refresh(item)
        self.assertEqual(stats["email_sent"], 1)
        self.assertEqual(item.status, "sent")
        self.assertEqual(item.payload_sealed, legacy_payload)

    def test_terminal_payloads_are_pruned_after_retention(self):
        item = self._enqueue()
        item_id = item.id
        process_pending_emails(limit=10)
        item.updated_at = datetime.utcnow() - timedelta(days=31)
        db.session.commit()

        removed = prune_email_outbox()
        db.session.commit()

        self.assertEqual(removed, 1)
        self.assertIsNone(db.session.get(EmailOutbox, item_id))

    def test_certification_cli_proves_idempotency_without_exposing_recipient(self):
        runner = self.app.test_cli_runner()
        args = [
            "email-outbox", "certify-idempotency",
            "--empresa-slug", self.empresa.slug,
            "--user-email", self.user.email,
            "--run-id", "pilot-20260801",
        ]

        first = runner.invoke(args=args)
        second = runner.invoke(args=args)

        self.assertEqual(first.exit_code, 0, first.output)
        self.assertEqual(second.exit_code, 0, second.output)
        self.assertIn('"approved": true', first.output)
        self.assertIn('"row_count": 1', second.output)
        self.assertNotIn(self.user.email, first.output)
        self.assertEqual(EmailOutbox.query.count(), 1)


if __name__ == "__main__":
    unittest.main()
