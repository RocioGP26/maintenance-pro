"""Observabilidad HTTP, métricas y eventos operativos de Roustix."""

from __future__ import annotations

import hmac
import logging
import re
import secrets
import smtplib
import ssl
import threading
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime

from flask import abort, current_app, g, got_request_exception, request
from flask_login import current_user

from app.timezone_utils import timezone_obj
from app.version import __version__, get_build_commit


REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
logger = logging.getLogger("app.observability")
_alert_lock = threading.Lock()
_last_alert: dict[str, float] = {}


def request_id() -> str:
    value = getattr(g, "request_id", None)
    if value:
        return str(value)
    value = f"req_{secrets.token_hex(12)}"
    g.request_id = value
    return value


def _request_context() -> dict:
    user_id = None
    empresa_id = None
    try:
        if current_user.is_authenticated:
            user_id = getattr(current_user, "id", None)
            empresa_id = getattr(current_user, "empresa_id", None)
    except Exception:
        pass
    return {
        "request_id": getattr(g, "request_id", None),
        "empresa_id": empresa_id,
        "user_id": user_id,
        "path": request.path,
        "method": request.method,
        "endpoint": request.endpoint or "unmatched",
    }


def _scrub_sentry_event(event, _hint):
    request_data = event.get("request") or {}
    request_data.pop("data", None)
    request_data.pop("cookies", None)
    headers = request_data.get("headers") or {}
    for key in list(headers):
        if key.lower() in {"authorization", "cookie", "x-platform-key", "x-api-key"}:
            headers[key] = "[Filtered]"
    user = event.get("user")
    if isinstance(user, dict):
        event["user"] = {"id": user.get("id")}
    return event


def _init_sentry(app) -> bool:
    dsn = (app.config.get("SENTRY_DSN") or "").strip()
    if not dsn:
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
    except ImportError:
        app.logger.error("SENTRY_DSN configurado pero sentry-sdk no está instalado.")
        return False

    commit = get_build_commit() or "local"
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration(transaction_style="endpoint")],
        environment=app.config.get("ROUSTIX_ENV", "development"),
        release=f"roustix@{__version__}+{commit}",
        traces_sample_rate=float(app.config.get("SENTRY_TRACES_SAMPLE_RATE", 0.1)),
        send_default_pii=False,
        max_request_body_size="never",
        before_send=_scrub_sentry_event,
    )
    return True


def _send_support_email(component: str, event: str, message: str, severity: str) -> None:
    """Envía un aviso mínimo sin incluir datos del cliente ni secretos."""
    recipient = (current_app.config.get("OPS_ALERT_EMAIL") or "").strip()
    sender = (
        current_app.config.get("MAIL_DEFAULT_SENDER")
        or current_app.config.get("MAIL_USERNAME")
        or ""
    ).strip()
    server = (current_app.config.get("MAIL_SERVER") or "").strip()
    username = (current_app.config.get("MAIL_USERNAME") or "").strip()
    password = current_app.config.get("MAIL_PASSWORD") or ""
    if not all((recipient, sender, server, username, password)):
        return

    email = EmailMessage()
    email["Subject"] = f"[Roustix][{severity.upper()}] {component}: {event}"
    email["From"] = sender
    email["To"] = recipient
    local_tz = timezone_obj(tz_name=current_app.config.get("OPS_TIMEZONE"))
    local_now = datetime.now(local_tz)
    email["Date"] = format_datetime(local_now)
    email.set_content(
        "Se detectó un evento operativo en Roustix.\n\n"
        f"Componente: {component}\nEvento: {event}\nSeveridad: {severity}\n"
        f"Fecha Colombia: {local_now.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
        f"Detalle: {message}\n\n"
        "Consulte los logs centralizados usando el componente y el evento."
    )
    try:
        with smtplib.SMTP(
            server,
            int(current_app.config.get("MAIL_PORT", 587)),
            timeout=int(current_app.config.get("MAIL_TIMEOUT_SECONDS", 10)),
        ) as smtp:
            smtp.ehlo()
            if current_app.config.get("MAIL_USE_TLS", True):
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(email)
    except (OSError, UnicodeError, ValueError, smtplib.SMTPException):
        logger.exception(
            "Operational support email delivery failed",
            extra={"component": "smtp", "event": "ops_alert_delivery_failed"},
        )


def emit_operational_alert(
    component: str,
    event: str,
    message: str,
    *,
    severity: str = "error",
    exc: Exception | None = None,
    context: dict | None = None,
    dedupe_key: str | None = None,
) -> bool:
    """Registra y centraliza una alerta evitando tormentas dentro del proceso."""
    key = dedupe_key or f"{component}:{event}"
    cooldown = max(0, int(current_app.config.get("OPS_ALERT_COOLDOWN_SECONDS", 300)))
    now = time.monotonic()
    with _alert_lock:
        previous = _last_alert.get(key, 0.0)
        if cooldown and now - previous < cooldown:
            return False
        _last_alert[key] = now

    extra = {
        "component": component,
        "event": event,
        "severity": severity,
        "error_type": type(exc).__name__ if exc else None,
    }
    if context:
        for allowed in ("empresa_id", "endpoint_id", "delivery_id", "status_code"):
            if allowed in context:
                extra[allowed] = context[allowed]
    exc_info = (type(exc), exc, exc.__traceback__) if exc else None
    log_level = logging.WARNING if severity == "warning" else logging.ERROR
    logger.log(log_level, message, exc_info=exc_info, extra=extra)

    if current_app.extensions.get("sentry_enabled"):
        try:
            import sentry_sdk

            with sentry_sdk.push_scope() as scope:
                scope.set_tag("component", component)
                scope.set_tag("operational_event", event)
                scope.set_level(severity)
                if context:
                    scope.set_context("operation", {
                        key: value for key, value in context.items()
                        if key in {"empresa_id", "endpoint_id", "delivery_id", "status_code"}
                    })
                if exc:
                    sentry_sdk.capture_exception(exc)
                else:
                    sentry_sdk.capture_message(message, level=severity)
        except Exception:
            logger.exception("No fue posible publicar la alerta en Sentry.")
    # Un fallo del propio SMTP no se reenvía por el mismo canal; permanece en
    # logs/Sentry para evitar recursión y tormentas de conexión.
    if component != "smtp":
        _send_support_email(component, event, message, severity)
    return True


def register_observability(app) -> None:
    """Instala correlación, logging HTTP, Sentry y métricas Prometheus."""
    app.extensions["sentry_enabled"] = _init_sentry(app)

    try:
        from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

        registry = CollectorRegistry()
        http_requests = Counter(
            "roustix_http_requests_total",
            "Solicitudes HTTP procesadas.",
            ("method", "endpoint", "status"),
            registry=registry,
        )
        http_latency = Histogram(
            "roustix_http_request_duration_seconds",
            "Latencia HTTP por endpoint.",
            ("method", "endpoint"),
            buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
            registry=registry,
        )
        unhandled = Counter(
            "roustix_unhandled_exceptions_total",
            "Excepciones no controladas.",
            ("endpoint", "exception"),
            registry=registry,
        )
        build = Gauge(
            "roustix_build_info",
            "Versión desplegada de Roustix.",
            ("version", "commit", "environment"),
            registry=registry,
        )
        build.labels(
            __version__, get_build_commit() or "local", app.config.get("ROUSTIX_ENV", "development")
        ).set(1)
        app.extensions["prometheus"] = {
            "registry": registry,
            "requests": http_requests,
            "latency": http_latency,
            "exceptions": unhandled,
        }
    except ImportError:
        app.extensions["prometheus"] = None
        app.logger.warning("prometheus-client no está instalado; métricas desactivadas.")

    @app.before_request
    def _start_observed_request():
        supplied = (request.headers.get("X-Request-Id") or "").strip()
        g.request_id = supplied if REQUEST_ID_RE.fullmatch(supplied) else f"req_{secrets.token_hex(12)}"
        g.request_started_at = time.perf_counter()

    @app.after_request
    def _finish_observed_request(response):
        elapsed = max(0.0, time.perf_counter() - getattr(g, "request_started_at", time.perf_counter()))
        endpoint = request.endpoint or "unmatched"
        response.headers["X-Request-Id"] = request_id()
        metrics = app.extensions.get("prometheus")
        if metrics and endpoint != "observability_metrics":
            metrics["requests"].labels(request.method, endpoint, str(response.status_code)).inc()
            metrics["latency"].labels(request.method, endpoint).observe(elapsed)
        if endpoint != "static" and endpoint != "observability_metrics":
            level = logging.ERROR if response.status_code >= 500 else logging.INFO
            logger.log(
                level,
                "HTTP request completed",
                extra={
                    **_request_context(),
                    "status_code": response.status_code,
                    "duration_ms": round(elapsed * 1000, 2),
                    "event": "http_request_completed",
                },
            )
        return response

    def _on_exception(_sender, exception, **_extra):
        metrics = app.extensions.get("prometheus")
        endpoint = request.endpoint or "unmatched"
        if metrics:
            metrics["exceptions"].labels(endpoint, type(exception).__name__).inc()
        logger.error(
            "Unhandled request exception",
            exc_info=(type(exception), exception, exception.__traceback__),
            extra={**_request_context(), "event": "unhandled_exception", "error_type": type(exception).__name__},
        )

    got_request_exception.connect(_on_exception, app, weak=False)

    def metrics_view():
        token = (current_app.config.get("METRICS_TOKEN") or "").strip()
        if not token:
            abort(404)
        supplied = (request.headers.get("X-Metrics-Token") or "").strip()
        if not hmac.compare_digest(supplied, token):
            abort(403)
        metrics = current_app.extensions.get("prometheus")
        if not metrics:
            abort(503)
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        return current_app.response_class(
            generate_latest(metrics["registry"]), content_type=CONTENT_TYPE_LATEST
        )

    app.add_url_rule("/internal/metrics", "observability_metrics", metrics_view, methods=["GET"])
