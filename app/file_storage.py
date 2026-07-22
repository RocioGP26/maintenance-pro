"""Almacenamiento de archivos desacoplado del contenedor de la aplicación.

El backend ``local`` se conserva para desarrollo y pruebas. En producción se
debe usar ``s3``; la implementación es compatible con Amazon S3, Cloudflare R2
y Backblaze B2 mediante ``STORAGE_ENDPOINT_URL``.
"""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from flask import Blueprint, abort, current_app, send_file, session
from flask_login import current_user


STORAGE_SCHEME = "storage://"
storage_bp = Blueprint("storage", __name__, url_prefix="/media")


def _backend() -> str:
    return (current_app.config.get("STORAGE_BACKEND") or "local").strip().lower()


def _local_root() -> Path:
    configured = current_app.config.get("STORAGE_LOCAL_ROOT")
    root = Path(configured) if configured else Path(current_app.instance_path) / "uploads"
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _safe_key(key: str) -> str:
    value = (key or "").strip().replace("\\", "/").lstrip("/")
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValueError("Clave de almacenamiento no válida.")
    return path.as_posix()


def reference(key: str) -> str:
    return STORAGE_SCHEME + _safe_key(key)


def key_from_reference(value: str) -> str | None:
    raw = (value or "").strip()
    if not raw.startswith(STORAGE_SCHEME):
        return None
    return _safe_key(raw[len(STORAGE_SCHEME) :])


def _local_path(key: str) -> Path:
    root = _local_root()
    target = (root / _safe_key(key)).resolve()
    if target == root or root not in target.parents:
        raise ValueError("Ruta de almacenamiento no válida.")
    return target


def local_path(key: str) -> Path:
    """Devuelve la ruta local; solo está disponible con backend local."""
    if _backend() != "local":
        raise RuntimeError("El archivo no está almacenado localmente.")
    return _local_path(key)


def _s3_client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:  # pragma: no cover - depende del despliegue
        raise RuntimeError("Instala boto3 para usar STORAGE_BACKEND=s3.") from exc

    endpoint = (current_app.config.get("STORAGE_ENDPOINT_URL") or "").strip() or None
    region = (current_app.config.get("STORAGE_REGION") or "auto").strip()
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id=current_app.config.get("STORAGE_ACCESS_KEY_ID") or None,
        aws_secret_access_key=current_app.config.get("STORAGE_SECRET_ACCESS_KEY") or None,
        config=Config(signature_version="s3v4"),
    )


def _bucket() -> str:
    value = (current_app.config.get("STORAGE_BUCKET") or "").strip()
    if not value:
        raise RuntimeError("STORAGE_BUCKET debe estar configurado para el backend S3.")
    return value


def save_bytes(key: str, content: bytes, *, content_type: str = "application/octet-stream") -> str:
    safe = _safe_key(key)
    if _backend() == "local":
        target = _local_path(safe)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    elif _backend() == "s3":
        _s3_client().put_object(
            Bucket=_bucket(), Key=safe, Body=content, ContentType=content_type
        )
    else:
        raise RuntimeError(f"Backend de almacenamiento no soportado: {_backend()}")
    return safe


def read_bytes(key: str) -> bytes:
    safe = _safe_key(key)
    if _backend() == "local":
        return _local_path(safe).read_bytes()
    if _backend() == "s3":
        try:
            return _s3_client().get_object(Bucket=_bucket(), Key=safe)["Body"].read()
        except Exception as exc:
            response = getattr(exc, "response", {})
            code = str(response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                raise FileNotFoundError(safe) from exc
            raise
    raise RuntimeError(f"Backend de almacenamiento no soportado: {_backend()}")


def delete(key: str) -> None:
    safe = _safe_key(key)
    if _backend() == "local":
        _local_path(safe).unlink(missing_ok=True)
        return
    if _backend() == "s3":
        _s3_client().delete_object(Bucket=_bucket(), Key=safe)
        return
    raise RuntimeError(f"Backend de almacenamiento no soportado: {_backend()}")


def exists(key: str) -> bool:
    safe = _safe_key(key)
    if _backend() == "local":
        return _local_path(safe).is_file()
    if _backend() == "s3":
        try:
            _s3_client().head_object(Bucket=_bucket(), Key=safe)
            return True
        except Exception as exc:  # botocore no se importa en modo local
            response = getattr(exc, "response", {})
            code = str(response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise
    raise RuntimeError(f"Backend de almacenamiento no soportado: {_backend()}")


def tenant_key(empresa_id: int, *parts: object) -> str:
    return _safe_key("/".join(["empresas", str(int(empresa_id)), *[str(p) for p in parts]]))


def size_for_prefix(prefix: str) -> int:
    safe_prefix = _safe_key(prefix).rstrip("/") + "/"
    if _backend() == "local":
        root = _local_path(safe_prefix)
        if not root.is_dir():
            return 0
        return sum(path.stat().st_size for path in root.rglob("*") if path.is_file())
    if _backend() == "s3":
        total = 0
        paginator = _s3_client().get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=_bucket(), Prefix=safe_prefix):
            total += sum(int(item.get("Size", 0)) for item in page.get("Contents", []))
        return total
    raise RuntimeError(f"Backend de almacenamiento no soportado: {_backend()}")


def url_for_reference(value: str | None) -> str | None:
    from flask import url_for

    raw = (value or "").strip()
    if not raw:
        return None
    if raw.startswith(("https://", "http://")):
        return raw
    key = key_from_reference(raw)
    if key:
        return url_for("storage.media", key=key)
    if raw.startswith("uploads/") and ".." not in raw:
        return url_for("static", filename=raw)
    return None


def _tenant_can_read(key: str) -> bool:
    parts = PurePosixPath(_safe_key(key)).parts
    if len(parts) < 3 or parts[0] != "empresas" or not parts[1].isdigit():
        return False
    # Este endpoint solo sirve medios visuales. Informes, evidencias y adjuntos
    # tienen rutas propias con permisos del recurso y nunca se exponen aquí.
    if not (parts[2] in {"activos", "productos"} or parts[2].startswith("logo.")):
        return False
    if session.get("platform_admin"):
        return True
    return bool(
        current_user.is_authenticated
        and getattr(current_user, "empresa_id", None) == int(parts[1])
    )


@storage_bp.get("/<path:key>")
def media(key: str):
    if not _tenant_can_read(key):
        abort(403)
    try:
        content = read_bytes(key)
    except (FileNotFoundError, ValueError):
        abort(404)
    name = PurePosixPath(key).name
    return send_file(BytesIO(content), download_name=name, max_age=300)
