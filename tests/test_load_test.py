"""Contrato del runner de carga sin tocar servicios externos."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.load_test import (
    Sample,
    load_env_file,
    main,
    percentile,
    summarize,
    traffic_light,
    web_session_cookie,
)


class TestLoadTest(unittest.TestCase):
    def test_percentile_uses_nearest_rank(self):
        self.assertEqual(percentile([10, 20, 30, 40], 50), 20)
        self.assertEqual(percentile([10, 20, 30, 40], 95), 40)

    def test_green_yellow_red_thresholds(self):
        self.assertEqual(traffic_light(p95_ms=2000, error_rate=0), "green")
        self.assertEqual(traffic_light(p95_ms=3000, error_rate=0), "yellow")
        self.assertEqual(traffic_light(p95_ms=1000, error_rate=2), "yellow")
        self.assertEqual(traffic_light(p95_ms=6000, error_rate=0), "red")
        self.assertEqual(traffic_light(p95_ms=1000, error_rate=4), "red")

    def test_summary_does_not_include_sensitive_payloads(self):
        report = summarize(
            [
                Sample("/dashboard", 200, 100, True),
                Sample("/dashboard", 503, 200, False, "HTTPError"),
            ]
        )
        self.assertEqual(report["requests"], 2)
        self.assertEqual(report["failures"], 1)
        self.assertEqual(report["error_rate_pct"], 50)
        self.assertEqual(report["verdict"], "red")

    def test_empty_endpoint_is_reported_as_no_data(self):
        report = summarize([])
        self.assertEqual(report["requests"], 0)
        self.assertEqual(report["error_rate_pct"], 0)
        self.assertEqual(report["verdict"], "no_data")

    def test_remote_target_requires_explicit_permission(self):
        with self.assertRaisesRegex(SystemExit, "Destino remoto bloqueado"):
            main(
                [
                    "--base-url",
                    "https://roustix.example",
                    "--public-only",
                    "--duration",
                    "5",
                ]
            )

    def test_local_credentials_file_only_loads_allowed_keys(self):
        names = (
            "LOAD_TEST_USERNAME",
            "LOAD_TEST_PASSWORD",
            "LOAD_TEST_EMPRESA_SLUG",
        )
        previous = {name: os.environ.pop(name, None) for name in names}
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "load.env"
                path.write_text(
                    "LOAD_TEST_USERNAME=carga\n"
                    "LOAD_TEST_PASSWORD='reservada'\n"
                    "LOAD_TEST_EMPRESA_SLUG=piloto\n"
                    "SECRET_KEY=no-debe-cargarse\n",
                    encoding="utf-8",
                )
                load_env_file(path)
            self.assertEqual(os.environ["LOAD_TEST_USERNAME"], "carga")
            self.assertEqual(os.environ["LOAD_TEST_PASSWORD"], "reservada")
            self.assertEqual(os.environ["LOAD_TEST_EMPRESA_SLUG"], "piloto")
            self.assertNotEqual(os.environ.get("SECRET_KEY"), "no-debe-cargarse")
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_auth_failure_is_controlled_and_skips_web_login(self):
        names = (
            "LOAD_TEST_USERNAME",
            "LOAD_TEST_PASSWORD",
            "LOAD_TEST_EMPRESA_SLUG",
        )
        previous = {name: os.environ.get(name) for name in names}
        os.environ.update(
            {
                "LOAD_TEST_USERNAME": "carga@example.com",
                "LOAD_TEST_PASSWORD": "reservada",
                "LOAD_TEST_EMPRESA_SLUG": "piloto",
            }
        )
        try:
            with patch("scripts.load_test.api_token", side_effect=RuntimeError("HTTP 429")):
                with patch("scripts.load_test.web_session_cookie") as web_login:
                    result = main(["--duration", "5"])
            self.assertEqual(result, 2)
            web_login.assert_not_called()
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

    def test_web_session_cookie_reports_rate_limit(self):
        page = b'<input name="csrf_token" value="csrf-value">'
        responses = [
            (200, page, "https://example.test/login"),
            (429, b"", "https://example.test/login"),
        ]
        with patch("scripts.load_test._request", side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, "HTTP 429"):
                web_session_cookie(
                    "https://example.test", "user", "secret", "tenant"
                )

    def test_web_session_cookie_sends_https_csrf_headers(self):
        page = b'<input name="csrf_token" value="csrf-value">'
        responses = [
            (200, page, "https://example.test/login"),
            (200, b"", "https://example.test/dashboard"),
        ]
        with patch("scripts.load_test._request", side_effect=responses) as request:
            web_session_cookie(
                "https://example.test", "user", "secret", "tenant"
            )
        post_headers = request.call_args_list[1].kwargs["headers"]
        self.assertEqual(post_headers["Origin"], "https://example.test")
        self.assertEqual(post_headers["Referer"], "https://example.test/login")


if __name__ == "__main__":
    unittest.main()
