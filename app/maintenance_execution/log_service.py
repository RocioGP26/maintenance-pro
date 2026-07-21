"""Servicios tenant-safe de bitácora contextual."""

from __future__ import annotations

from datetime import datetime

from app import db
from app.models import Incident, Machine, User, WorkOrder
from app.maintenance_execution.models import (
    MaintenanceLogAttachment,
    MaintenanceLogEntry,
    MaintenanceLogEvent,
    MaintenanceLogNotification,
)

MANAGER_ROLES = {"admin", "superadmin", "supervisor"}
ENTITY_MODELS = {"work_order": WorkOrder, "incident": Incident, "machine": Machine}


def resolve_log_context(entity_type: str, entity_id: int, empresa_id: int):
    model = ENTITY_MODELS.get(entity_type)
    if not model:
        raise ValueError("Tipo de contexto no válido.")
    entity = model.query.filter_by(id=entity_id, empresa_id=empresa_id).first()
    if not entity:
        raise ValueError("Contexto no disponible.")
    return entity


def _technician_related(user, entity_type: str, entity) -> bool:
    if user.rol != "tecnico":
        return False
    if entity_type == "work_order":
        return bool(entity.technician and entity.technician.user_id == user.id)
    if entity_type == "incident":
        return bool(entity.tecnico_asignado and entity.tecnico_asignado.user_id == user.id)
    if entity.responsable_user_id == user.id:
        return True
    if entity.responsable and entity.responsable.user_id == user.id:
        return True
    return WorkOrder.query.join(WorkOrder.technician).filter(
        WorkOrder.empresa_id == user.empresa_id,
        WorkOrder.machine_id == entity.id,
        WorkOrder.technician.has(user_id=user.id),
    ).first() is not None


def is_requester_for(user, entity_type: str, entity) -> bool:
    return bool(entity_type == "incident" and entity.user_id == user.id)


def can_view_log(user, entity_type: str, entity) -> bool:
    if not user or not user.is_authenticated or user.empresa_id != entity.empresa_id:
        return False
    return user.rol in MANAGER_ROLES or _technician_related(user, entity_type, entity) or is_requester_for(user, entity_type, entity)


def can_write_log(user, entity_type: str, entity) -> bool:
    if not user or not user.is_authenticated or user.empresa_id != entity.empresa_id:
        return False
    return bool(user.rol in MANAGER_ROLES or _technician_related(user, entity_type, entity))


def entries_for_context(user, entity_type: str, entity):
    query = MaintenanceLogEntry.query.filter_by(empresa_id=entity.empresa_id)
    query = query.filter(getattr(MaintenanceLogEntry, f"{entity_type}_id") == entity.id)
    if is_requester_for(user, entity_type, entity) and user.rol not in MANAGER_ROLES:
        query = query.filter(MaintenanceLogEntry.visibility == "requester")
    return query.order_by(MaintenanceLogEntry.created_at.desc()).all()


def create_log_entry(user, entity_type: str, entity, data):
    if not can_write_log(user, entity_type, entity):
        raise ValueError("No tienes permiso para escribir en esta bitácora.")
    body = (data.get("body") or "").strip()
    if len(body) < 2 or len(body) > 5000:
        raise ValueError("La entrada debe tener entre 2 y 5000 caracteres.")
    entry_type = (data.get("entry_type") or "comment").strip()
    if entry_type not in {"comment", "diagnosis", "action", "observation", "correction"}:
        raise ValueError("Tipo de entrada no válido.")
    visibility = (data.get("visibility") or "internal").strip()
    if visibility == "requester" and not (user.rol in MANAGER_ROLES and entity_type == "incident"):
        raise ValueError("Solo responsables autorizados pueden publicar al reportante.")
    if visibility not in {"internal", "requester"}:
        raise ValueError("Visibilidad no válida.")
    performed_by_id = user.id
    requested_performer = data.get("performed_by_user_id")
    if requested_performer and user.rol in MANAGER_ROLES:
        performer = User.query.filter_by(id=int(requested_performer), empresa_id=user.empresa_id, activo=True).first()
        if not performer:
            raise ValueError("El ejecutor no pertenece a la empresa.")
        performed_by_id = performer.id
    correction = None
    correction_id = data.get("correction_of_id")
    if correction_id:
        correction = MaintenanceLogEntry.query.filter_by(id=int(correction_id), empresa_id=user.empresa_id).first()
        if not correction or getattr(correction, f"{entity_type}_id") != entity.id:
            raise ValueError("La entrada corregida no pertenece a este contexto.")
        entry_type = "correction"
    entry = MaintenanceLogEntry(
        empresa_id=user.empresa_id, entry_type=entry_type, visibility=visibility,
        body=body, author_id=user.id, performed_by_user_id=performed_by_id,
        correction_of=correction,
    )
    setattr(entry, f"{entity_type}_id", entity.id)
    db.session.add(entry); db.session.flush()
    db.session.add(MaintenanceLogEvent(
        empresa_id=user.empresa_id, entry=entry, event="log_entry_created",
        actor_id=user.id, detail=f"{entity_type}:{entity.id} · {visibility}",
    ))
    create_log_notifications(entry, entity_type, entity)
    return entry


def _manager_recipients(entry, entity) -> list[User]:
    query = User.query.filter(
        User.empresa_id == entry.empresa_id,
        User.activo.is_(True),
        User.rol.in_(MANAGER_ROLES),
    )
    area = (getattr(entity, "area", "") or getattr(entity, "area_responsable", "") or "").strip().lower()
    users = query.all()
    if not area:
        return users
    return [
        user for user in users
        if user.rol in {"admin", "superadmin"} or (user.area or "").strip().lower() == area
    ]


def create_log_notifications(entry: MaintenanceLogEntry, entity_type: str, entity) -> list[MaintenanceLogNotification]:
    """Notifica a participantes del contexto, sin alertar al mismo autor."""
    recipients = {user.id: user for user in _manager_recipients(entry, entity)}

    technician = None
    if entity_type == "work_order":
        technician = getattr(entity, "technician", None)
    elif entity_type == "incident":
        technician = getattr(entity, "tecnico_asignado", None)
        requester = getattr(entity, "usuario", None)
        if entry.visibility == "requester" and requester:
            recipients[requester.id] = requester
    else:
        technician = getattr(entity, "responsable", None)
        responsible_user = getattr(entity, "responsable_usuario", None)
        if responsible_user:
            recipients[responsible_user.id] = responsible_user

    technician_user = getattr(technician, "user", None)
    if technician_user and technician_user.activo:
        recipients[technician_user.id] = technician_user

    notifications = []
    for recipient_id in sorted(recipients):
        if recipient_id == entry.author_id:
            continue
        item = MaintenanceLogNotification(
            empresa_id=entry.empresa_id,
            entry=entry,
            user_id=recipient_id,
        )
        db.session.add(item)
        notifications.append(item)
    return notifications


def unread_log_notifications(user) -> list[MaintenanceLogNotification]:
    if not user or not user.is_authenticated or not user.empresa_id:
        return []
    return MaintenanceLogNotification.query.filter_by(
        empresa_id=user.empresa_id, user_id=user.id, read_at=None
    ).order_by(MaintenanceLogNotification.created_at.desc()).all()


def log_notifications_for_user(user) -> list[MaintenanceLogNotification]:
    if not user or not user.is_authenticated or not user.empresa_id:
        return []
    return MaintenanceLogNotification.query.filter_by(
        empresa_id=user.empresa_id, user_id=user.id
    ).order_by(MaintenanceLogNotification.created_at.desc()).limit(100).all()


def mark_log_notification_read(notification: MaintenanceLogNotification, user) -> None:
    if notification.empresa_id != user.empresa_id or notification.user_id != user.id:
        raise ValueError("Notificación no disponible.")
    notification.read_at = notification.read_at or datetime.utcnow()
    db.session.add(MaintenanceLogEvent(
        empresa_id=notification.empresa_id,
        entry=notification.entry,
        event="log_notification_read",
        actor_id=user.id,
        detail=f"notification:{notification.id}",
    ))


def attach_log_file(entry, actor_id: int, metadata):
    attachment = MaintenanceLogAttachment(
        empresa_id=entry.empresa_id, entry=entry, uploaded_by_id=actor_id,
        storage_key=metadata["storage_key"], original_name=metadata["original_name"],
        mime_type=metadata["mime_type"], size_bytes=metadata["size_bytes"],
        checksum_sha256=metadata["checksum"],
    )
    db.session.add(attachment)
    db.session.add(MaintenanceLogEvent(
        empresa_id=entry.empresa_id, entry=entry, event="log_attachment_uploaded",
        actor_id=actor_id, detail=attachment.original_name[:500],
    ))
    return attachment


def audit_log_access(entry, actor_id: int, event: str, detail: str):
    db.session.add(MaintenanceLogEvent(
        empresa_id=entry.empresa_id, entry=entry, event=event,
        actor_id=actor_id, detail=(detail or "")[:500], created_at=datetime.utcnow(),
    ))
