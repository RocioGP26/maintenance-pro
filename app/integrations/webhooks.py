"""Webhooks Sprint 22.3 · outbox, endpoints, HMAC y entregas."""

from __future__ import annotations

from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import ipaddress
import json
import secrets
import socket
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app

from app import db
from app.models import Empresa, IntegrationEvent, WebhookDelivery, WebhookEndpoint


WEBHOOK_EVENTS = (
    "incident.created",
    "incident.status_changed",
    "work_order.created",
    "work_order.assigned",
    "work_order.status_changed",
    "work_order.completed",
    "work_order.closed",
    "meter.reading_created",
    "meter.reading_flagged",
    "asset_health.band_changed",
)
ENVIRONMENTS = ("test", "live")
ENDPOINT_STATUSES = ("active", "paused", "disabled")
RETRY_DELAYS = (
    timedelta(seconds=0),
    timedelta(minutes=1),
    timedelta(minutes=5),
    timedelta(minutes=15),
    timedelta(hours=1),
)
MAX_ATTEMPTS = 5
DELIVERY_TIMEOUT_SEC = 5
MAX_FAILURES_BEFORE_DISABLE = 20
LEASE_SECONDS = 60
SIGNATURE_MAX_SKEW_SEC = 300
RESPONSE_EXCERPT_MAX = 240


class WebhookError(ValueError):
    """Entrada inválida al administrar webhooks."""


def _app_secret() -> str:
    return str(current_app.config.get("SECRET_KEY") or "dev")


def seal_secret(plaintext: str) -> str:
    key = hashlib.sha256(f"rtx-wh:{_app_secret()}".encode("utf-8")).digest()
    raw = plaintext.encode("utf-8")
    stream = b"".join(
        hashlib.sha256(key + counter.to_bytes(2, "big")).digest()
        for counter in range((len(raw) // 32) + 1)
    )
    cipher = bytes(a ^ b for a, b in zip(raw, stream[: len(raw)]))
    mac = hmac.new(key, cipher, hashlib.sha256).digest()[:16]
    return base64.urlsafe_b64encode(mac + cipher).decode("ascii")


def unseal_secret(sealed: str) -> str:
    key = hashlib.sha256(f"rtx-wh:{_app_secret()}".encode("utf-8")).digest()
    blob = base64.urlsafe_b64decode(sealed.encode("ascii"))
    mac, cipher = blob[:16], blob[16:]
    expected = hmac.new(key, cipher, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(mac, expected):
        raise WebhookError("No se pudo recuperar el secreto del endpoint.")
    stream = b"".join(
        hashlib.sha256(key + counter.to_bytes(2, "big")).digest()
        for counter in range((len(cipher) // 32) + 1)
    )
    raw = bytes(a ^ b for a, b in zip(cipher, stream[: len(cipher)]))
    return raw.decode("utf-8")


def normalize_events(values) -> list[str]:
    requested = {str(value).strip() for value in (values or []) if str(value).strip()}
    unknown = requested.difference(WEBHOOK_EVENTS)
    if unknown:
        raise WebhookError(f"Eventos no reconocidos: {', '.join(sorted(unknown))}")
    if not requested:
        raise WebhookError("Selecciona al menos un evento.")
    return sorted(requested)


def _is_blocked_host(hostname: str) -> bool:
    host = (hostname or "").strip().lower().rstrip(".")
    if not host or host == "localhost" or host.endswith(".localhost"):
        return True
    if host in {"metadata.google.internal", "metadata"}:
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise WebhookError("No se pudo resolver el host del endpoint.") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return True
    return False


def validate_webhook_url(
    url: str, *, allow_http: bool = False, allow_private: bool = False
) -> str:
    clean = (url or "").strip()
    parsed = urlparse(clean)
    scheme = (parsed.scheme or "").lower()
    if scheme not in (("http", "https") if allow_http else ("https",)):
        raise WebhookError("La URL del webhook debe usar HTTPS.")
    if not parsed.hostname:
        raise WebhookError("La URL del webhook no es válida.")
    if parsed.username or parsed.password:
        raise WebhookError("La URL no puede incluir credenciales.")
    if not allow_private and _is_blocked_host(parsed.hostname):
        raise WebhookError("La URL apunta a una red no permitida.")
    return clean


def create_endpoint(
    *,
    empresa_id: int,
    name: str,
    url: str,
    events,
    environment: str = "test",
    created_by_id: int | None = None,
    allow_http: bool = False,
) -> tuple[WebhookEndpoint, str]:
    from app.integrations.entitlements import entitlement_bool, entitlement_int

    if not entitlement_bool(empresa_id, "webhooks.enabled", False):
        raise WebhookError("Los webhooks no están habilitados para este plan.")
    max_endpoints = entitlement_int(empresa_id, "webhooks.endpoints_max", 0)
    current = WebhookEndpoint.query.filter_by(empresa_id=int(empresa_id)).count()
    if current >= max_endpoints:
        raise WebhookError(f"Límite de endpoints alcanzado ({max_endpoints}).")

    clean_name = (name or "").strip()
    if not clean_name:
        raise WebhookError("El nombre del endpoint es obligatorio.")
    environment = (environment or "test").strip().lower()
    if environment not in ENVIRONMENTS:
        raise WebhookError("El ambiente debe ser test o live.")
    allow_private = environment == "test"
    if environment == "test":
        allow_http = True
    validated = validate_webhook_url(
        url, allow_http=allow_http, allow_private=allow_private
    )
    raw_secret = f"whsec_{secrets.token_urlsafe(24)}"
    item = WebhookEndpoint(
        empresa_id=int(empresa_id),
        name=clean_name[:120],
        url=validated,
        secret_sealed=seal_secret(raw_secret),
        environment=environment,
        status="active",
        created_by_id=created_by_id,
    )
    item.set_events(normalize_events(events))
    db.session.add(item)
    db.session.flush()
    return item, raw_secret


def rotate_endpoint_secret(item: WebhookEndpoint) -> str:
    raw_secret = f"whsec_{secrets.token_urlsafe(24)}"
    item.secret_sealed = seal_secret(raw_secret)
    item.updated_at = datetime.utcnow()
    db.session.flush()
    return raw_secret


def set_endpoint_status(item: WebhookEndpoint, status: str) -> None:
    status = (status or "").strip().lower()
    if status not in ENDPOINT_STATUSES:
        raise WebhookError("Estado de endpoint no válido.")
    item.status = status
    item.disabled_at = datetime.utcnow() if status == "disabled" else None
    if status == "active":
        item.failure_count = 0
    item.updated_at = datetime.utcnow()
    db.session.flush()


def _new_public_id() -> str:
    return f"evt_{secrets.token_hex(16)}"


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.replace(microsecond=0).isoformat() + "Z"


def emit_event(
    *,
    empresa_id: int,
    event_type: str,
    resource_type: str,
    resource_id: int,
    data: dict,
    occurred_at: datetime | None = None,
) -> IntegrationEvent | None:
    """Persiste el evento y crea entregas pendientes en la misma transacción."""
    from app.integrations.entitlements import entitlement_bool

    if event_type not in WEBHOOK_EVENTS:
        return None
    if not empresa_id:
        return None
    if not entitlement_bool(empresa_id, "webhooks.enabled", False):
        return None
    empresa = Empresa.query.get(int(empresa_id))
    if empresa is None:
        return None
    # Protección de datos: el payload solo incluye IDs y campos no secretos.
    safe_data = {key: value for key, value in (data or {}).items() if key not in {"secret", "token", "password"}}
    occurred = occurred_at or datetime.utcnow()
    envelope = {
        "id": _new_public_id(),
        "type": event_type,
        "api_version": "v1",
        "occurred_at": _iso(occurred),
        "tenant": {"slug": empresa.slug, "id": empresa.id},
        "data": {"object": safe_data},
    }
    event = IntegrationEvent(
        public_id=envelope["id"],
        empresa_id=int(empresa_id),
        event_type=event_type,
        api_version="v1",
        resource_type=resource_type[:40],
        resource_id=int(resource_id),
        occurred_at=occurred,
        payload_json=json.dumps(envelope, ensure_ascii=False, separators=(",", ":")),
    )
    db.session.add(event)
    db.session.flush()
    endpoints = WebhookEndpoint.query.filter_by(
        empresa_id=int(empresa_id), status="active"
    ).filter(WebhookEndpoint.disabled_at.is_(None)).all()
    now = datetime.utcnow()
    for endpoint in endpoints:
        if endpoint.empresa_id != int(empresa_id):
            continue
        if event_type not in endpoint.events:
            continue
        db.session.add(
            WebhookDelivery(
                empresa_id=int(empresa_id),
                event_id=event.id,
                endpoint_id=endpoint.id,
                attempt=1,
                status="pending",
                next_attempt_at=now,
            )
        )
    db.session.flush()
    return event


def sign_payload(secret: str, timestamp: int, raw_body: bytes) -> str:
    message = f"{timestamp}.".encode("utf-8") + raw_body
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"v1={digest}"


def verify_signature(
    secret: str,
    timestamp: int | str,
    raw_body: bytes,
    signature_header: str,
    *,
    now: int | None = None,
    max_skew_sec: int = SIGNATURE_MAX_SKEW_SEC,
) -> bool:
    """Valida firma HMAC en tiempo constante y rechaza timestamps fuera de ventana."""
    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return False
    current = int(now if now is not None else time.time())
    if abs(current - ts) > max_skew_sec:
        return False
    expected = sign_payload(secret, ts, raw_body)
    provided = (signature_header or "").strip()
    return hmac.compare_digest(expected, provided)


def _disable_endpoint(endpoint: WebhookEndpoint, *, reason: str) -> None:
    if endpoint.status == "disabled":
        return
    set_endpoint_status(endpoint, "disabled")
    try:
        from app.tenant_activity import registrar_actividad_tenant

        registrar_actividad_tenant(
            endpoint.empresa_id,
            "webhook_endpoint_auto_disabled",
            detalle=f"{endpoint.name}: {reason} (fallos={endpoint.failure_count})",
        )
    except Exception:
        pass


def _failure_threshold(empresa_id: int) -> int:
    from app.integrations.entitlements import entitlement_int

    return max(1, entitlement_int(empresa_id, "webhooks.auto_disable_after", MAX_FAILURES_BEFORE_DISABLE))


def _note_failure(endpoint: WebhookEndpoint) -> None:
    endpoint.failure_count = int(endpoint.failure_count or 0) + 1
    if endpoint.failure_count >= _failure_threshold(endpoint.empresa_id) and endpoint.status == "active":
        _disable_endpoint(endpoint, reason="fallos consecutivos")


def _retryable_status(code: int | None) -> bool:
    if code is None:
        return True
    return code in (408, 425, 429) or 500 <= code <= 599


def _schedule_retry(delivery: WebhookDelivery, *, error_code: str, http_status: int | None) -> None:
    if delivery.attempt >= MAX_ATTEMPTS:
        delivery.status = "failed"
        delivery.error_code = error_code
        delivery.http_status = http_status
        return
    delay = RETRY_DELAYS[min(delivery.attempt, len(RETRY_DELAYS) - 1)]
    delivery.status = "retry_scheduled"
    delivery.error_code = error_code
    delivery.http_status = http_status
    next_attempt = delivery.attempt + 1
    db.session.add(
        WebhookDelivery(
            empresa_id=delivery.empresa_id,
            event_id=delivery.event_id,
            endpoint_id=delivery.endpoint_id,
            attempt=next_attempt,
            status="pending",
            next_attempt_at=datetime.utcnow() + delay,
        )
    )


def deliver_once(delivery: WebhookDelivery) -> WebhookDelivery:
    endpoint = delivery.endpoint
    event = delivery.event
    if endpoint is None or event is None:
        delivery.status = "failed"
        delivery.error_code = "missing_relations"
        return delivery
    if delivery.empresa_id != endpoint.empresa_id or delivery.empresa_id != event.empresa_id:
        delivery.status = "failed"
        delivery.error_code = "tenant_mismatch"
        return delivery
    if not endpoint.active:
        delivery.status = "failed"
        delivery.error_code = "endpoint_inactive"
        return delivery

    raw_body = (event.payload_json or "").encode("utf-8")
    timestamp = int(time.time())
    secret = unseal_secret(endpoint.secret_sealed)
    signature = sign_payload(secret, timestamp, raw_body)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Roustix-Webhooks/1.0",
        "X-Roustix-Event-Id": event.public_id,
        "X-Roustix-Timestamp": str(timestamp),
        "X-Roustix-Signature": signature,
    }
    allow_http = endpoint.environment == "test"
    allow_private = endpoint.environment == "test"
    try:
        validate_webhook_url(endpoint.url, allow_http=allow_http, allow_private=allow_private)
    except WebhookError:
        delivery.status = "failed"
        delivery.error_code = "ssrf_blocked"
        _note_failure(endpoint)
        return delivery

    started = time.perf_counter()
    req = Request(endpoint.url, data=raw_body, headers=headers, method="POST")
    body_excerpt = ""
    try:
        with urlopen(req, timeout=DELIVERY_TIMEOUT_SEC) as response:
            status = int(getattr(response, "status", 200) or 200)
            body_excerpt = response.read(RESPONSE_EXCERPT_MAX).decode("utf-8", errors="replace")
    except HTTPError as exc:
        status = int(exc.code)
        try:
            body_excerpt = exc.read(RESPONSE_EXCERPT_MAX).decode("utf-8", errors="replace")
        except Exception:
            body_excerpt = ""
        duration = int((time.perf_counter() - started) * 1000)
        delivery.duration_ms = duration
        delivery.http_status = status
        delivery.response_excerpt = (body_excerpt or "")[:RESPONSE_EXCERPT_MAX]
        if _retryable_status(status):
            _schedule_retry(delivery, error_code=f"http_{status}", http_status=status)
        else:
            delivery.status = "failed"
            delivery.error_code = f"http_{status}"
        _note_failure(endpoint)
    except (URLError, TimeoutError, OSError) as exc:
        duration = int((time.perf_counter() - started) * 1000)
        delivery.duration_ms = duration
        _schedule_retry(delivery, error_code="network_error", http_status=None)
        _note_failure(endpoint)
        delivery.error_code = delivery.error_code or type(exc).__name__
    else:
        duration = int((time.perf_counter() - started) * 1000)
        delivery.duration_ms = duration
        delivery.http_status = status
        delivery.response_excerpt = (body_excerpt or "")[:RESPONSE_EXCERPT_MAX]
        if 200 <= status <= 299:
            delivery.status = "delivered"
            delivery.error_code = None
            endpoint.failure_count = 0
        elif _retryable_status(status):
            _schedule_retry(delivery, error_code=f"http_{status}", http_status=status)
            _note_failure(endpoint)
        else:
            delivery.status = "failed"
            delivery.error_code = f"http_{status}"
            _note_failure(endpoint)

    delivery.lease_expires_at = None
    delivery.updated_at = datetime.utcnow()
    db.session.flush()
    return delivery


def recover_stale_leases(*, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    stale = WebhookDelivery.query.filter(
        WebhookDelivery.status == "processing",
        WebhookDelivery.lease_expires_at.isnot(None),
        WebhookDelivery.lease_expires_at < now,
    ).all()
    for item in stale:
        item.status = "pending"
        item.lease_expires_at = None
        item.next_attempt_at = now
    db.session.flush()
    return len(stale)


def process_pending_deliveries(*, limit: int = 50) -> dict:
    now = datetime.utcnow()
    recovered = recover_stale_leases(now=now)
    due = (
        WebhookDelivery.query.filter(
            WebhookDelivery.status == "pending",
            WebhookDelivery.next_attempt_at <= now,
        )
        .order_by(WebhookDelivery.next_attempt_at.asc(), WebhookDelivery.id.asc())
        .limit(limit)
        .all()
    )
    stats = {"recovered": recovered, "claimed": 0, "delivered": 0, "failed": 0, "retry": 0}
    for delivery in due:
        delivery.status = "processing"
        delivery.lease_expires_at = now + timedelta(seconds=LEASE_SECONDS)
        stats["claimed"] += 1
    db.session.flush()
    for delivery in due:
        deliver_once(delivery)
        if delivery.status == "delivered":
            stats["delivered"] += 1
        elif delivery.status == "failed":
            stats["failed"] += 1
        else:
            stats["retry"] += 1
    db.session.commit()
    return stats


def retry_delivery(delivery: WebhookDelivery) -> WebhookDelivery:
    from app.integrations.entitlements import entitlement_bool

    if not entitlement_bool(delivery.empresa_id, "webhooks.manual_retry", False):
        raise WebhookError("El reintento manual no está habilitado para este plan.")
    if delivery.status == "delivered":
        raise WebhookError("La entrega ya fue exitosa.")
    latest_attempt = (
        WebhookDelivery.query.filter_by(
            event_id=delivery.event_id, endpoint_id=delivery.endpoint_id
        )
        .order_by(WebhookDelivery.attempt.desc())
        .first()
    )
    attempt = (latest_attempt.attempt if latest_attempt else delivery.attempt) + 1
    item = WebhookDelivery(
        empresa_id=delivery.empresa_id,
        event_id=delivery.event_id,
        endpoint_id=delivery.endpoint_id,
        attempt=attempt,
        status="pending",
        next_attempt_at=datetime.utcnow(),
    )
    db.session.add(item)
    db.session.flush()
    return item


def delivery_stats(empresa_id: int) -> dict:
    """Resumen de entregas del tenant (observabilidad)."""
    base = WebhookDelivery.query.filter_by(empresa_id=int(empresa_id))
    counts = {
        "pending": base.filter_by(status="pending").count(),
        "processing": base.filter_by(status="processing").count(),
        "delivered": base.filter_by(status="delivered").count(),
        "retry_scheduled": base.filter_by(status="retry_scheduled").count(),
        "failed": base.filter_by(status="failed").count(),
    }
    counts["total"] = sum(counts.values())
    oldest = (
        base.filter(WebhookDelivery.status.in_(("pending", "retry_scheduled", "processing")))
        .order_by(WebhookDelivery.created_at.asc())
        .first()
    )
    return {
        "counts": counts,
        "oldest_pending_at": _iso(oldest.created_at) if oldest else None,
        "endpoints_active": WebhookEndpoint.query.filter_by(
            empresa_id=int(empresa_id), status="active"
        ).count(),
    }


def prune_deliveries(empresa_id: int | None = None) -> int:
    """Elimina historial de entregas más antiguo que la retención del plan."""
    from app.integrations.entitlements import entitlement_int

    query = WebhookEndpoint.query
    if empresa_id is not None:
        query = query.filter_by(empresa_id=int(empresa_id))
    removed = 0
    for endpoint in query.all():
        days = entitlement_int(endpoint.empresa_id, "webhooks.retention_days", 14)
        cutoff = datetime.utcnow() - timedelta(days=max(1, days))
        stale = WebhookDelivery.query.filter(
            WebhookDelivery.empresa_id == endpoint.empresa_id,
            WebhookDelivery.endpoint_id == endpoint.id,
            WebhookDelivery.created_at < cutoff,
            WebhookDelivery.status.in_(("delivered", "failed", "retry_scheduled")),
        ).all()
        for row in stale:
            db.session.delete(row)
            removed += 1
    db.session.flush()
    return removed


def assert_tenant_owned(obj, empresa_id: int, *, label: str = "recurso") -> None:
    if obj is None or getattr(obj, "empresa_id", None) != int(empresa_id):
        raise WebhookError(f"{label} no encontrado.")


def serialize_endpoint(item: WebhookEndpoint) -> dict:
    return {
        "endpoint_id": item.id,
        "name": item.name,
        "url": item.url,
        "environment": item.environment,
        "events": item.events,
        "status": item.status,
        "active": item.active,
        "failure_count": item.failure_count,
        "disabled_at": _iso(item.disabled_at),
        "created_at": _iso(item.created_at),
        "updated_at": _iso(item.updated_at),
    }


def serialize_delivery(item: WebhookDelivery) -> dict:
    return {
        "delivery_id": item.id,
        "event_id": item.event.public_id if item.event else None,
        "event_type": item.event.event_type if item.event else None,
        "endpoint_id": item.endpoint_id,
        "attempt": item.attempt,
        "status": item.status,
        "http_status": item.http_status,
        "duration_ms": item.duration_ms,
        "error_code": item.error_code,
        "response_excerpt": item.response_excerpt,
        "next_attempt_at": _iso(item.next_attempt_at),
        "created_at": _iso(item.created_at),
    }
