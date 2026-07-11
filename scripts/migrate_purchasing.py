#!/usr/bin/env python3
"""Migra compras legacy a Purchasing sin alterar stock ni CxP."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.purchasing.migration import migrate_legacy_purchases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Aplica la migración; sin esta opción solo simula.")
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        stats = migrate_legacy_purchases(dry_run=not args.apply)
    mode = "APLICADA" if args.apply else "DRY-RUN"
    print(f"Purchasing migration {mode}: {stats}")


if __name__ == "__main__":
    main()
