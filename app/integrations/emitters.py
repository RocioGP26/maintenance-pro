"""Emisores de dominio hacia el outbox de webhooks."""

from __future__ import annotations

from app.integrations.webhooks import emit_event
from app.models import WorkOrderStatus


def emit_incident_created(incident) -> None:
    emit_event(
        empresa_id=incident.empresa_id,
        event_type="incident.created",
        resource_type="incident",
        resource_id=incident.id,
        data={
            "incident_id": incident.id,
            "number": incident.numero,
            "status": incident.estado or "reportado",
            "asset_id": incident.machine_id,
            "priority": incident.prioridad,
            "type": incident.tipo,
        },
    )


def emit_incident_status_changed(incident, *, previous_status: str, new_status: str) -> None:
    if (previous_status or "") == (new_status or ""):
        return
    emit_event(
        empresa_id=incident.empresa_id,
        event_type="incident.status_changed",
        resource_type="incident",
        resource_id=incident.id,
        data={
            "incident_id": incident.id,
            "number": incident.numero,
            "previous_status": previous_status,
            "status": new_status,
            "asset_id": incident.machine_id,
        },
    )


def emit_work_order_created(order) -> None:
    emit_event(
        empresa_id=order.empresa_id,
        event_type="work_order.created",
        resource_type="work_order",
        resource_id=order.id,
        data={
            "work_order_id": order.id,
            "number": order.numero,
            "status": order.status,
            "asset_id": order.machine_id,
            "technician_id": order.technician_id,
        },
    )


def emit_work_order_assigned(order, *, previous_technician_id: int | None) -> None:
    if previous_technician_id == order.technician_id:
        return
    emit_event(
        empresa_id=order.empresa_id,
        event_type="work_order.assigned",
        resource_type="work_order",
        resource_id=order.id,
        data={
            "work_order_id": order.id,
            "number": order.numero,
            "asset_id": order.machine_id,
            "previous_technician_id": previous_technician_id,
            "technician_id": order.technician_id,
            "status": order.status,
        },
    )


def emit_work_order_status_changed(order, *, previous_status: str) -> None:
    new_status = (order.status or "").strip().lower()
    previous = (previous_status or "").strip().lower()
    if previous == new_status:
        return
    emit_event(
        empresa_id=order.empresa_id,
        event_type="work_order.status_changed",
        resource_type="work_order",
        resource_id=order.id,
        data={
            "work_order_id": order.id,
            "number": order.numero,
            "asset_id": order.machine_id,
            "previous_status": previous,
            "status": new_status,
        },
    )
    if new_status == WorkOrderStatus.COMPLETADO.value:
        emit_event(
            empresa_id=order.empresa_id,
            event_type="work_order.completed",
            resource_type="work_order",
            resource_id=order.id,
            data={
                "work_order_id": order.id,
                "number": order.numero,
                "asset_id": order.machine_id,
                "status": new_status,
            },
        )
    elif new_status == WorkOrderStatus.CERRADA.value:
        emit_event(
            empresa_id=order.empresa_id,
            event_type="work_order.closed",
            resource_type="work_order",
            resource_id=order.id,
            data={
                "work_order_id": order.id,
                "number": order.numero,
                "asset_id": order.machine_id,
                "status": new_status,
            },
        )


def emit_meter_reading(reading, *, flagged: bool) -> None:
    event_type = "meter.reading_flagged" if flagged else "meter.reading_created"
    emit_event(
        empresa_id=reading.empresa_id,
        event_type=event_type,
        resource_type="meter_reading",
        resource_id=reading.id,
        data={
            "reading_id": reading.id,
            "meter_id": reading.meter_id,
            "asset_id": reading.meter.machine_id if reading.meter else None,
            "value": str(reading.value),
            "flagged": bool(flagged),
            "anomaly_type": reading.anomaly_type or None,
            "work_order_id": reading.work_order_id,
        },
    )


def emit_asset_health_band_changed(snapshot, *, previous_band: str | None) -> None:
    if previous_band == snapshot.band:
        return
    emit_event(
        empresa_id=snapshot.empresa_id,
        event_type="asset_health.band_changed",
        resource_type="asset_health",
        resource_id=snapshot.id,
        data={
            "snapshot_id": snapshot.id,
            "asset_id": snapshot.machine_id,
            "previous_band": previous_band,
            "band": snapshot.band,
            "score": snapshot.score,
            "confidence": snapshot.confidence,
            "trigger": snapshot.trigger,
        },
    )
