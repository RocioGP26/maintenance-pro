"""Emisión y verificación segura de credenciales de integración."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import IntegrationCredential


SCOPES = (
    "maintenance.assets:read",
    "maintenance.incidents:read",
    "maintenance.incidents:write",
    "maintenance.work_orders:read",
    "maintenance.meters:read",
    "maintenance.meters:write",
    "webhooks:read",
    "webhooks:manage",
)
ENVIRONMENTS = ("test", "live")
LAST_USED_WRITE_INTERVAL = timedelta(minutes=5)


class CredentialError(ValueError):
    """Entrada inválida al administrar una credencial."""


@dataclass(frozen=True)
class IssuedCredential:
    credential: IntegrationCredential
    secret: str


def normalize_scopes(values) -> list[str]:
    requested = {str(value).strip() for value in (values or []) if str(value).strip()}
    unknown = requested.difference(SCOPES)
    if unknown:
        raise CredentialError(f"Scopes no reconocidos: {', '.join(sorted(unknown))}")
    if not requested:
        raise CredentialError("Selecciona al menos un scope.")
    return sorted(requested)


def _expiration(value) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except ValueError as exc:
            raise CredentialError("La fecha de expiración no es válida.") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    if parsed <= datetime.utcnow():
        raise CredentialError("La expiración debe estar en el futuro.")
    return parsed


def issue_credential(
    *, empresa_id: int, name: str, environment: str, scopes, created_by_id: int | None,
    expires_at=None, rotated_from_id: int | None = None,
) -> IssuedCredential:
    from app.integrations.entitlements import entitlement_bool, entitlement_int

    if not entitlement_bool(empresa_id, "public_api.enabled", False):
        raise CredentialError("La API pública no está habilitada para este plan.")
    max_creds = entitlement_int(empresa_id, "public_api.credentials_max", 1)
    current = IntegrationCredential.query.filter_by(empresa_id=int(empresa_id)).filter(
        IntegrationCredential.revoked_at.is_(None)
    ).count()
    if current >= max_creds:
        raise CredentialError(f"Límite de credenciales alcanzado ({max_creds}).")

    clean_name = (name or "").strip()
    if not clean_name:
        raise CredentialError("El nombre de la credencial es obligatorio.")
    environment = (environment or "test").strip().lower()
    if environment not in ENVIRONMENTS:
        raise CredentialError("El ambiente debe ser test o live.")
    prefix = f"rtx_{environment}_{secrets.token_hex(6)}"
    raw_secret = secrets.token_urlsafe(32)
    item = IntegrationCredential(
        empresa_id=int(empresa_id),
        name=clean_name[:120],
        key_prefix=prefix,
        secret_hash=generate_password_hash(raw_secret, method="scrypt"),
        environment=environment,
        expires_at=_expiration(expires_at),
        created_by_id=created_by_id,
        rotated_from_id=rotated_from_id,
    )
    item.set_scopes(normalize_scopes(scopes))
    db.session.add(item)
    db.session.flush()
    return IssuedCredential(item, f"{prefix}.{raw_secret}")


def revoke_credential(item: IntegrationCredential, *, at: datetime | None = None) -> bool:
    if item.revoked_at is not None:
        return False
    item.revoked_at = at or datetime.utcnow()
    db.session.flush()
    return True


def rotate_credential(
    item: IntegrationCredential, *, created_by_id: int | None, grace_minutes: int = 10
) -> IssuedCredential:
    if not item.active:
        raise CredentialError("Solo se pueden rotar credenciales activas.")
    grace = max(0, min(int(grace_minutes), 60))
    issued = issue_credential(
        empresa_id=item.empresa_id,
        name=item.name,
        environment=item.environment,
        scopes=item.scopes,
        created_by_id=created_by_id,
        expires_at=item.expires_at,
        rotated_from_id=item.id,
    )
    cutoff = datetime.utcnow() + timedelta(minutes=grace)
    if item.expires_at is None or item.expires_at > cutoff:
        item.expires_at = cutoff
    return issued


def authenticate_credential(raw: str) -> IntegrationCredential | None:
    item, _reason = authenticate_credential_result(raw)
    return item


def authenticate_credential_result(raw: str) -> tuple[IntegrationCredential | None, str]:
    """Autentica y devuelve un código seguro para respuestas API.

    El estado expirada/revocada solo se revela después de comprobar el secreto.
    """

    token = (raw or "").strip()
    if "." not in token:
        return None, "invalid_api_key"
    prefix, secret = token.split(".", 1)
    if not prefix.startswith(("rtx_test_", "rtx_live_")) or not secret:
        return None, "invalid_api_key"
    item = IntegrationCredential.query.filter_by(key_prefix=prefix).first()
    if item is None or not check_password_hash(item.secret_hash, secret):
        return None, "invalid_api_key"
    now = datetime.utcnow()
    if item.revoked_at is not None:
        return None, "api_key_revoked"
    if item.expires_at is not None and item.expires_at <= now:
        return None, "api_key_expired"
    if item.last_used_at is None or now - item.last_used_at >= LAST_USED_WRITE_INTERVAL:
        item.last_used_at = now
    return item, ""
