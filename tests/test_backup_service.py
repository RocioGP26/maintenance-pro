import gzip
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.backup_service import (
    backup_postgresql,
    restore_sqlite_backup,
    verify_backup,
)


class TestBackupService(unittest.TestCase):
    def test_sqlite_restore_is_integrity_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.db"
            connection = sqlite3.connect(source)
            connection.execute("create table demo (id integer primary key, value text)")
            connection.execute("insert into demo(value) values ('ok')")
            connection.commit()
            connection.close()

            target = Path(folder) / "restored.db"
            restore_sqlite_backup(source, target)
            verify_backup(target)
            restored = sqlite3.connect(target)
            try:
                self.assertEqual(restored.execute("select value from demo").fetchone()[0], "ok")
            finally:
                restored.close()

    def test_postgresql_backup_uses_environment_ssl_and_real_gzip(self):
        captured = {}

        def fake_run(command, *, env, stdout, stderr, check):
            captured["command"] = command
            captured["sslmode"] = env.get("PGSSLMODE")
            stdout.write(b"-- PostgreSQL database dump\ncreate table demo(id integer);\n")

            class Result:
                returncode = 0
                stderr = b""

            return Result()

        with tempfile.TemporaryDirectory() as folder, patch.dict(
            "os.environ", {"BACKUP_DIR": folder}, clear=False
        ), patch("app.backup_service.subprocess.run", side_effect=fake_run):
            output = backup_postgresql(
                "postgresql+psycopg://user:secret@db.example/roustix?sslmode=require"
            )
            self.assertEqual(captured["sslmode"], "require")
            self.assertNotIn("--sslmode", captured["command"])
            with gzip.open(output, "rb") as source:
                self.assertIn(b"PostgreSQL database dump", source.read())


if __name__ == "__main__":
    unittest.main()
