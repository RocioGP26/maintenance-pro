"""Migración explícita de archivos históricos hacia almacenamiento de objetos."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from flask import current_app

from app import db
from app.file_storage import STORAGE_SCHEME, exists, reference, save_bytes, tenant_key
from app.maintenance_execution.models import MaintenanceLogAttachment, WorkOrderChecklistEvidence
from app.models import Empresa, InvProducto, Machine, WorkOrderInforme


def _ensure_object(path: Path, key: str, *, apply: bool) -> str:
    """Garantiza el objeto en el backend.

    Retorna:
      - ``ok`` si el archivo local se (puede) copiar
      - ``remote`` si ya existía en object storage
      - ``missing`` si no hay local ni remoto
    """
    try:
        if exists(key):
            return "remote"
    except Exception:
        pass
    if not path.is_file():
        return "missing"
    if apply:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        save_bytes(key, path.read_bytes(), content_type=mime, enforce_quota=False)
    return "ok"


def _empty_stats() -> dict[str, int]:
    return {
        "public_media": 0,
        "reports": 0,
        "evidence": 0,
        "log_attachments": 0,
        "missing": 0,
        "from_remote": 0,
        "already_migrated": 0,
        "legacy_refs_pending": 0,
    }


def _bump(stats: dict[str, Any], category: str, status: str) -> None:
    if status in {"ok", "remote"}:
        stats[category] += 1
        if status == "remote":
            stats["from_remote"] += 1
    else:
        stats["missing"] += 1


def inventory_legacy_refs() -> dict[str, int]:
    """Cuenta referencias legacy aún pendientes en BD (sin tocar disco)."""
    stats = {
        "public_media_legacy": 0,
        "reports_legacy": 0,
        "evidence_legacy": 0,
        "log_attachments_legacy": 0,
        "already_object": 0,
        "legacy_total": 0,
    }
    for model, field in (
        (Empresa, "logo"),
        (Machine, "foto_url"),
        (InvProducto, "imagen"),
    ):
        for row in model.query.all():
            value = (getattr(row, field, "") or "").replace("\\", "/").strip()
            if not value:
                continue
            if value.startswith(STORAGE_SCHEME) or value.startswith("empresas/"):
                stats["already_object"] += 1
            elif value.lstrip("/").startswith("uploads/empresas/"):
                stats["public_media_legacy"] += 1

    for report in WorkOrderInforme.query.all():
        value = (report.ruta_archivo or "").replace("\\", "/").strip()
        if not value:
            continue
        if value.startswith(STORAGE_SCHEME) or value.startswith("empresas/"):
            stats["already_object"] += 1
        elif value.lstrip("/").startswith("uploads/empresas/"):
            stats["reports_legacy"] += 1

    for evidence in WorkOrderChecklistEvidence.query.all():
        old_key = (evidence.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key:
            continue
        if old_key.startswith("empresas/"):
            stats["already_object"] += 1
        else:
            stats["evidence_legacy"] += 1

    for attachment in MaintenanceLogAttachment.query.all():
        old_key = (attachment.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key:
            continue
        if old_key.startswith("empresas/"):
            stats["already_object"] += 1
        else:
            stats["log_attachments_legacy"] += 1

    stats["legacy_total"] = (
        stats["public_media_legacy"]
        + stats["reports_legacy"]
        + stats["evidence_legacy"]
        + stats["log_attachments_legacy"]
    )
    return stats


def list_legacy_pending() -> list[dict[str, Any]]:
    """Detalle de refs legacy: ruta, key destino y si existe en R2/local."""
    static_root = Path(current_app.static_folder).resolve()
    data_root = Path(current_app.root_path).resolve().parent / "data"
    rows: list[dict[str, Any]] = []

    def _remote(key: str) -> bool:
        try:
            return bool(exists(key))
        except Exception:
            return False

    for model, field, kind in (
        (Empresa, "logo", "empresa.logo"),
        (Machine, "foto_url", "machine.foto_url"),
        (InvProducto, "imagen", "producto.imagen"),
    ):
        for row in model.query.all():
            raw = (getattr(row, field, "") or "").replace("\\", "/").strip()
            value = raw.lstrip("/")
            if not value.startswith("uploads/empresas/") or ".." in value:
                continue
            key = value[len("uploads/") :]
            local = static_root / value
            rows.append(
                {
                    "kind": kind,
                    "id": row.id,
                    "legacy": raw,
                    "key": key,
                    "local": local.is_file(),
                    "remote": _remote(key),
                }
            )

    for report in WorkOrderInforme.query.all():
        raw = (report.ruta_archivo or "").replace("\\", "/").strip()
        value = raw.lstrip("/")
        if not value.startswith("uploads/empresas/") or ".." in value:
            continue
        key = value[len("uploads/") :]
        local = static_root / value
        rows.append(
            {
                "kind": "informe.ruta_archivo",
                "id": report.id,
                "legacy": raw,
                "key": key,
                "local": local.is_file(),
                "remote": _remote(key),
            }
        )

    for evidence in WorkOrderChecklistEvidence.query.all():
        old_key = (evidence.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key or old_key.startswith("empresas/") or ".." in old_key:
            continue
        parts = Path(old_key).parts
        if len(parts) < 3:
            rows.append(
                {
                    "kind": "evidence.storage_key",
                    "id": evidence.id,
                    "legacy": old_key,
                    "key": "",
                    "local": False,
                    "remote": False,
                }
            )
            continue
        key = tenant_key(evidence.empresa_id, "checklists", evidence.checklist_id, parts[-1])
        local = data_root / "checklist_evidence" / old_key
        rows.append(
            {
                "kind": "evidence.storage_key",
                "id": evidence.id,
                "legacy": old_key,
                "key": key,
                "local": local.is_file(),
                "remote": _remote(key),
            }
        )

    for attachment in MaintenanceLogAttachment.query.all():
        old_key = (attachment.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key or old_key.startswith("empresas/") or ".." in old_key:
            continue
        parts = Path(old_key).parts
        if len(parts) < 3:
            rows.append(
                {
                    "kind": "bitacora.storage_key",
                    "id": attachment.id,
                    "legacy": old_key,
                    "key": "",
                    "local": False,
                    "remote": False,
                }
            )
            continue
        key = tenant_key(attachment.empresa_id, "bitacora", attachment.entry_id, parts[-1])
        local = data_root / "maintenance_log" / old_key
        rows.append(
            {
                "kind": "bitacora.storage_key",
                "id": attachment.id,
                "legacy": old_key,
                "key": key,
                "local": local.is_file(),
                "remote": _remote(key),
            }
        )

    return rows


def clear_broken_legacy_refs(*, apply: bool = False) -> dict[str, int]:
    """Limpia refs legacy sin archivo local ni objeto remoto (huérfanas)."""
    cleared = 0
    kept = 0
    for item in list_legacy_pending():
        if item["local"] or item["remote"]:
            kept += 1
            continue
        if not apply:
            cleared += 1
            continue
        kind = item["kind"]
        row_id = item["id"]
        if kind == "empresa.logo":
            row = db.session.get(Empresa, row_id)
            if row:
                row.logo = ""
        elif kind == "machine.foto_url":
            row = db.session.get(Machine, row_id)
            if row:
                row.foto_url = ""
        elif kind == "producto.imagen":
            row = db.session.get(InvProducto, row_id)
            if row:
                row.imagen = ""
        elif kind == "informe.ruta_archivo":
            row = db.session.get(WorkOrderInforme, row_id)
            if row:
                # Mantener fila; marcar ruta vacía para forzar re-subida.
                row.ruta_archivo = ""
        elif kind == "evidence.storage_key":
            row = db.session.get(WorkOrderChecklistEvidence, row_id)
            if row:
                row.storage_key = ""
        elif kind == "bitacora.storage_key":
            row = db.session.get(MaintenanceLogAttachment, row_id)
            if row:
                row.storage_key = ""
        cleared += 1
    if apply:
        db.session.commit()
    else:
        db.session.rollback()
    return {"would_clear" if not apply else "cleared": cleared, "kept": kept}


def migrate_legacy_storage(*, apply: bool = False) -> dict[str, Any]:
    """Copia archivos y actualiza referencias; en modo lectura solo cuenta cambios.

    Si el objeto ya está en R2/S3 pero la BD sigue con ``uploads/...``, reescribe
    la referencia sin necesitar el disco local del contenedor.
    """
    stats: dict[str, Any] = _empty_stats()
    static_root = Path(current_app.static_folder).resolve()
    data_root = Path(current_app.root_path).resolve().parent / "data"

    for model, field in (
        (Empresa, "logo"),
        (Machine, "foto_url"),
        (InvProducto, "imagen"),
    ):
        for row in model.query.all():
            raw = (getattr(row, field, "") or "").replace("\\", "/").strip()
            if not raw:
                continue
            if raw.startswith(STORAGE_SCHEME):
                stats["already_migrated"] += 1
                continue
            value = raw.lstrip("/")
            if not value.startswith("uploads/empresas/") or ".." in value:
                continue
            stats["legacy_refs_pending"] += 1
            key = value[len("uploads/") :]
            status = _ensure_object(static_root / value, key, apply=apply)
            _bump(stats, "public_media", status)
            if apply and status in {"ok", "remote"}:
                setattr(row, field, reference(key))

    for report in WorkOrderInforme.query.all():
        raw = (report.ruta_archivo or "").replace("\\", "/").strip()
        if not raw:
            continue
        if raw.startswith(STORAGE_SCHEME):
            stats["already_migrated"] += 1
            continue
        value = raw.lstrip("/")
        if not value.startswith("uploads/empresas/") or ".." in value:
            continue
        stats["legacy_refs_pending"] += 1
        key = value[len("uploads/") :]
        status = _ensure_object(static_root / value, key, apply=apply)
        _bump(stats, "reports", status)
        if apply and status in {"ok", "remote"}:
            report.ruta_archivo = reference(key)

    for evidence in WorkOrderChecklistEvidence.query.all():
        old_key = (evidence.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key:
            continue
        if old_key.startswith("empresas/"):
            stats["already_migrated"] += 1
            continue
        if ".." in old_key:
            continue
        stats["legacy_refs_pending"] += 1
        parts = Path(old_key).parts
        if len(parts) < 3:
            stats["missing"] += 1
            continue
        key = tenant_key(evidence.empresa_id, "checklists", evidence.checklist_id, parts[-1])
        status = _ensure_object(data_root / "checklist_evidence" / old_key, key, apply=apply)
        _bump(stats, "evidence", status)
        if apply and status in {"ok", "remote"}:
            evidence.storage_key = key

    for attachment in MaintenanceLogAttachment.query.all():
        old_key = (attachment.storage_key or "").replace("\\", "/").lstrip("/")
        if not old_key:
            continue
        if old_key.startswith("empresas/"):
            stats["already_migrated"] += 1
            continue
        if ".." in old_key:
            continue
        stats["legacy_refs_pending"] += 1
        parts = Path(old_key).parts
        if len(parts) < 3:
            stats["missing"] += 1
            continue
        key = tenant_key(attachment.empresa_id, "bitacora", attachment.entry_id, parts[-1])
        status = _ensure_object(data_root / "maintenance_log" / old_key, key, apply=apply)
        _bump(stats, "log_attachments", status)
        if apply and status in {"ok", "remote"}:
            attachment.storage_key = key

    if apply:
        db.session.commit()
    else:
        db.session.rollback()

    stats["inventory"] = inventory_legacy_refs()
    return stats
