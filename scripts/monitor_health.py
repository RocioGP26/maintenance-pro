"""Monitor externo mínimo para liveness/readiness de Roustix.

Diseñado para ejecutarse fuera de Render (GitHub Actions durante el piloto).
No imprime secretos ni cuerpos de respuesta completos.
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class HealthResult:
    endpoint: str
    ok: bool
    status_code: int | None
    status: str
    error: str | None = None


def check_endpoint(base_url: str, endpoint: str, *, timeout: int = 15) -> HealthResult:
    url = urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
    request = Request(url, headers={"User-Agent": "Roustix-Uptime-Monitor/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - URL controlada
            status_code = int(response.status)
            payload = json.loads(response.read(64 * 1024).decode("utf-8"))
        status = str(payload.get("status") or "unknown")
        return HealthResult(
            endpoint=endpoint,
            ok=status_code == 200 and status == "ok",
            status_code=status_code,
            status=status,
        )
    except HTTPError as exc:
        return HealthResult(endpoint, False, int(exc.code), "error", type(exc).__name__)
    except (URLError, OSError, ValueError, json.JSONDecodeError) as exc:
        return HealthResult(endpoint, False, None, "error", type(exc).__name__)


def send_failure_email(results: list[HealthResult]) -> bool:
    recipient = os.environ.get("OPS_ALERT_EMAIL", "").strip()
    server = os.environ.get("MAIL_SERVER", "").strip()
    username = os.environ.get("MAIL_USERNAME", "").strip()
    password = os.environ.get("MAIL_PASSWORD", "")
    sender = (os.environ.get("MAIL_DEFAULT_SENDER") or username).strip()
    if not all((recipient, server, username, password, sender)):
        return False

    message = EmailMessage()
    message["Subject"] = "[Roustix][ERROR] Monitor externo de disponibilidad"
    message["From"] = sender
    message["To"] = recipient
    local_now = datetime.now(ZoneInfo(os.environ.get("OPS_TIMEZONE", "America/Bogota")))
    message["Date"] = format_datetime(local_now)
    lines = [
        "El monitor externo detectó un estado no saludable.",
        f"Fecha Colombia: {local_now.strftime('%Y-%m-%d %H:%M:%S %z')}",
        "",
    ]
    for result in results:
        lines.append(
            f"{result.endpoint}: status={result.status}; "
            f"http={result.status_code}; error={result.error or '-'}"
        )
    message.set_content("\n".join(lines))

    try:
        with smtplib.SMTP(server, int(os.environ.get("MAIL_PORT") or "587"), timeout=15) as smtp:
            smtp.ehlo()
            if os.environ.get("MAIL_USE_TLS", "true").lower() not in {"0", "false", "no"}:
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
        return True
    except (OSError, UnicodeError, ValueError, smtplib.SMTPException):
        return False


def check_with_retries(
    base_url: str,
    endpoint: str,
    *,
    attempts: int = 3,
    delay_seconds: int = 5,
) -> HealthResult:
    result = HealthResult(endpoint, False, None, "error", "not_checked")
    for attempt in range(max(1, attempts)):
        result = check_endpoint(base_url, endpoint)
        if result.ok:
            return result
        if attempt + 1 < attempts:
            time.sleep(max(0, delay_seconds))
    return result


def run(base_url: str) -> list[HealthResult]:
    return [
        check_with_retries(base_url, "/health/live"),
        check_with_retries(base_url, "/health/ready"),
    ]


def main() -> int:
    base_url = os.environ.get("ROUSTIX_BASE_URL", "https://roustix.com").strip()
    results = run(base_url)
    for result in results:
        print(
            f"{result.endpoint}: ok={str(result.ok).lower()} "
            f"status={result.status} http={result.status_code}"
        )
    failures = [result for result in results if not result.ok]
    if not failures:
        return 0
    delivered = send_failure_email(failures)
    print(f"operational_alert_delivered={str(delivered).lower()}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
