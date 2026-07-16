"""Enrutamiento y consulta de notificaciones individuales de incidencias."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import joinedload

from app import db
from app.models import (
    INCIDENT_ESTADO_LABELS,
    Incident,
    IncidentHistory,
    IncidentNotification,
    User,
)
from app.permissions import can_receive_incident_notification, is_technician


AUDIENCE_AREA = "area"
AUDIENCE_REPORTER = "reporter"


def create_incident_notifications(
    incident: Incident,
    *,
    event_key: str = "area_reported",
    event_type: str = "reported",
    title: str = "Nueva incidencia reportada",
) -> list[IncidentNotification]:
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
            IncidentNotification.event_key == event_key,
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
            audience=AUDIENCE_AREA,
            event_key=event_key,
            event_type=event_type,
            title=title,
            message=(
                f"{incident.numero or ('INC-' + str(incident.id))} fue asignada al área "
                f"{incident.area_responsable}."
            ),
            status_snapshot=incident.estado or "reportado",
        )
        db.session.add(item)
        created.append(item)
    return created


def create_reporter_status_notification(
    incident: Incident,
    *,
    previous_status: str,
    new_status: str,
    action: str,
    actor_user_id: int | None,
) -> IncidentNotification | None:
    """Notifica al autor del ticket cuando otra persona modifica su estado."""
    if (
        not incident.id
        or not incident.empresa_id
        or not incident.user_id
        or previous_status == new_status
        or actor_user_id == incident.user_id
    ):
        return None
    reporter = db.session.get(User, incident.user_id)
    if (
        reporter is None
        or reporter.empresa_id != incident.empresa_id
        or not reporter.activo
        or reporter.bloqueado
    ):
        return None

    code = incident.numero or f"INC-{incident.id}"
    previous_label = INCIDENT_ESTADO_LABELS.get(previous_status, previous_status)
    new_label = INCIDENT_ESTADO_LABELS.get(new_status, new_status)
    if new_status == "cerrado":
        title = "Tu ticket fue cerrado"
    elif new_status == "resuelto":
        title = "Tu ticket fue resuelto"
    elif action == "reabierto":
        title = "Tu ticket fue reabierto"
    else:
        title = "Tu ticket cambió de estado"
    item = IncidentNotification(
        empresa_id=incident.empresa_id,
        incident_id=incident.id,
        user=reporter,
        audience=AUDIENCE_REPORTER,
        event_key=f"status:{new_status}:{uuid4()}",
        event_type="status_changed",
        title=title,
        message=f"{code}: {previous_label} → {new_label}.",
        status_snapshot=new_status,
    )
    db.session.add(item)
    return item


def create_technician_assignment_notification(
    incident: Incident, *, technician_user: User
) -> IncidentNotification | None:
    """Notifica al tecnico concreto cuando una incidencia queda a su cargo."""
    if (
        not incident.id
        or not incident.empresa_id
        or technician_user is None
        or technician_user.empresa_id != incident.empresa_id
        or not technician_user.activo
        or technician_user.bloqueado
    ):
        return None
    existing = IncidentNotification.query.filter_by(
        incident_id=incident.id,
        user_id=technician_user.id,
        event_key=f"technician_assigned:{incident.tecnico_asignado_id}",
    ).first()
    if existing:
        return existing
    item = IncidentNotification(
        empresa_id=incident.empresa_id,
        incident_id=incident.id,
        user=technician_user,
        audience=AUDIENCE_AREA,
        event_key=f"technician_assigned:{incident.tecnico_asignado_id}",
        event_type="technician_assigned",
        title="Nueva incidencia asignada",
        message=f"{incident.numero or ('INC-' + str(incident.id))} fue asignada a tu bandeja.",
        status_snapshot=incident.estado or "asignado",
    )
    db.session.add(item)
    return item


def can_access_notification(user: User, item: IncidentNotification) -> bool:
    if (
        user is None
        or not user.activo
        or user.bloqueado
        or item.empresa_id != user.empresa_id
        or item.user_id != user.id
    ):
        return False
    if item.audience == AUDIENCE_REPORTER:
        return item.incident.user_id == user.id
    if is_technician(user):
        technician = getattr(user, "technician", None)
        return bool(
            technician
            and item.incident.tecnico_asignado_id == technician.id
        )
    return can_receive_incident_notification(user, item.incident.area_responsable)


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
        if can_access_notification(user, item)
    ]


def notification_for_user(notification_id: int, user: User) -> IncidentNotification | None:
    item = (
        IncidentNotification.query.filter(
            IncidentNotification.id == notification_id,
            IncidentNotification.empresa_id == user.empresa_id,
            IncidentNotification.user_id == user.id,
        ).first()
    )
    if item is None or not can_access_notification(user, item):
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
