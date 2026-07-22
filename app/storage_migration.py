"""Migración explícita de archivos históricos hacia almacenamiento de objetos."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from flask import current_app

from app import db
from app.file_storage import exists, reference, save_bytes, tenant_key
from app.maintenance_execution.models import MaintenanceLogAttachment, WorkOrderChecklistEvidence
from app.models import Empresa, InvProducto, Machine, WorkOrderInforme


def _upload(path: Path, key: str, *, apply: bool) -> bool:
    if not path.is_file():
        return False
    if apply and not exists(key):
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        save_bytes(key, path.read_bytes(), content_type=mime)
    return True


def migrate_legacy_storage(*, apply: bool = False) -> dict[str, int]:
    """Copia archivos y actualiza referencias; en modo lectura solo cuenta cambios."""
    stats = {"public_media": 0, "reports": 0, "evidence": 0, "log_attachments": 0, "missing": 0}
    static_root = Path(current_app.static_folder).resolve()
    data_root = Path(current_app.root_path).resolve().parent / "data"

    public_models = (
        (Empresa, "logo"),
        (Machine, "foto_url"),
        (InvProducto, "imagen"),
    )
    for model, field in public_models:
        for row in model.query.all():
            value = (getattr(row, field, "") or "").replace("\\", "/").lstrip("/")
            if not value.startswith("uploads/empresas/") or ".." in value:
                continue
            key = value[len("uploads/") :]
            if _upload(static_root / value, key, apply=apply):
                stats["public_media"] += 1
                if apply:
                    setattr(row, field, reference(key))
            else:
                stats["missing"] += 1

    for report in WorkOrderInforme.query.all():
        value = (report.ruta_archivo or "").replace("\\", "/").lstrip("/")
        if not value.startswith("uploads/empresas/") or ".." in value:
            continue
        key = value[len("uploads/") :]
        if _upload(static_root / value, key, apply=apply):
            stats["reports"] += 1
            if apply:
                report.ruta_archivo = reference(key)
        else:
            stats["missing"] += 1

    for evidence in WorkOrderChecklistEvidence.query.all():
        old_key = (evidence.storage_key or "").replace("\\", "/").lstrip("/")
        if old_key.startswith("empresas/") or ".." in old_key:
            continue
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
        if old_key.startswith("empresas/") or ".." in old_key:
            continue
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
    return stats

