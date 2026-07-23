"""Acceso híbrido a Roustix Docs (público / privado)."""

from __future__ import annotations

import unittest

from app import create_app
from app.docs_access import is_docs_hub_path_public, is_mkt_path_public, is_msd_path_public


class TestDocsAccessPolicy(unittest.TestCase):
    def test_hub_path_matrix(self) -> None:
        self.assertTrue(is_docs_hub_path_public(""))
        self.assertTrue(is_docs_hub_path_public("css/docs-hub.css"))
        self.assertTrue(is_docs_hub_path_public("release-notes/README.md"))
        self.assertTrue(is_docs_hub_path_public("api/collections/README.md"))
        self.assertTrue(is_docs_hub_path_public("api/openapi.v1.yaml"))
        self.assertTrue(is_docs_hub_path_public("mkt/assets/brochure-corporativo.html"))
        self.assertTrue(is_docs_hub_path_public("mkt/mtx-case/README.md"))
        self.assertFalse(is_docs_hub_path_public("ACCESS.md"))
        self.assertFalse(is_docs_hub_path_public("mkt/chapters/01-identidad-mensajes-marca.md"))
        self.assertFalse(is_docs_hub_path_public("developer/README.md"))
        self.assertFalse(is_docs_hub_path_public("publishing/README.md"))
        self.assertFalse(is_docs_hub_path_public("mcm/README.md"))
        self.assertFalse(is_docs_hub_path_public("mpa/README.md"))
        self.assertFalse(is_docs_hub_path_public("api/SPRINT22.5-REPORT.md"))
        self.assertFalse(is_docs_hub_path_public("api/architecture.md"))

    def test_mkt_path_matrix(self) -> None:
        self.assertTrue(is_mkt_path_public(endpoint="mkt.assets"))
        self.assertTrue(is_mkt_path_public(endpoint="mkt.mtx_case"))
        self.assertFalse(is_mkt_path_public(endpoint="mkt.index"))
        self.assertFalse(is_mkt_path_public(endpoint="mkt.chapters"))
        self.assertFalse(
            is_mkt_path_public("01-identidad-mensajes-marca.md", endpoint="mkt.chapters")
        )
        self.assertFalse(is_mkt_path_public("README.md", endpoint="mkt.docs_file"))

    def test_msd_path_matrix(self) -> None:
        self.assertTrue(is_msd_path_public(endpoint="msd.index"))
        self.assertTrue(is_msd_path_public(endpoint="msd.guide"))
        self.assertTrue(is_msd_path_public(endpoint="msd.chapters"))
        self.assertFalse(is_msd_path_public(endpoint="msd.docs_file"))
        self.assertFalse(is_docs_hub_path_public("msd/strategy.md"))
        self.assertFalse(is_docs_hub_path_public("msd/NOMENCLATURE.md"))
        self.assertFalse(is_docs_hub_path_public("msd/chapters/07-quick-start.md"))
        self.assertTrue(is_docs_hub_path_public("msd/index.html"))


class TestDocsAccessHybridHttp(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from app import db

        cls.app = create_app("testing")
        cls.app.config["DOCS_ACCESS_POLICY"] = "hybrid"
        cls._ctx = cls.app.app_context()
        cls._ctx.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls) -> None:
        from app import db

        db.session.remove()
        db.drop_all()
        cls._ctx.pop()

    def test_public_manuals_open(self) -> None:
        client = self.app.test_client()
        for path in (
            "/docs/",
            "/brandbook/",
            "/mag/",
            "/msd/",
            "/guia",
            "/api/v1/openapi.yaml",
            "/mkt/assets/brochure-corporativo.html",
            "/mkt/mtx-case/README.md",
        ):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, msg=path)
            response.close()

    def test_mrg_portal_private_guia_public(self) -> None:
        client = self.app.test_client()
        private = client.get("/mrg/")
        self.assertIn(private.status_code, (302, 303))
        self.assertIn("/login", private.headers.get("Location", ""))
        public = client.get("/guia")
        self.assertEqual(public.status_code, 200)
        body = public.get_data(as_text=True)
        self.assertIn("Cómo funciona Roustix", body)
        self.assertNotIn("Sprint 10", body)
        self.assertNotIn("ALIGN", body)
        public.close()

    def test_mag_portal_public_and_clean(self) -> None:
        client = self.app.test_client()
        response = client.get("/mag/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Integra Roustix con confianza", body)
        self.assertIn("Documentación pública", body)
        self.assertNotIn("Sprint 8", body)
        self.assertNotIn("Entregado", body)
        self.assertIn("/mag/guide/autenticacion-jwt", body)
        response.close()

    def test_msd_portal_public_and_clean(self) -> None:
        client = self.app.test_client()
        response = client.get("/msd/")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("MSD v1.0.0", body)
        self.assertIn("/msd/guide/quick-start", body)
        self.assertNotIn("Sprint 9", body)
        self.assertNotIn("NOMENCLATURE", body)
        self.assertNotIn("strategy.md", body)
        self.assertNotIn("/mpa/", body)
        response.close()

        guide = client.get("/msd/guide/quick-start")
        self.assertEqual(guide.status_code, 200)
        gbody = guide.get_data(as_text=True)
        self.assertIn("Quick Start", gbody)
        self.assertIn("JWT", gbody)
        self.assertNotIn("Sprint 9", gbody)
        self.assertNotIn("Exit Criteria", gbody)
        guide.close()

        raw = client.get("/msd/chapters/07-quick-start.md")
        self.assertIn(raw.status_code, (302, 303))
        self.assertIn("/msd/guide/quick-start", raw.headers.get("Location", ""))

        meta = client.get("/msd/strategy.md")
        self.assertIn(meta.status_code, (302, 303))
        self.assertIn("/msd/", meta.headers.get("Location", ""))

    def test_mag_guide_public_md_private(self) -> None:
        client = self.app.test_client()
        guide = client.get("/mag/guide/autenticacion-jwt")
        self.assertEqual(guide.status_code, 200)
        body = guide.get_data(as_text=True)
        self.assertIn("JWT", body)
        self.assertIn("/api/v1/auth/login", body)
        self.assertNotIn("app/tenancy", body)
        self.assertNotIn("/mpa/", body)
        self.assertNotIn("Sprint 22", body)
        guide.close()

        # URL antigua a .md → redirige a la guía HTML (no expone el fuente)
        raw = client.get("/mag/chapters/02-autenticacion-jwt.md")
        self.assertIn(raw.status_code, (302, 303))
        location = raw.headers.get("Location", "")
        self.assertIn("/mag/guide/autenticacion-jwt", location)
        self.assertNotIn("/login", location)

    def test_mkt_chapters_and_portal_private(self) -> None:
        client = self.app.test_client()
        for path in (
            "/mkt/",
            "/mkt/chapters/01-identidad-mensajes-marca.md",
            "/mkt/chapters/02-elevator-pitch-guiones.md",
            "/mkt/README.md",
        ):
            response = client.get(path)
            self.assertIn(response.status_code, (302, 303), msg=path)
            self.assertIn("/login", response.headers.get("Location", ""), msg=path)

    def test_private_manuals_redirect_to_login(self) -> None:
        client = self.app.test_client()
        for path in ("/mcm/", "/mpa/", "/mdl/", "/mux/", "/mrl/", "/mdo/", "/mrg/"):
            response = client.get(path)
            self.assertIn(response.status_code, (302, 303), msg=path)
            location = response.headers.get("Location", "")
            self.assertIn("/login", location, msg=path)

    def test_private_hub_paths_redirect(self) -> None:
        client = self.app.test_client()
        for path in (
            "/docs/developer/README.md",
            "/docs/publishing/README.md",
            "/docs/ACCESS.md",
        ):
            response = client.get(path)
            self.assertIn(response.status_code, (302, 303), msg=path)
            self.assertIn("/login", response.headers.get("Location", ""), msg=path)

    def test_public_hub_meta_open(self) -> None:
        client = self.app.test_client()
        response = client.get("/docs/release-notes/README.md")
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_platform_documentacion_requires_superadmin(self) -> None:
        client = self.app.test_client()
        anon = client.get("/platform/documentacion")
        self.assertIn(anon.status_code, (302, 303))
        self.assertIn("/platform/login", anon.headers.get("Location", ""))

        with client.session_transaction() as sess:
            sess["platform_admin"] = True
            sess["platform_actor"] = "test-platform"
        ok = client.get("/platform/documentacion")
        self.assertEqual(ok.status_code, 200)
        body = ok.get_data(as_text=True)
        self.assertIn("Documentación interna", body)
        self.assertIn("/mcm/", body)
        self.assertIn("/mpa/", body)
        self.assertIn("/docs/ACCESS.md", body)
        ok.close()

        # Con sesión SuperAdmin, docs privadas abren
        access = client.get("/docs/ACCESS.md")
        self.assertEqual(access.status_code, 200)
        access.close()


if __name__ == "__main__":
    unittest.main()
