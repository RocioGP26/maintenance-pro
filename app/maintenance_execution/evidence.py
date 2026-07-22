"""Almacenamiento privado y validado de evidencias de checklist."""

from __future__ import annotations

import hashlib
from uuid import uuid4

from werkzeug.utils import secure_filename

from pathlib import Path

from flask import current_app

from app.file_storage import local_path, read_bytes, save_bytes, tenant_key


ALLOWED_EVIDENCE = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}
MAX_EVIDENCE_BYTES = 5 * 1024 * 1024


def save_evidence_file(file, empresa_id: int, checklist_id: int):
    original = secure_filename(getattr(file, "filename", "") or "")
    extension = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if extension not in ALLOWED_EVIDENCE:
        raise ValueError("Formato no permitido. Usa PDF, PNG, JPG o WEBP.")
    mime = (getattr(file, "mimetype", "") or "").lower()
    if mime and mime != ALLOWED_EVIDENCE[extension]:
        raise ValueError("El tipo declarado del archivo no coincide con su extensión.")
    content = file.stream.read(MAX_EVIDENCE_BYTES + 1)
    if not content:
        raise ValueError("La evidencia está vacía.")
    if len(content) > MAX_EVIDENCE_BYTES:
        raise ValueError("La evidencia supera el límite de 5 MB.")
    signatures = {
        "pdf": content.startswith(b"%PDF"),
        "png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "jpg": content.startswith(b"\xff\xd8\xff"),
        "jpeg": content.startswith(b"\xff\xd8\xff"),
        "webp": len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP",
    }
    if not signatures.get(extension, False):
        raise ValueError("El contenido del archivo no corresponde al formato declarado.")
    key = tenant_key(empresa_id, "checklists", checklist_id, f"{uuid4().hex}.{extension}")
    save_bytes(key, content, content_type=ALLOWED_EVIDENCE[extension])
    return {
        "storage_key": key,
        "original_name": original,
        "mime_type": ALLOWED_EVIDENCE[extension],
        "size_bytes": len(content),
        "checksum": hashlib.sha256(content).hexdigest(),
    }


def resolve_evidence_path(storage_key: str):
    """Compatibilidad para pruebas/herramientas que usan el backend local."""
    if not (storage_key or "").startswith("empresas/"):
        root = Path(current_app.root_path).resolve().parent / "data" / "checklist_evidence"
        target = (root / (storage_key or "")).resolve()
        if root.resolve() not in target.parents:
            raise ValueError("Ruta de evidencia no válida.")
        return target
    return local_path(storage_key)


def read_evidence_file(storage_key: str) -> bytes:
    if not (storage_key or "").startswith("empresas/"):
        return resolve_evidence_path(storage_key).read_bytes()
    return read_bytes(storage_key)
