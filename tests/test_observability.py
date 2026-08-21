"""Sprint 23.4 · correlación, métricas y salud operativa."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app import create_app


class FakeRedis:
    def __init__(self, *, heartbeat=None, failure=None):
        self.heartbeat = heartbeat
        self.failure = failure

    def ping(self):
        if self.failure:
            raise self.failure
        return True

    def get(self, _key):
        return self.heartbeat


class TestObservability(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app.config.update(
            METRICS_TOKEN="metrics-test-token",
            PROPAGATE_EXCEPTIONS=False,
            DB_HEALTH_DEGRADED_MS=100,
        )

        @self.app.get("/_test/unhandled")
        def _unhandled():
            raise RuntimeError("controlled test failure")

        self.client = self.app.test_client()

    def test_request_id_is_generated_and_returned(self):
        response = self.client.get("/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.headers["X-Request-Id"], r"^req_[0-9a-f]{24}$")

    @patch("app.health_routes._migration_revision")
    @patch("app.health_routes._check_database")
    def test_health_is_lightweight(self, db_check, migration_check):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")
        self.assertIn("version", response.json)
        self.assertIn("timestamp", response.json)
        self.assertNotIn("checks", response.json)
        db_check.assert_not_called()
        migration_check.assert_not_called()

    @patch("app.health_routes._migration_revision", return_value=("revision-ok", None))
    @patch("app.health_routes._check_database", return_value=(True, None, 2.0))
    def test_health_ready_has_dependency_checks(self, db_check, migration_check):
        response = self.client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json["checks"]),
            {"database", "migrations", "redis", "worker"},
        )
        db_check.assert_called_once_with()
        migration_check.assert_called_once_with()

    def test_valid_request_id_is_preserved_and_invalid_one_is_replaced(self):
        valid = self.client.get("/health/live", headers={"X-Request-Id": "client-request-123"})
        self.assertEqual(valid.headers["X-Request-Id"], "client-request-123")

        invalid = self.client.get("/health/live", headers={"X-Request-Id": "bad value"})
        self.assertNotEqual(invalid.headers["X-Request-Id"], "bad value")
        self.assertRegex(invalid.headers["X-Request-Id"], r"^req_[0-9a-f]{24}$")

    def test_metrics_endpoint_is_protected_and_exports_http_metrics(self):
        self.client.get("/health/live")
        self.assertEqual(self.client.get("/internal/metrics").status_code, 403)
        self.assertEqual(
            self.client.get(
                "/internal/metrics", headers={"X-Metrics-Token": "wrong"}
            ).status_code,
            403,
        )

        response = self.client.get(
            "/internal/metrics",
            headers={"X-Metrics-Token": "metrics-test-token"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"roustix_http_requests_total", response.data)
        self.assertIn(b"roustix_http_request_duration_seconds", response.data)
        self.assertIn(b"roustix_build_info", response.data)

    def test_unhandled_error_is_correlated_and_counted(self):
        response = self.client.get("/_test/unhandled")
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.headers.get("X-Request-Id"))

        metrics = self.client.get(
            "/internal/metrics", headers={"X-Metrics-Token": "metrics-test-token"}
        )
        self.assertIn(b"roustix_unhandled_exceptions_total", metrics.data)
        self.assertIn(b'exception="RuntimeError"', metrics.data)

    @patch("app.health_routes._migration_revision", return_value=("revision-ok", None))
    @patch("app.health_routes._check_database", return_value=(True, None, 250.0))
    def test_slow_database_is_degraded_but_still_ready(self, _db_check, _migration):
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "degraded")
        self.assertTrue(response.json["checks"]["database"]["degraded"])
        self.assertEqual(response.json["checks"]["database"]["latency_ms"], 250.0)

    def test_metrics_endpoint_is_hidden_when_not_configured(self):
        self.app.config["METRICS_TOKEN"] = ""
        self.assertEqual(self.client.get("/internal/metrics").status_code, 404)

    @patch("app.health_routes._migration_revision", return_value=("revision-ok", None))
    @patch("app.health_routes._check_database", return_value=(True, None, 2.0))
    def test_required_redis_failure_blocks_readiness(self, _db_check, _migration):
        self.app.config.update(
            REDIS_URL="redis://keyvalue:6379/0",
            DISTRIBUTED_RATE_LIMITS_REQUIRED=True,
        )
        self.app.extensions["roustix_redis"] = FakeRedis(failure=ConnectionError("down"))
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json["checks"]["redis"]["ok"])

    @patch("app.health_routes._migration_revision", return_value=("revision-ok", None))
    @patch("app.health_routes._check_database", return_value=(True, None, 2.0))
    def test_stale_worker_heartbeat_degrades_without_dropping_web(self, _db_check, _migration):
        import time

        self.app.config.update(
            REDIS_URL="redis://keyvalue:6379/0",
            DISTRIBUTED_RATE_LIMITS_REQUIRED=True,
            WORKER_HEARTBEAT_REQUIRED=True,
            WORKER_HEARTBEAT_MAX_AGE_SECONDS=30,
        )
        self.app.extensions["roustix_redis"] = FakeRedis(heartbeat=str(time.time() - 120))
        response = self.client.get("/health/ready")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "degraded")
        self.assertFalse(response.json["checks"]["worker"]["ok"])


if __name__ == "__main__":
    unittest.main()
