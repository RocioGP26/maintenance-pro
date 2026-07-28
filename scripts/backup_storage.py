"""Replica el almacenamiento S3 operativo a un bucket de recuperación."""

from __future__ import annotations

import argparse
import json

from dotenv import load_dotenv

load_dotenv()

from app.storage_backup import backup_s3_storage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", default="storage.manifest.json", help="Manifiesto local de salida."
    )
    parser.add_argument(
        "--recovery-file",
        action="append",
        default=[],
        help="Artefacto adicional que se conserva en el bucket de recuperación.",
    )
    args = parser.parse_args()
    result = backup_s3_storage(args.manifest, recovery_files=args.recovery_file)
    print(
        json.dumps(
            {
                "object_count": result["object_count"],
                "copied": result["copied"],
                "skipped": result["skipped"],
                "total_bytes": result["total_bytes"],
                "manifest_key": result["manifest_key"],
                "recovery_files": len(result["recovery_files"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
