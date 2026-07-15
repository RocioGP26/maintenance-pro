"""Enrutamiento y consulta de notificaciones individuales de incidencias."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import joinedload

from app import db
from app.models import Incident, IncidentHistory, IncidentNotification, User
from app.permissions import can_receive_incident_notification


def create_incident_notifications(incident: Incident) -> list[IncidentNotification]:
    """Crea una entrega por destinatario activo, autorizado y de la misma área."""
    if not incident.id or not incident.empresa_id or not incident.area_responsable:
        return []

    candidates = User.query.filter_by(
        empresa_id=incident.empresa_id,
        activo=True,
        bloqueado=False,
    ).all()
    recipients = [
        user
        for user in candidates
        if can_receive_incident_notification(user, incident.area_responsable)
    ]
    if not recipients:
        return []

    existing_user_ids = {
        row[0]
        for row in db.session.query(IncidentNotification.user_id)
        .filter(
            IncidentNotification.incident_id == incident.id,
            IncidentNotification.user_id.in_([user.id for user in recipients]),
        )
        .all()
    }
    created = []
    for user in recipients:
        if user.id in existing_user_ids:
            continue
        item = IncidentNotification(
            empresa_id=incident.empresa_id,
            incident_id=incident.id,
            user=user,
        )
        db.session.add(item)
        created.append(item)
    return created


def unread_notifications_for(user: User):
    """Consulta tenant-safe: empresa y usuario forman parte obligatoria del alcance."""
    return (
        IncidentNotification.query.options(
            joinedload(IncidentNotification.incident).joinedload(Incident.machine)
        )
        .filter(
            IncidentNotification.empresa_id == user.empresa_id,
            IncidentNotification.user_id == user.id,
            IncidentNotification.read_at.is_(None),
        )
    )


def authorized_unread_notifications(user: User) -> list[IncidentNotification]:
    return [
        item
        for item in unread_notifications_for(user)
        .order_by(IncidentNotification.created_at.desc())
        .all()
        if can_receive_incident_notification(user, item.incident.area_responsable)
    ]


def notification_for_user(notification_id: int, user: User) -> IncidentNotification | None:
    item = (
        IncidentNotification.query.filter(
            IncidentNotification.id == notification_id,
            IncidentNotification.empresa_id == user.empresa_id,
            IncidentNotification.user_id == user.id,
        ).first()
    )
    if item is None or not can_receive_incident_notification(
        user, item.incident.area_responsable
    ):
        return None
    return item


def mark_notification_shown(item: IncidentNotification) -> None:
    if item.shown_at is None:
        item.shown_at = datetime.utcnow()


def mark_notification_read(
    item: IncidentNotification, *, accessed: bool = False
) -> None:
    now = datetime.utcnow()
    if item.shown_at is None:
        item.shown_at = now
    if item.read_at is None:
        item.read_at = now
        db.session.add(
            IncidentHistory(
                incident_id=item.incident_id,
                user_id=item.user_id,
                accion="notificacion_leida",
                comentario="Notificación de incidencia marcada como vista.",
            )
        )
    if accessed:
        item.accessed_at = now
        db.session.add(
            IncidentHistory(
                incident_id=item.incident_id,
                user_id=item.user_id,
                accion="acceso_desde_notificacion",
                comentario="Acceso al detalle desde la alerta de incidencia.",
            )
        )
