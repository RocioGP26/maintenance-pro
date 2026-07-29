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


def _upload(path: Path, key: str, *, apply: bool) -> bool:
    if not path.is_file():
        return False
    if apply and not exists(key):
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        save_bytes(key, path.read_bytes(), content_type=mime, enforce_quota=False)
    return True


def _empty_stats() -> dict[str, int]:
    return {
        "public_media": 0,
        "reports": 0,
        "evidence": 0,
        "log_attachments": 0,
        "missing": 0,
        "already_migrated": 0,
        "legacy_refs_pending": 0,
    }


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


def migrate_legacy_storage(*, apply: bool = False) -> dict[str, Any]:
    """Copia archivos y actualiza referencias; en modo lectura solo cuenta cambios."""
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
            if _upload(static_root / value, key, apply=apply):
                stats["public_media"] += 1
                if apply:
                    setattr(row, field, reference(key))
            else:
                stats["missing"] += 1

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
        if _upload(static_root / value, key, apply=apply):
            stats["reports"] += 1
            if apply:
                report.ruta_archivo = reference(key)
        else:
            stats["missing"] += 1

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
        if _upload(data_root / "checklist_evidence" / old_key, key, apply=apply):
            stats["evidence"] += 1
            if apply:
                evidence.storage_key = key
        else:
            stats["missing"] += 1

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
        if _upload(data_root / "maintenance_log" / old_key, key, apply=apply):
            stats["log_attachments"] += 1
            if apply:
                attachment.storage_key = key
        else:
            stats["missing"] += 1

    if apply:
        db.session.commit()
    else:
        db.session.rollback()

    stats["inventory"] = inventory_legacy_refs()
    return stats
