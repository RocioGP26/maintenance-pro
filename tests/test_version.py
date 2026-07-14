"""Contrato de versionado de la aplicación Maintix."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from app import create_app
from app.version import __version__, get_build_commit, get_version_info, is_valid_semver


class TestApplicationVersion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = create_app("testing")

    def test_canonical_version_is_semver(self) -> None:
        self.assertTrue(is_valid_semver(__version__))
        self.assertEqual(self.app.config["APP_VERSION"], __version__)

    def test_public_version_endpoints_share_canonical_version(self) -> None:
        client = self.app.test_client()
        for path in ("/version", "/api/v1/version"):
            response = client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["application"], "Maintix")
            self.assertEqual(response.json["version"], __version__)
            self.assertEqual(response.json["release"], f"v{__version__}")
            self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_template_context_exposes_version(self) -> None:
        with self.app.test_request_context("/login"):
            context: dict[str, object] = {}
            self.app.update_template_context(context)
        self.assertEqual(context["app_version"], __version__)

    def test_flask_version_command(self) -> None:
        result = self.app.test_cli_runner().invoke(args=["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"Maintix v{__version__}", result.output)

    def test_build_commit_supports_render_and_github(self) -> None:
        with patch.dict("os.environ", {"RENDER_GIT_COMMIT": "abcdef1234567890"}, clear=True):
            self.assertEqual(get_build_commit(), "abcdef123456")
            self.assertEqual(get_version_info()["commit"], "abcdef123456")
        with patch.dict("os.environ", {"GITHUB_SHA": "1234567890abcdef"}, clear=True):
            self.assertEqual(get_build_commit(), "1234567890ab")


if __name__ == "__main__":
    unittest.main()
