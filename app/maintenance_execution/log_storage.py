"""Almacenamiento privado de adjuntos de bitácora."""

from __future__ import annotations

import hashlib
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED = {"pdf":"application/pdf", "png":"image/png", "jpg":"image/jpeg", "jpeg":"image/jpeg", "webp":"image/webp"}
MAX_BYTES = 5 * 1024 * 1024


def log_storage_root():
    return Path(current_app.root_path).resolve().parent / "data" / "maintenance_log"


def save_log_file(file, empresa_id: int, entry_id: int):
    original = secure_filename(getattr(file, "filename", "") or "")
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED:
        raise ValueError("Formato no permitido. Usa PDF, PNG, JPG o WEBP.")
    mime = (getattr(file, "mimetype", "") or "").lower()
    if mime and mime != ALLOWED[ext]:
        raise ValueError("El tipo declarado no coincide con la extensión.")
    content = file.stream.read(MAX_BYTES + 1)
    if not content or len(content) > MAX_BYTES:
        raise ValueError("El archivo está vacío o supera 5 MB.")
    valid = {
        "pdf": content.startswith(b"%PDF"), "png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "jpg": content.startswith(b"\xff\xd8\xff"), "jpeg": content.startswith(b"\xff\xd8\xff"),
        "webp": len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP",
    }[ext]
    if not valid:
        raise ValueError("El contenido no corresponde al formato declarado.")
    key = Path(str(empresa_id)) / str(entry_id) / f"{uuid4().hex}.{ext}"
    target = (log_storage_root() / key).resolve(); root = log_storage_root().resolve()
    if root not in target.parents: raise ValueError("Ruta de archivo no válida.")
    target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(content)
    return {"storage_key":key.as_posix(), "original_name":original, "mime_type":ALLOWED[ext], "size_bytes":len(content), "checksum":hashlib.sha256(content).hexdigest(), "path":target}


def resolve_log_file(storage_key: str):
    root = log_storage_root().resolve(); target = (root / (storage_key or "")).resolve()
    if root not in target.parents: raise ValueError("Ruta de archivo no válida.")
    return target
