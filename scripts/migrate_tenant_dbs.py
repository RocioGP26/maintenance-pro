#!/usr/bin/env python3
"""
Fusiona archivos SQLite por tenant (data/tenants/mantis_*.db) en mantenimiento.db.

Uso:
  python scripts/migrate_tenant_dbs.py --dry-run
  python scripts/migrate_tenant_dbs.py
  python scripts/migrate_tenant_dbs.py --delete-empty

Requisitos:
  - Cada archivo debe llamarse mantis_{slug}.db
  - Debe existir Empresa.slug == slug en mantenimiento.db
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TENANT_FILE_RE = re.compile(r"^mantis_(?P<slug>.+)\.db$", re.IGNORECASE)
TRACKED_TABLES = (
    "machine_types",
    "technicians",
    "machines",
    "spare_parts",
    "preventive_maintenance_plans",
    "work_orders",
    "work_order_jornadas",
    "work_order_repuestos",
    "machine_monthly_plans",
    "incidents",
)


def _tenant_counts(db_path: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        for table in TRACKED_TABLES:
            try:
                (n,) = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                counts[table] = int(n)
            except sqlite3.OperationalError:
                counts[table] = 0
    finally:
        conn.close()
    return counts


def _total_rows(counts: dict[str, int]) -> int:
    return sum(counts.values())


def _unique_codigo(slug: str, codigo: str) -> str:
    from app.models import Machine

    base = (codigo or "EQ-001").strip()[:64]
    cand = base
    n = 2
    while Machine.query.filter_by(codigo=cand).first() is not None:
        suffix = f"-{slug}" if n == 2 else f"-{slug}-{n}"
        cand = (base[: max(1, 64 - len(suffix))] + suffix)[:64]
        n += 1
    return cand


def _unique_prefijo(slug: str, prefijo: str) -> str:
    from app.models import MachineType

    base = (prefijo or "EQ").strip().upper()[:8]
    cand = base
    n = 2
    while MachineType.query.filter_by(prefijo=cand).first() is not None:
        suffix = slug[: max(1, 8 - len(str(n)))].upper()
        cand = (base[: max(1, 8 - len(suffix))] + suffix)[:8]
        n += 1
    return cand


def _row_dict(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    try:
        return list(conn.execute(f"SELECT * FROM {table}"))
    except sqlite3.OperationalError:
        return []


def migrate_tenant_db(db_path: Path, empresa_id: int, slug: str, dry_run: bool) -> dict[str, int]:
    from app import db
    from app.models import (
        Incident,
        Machine,
        MachineMonthlyPlan,
        MachineType,
        PreventiveMaintenancePlan,
        SparePart,
        Technician,
        WorkOrder,
        WorkOrderJornada,
        WorkOrderRepuesto,
    )

    imported: dict[str, int] = {t: 0 for t in TRACKED_TABLES}
    if dry_run:
        return imported

    conn = sqlite3.connect(db_path)
    try:
        type_map: dict[int, int] = {}
        tech_map: dict[int, int] = {}
        machine_map: dict[int, int] = {}
        spare_map: dict[int, int] = {}
        plan_map: dict[int, int] = {}
        wo_map: dict[int, int] = {}

        for row in _row_dict(conn, "machine_types"):
            mt = MachineType(
                empresa_id=empresa_id,
                clave=row["clave"],
                nombre=row["nombre"],
                prefijo=_unique_prefijo(slug, row["prefijo"]),
                activo=bool(row["activo"]),
                orden=row["orden"] or 0,
                sector_industrial=row["sector_industrial"],
            )
            db.session.add(mt)
            db.session.flush()
            type_map[int(row["id"])] = mt.id
            imported["machine_types"] += 1

        for row in _row_dict(conn, "technicians"):
            tech = Technician(
                empresa_id=empresa_id,
                nombre=row["nombre"],
                especialidad=row["especialidad"] or "",
                telefono=row["telefono"] or "",
                email=row["email"] or "",
                activo=bool(row["activo"]),
            )
            db.session.add(tech)
            db.session.flush()
            tech_map[int(row["id"])] = tech.id
            imported["technicians"] += 1

        for row in _row_dict(conn, "machines"):
            old_type_id = row["machine_type_id"]
            new_type_id = type_map.get(old_type_id)
            if new_type_id is None:
                continue
            old_parent = row["parent_machine_id"]
            m = Machine(
                empresa_id=empresa_id,
                codigo=_unique_codigo(slug, row["codigo"]),
                machine_type_id=new_type_id,
                nombre=row["nombre"],
                descripcion=row["descripcion"] or "",
                ubicacion=row["ubicacion"] or "",
                area=row["area"] or "",
                status=row["status"],
                es_critico=bool(row["es_critico"]) if "es_critico" in row.keys() else False,
            )
            db.session.add(m)
            db.session.flush()
            machine_map[int(row["id"])] = m.id
            if old_parent:
                m.parent_machine_id = machine_map.get(int(old_parent))
            old_resp = row["responsable_technician_id"] if "responsable_technician_id" in row.keys() else None
            if old_resp:
                m.responsable_technician_id = tech_map.get(int(old_resp))
            imported["machines"] += 1
        db.session.flush()

        for row in _row_dict(conn, "spare_parts"):
            sp = SparePart(
                empresa_id=empresa_id,
                sku=row["sku"],
                nombre=row["nombre"],
                categoria=row["categoria"] or "",
                unidad=row["unidad"] or "pza",
                cantidad=row["cantidad"] or 0,
                stock_minimo=row["stock_minimo"] or 0,
                ubicacion_almacen=row["ubicacion_almacen"] or "",
                costo_unitario=row["costo_unitario"] or 0,
            )
            db.session.add(sp)
            db.session.flush()
            spare_map[int(row["id"])] = sp.id
            imported["spare_parts"] += 1

        for row in _row_dict(conn, "preventive_maintenance_plans"):
            mid = machine_map.get(int(row["machine_id"]))
            if mid is None:
                continue
            plan = PreventiveMaintenancePlan(
                empresa_id=empresa_id,
                machine_id=mid,
                actividad=row["actividad"],
                actividad_key=row["actividad_key"],
                frecuencia_valor=row["frecuencia_valor"] or 1,
                frecuencia_unidad=row["frecuencia_unidad"] or "meses",
                activo=bool(row["activo"]),
            )
            db.session.add(plan)
            db.session.flush()
            plan_map[int(row["id"])] = plan.id
            imported["preventive_maintenance_plans"] += 1

        for row in _row_dict(conn, "work_orders"):
            mid = machine_map.get(int(row["machine_id"]))
            if mid is None:
                continue
            old_tech = row["technician_id"]
            old_plan = row["preventive_plan_id"] if "preventive_plan_id" in row.keys() else None
            wo = WorkOrder(
                empresa_id=empresa_id,
                titulo=row["titulo"],
                descripcion=row["descripcion"] or "",
                tipo=row["tipo"],
                status=row["status"],
                prioridad=row["prioridad"] or "media",
                fecha_programada=row["fecha_programada"],
                machine_id=mid,
                technician_id=tech_map.get(int(old_tech)) if old_tech else None,
                preventive_plan_id=plan_map.get(int(old_plan)) if old_plan else None,
                numero=row["numero"] if "numero" in row.keys() else None,
            )
            db.session.add(wo)
            db.session.flush()
            wo_map[int(row["id"])] = wo.id
            imported["work_orders"] += 1

        for row in _row_dict(conn, "work_order_jornadas"):
            woid = wo_map.get(int(row["work_order_id"]))
            if woid is None:
                continue
            db.session.add(
                WorkOrderJornada(
                    work_order_id=woid,
                    orden=row["orden"] or 1,
                    fecha_inicio=row["fecha_inicio"],
                    fecha_fin=row["fecha_fin"],
                    technician_id=tech_map.get(int(row["technician_id"]))
                    if row["technician_id"]
                    else None,
                    descripcion_avance=row["descripcion_avance"] or "",
                )
            )
            imported["work_order_jornadas"] += 1

        for row in _row_dict(conn, "work_order_repuestos"):
            woid = wo_map.get(int(row["work_order_id"]))
            spid = spare_map.get(int(row["spare_part_id"]))
            if woid is None or spid is None:
                continue
            db.session.add(
                WorkOrderRepuesto(
                    work_order_id=woid,
                    spare_part_id=spid,
                    cantidad=row["cantidad"] or 1,
                    notas=row["notas"] or "",
                )
            )
            imported["work_order_repuestos"] += 1

        for row in _row_dict(conn, "machine_monthly_plans"):
            mid = machine_map.get(int(row["machine_id"]))
            if mid is None:
                continue
            db.session.add(
                MachineMonthlyPlan(
                    empresa_id=empresa_id,
                    machine_id=mid,
                    anio=row["anio"],
                    mes=row["mes"],
                    horas_meta=row["horas_meta"],
                    guardado_at=row["guardado_at"] if "guardado_at" in row.keys() else None,
                )
            )
            imported["machine_monthly_plans"] += 1

        for row in _row_dict(conn, "incidents"):
            mid = machine_map.get(int(row["machine_id"])) if row["machine_id"] else None
            db.session.add(
                Incident(
                    empresa_id=empresa_id,
                    titulo=row["titulo"],
                    descripcion=row["descripcion"] or "",
                    machine_id=mid,
                    resuelto=bool(row["resuelto"]),
                )
            )
            imported["incidents"] += 1

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    finally:
        conn.close()

    return imported


def main() -> int:
    parser = argparse.ArgumentParser(description="Fusiona mantis_*.db en mantenimiento.db")
    parser.add_argument(
        "--tenants-dir",
        type=Path,
        default=ROOT / "data" / "tenants",
        help="Directorio con archivos mantis_{slug}.db",
    )
    parser.add_argument("--dry-run", action="store_true", help="Solo informa, no escribe")
    parser.add_argument(
        "--delete-empty",
        action="store_true",
        help="Elimina archivos tenant vacíos tras verificar",
    )
    args = parser.parse_args()

    tenants_dir = args.tenants_dir
    if not tenants_dir.is_dir():
        print(f"No existe {tenants_dir} — nada que migrar.")
        return 0

    tenant_files = sorted(tenants_dir.glob("mantis_*.db"))
    if not tenant_files:
        print(f"Sin archivos mantis_*.db en {tenants_dir}")
        return 0

    from app import create_app, db
    from app.models import Empresa

    app = create_app()
    exit_code = 0

    with app.app_context():
        for path in tenant_files:
            match = TENANT_FILE_RE.match(path.name)
            if not match:
                print(f"[SKIP] Nombre no reconocido: {path.name}")
                continue
            slug = match.group("slug")
            empresa = Empresa.query.filter_by(slug=slug).first()
            if empresa is None:
                print(f"[ERROR] {path.name}: no hay Empresa con slug={slug!r}")
                exit_code = 1
                continue

            counts = _tenant_counts(path)
            total = _total_rows(counts)
            print(f"\n{path.name} -> empresa_id={empresa.id} ({empresa.razon_social})")
            for table, n in counts.items():
                if n:
                    print(f"  {table}: {n}")

            if total == 0:
                print("  (vacio — datos ya estan en mantenimiento.db o nunca se uso)")
                if args.delete_empty and not args.dry_run:
                    path.unlink()
                    print(f"  Eliminado {path.name}")
                continue

            if args.dry_run:
                print(f"  [dry-run] Se importarían ~{total} filas")
                continue

            try:
                imported = migrate_tenant_db(path, empresa.id, slug, dry_run=False)
                moved = sum(imported.values())
                print(f"  Importadas {moved} filas: {imported}")
            except Exception as exc:
                db.session.rollback()
                print(f"  [ERROR] Falló la migración: {exc}")
                exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
