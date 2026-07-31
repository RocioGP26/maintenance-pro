"""Outbox cifrada para correo transaccional y entrega mediante SMTP."""

from __future__ import annotations

import base64
import hashlib
import json
import smtplib
import ssl
from datetime import datetime, timedelta
from email.message import EmailMessage

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

from app import db
from app.models import EmailOutbox, EmailVerification, PasswordReset


RETRY_DELAYS = (
    timedelta(minutes=1), timedelta(minutes=5), timedelta(minutes=15),
    timedelta(hours=1), timedelta(hours=4),
)


class EmailDeliveryError(RuntimeError):
    """El proveedor SMTP no pudo aceptar el mensaje."""


class EmailPayloadError(RuntimeError):
    """El contenido cifrado de la outbox no pudo autenticarse."""


def _fernet_for_secret(root_secret: str) -> Fernet:
    digest = hashlib.sha256(f"roustix:email-outbox:v1:{root_secret}".encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _fernet() -> Fernet:
    configured = str(current_app.config.get("OUTBOX_ENCRYPTION_KEY") or "")
    root_secret = configured or str(current_app.config.get("SECRET_KEY") or "")
    return _fernet_for_secret(root_secret)


def _seal_payload(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(raw).decode("ascii")


def _unseal_payload(value: str) -> dict:
    token = (value or "").encode("ascii")
    configured = str(current_app.config.get("OUTBOX_ENCRYPTION_KEY") or "")
    candidates = [_fernet()]
    # Durante la adopción de una clave dedicada, conserva lectura de sobres
    # pendientes creados con la derivación histórica de SECRET_KEY.
    if configured:
        candidates.append(
            _fernet_for_secret(str(current_app.config.get("SECRET_KEY") or ""))
        )
    raw = None
    for candidate in candidates:
        try:
            raw = candidate.decrypt(token)
            break
        except InvalidToken:
            continue
    try:
        if raw is None:
            raise InvalidToken
        payload = json.loads(raw.decode("utf-8"))
    except (InvalidToken, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise EmailPayloadError("El sobre de correo no es válido o fue alterado.") from exc
    if not isinstance(payload, dict):
        raise EmailPayloadError("El sobre de correo no contiene un objeto válido.")
    return payload


def _build_message(payload: dict) -> EmailMessage:
    required = ("recipient", "subject", "sender", "text_body", "html_body")
    if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
        raise EmailPayloadError("El sobre de correo está incompleto.")
    message = EmailMessage()
    message["Subject"] = payload["subject"]
    message["To"] = payload["recipient"]
    message["From"] = payload["sender"]
    message.set_content(payload["text_body"])
    message.add_alternative(payload["html_body"], subtype="html")
    return message


def _deliver_message(message: EmailMessage) -> None:
    app = current_app
    if app.config.get("MAIL_SUPPRESS_SEND"):
        app.extensions.setdefault("mail_outbox", []).append(message)
        return
    server = app.config.get("MAIL_SERVER")
    username = app.config.get("MAIL_USERNAME")
    password = app.config.get("MAIL_PASSWORD")
    if not server or not username or not password or not message["From"]:
        raise EmailDeliveryError(
            "Configura MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD y MAIL_DEFAULT_SENDER."
        )
    try:
        with smtplib.SMTP(
            server, int(app.config.get("MAIL_PORT", 587)),
            timeout=int(app.config.get("MAIL_TIMEOUT_SECONDS", 10)),
        ) as smtp:
            smtp.ehlo()
            if app.config.get("MAIL_USE_TLS", True):
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("No fue posible entregar el correo mediante SMTP.") from exc


def _mark_source_sent(item: EmailOutbox, sent_at: datetime) -> None:
    source = None
    if item.source_type == "email_verification":
        source = db.session.get(EmailVerification, item.source_id)
    elif item.source_type == "password_reset":
        source = db.session.get(PasswordReset, item.source_id)
    if source is not None and source.empresa_id == item.empresa_id:
        source.sent_at = sent_at


def deliver_email_once(item: EmailOutbox) -> EmailOutbox:
    """Realiza un intento y deja el estado listo para commit del llamador."""
    item.attempts = int(item.attempts or 0) + 1
    try:
        _deliver_message(_build_message(_unseal_payload(item.payload_sealed)))
    except (EmailDeliveryError, EmailPayloadError) as exc:
        item.lease_expires_at = None
        item.last_error = type(exc).__name__[:120]
        if item.attempts >= item.max_attempts or isinstance(exc, EmailPayloadError):
            item.status = "failed"
        else:
            item.status = "pending"
            delay = RETRY_DELAYS[min(item.attempts - 1, len(RETRY_DELAYS) - 1)]
            item.next_attempt_at = datetime.utcnow() + delay
        return item
    sent_at = datetime.utcnow()
    item.status = "sent"
    item.sent_at = sent_at
    item.lease_expires_at = None
    item.last_error = None
    _mark_source_sent(item, sent_at)
    return item


def send_templated_email(
    *, empresa_id: int, recipient: str, subject: str, template_name: str,
    context: dict, idempotency_key: str, source_type: str | None = None,
    source_id: int | None = None,
) -> EmailOutbox:
    """Renderiza y encola una sola vez el correo, sin persistir secretos en claro."""
    existing = EmailOutbox.query.filter_by(
        empresa_id=int(empresa_id), idempotency_key=idempotency_key
    ).first()
    if existing is not None:
        return existing
    app = current_app
    text_body = app.jinja_env.get_template(f"emails/{template_name}.txt").render(**context)
    html_body = app.jinja_env.get_template(f"emails/{template_name}.html").render(**context)
    sender = app.config.get("MAIL_DEFAULT_SENDER") or app.config.get("MAIL_USERNAME")
    if not sender:
        raise EmailDeliveryError("Configura MAIL_DEFAULT_SENDER o MAIL_USERNAME.")
    item = EmailOutbox(
        empresa_id=int(empresa_id), kind=template_name[:40],
        idempotency_key=idempotency_key[:160],
        payload_sealed=_seal_payload({
            "recipient": recipient, "subject": subject, "sender": sender,
            "text_body": text_body, "html_body": html_body,
        }),
        max_attempts=max(1, int(app.config.get("EMAIL_OUTBOX_MAX_ATTEMPTS", 5))),
        source_type=source_type, source_id=source_id,
    )
    db.session.add(item)
    db.session.flush()
    if app.testing and app.config.get("EMAIL_OUTBOX_SYNC_IN_TESTS", True):
        item.status = "processing"
        deliver_email_once(item)
    return item


def recover_stale_email_leases(*, now: datetime | None = None) -> int:
    now = now or datetime.utcnow()
    stale = EmailOutbox.query.filter(
        EmailOutbox.status == "processing", EmailOutbox.lease_expires_at.isnot(None),
        EmailOutbox.lease_expires_at < now,
    ).all()
    for item in stale:
        item.status = "pending"
        item.lease_expires_at = None
        item.next_attempt_at = now
    db.session.flush()
    return len(stale)


def process_pending_emails(*, limit: int = 50) -> dict:
    """Reclama un lote apto para múltiples workers y procesa cada correo."""
    now = datetime.utcnow()
    recovered = recover_stale_email_leases(now=now)
    query = (EmailOutbox.query.filter(
        EmailOutbox.status == "pending", EmailOutbox.next_attempt_at <= now,
    ).order_by(EmailOutbox.next_attempt_at.asc(), EmailOutbox.id.asc()).limit(max(1, limit)))
    if db.session.get_bind().dialect.name != "sqlite":
        query = query.with_for_update(skip_locked=True)
    due = query.all()
    lease_seconds = max(15, int(current_app.config.get("EMAIL_OUTBOX_LEASE_SECONDS", 60)))
    for item in due:
        item.status = "processing"
        item.lease_expires_at = now + timedelta(seconds=lease_seconds)
    claimed_ids = [item.id for item in due]
    db.session.commit()
    stats = {"email_recovered": recovered, "email_claimed": len(claimed_ids),
             "email_sent": 0, "email_failed": 0, "email_retry": 0}
    for item_id in claimed_ids:
        item = db.session.get(EmailOutbox, item_id)
        if item is None or item.status != "processing":
            continue
        deliver_email_once(item)
        db.session.commit()
        if item.status == "sent":
            stats["email_sent"] += 1
        elif item.status == "failed":
            stats["email_failed"] += 1
        else:
            stats["email_retry"] += 1
        if item.status in {"pending", "failed"}:
            from app.observability import emit_operational_alert
            event = "delivery_failed" if item.status == "failed" else "delivery_retry_scheduled"
            emit_operational_alert(
                "smtp", event,
                "Transactional email delivery failed" if item.status == "failed"
                else "Transactional email delivery retry scheduled",
                context={"delivery_id": item.id},
                dedupe_key=f"smtp:outbox:{item.id}",
            )
    return stats


def prune_email_outbox(*, now: datetime | None = None) -> int:
    """Elimina sobres terminales antiguos para minimizar datos sensibles."""
    now = now or datetime.utcnow()
    retention_days = max(
        1, int(current_app.config.get("EMAIL_OUTBOX_RETENTION_DAYS", 30))
    )
    cutoff = now - timedelta(days=retention_days)
    removed = EmailOutbox.query.filter(
        EmailOutbox.status.in_(("sent", "failed")),
        EmailOutbox.updated_at < cutoff,
    ).delete(synchronize_session=False)
    db.session.flush()
    return int(removed or 0)
