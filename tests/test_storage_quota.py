"""Tests · hard-limit de cuota de almacenamiento (S1)."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch
from werkzeug.datastructures import FileStorage

from app import create_app, db
from app.file_storage import save_bytes, tenant_key
from app.models import Empresa, Machine, MachineType, PlanSuscripcion, PlanTipo, User
from app.storage_quota import (
    StorageQuotaExceeded,
    assert_storage_capacity,
    empresa_id_from_storage_key,
    quota_mb_efectiva,
)


class TestStorageQuotaHelpers(unittest.TestCase):
    def test_empresa_id_from_key(self):
        self.assertEqual(empresa_id_from_storage_key("empresas/42/logo.png"), 42)
        self.assertIsNone(empresa_id_from_storage_key("otros/1/x"))

    def test_assert_allows_when_fits(self):
        empresa = SimpleNamespace(id=1, plan_activo=SimpleNamespace(plan="basico"), storage_addon_mb=0)
        with (
            patch("app.db.session.get", return_value=empresa),
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch("app.platform_service.storage_bytes_empresa", return_value=100),
        ):
            assert_storage_capacity(1, 1024)  # 1 KB extra — ok

    def test_assert_rejects_when_over_quota(self):
        empresa = SimpleNamespace(id=1, plan_activo=SimpleNamespace(plan="basico"), storage_addon_mb=0)
        used = 1024 * 1024 * 1024  # 1 GB used of 1 GB plan
        with (
            patch("app.db.session.get", return_value=empresa),
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch("app.platform_service.storage_bytes_empresa", return_value=used),
        ):
            with self.assertRaises(StorageQuotaExceeded) as ctx:
                assert_storage_capacity(1, 1)
            self.assertIn("límite de almacenamiento", str(ctx.exception))
            self.assertIn("contacto@roustix.com", str(ctx.exception))

    def test_replacing_bytes_credits_overwrite(self):
        empresa = SimpleNamespace(id=1, plan_activo=SimpleNamespace(plan="basico"), storage_addon_mb=0)
        used = 1024 * 1024 * 1024
        with (
            patch("app.db.session.get", return_value=empresa),
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch("app.platform_service.storage_bytes_empresa", return_value=used),
        ):
            # Reemplazo 10 bytes por 10 bytes → net 0
            assert_storage_capacity(1, 10, replacing_bytes=10)

    def test_quota_incluye_addon_atributo(self):
        empresa = SimpleNamespace(
            id=9,
            plan_activo=SimpleNamespace(plan="basico"),
            storage_addon_mb=2048,
        )
        with patch(
            "app.platform_service.plan_meta",
            return_value={"storage_mb": 1024},
        ):
            self.assertEqual(quota_mb_efectiva(empresa), 1024 + 2048)


class TestSaveBytesEnforcesQuota(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(STORAGE_BACKEND="local", STORAGE_LOCAL_ROOT=self.temp.name)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Cuota SA",
            slug="cuota-sa",
            nit="900",
            sector="industrial",
        )
        db.session.add(self.empresa)
        db.session.flush()
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.empresa.id,
                plan=PlanTipo.BASICO.value,
                fecha_inicio=date.today(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.temp.cleanup()

    def test_save_rejects_when_plan_full(self):
        key = tenant_key(self.empresa.id, "activos", "1.png")
        with (
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch(
                "app.platform_service.storage_bytes_empresa",
                return_value=1024 * 1024 * 1024,
            ),
        ):
            with self.assertRaises(StorageQuotaExceeded):
                save_bytes(key, b"x" * 100, content_type="image/png")

    def test_save_allows_without_empresa_row(self):
        # Tests legacy / ids huérfanos: sin fila Empresa no bloquea
        key = tenant_key(99999, "activos", "1.png")
        save_bytes(key, b"ok", content_type="image/png")

    def test_addon_raises_effective_quota(self):
        from app.storage_quota import ADDON_STG_2G_MB, set_addon_stg_2g

        key = tenant_key(self.empresa.id, "activos", "addon.png")
        set_addon_stg_2g(self.empresa, active=True)
        db.session.commit()
        # Uso = cupo del plan (1024 MB); con add-on debe caber
        with (
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024 + ADDON_STG_2G_MB),
            patch(
                "app.platform_service.storage_bytes_empresa",
                return_value=1024 * 1024 * 1024,
            ),
        ):
            save_bytes(key, b"cabe-con-addon", content_type="image/png")

    def test_removing_addon_preserves_files_and_blocks_new_uploads_over_base(self):
        from app.file_storage import exists
        from app.storage_quota import set_addon_stg_2g

        existing_key = tenant_key(self.empresa.id, "activos", "conservado.png")
        save_bytes(
            existing_key,
            b"archivo-existente",
            content_type="image/png",
            enforce_quota=False,
        )
        set_addon_stg_2g(self.empresa, active=True)
        set_addon_stg_2g(self.empresa, active=False)

        self.assertTrue(exists(existing_key))
        used_over_base = 2 * 1024 * 1024 * 1024
        with (
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch(
                "app.platform_service.storage_bytes_empresa",
                return_value=used_over_base,
            ),
        ):
            with self.assertRaises(StorageQuotaExceeded):
                assert_storage_capacity(self.empresa.id, 1)

    def test_migration_bypass(self):
        key = tenant_key(self.empresa.id, "activos", "mig.png")
        with patch(
            "app.platform_service.storage_bytes_empresa",
            return_value=1024 * 1024 * 1024,
        ):
            save_bytes(key, b"migrado", content_type="image/png", enforce_quota=False)

    def test_image_extension_change_credits_old_file_without_predelete(self):
        from app.file_storage import exists, reference
        from app.routes import _guardar_imagen_activo

        old_key = tenant_key(self.empresa.id, "activos", "77.png")
        save_bytes(old_key, b"old-image", content_type="image/png", enforce_quota=False)
        machine = SimpleNamespace(
            id=77,
            empresa_id=self.empresa.id,
            foto_url=reference(old_key),
        )
        upload = FileStorage(stream=BytesIO(b"new-image"), filename="foto.jpg")
        quota_bytes = 1024 * 1024 * 1024
        with (
            patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
            patch("app.platform_service.storage_bytes_empresa", return_value=quota_bytes),
        ):
            obsolete = _guardar_imagen_activo(machine, upload)

        new_key = tenant_key(self.empresa.id, "activos", "77.jpg")
        self.assertTrue(exists(old_key), "el objeto anterior debe vivir hasta el commit")
        self.assertTrue(exists(new_key))
        self.assertIn(old_key, obsolete)
        self.assertEqual(machine.foto_url, reference(new_key))


class TestAssetFileDeletion(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        from app.file_storage import reference

        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(
            STORAGE_BACKEND="local",
            STORAGE_LOCAL_ROOT=self.temp.name,
        )
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Archivos SA",
            slug="archivos-sa",
            email_verified_at=datetime.utcnow(),
        )
        self.otra_empresa = Empresa(
            razon_social="Otro Tenant SA",
            slug="otro-tenant-archivos",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add_all([self.empresa, self.otra_empresa])
        db.session.flush()
        for empresa in (self.empresa, self.otra_empresa):
            db.session.add(
                PlanSuscripcion(
                    empresa_id=empresa.id,
                    plan=PlanTipo.BASICO.value,
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                )
            )
        self.usuario = self._crear_usuario(self.empresa, "admin_archivos")
        self.otro_usuario = self._crear_usuario(self.otra_empresa, "admin_otro")
        tipo = MachineType(
            empresa_id=self.empresa.id,
            clave="general",
            nombre="General",
            prefijo="AF",
        )
        db.session.add(tipo)
        db.session.flush()
        self.machine = Machine(
            empresa_id=self.empresa.id,
            codigo="AF-001",
            machine_type_id=tipo.id,
            nombre="Activo con archivos",
        )
        db.session.add(self.machine)
        db.session.flush()
        self.keys = {
            "foto": tenant_key(self.empresa.id, "activos", f"{self.machine.id}.png"),
            "manual": tenant_key(
                self.empresa.id, "activos", f"{self.machine.id}-manual.pdf"
            ),
            "ficha": tenant_key(
                self.empresa.id, "activos", f"{self.machine.id}-ficha.pdf"
            ),
        }
        for key in self.keys.values():
            save_bytes(key, b"contenido", enforce_quota=False)
        self.machine.foto_url = reference(self.keys["foto"])
        self.machine.manual_url = reference(self.keys["manual"])
        self.machine.ficha_tecnica_url = reference(self.keys["ficha"])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
        self.temp.cleanup()

    def _crear_usuario(self, empresa, username):
        usuario = User(
            empresa_id=empresa.id,
            username=username,
            nombre_visible=username,
            rol="admin",
            area="Mantenimiento",
            cargo="Administrador",
            activo=True,
            onboarding_completado=True,
        )
        usuario.set_password(self.PASSWORD)
        db.session.add(usuario)
        return usuario

    def _login(self, username, slug):
        client = self.app.test_client()
        response = client.post(
            "/login",
            data={"username": username, "empresa_slug": slug, "password": self.PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        return client

    def test_delete_each_asset_file_clears_reference_and_storage(self):
        from app.file_storage import exists

        client = self._login("admin_archivos", "archivos-sa")
        attrs = {"foto": "foto_url", "manual": "manual_url", "ficha": "ficha_tecnica_url"}
        for tipo, attr in attrs.items():
            with self.subTest(tipo=tipo):
                response = client.post(
                    f"/activos/{self.machine.id}/archivo/{tipo}/eliminar"
                )
                self.assertEqual(response.status_code, 302)
                db.session.refresh(self.machine)
                self.assertEqual(getattr(self.machine, attr), "")
                self.assertFalse(exists(self.keys[tipo]))

    def test_other_tenant_cannot_delete_asset_file(self):
        from app.file_storage import exists

        client = self._login("admin_otro", "otro-tenant-archivos")
        response = client.post(
            f"/activos/{self.machine.id}/archivo/foto/eliminar"
        )
        self.assertEqual(response.status_code, 404)
        db.session.refresh(self.machine)
        self.assertTrue(self.machine.foto_url)
        self.assertTrue(exists(self.keys["foto"]))


if __name__ == "__main__":
    unittest.main()
