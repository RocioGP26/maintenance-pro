"""Punto de entrada para copias de seguridad (cron / GitHub Actions)."""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from app.backup_service import prune_old_backups, run_backup

if __name__ == "__main__":
    uri = os.environ.get("DATABASE_URL", "")
    path = run_backup(uri)
    prune_old_backups(int(os.environ.get("BACKUP_RETENTION_DAYS", "7")))
    print(path)
    sys.exit(0)
