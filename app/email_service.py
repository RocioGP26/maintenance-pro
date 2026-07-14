"""Envío mínimo de correo transaccional mediante SMTP configurable."""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app


class EmailDeliveryError(RuntimeError):
    """El proveedor SMTP no pudo aceptar el mensaje."""


def send_templated_email(
    *,
    recipient: str,
    subject: str,
    template_name: str,
    context: dict,
) -> None:
    """Renderiza y envía las variantes texto/HTML de un correo."""
    app = current_app
    # Render directo: los correos también pueden enviarse desde tareas sin request.
    text_body = app.jinja_env.get_template(f"emails/{template_name}.txt").render(**context)
    html_body = app.jinja_env.get_template(f"emails/{template_name}.html").render(**context)

    message = EmailMessage()
    message["Subject"] = subject
    message["To"] = recipient
    message["From"] = app.config.get("MAIL_DEFAULT_SENDER") or app.config.get("MAIL_USERNAME")
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

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
            server,
            int(app.config.get("MAIL_PORT", 587)),
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
