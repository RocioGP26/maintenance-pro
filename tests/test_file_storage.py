import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.file_storage import (
    delete,
    key_from_reference,
    read_bytes,
    reference,
    save_bytes,
    size_for_prefix,
    tenant_key,
)


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


if __name__ == "__main__":
    unittest.main()
