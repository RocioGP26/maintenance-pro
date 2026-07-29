"""Tests · panel de infraestructura SuperAdmin."""

from __future__ import annotations

import os
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app
from app.infra_status import backups_status, smtp_status, workers_status
from app.platform_service import infra_snapshot


class TestInfraStatus(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_smtp_missing_config(self):
        self.app.config.update(
            MAIL_SUPPRESS_SEND=False,
            MAIL_SERVER="",
            MAIL_USERNAME="",
            MAIL_PASSWORD="",
            MAIL_DEFAULT_SENDER="",
        )
        card = smtp_status(probe=False)
        self.assertEqual(card["status"], "error")
        self.assertIn("servidor", card["detail"])

    def test_smtp_suppress_is_warn(self):
        self.app.config["MAIL_SUPPRESS_SEND"] = True
        card = smtp_status(probe=True)
        self.assertEqual(card["status"], "warn")
        self.assertEqual(card["status_label"], "Suprimido")

    def test_smtp_configured_without_probe(self):
        self.app.config.update(
            MAIL_SUPPRESS_SEND=False,
            MAIL_SERVER="smtp.example.com",
            MAIL_USERNAME="ops@roustix.com",
            MAIL_PASSWORD="secret",
            MAIL_DEFAULT_SENDER="ops@roustix.com",
            MAIL_PORT=587,
        )
        card = smtp_status(probe=False)
        self.assertEqual(card["status"], "ok")
        self.assertIn("smtp.example.com", card["detail"])

    def test_workers_without_redis(self):
        self.app.config["REDIS_URL"] = ""
        self.app.config["WORKER_HEARTBEAT_REQUIRED"] = False
        card = workers_status()
        self.assertEqual(card["status"], "warn")
        self.assertEqual(card["status_label"], "Sin Redis")

    def test_workers_active_heartbeat(self):
        class FakeRedis:
            def ping(self):
                return True

            def get(self, _key):
                return str(time.time() - 5)

        self.app.config.update(
            REDIS_URL="redis://localhost:6379/0",
            WORKER_HEARTBEAT_REQUIRED=True,
            WORKER_HEARTBEAT_MAX_AGE_SECONDS=90,
        )
        self.app.extensions["roustix_redis"] = FakeRedis()
        card = workers_status()
        self.assertEqual(card["status"], "ok")
        self.assertEqual(card["status_label"], "Activo")

    def test_backups_storage_configured_without_local(self):
        env = {
            "STORAGE_BUCKET": "ops",
            "STORAGE_BACKUP_BUCKET": "ops-backup",
            "STORAGE_ACCESS_KEY_ID": "a",
            "STORAGE_SECRET_ACCESS_KEY": "b",
            "STORAGE_BACKUP_ACCESS_KEY_ID": "c",
            "STORAGE_BACKUP_SECRET_ACCESS_KEY": "d",
            "STORAGE_ENDPOINT_URL": "https://example.com",
            "BACKUP_DIR": str(Path(self.app.instance_path) / "empty-backups"),
        }
        Path(env["BACKUP_DIR"]).mkdir(parents=True, exist_ok=True)
        with patch.dict(os.environ, env, clear=False):
            card = backups_status()
        self.assertTrue(card["storage_configured"])
        self.assertEqual(card["status"], "warn")

    def test_infra_snapshot_includes_services(self):
        with (
            patch("app.platform_service.database_size_bytes", return_value=73 * 1024 * 1024),
            patch("app.platform_service.files_storage_total_bytes", return_value=int(3.1 * 1024**3)),
            patch("app.infra_status.service_statuses", return_value=[
                {"key": "smtp", "label": "Estado SMTP", "status": "ok", "status_label": "OK", "detail": "x"},
            ]),
        ):
            snap = infra_snapshot(probe_smtp=False)
        self.assertEqual(snap["database"]["label"], "PostgreSQL")
        self.assertEqual(snap["files"]["label"], "Cloudflare R2")
        self.assertEqual(snap["database"]["used_label"], "73 MB")
        self.assertTrue(snap["files"]["used_label"].startswith("3.1"))
        self.assertEqual(len(snap["services"]), 1)


if __name__ == "__main__":
    unittest.main()
