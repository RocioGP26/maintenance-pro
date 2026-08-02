import tempfile
import unittest
from datetime import date, datetime, timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from app import create_app, db
from app.file_storage import (
    delete,
    delete_best_effort,
    exists,
    key_from_reference,
    object_size,
    read_bytes,
    reference,
    save_bytes,
    size_for_prefix,
    tenant_key,
)
from app.models import Empresa, PlanSuscripcion, PlanTipo, User


class MissingObject(Exception):
    response = {"Error": {"Code": "404"}}


class FakePaginator:
    def __init__(self, client):
        self.client = client

    def paginate(self, *, Bucket, Prefix):
        return [
            {
                "Contents": [
                    {"Key": key, "Size": len(content)}
                    for (bucket, key), content in self.client.objects.items()
                    if bucket == Bucket and key.startswith(Prefix)
                ]
            }
        ]


class FakeS3:
    def __init__(self):
        self.objects = {}
        self.fail_put = None

    def head_object(self, *, Bucket, Key):
        try:
            content = self.objects[(Bucket, Key)]
        except KeyError as exc:
            raise MissingObject() from exc
        return {"ContentLength": len(content)}

    def put_object(self, *, Bucket, Key, Body, ContentType):
        if self.fail_put:
            raise self.fail_put
        self.objects[(Bucket, Key)] = bytes(Body)

    def get_object(self, *, Bucket, Key):
        try:
            content = self.objects[(Bucket, Key)]
        except KeyError as exc:
            raise MissingObject() from exc
        return {"Body": BytesIO(content)}

    def delete_object(self, *, Bucket, Key):
        self.objects.pop((Bucket, Key), None)

    def get_paginator(self, name):
        assert name == "list_objects_v2"
        return FakePaginator(self)


class TestFileStorage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(
            STORAGE_BACKEND="local",
            STORAGE_LOCAL_ROOT=self.temp.name,
        )
        self.context = self.app.app_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()
        self.temp.cleanup()

    def test_local_backend_roundtrip_and_usage(self):
        key = tenant_key(12, "activos", "7.png")
        self.assertEqual(key, "empresas/12/activos/7.png")
        save_bytes(key, b"imagen", content_type="image/png")
        self.assertEqual(read_bytes(key), b"imagen")
        self.assertEqual(size_for_prefix("empresas/12"), 6)
        self.assertEqual(key_from_reference(reference(key)), key)
        delete(key)
        self.assertFalse((Path(self.temp.name) / key).exists())

    def test_keys_cannot_escape_storage_root(self):
        with self.assertRaises(ValueError):
            save_bytes("empresas/12/../../secreto", b"x")

    def test_media_requires_authenticated_tenant(self):
        key = tenant_key(12, "activos", "7.png")
        save_bytes(key, b"imagen", content_type="image/png")
        response = self.app.test_client().get(f"/media/{key}")
        self.assertEqual(response.status_code, 403)

    def test_private_document_is_never_served_by_media_endpoint(self):
        key = tenant_key(12, "ordenes", "9", "informes", "secret.pdf")
        save_bytes(key, b"%PDF-private", content_type="application/pdf")
        client = self.app.test_client()
        with client.session_transaction() as session:
            session["platform_admin"] = True
        response = client.get(f"/media/{key}")
        self.assertEqual(response.status_code, 403)


class TestS3FileStorage(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app.config.update(STORAGE_BACKEND="s3", STORAGE_BUCKET="operativo")
        self.context = self.app.app_context()
        self.context.push()
        self.client = FakeS3()
        self.patcher = patch("app.file_storage._s3_client", return_value=self.client)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.context.pop()

    def test_s3_roundtrip_metering_and_delete(self):
        key = tenant_key(12, "activos", "7.png")
        save_bytes(key, b"imagen", content_type="image/png")
        self.assertTrue(exists(key))
        self.assertEqual(object_size(key), 6)
        self.assertEqual(read_bytes(key), b"imagen")
        self.assertEqual(size_for_prefix("empresas/12"), 6)
        delete(key)
        self.assertFalse(exists(key))

    def test_s3_write_failure_is_alerted_and_propagated(self):
        self.client.fail_put = RuntimeError("R2 no disponible")
        with patch("app.file_storage._alert_storage_failure") as alert:
            with self.assertRaisesRegex(RuntimeError, "R2 no disponible"):
                save_bytes(tenant_key(12, "activos", "7.png"), b"imagen")
        alert.assert_called_once()

    def test_cross_tenant_replacement_credit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "misma empresa"):
            save_bytes(
                tenant_key(12, "activos", "new.jpg"),
                b"imagen",
                replacing_key=tenant_key(13, "activos", "old.png"),
            )

    def test_cleanup_failure_does_not_raise_to_user(self):
        with patch("app.file_storage.delete", side_effect=RuntimeError("R2 caído")):
            with patch("app.file_storage._alert_storage_failure") as alert:
                self.assertFalse(delete_best_effort("empresas/12/activos/7.png"))
        alert.assert_called_once()


class TestMediaTenantIsolation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app("testing")
        self.app.config.update(
            STORAGE_BACKEND="local",
            STORAGE_LOCAL_ROOT=self.temp.name,
        )
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.one = Empresa(
            razon_social="Tenant Uno",
            slug="tenant-uno",
            email_verified_at=datetime.utcnow(),
        )
        self.two = Empresa(
            razon_social="Tenant Dos",
            slug="tenant-dos",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add_all((self.one, self.two))
        db.session.flush()
        self.user = User(
            empresa_id=self.one.id,
            username="tenant.uno",
            email="uno@example.com",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        self.user.set_password("Clave-Segura-123!")
        db.session.add(self.user)
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.one.id,
                plan=PlanTipo.BASICO.value,
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=30),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()
        save_bytes(tenant_key(self.one.id, "activos", "1.png"), b"propio")
        save_bytes(tenant_key(self.two.id, "activos", "2.png"), b"ajeno")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()
        self.temp.cleanup()

    def test_media_only_serves_objects_from_authenticated_tenant(self):
        client = self.app.test_client()
        login = client.post(
            "/login",
            data={
                "username": self.user.username,
                "empresa_slug": self.one.slug,
                "password": "Clave-Segura-123!",
            },
        )
        self.assertIn(login.status_code, (302, 303))

        own = client.get(f"/media/empresas/{self.one.id}/activos/1.png")
        other = client.get(f"/media/empresas/{self.two.id}/activos/2.png")

        self.assertEqual(own.status_code, 200)
        self.assertEqual(own.data, b"propio")
        self.assertEqual(own.headers["Cache-Control"], "private, no-store, max-age=0")
        self.assertEqual(other.status_code, 403)

if __name__ == "__main__":
    unittest.main()
