from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from flask import Flask

from app import create_app
from config import TestingConfig, normalize_database_url
from scripts.ci_seed_e2e import seed
from scripts.e2e_smoke import run as run_e2e_smoke


class TestCiDatabaseConfiguration(unittest.TestCase):
    def test_testing_defaults_to_in_memory_sqlite(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_DATABASE_URL", None)
            app = create_app("testing")
        self.assertEqual(app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///:memory:")
        self.assertEqual(app.config["SQLALCHEMY_ENGINE_OPTIONS"], {})

    def test_testing_accepts_dedicated_postgresql_url(self):
        url = "postgres://ci:secret@127.0.0.1:5432/roustix_ci"
        with patch.dict(os.environ, {"TEST_DATABASE_URL": url}):
            app = Flask(__name__)
            app.config.from_object(TestingConfig)
            TestingConfig.init_app(app)
        self.assertEqual(
            app.config["SQLALCHEMY_DATABASE_URI"],
            normalize_database_url(url),
        )
        self.assertTrue(app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://"))
        self.assertTrue(app.config["SQLALCHEMY_ENGINE_OPTIONS"]["pool_pre_ping"])

    def test_e2e_seed_refuses_non_postgresql_database(self):
        with patch.dict(
            os.environ,
            {"TEST_DATABASE_URL": "", "E2E_USER_PASSWORD": "valid-password-123"},
        ):
            with self.assertRaisesRegex(RuntimeError, "PostgreSQL"):
                seed()

    def test_e2e_smoke_requires_ephemeral_credentials(self):
        with patch.dict(
            os.environ,
            {
                "E2E_USER_PASSWORD": "",
                "PLATFORM_ADMIN_KEY": "",
                "PLATFORM_ADMIN_TOTP_SECRET": "",
            },
        ):
            with self.assertRaisesRegex(RuntimeError, "credenciales efímeras"):

                run_e2e_smoke()

if __name__ == "__main__":
    unittest.main()
