import json
import tempfile
import unittest
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from app.storage_backup import StorageBackupConfig, backup_s3_storage


class MissingObject(Exception):
    response = {"Error": {"Code": "404"}}


class FakePaginator:
    def __init__(self, contents):
        self.contents = contents

    def paginate(self, **kwargs):
        return [{"Contents": self.contents}]


class FakeSource:
    def __init__(self):
        now = datetime(2026, 7, 28, tzinfo=timezone.utc)
        self.contents = [
            {"Key": "empresas/1/logo.svg", "Size": 3, "ETag": '"etag-a"', "LastModified": now},
            {"Key": "empresas/1/evidencias/foto.jpg", "Size": 4, "ETag": '"etag-b"', "LastModified": now},
        ]
        self.payloads = {
            "empresas/1/logo.svg": b"svg",
            "empresas/1/evidencias/foto.jpg": b"foto",
        }
        self.read = []

    def get_paginator(self, name):
        self.paginator_name = name
        return FakePaginator(self.contents)

    def get_object(self, *, Bucket, Key):
        self.read.append((Bucket, Key))
        etag = next(item["ETag"] for item in self.contents if item["Key"] == Key)
        return {
            "Body": BytesIO(self.payloads[Key]),
            "ContentType": "application/octet-stream",
            "ETag": etag,
        }


class FakeTarget:
    def __init__(self):
        self.uploads = {}
        self.manifests = {}

    def head_object(self, *, Bucket, Key):
        uploaded = self.uploads.get((Bucket, Key))
        if uploaded:
            return {"Metadata": uploaded["extra"]["Metadata"]}
        if Key.endswith("logo.svg"):
            return {
                "Metadata": {"source-etag": "etag-a", "source-size": "3"},
            }
        raise MissingObject()

    def upload_fileobj(self, body, bucket, key, ExtraArgs):
        self.uploads[(bucket, key)] = {
            "content": body.read(),
            "extra": ExtraArgs,
        }

    def upload_file(self, filename, bucket, key, ExtraArgs):
        self.uploads[(bucket, key)] = {
            "content": Path(filename).read_bytes(),
            "extra": ExtraArgs,
        }

    def put_object(self, *, Bucket, Key, Body, ContentType):
        self.manifests[(Bucket, Key)] = {
            "content": Body,
            "content_type": ContentType,
        }


def config(**overrides):
    values = {
        "source_bucket": "operativo",
        "target_bucket": "recuperacion",
        "prefix": "roustix",
        "source_access_key": "source-key",
        "source_secret_key": "source-secret",
        "target_access_key": "target-key",
        "target_secret_key": "target-secret",
    }
    values.update(overrides)
    return StorageBackupConfig(**values)


class TestStorageBackup(unittest.TestCase):
    def test_incremental_backup_skips_unchanged_and_copies_changed(self):
        source = FakeSource()
        target = FakeTarget()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "storage.manifest.json"
            dump = Path(folder) / "database.dump"
            dump.write_bytes(b"valid-dump")
            stats = backup_s3_storage(
                output,
                recovery_files=[dump],
                config=config(),
                source_client=source,
                target_client=target,
            )
            manifest = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(stats["object_count"], 2)
        self.assertEqual(stats["copied"], 1)
        self.assertEqual(stats["skipped"], 1)
        self.assertEqual(stats["total_bytes"], 7)
        self.assertEqual(source.read, [("operativo", "empresas/1/evidencias/foto.jpg")])
        copied = next(
            value
            for (bucket, key), value in target.uploads.items()
            if bucket == "recuperacion" and key.endswith("empresas/1/evidencias/foto.jpg")
        )
        self.assertEqual(copied["content"], b"foto")
        self.assertEqual(copied["extra"]["Metadata"]["source-etag"], "etag-b")
        self.assertEqual(manifest["format"], "roustix-storage-backup-v1")
        self.assertEqual(manifest["recovery_files"][0]["name"], "database.dump")
        self.assertEqual(len(manifest["recovery_files"][0]["sha256"]), 64)
        self.assertEqual(len(target.manifests), 1)

    def test_source_and_target_bucket_must_be_different(self):
        with self.assertRaisesRegex(ValueError, "diferente"):
            config(target_bucket="operativo").validate()

    def test_missing_credentials_fail_fast(self):
        with self.assertRaisesRegex(ValueError, "STORAGE_BACKUP_ACCESS_KEY_ID"):
            config(target_access_key="").validate()

    def test_unsafe_prefix_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PREFIX"):
            config(prefix="../escape").validate()


if __name__ == "__main__":
    unittest.main()
