"""Pruebas del monitor externo de disponibilidad."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from scripts.monitor_health import HealthResult, check_endpoint, check_with_retries, run


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self.status = status
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class TestMonitorHealth(unittest.TestCase):
    @patch("scripts.monitor_health.urlopen")
    def test_ok_requires_http_200_and_status_ok(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse({"status": "ok"})

        result = check_endpoint("https://roustix.example", "/health/ready")

        self.assertTrue(result.ok)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.status, "ok")

    @patch("scripts.monitor_health.urlopen")
    def test_degraded_readiness_fails_monitor(self, mocked_urlopen):
        mocked_urlopen.return_value = FakeResponse({"status": "degraded"})

        result = check_endpoint("https://roustix.example", "/health/ready")

        self.assertFalse(result.ok)
        self.assertEqual(result.status, "degraded")

    @patch("scripts.monitor_health.check_with_retries")
    def test_run_checks_live_and_ready(self, mocked_check):
        mocked_check.side_effect = lambda _base, endpoint: endpoint

        results = run("https://roustix.example")

        self.assertEqual(results, ["/health/live", "/health/ready"])

    @patch("scripts.monitor_health.time.sleep")
    @patch("scripts.monitor_health.check_endpoint")
    def test_retry_recovers_from_transient_failure(self, mocked_check, mocked_sleep):
        mocked_check.side_effect = [
            HealthResult("/health/ready", False, 503, "error", "HTTPError"),
            HealthResult("/health/ready", True, 200, "ok"),
        ]

        result = check_with_retries(
            "https://roustix.example",
            "/health/ready",
            attempts=3,
            delay_seconds=1,
        )

        self.assertTrue(result.ok)
        self.assertEqual(mocked_check.call_count, 2)
        mocked_sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
