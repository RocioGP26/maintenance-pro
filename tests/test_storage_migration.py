"""Tests · migración legacy static/uploads → object storage (S0)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import create_app, db
from app.file_storage import reference, tenant_key
from app.models import Empresa, Machine, MachineType, WorkOrder, WorkOrderInforme
from app.storage_migration import inventory_legacy_refs, migrate_legacy_storage


class TestStorageMigration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.static = self.root / "static"
        self.object_root = self.root / "object"
        self.static.mkdir()
        self.object_root.mkdir()
        self.app = create_app("testing")
        self.app.config.update(
            STORAGE_BACKEND="local",
            STORAGE_LOCAL_ROOT=str(self.object_root),
            STORAGE_INCLUDE_LEGACY_UPLOADS=True,
        )
        # Apunta static_folder al temp para la migración.
        self.app.static_folder = str(self.static)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(razon_social="Migra SA", slug="migra-sa")
        db.session.add(self.empresa)
        db.session.flush()
        tipo = MachineType(
            empresa_id=self.empresa.id,
            clave="gen",
            nombre="General",
            prefijo="MG",
        )
        db.session.add(tipo)
        db.session.flush()
        self.machine = Machine(
            empresa_id=self.empresa.id,
            codigo="MG-001",
            machine_type_id=tipo.id,
            nombre="Bomba",
            foto_url=f"uploads/empresas/{self.empresa.id}/activos/{999}.png",
        )
        # Usaremos machine.id tras flush
        db.session.add(self.machine)
        db.session.flush()
        rel = f"uploads/empresas/{self.empresa.id}/activos/{self.machine.id}.png"
        self.machine.foto_url = rel
        logo_rel = f"uploads/empresas/{self.empresa.id}/logo.png"
        self.empresa.logo = logo_rel
        # Archivos en disco
        logo_path = self.static / logo_rel
        foto_path = self.static / rel
        logo_path.parent.mkdir(parents=True, exist_ok=True)
        foto_path.parent.mkdir(parents=True, exist_ok=True)
        logo_path.write_bytes(b"logo-bytes")
        foto_path.write_bytes(b"foto-bytes")
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.temp.cleanup()

    def test_inventory_counts_legacy(self):
        inv = inventory_legacy_refs()
        self.assertGreaterEqual(inv["public_media_legacy"], 2)
        self.assertGreaterEqual(inv["legacy_total"], 2)

    def test_dry_run_does_not_change_refs(self):
        stats = migrate_legacy_storage(apply=False)
        self.assertEqual(stats["missing"], 0)
        self.assertEqual(stats["public_media"], 2)
        db.session.refresh(self.empresa)
        self.assertTrue(self.empresa.logo.startswith("uploads/"))

    def test_apply_migrates_and_rewrites_refs(self):
        stats = migrate_legacy_storage(apply=True)
        self.assertEqual(stats["missing"], 0)
        self.assertEqual(stats["public_media"], 2)
        db.session.refresh(self.empresa)
        db.session.refresh(self.machine)
        self.assertTrue(self.empresa.logo.startswith("storage://"))
        self.assertTrue(self.machine.foto_url.startswith("storage://"))
        key = tenant_key(self.empresa.id, "logo.png")
        self.assertEqual(self.empresa.logo, reference(key))
        self.assertTrue((self.object_root / key).is_file())
        inv = inventory_legacy_refs()
        self.assertEqual(inv["legacy_total"], 0)

    def test_apply_rewrites_when_remote_exists_without_local(self):
        from app.file_storage import save_bytes

        # Simula cutover: objeto ya en R2/local backend, disco static vacío, BD legacy.
        key_logo = f"empresas/{self.empresa.id}/logo.png"
        save_bytes(key_logo, b"ya-en-r2", content_type="image/png", enforce_quota=False)
        (self.static / self.empresa.logo.lstrip("/")).unlink(missing_ok=True)
        stats = migrate_legacy_storage(apply=True)
        self.assertGreaterEqual(stats["from_remote"], 1)
        db.session.refresh(self.empresa)
        self.assertTrue(self.empresa.logo.startswith("storage://"))

    def test_cli_list_is_ascii_safe(self):
        result = self.app.test_cli_runner().invoke(args=["migrate-storage", "--list"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("->", result.output)


class TestLegacyMeteringFlag(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(
            STORAGE_BACKEND="local",
            STORAGE_LOCAL_ROOT=self.temp.name,
        )
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
        self.temp.cleanup()

    def test_s3_backend_skips_legacy_walk_by_default(self):
        from app.platform_service import _include_legacy_uploads

        self.app.config["STORAGE_BACKEND"] = "s3"
        self.app.config["STORAGE_INCLUDE_LEGACY_UPLOADS"] = None
        self.assertFalse(_include_legacy_uploads())

    def test_local_backend_includes_legacy_by_default(self):
        from app.platform_service import _include_legacy_uploads

        self.app.config["STORAGE_BACKEND"] = "local"
        self.app.config["STORAGE_INCLUDE_LEGACY_UPLOADS"] = None
        self.assertTrue(_include_legacy_uploads())


if __name__ == "__main__":
    unittest.main()
