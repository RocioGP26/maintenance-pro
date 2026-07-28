"""Réplica incremental y manifiesto del almacenamiento S3 de producción."""

from __future__ import annotations

import json
import os
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


def _clean_etag(value: object) -> str:
    return str(value or "").strip().strip('"')


def _safe_prefix(value: str) -> str:
    raw = (value or "roustix").strip().replace("\\", "/").strip("/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts:
        raise ValueError("STORAGE_BACKUP_PREFIX no es válido.")
    return path.as_posix()


@dataclass(frozen=True)
class StorageBackupConfig:
    source_bucket: str
    target_bucket: str
    prefix: str = "roustix"
    source_endpoint: str = ""
    source_region: str = "auto"
    source_access_key: str = ""
    source_secret_key: str = ""
    target_endpoint: str = ""
    target_region: str = "auto"
    target_access_key: str = ""
    target_secret_key: str = ""

    @classmethod
    def from_environment(cls) -> "StorageBackupConfig":
        source_endpoint = os.environ.get("STORAGE_ENDPOINT_URL", "").strip()
        source_region = os.environ.get("STORAGE_REGION", "auto").strip() or "auto"
        return cls(
            source_bucket=os.environ.get("STORAGE_BUCKET", "").strip(),
            target_bucket=os.environ.get("STORAGE_BACKUP_BUCKET", "").strip(),
            prefix=os.environ.get("STORAGE_BACKUP_PREFIX", "roustix").strip(),
            source_endpoint=source_endpoint,
            source_region=source_region,
            source_access_key=os.environ.get("STORAGE_ACCESS_KEY_ID", "").strip(),
            source_secret_key=os.environ.get("STORAGE_SECRET_ACCESS_KEY", ""),
            target_endpoint=os.environ.get(
                "STORAGE_BACKUP_ENDPOINT_URL", source_endpoint
            ).strip(),
            target_region=(
                os.environ.get("STORAGE_BACKUP_REGION", source_region).strip()
                or source_region
            ),
            target_access_key=os.environ.get(
                "STORAGE_BACKUP_ACCESS_KEY_ID", ""
            ).strip(),
            target_secret_key=os.environ.get(
                "STORAGE_BACKUP_SECRET_ACCESS_KEY", ""
            ),
        )

    def validate(self) -> None:
        missing = []
        for name, value in (
            ("STORAGE_BUCKET", self.source_bucket),
            ("STORAGE_BACKUP_BUCKET", self.target_bucket),
            ("STORAGE_ACCESS_KEY_ID", self.source_access_key),
            ("STORAGE_SECRET_ACCESS_KEY", self.source_secret_key),
            ("STORAGE_BACKUP_ACCESS_KEY_ID", self.target_access_key),
            ("STORAGE_BACKUP_SECRET_ACCESS_KEY", self.target_secret_key),
        ):
            if not value:
                missing.append(name)
        if missing:
            raise ValueError(
                "Configuración S3 incompleta para backup: " + ", ".join(missing)
            )
        if (
            self.source_bucket == self.target_bucket
            and (self.source_endpoint or "") == (self.target_endpoint or "")
        ):
            raise ValueError(
                "STORAGE_BACKUP_BUCKET debe ser diferente al bucket operativo."
            )
        _safe_prefix(self.prefix)


def _client(*, endpoint: str, region: str, access_key: str, secret_key: str):
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:  # pragma: no cover - dependencia de despliegue
        raise RuntimeError("Instala boto3 para ejecutar el backup S3.") from exc
    return boto3.client(
        "s3",
        endpoint_url=endpoint or None,
        region_name=region or "auto",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )


def _is_missing(exc: Exception) -> bool:
    response = getattr(exc, "response", {}) or {}
    code = str(response.get("Error", {}).get("Code", ""))
    return code in {"404", "NoSuchKey", "NotFound"}


def _target_matches(client, bucket: str, key: str, *, etag: str, size: int) -> bool:
    try:
        current = client.head_object(Bucket=bucket, Key=key)
    except Exception as exc:
        if _is_missing(exc):
            return False
        raise
    metadata = current.get("Metadata", {}) or {}
    return (
        metadata.get("source-etag", "") == etag
        and int(metadata.get("source-size", -1)) == int(size)
    )


def backup_s3_storage(
    manifest_path: str | Path,
    *,
    recovery_files: list[str | Path] | None = None,
    config: StorageBackupConfig | None = None,
    source_client=None,
    target_client=None,
) -> dict[str, Any]:
    """Replica objetos modificados y conserva un manifiesto auditable."""
    cfg = config or StorageBackupConfig.from_environment()
    cfg.validate()
    prefix = _safe_prefix(cfg.prefix)
    source = source_client or _client(
        endpoint=cfg.source_endpoint,
        region=cfg.source_region,
        access_key=cfg.source_access_key,
        secret_key=cfg.source_secret_key,
    )
    target = target_client or _client(
        endpoint=cfg.target_endpoint,
        region=cfg.target_region,
        access_key=cfg.target_access_key,
        secret_key=cfg.target_secret_key,
    )

    created_at = datetime.now(timezone.utc)
    copied = 0
    skipped = 0
    total_bytes = 0
    objects: list[dict[str, Any]] = []
    paginator = source.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=cfg.source_bucket):
        for item in page.get("Contents", []):
            key = str(item["Key"])
            size = int(item.get("Size", 0))
            etag = _clean_etag(item.get("ETag"))
            if not etag:
                raise RuntimeError(f"El objeto no tiene ETag verificable: {key}")
            version_key = hashlib.sha256(f"{etag}:{size}".encode("utf-8")).hexdigest()
            destination = f"{prefix}/objects/{version_key}/{key}"
            total_bytes += size
            if _target_matches(
                target, cfg.target_bucket, destination, etag=etag, size=size
            ):
                skipped += 1
            else:
                response = source.get_object(Bucket=cfg.source_bucket, Key=key)
                response_etag = _clean_etag(response.get("ETag")) or etag
                if etag and response_etag != etag:
                    raise RuntimeError(
                        f"El objeto cambió durante el backup; se reintentará: {key}"
                    )
                body = response["Body"]
                extra = {
                    "Metadata": {
                        "source-etag": response_etag,
                        "source-size": str(size),
                        "source-bucket": cfg.source_bucket,
                    }
                }
                content_type = response.get("ContentType")
                if content_type:
                    extra["ContentType"] = content_type
                try:
                    target.upload_fileobj(
                        body, cfg.target_bucket, destination, ExtraArgs=extra
                    )
                finally:
                    close = getattr(body, "close", None)
                    if close:
                        close()
                if not _target_matches(
                    target,
                    cfg.target_bucket,
                    destination,
                    etag=etag,
                    size=size,
                ):
                    raise RuntimeError(
                        f"El objeto replicado no superó la verificación: {key}"
                    )
                copied += 1
            last_modified = item.get("LastModified")
            objects.append(
                {
                    "key": key,
                    "size": size,
                    "etag": etag,
                    "last_modified": (
                        last_modified.isoformat()
                        if hasattr(last_modified, "isoformat")
                        else str(last_modified or "")
                    ),
                    "backup_key": destination,
                }
            )

    stamp = created_at.strftime("%Y%m%d_%H%M%S")
    recovery_records = []
    for value in recovery_files or []:
        recovery_path = Path(value)
        if not recovery_path.is_file() or recovery_path.stat().st_size == 0:
            raise ValueError(f"El artefacto de recuperación no existe o está vacío: {value}")
        digest = hashlib.sha256()
        with recovery_path.open("rb") as source_file:
            for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
                digest.update(chunk)
        size = recovery_path.stat().st_size
        sha256 = digest.hexdigest()
        backup_key = f"{prefix}/database/{stamp}/{recovery_path.name}"
        target.upload_file(
            str(recovery_path),
            cfg.target_bucket,
            backup_key,
            ExtraArgs={
                "Metadata": {"sha256": sha256, "source-size": str(size)}
            },
        )
        uploaded = target.head_object(Bucket=cfg.target_bucket, Key=backup_key)
        metadata = uploaded.get("Metadata", {}) or {}
        if (
            metadata.get("sha256") != sha256
            or int(metadata.get("source-size", -1)) != size
        ):
            raise RuntimeError(
                f"El artefacto no superó la verificación en S3: {recovery_path.name}"
            )
        recovery_records.append(
            {
                "name": recovery_path.name,
                "size": size,
                "sha256": sha256,
                "backup_key": backup_key,
            }
        )

    manifest = {
        "format": "roustix-storage-backup-v1",
        "created_at": created_at.isoformat(),
        "source_bucket": cfg.source_bucket,
        "target_bucket": cfg.target_bucket,
        "prefix": prefix,
        "object_count": len(objects),
        "total_bytes": total_bytes,
        "copied": copied,
        "skipped": skipped,
        "objects": objects,
        "recovery_files": recovery_records,
    }
    output = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    output.write_bytes(payload)
    manifest_key = f"{prefix}/manifests/{stamp}.json"
    target.put_object(
        Bucket=cfg.target_bucket,
        Key=manifest_key,
        Body=payload,
        ContentType="application/json",
    )
    manifest["manifest_key"] = manifest_key
    return manifest
