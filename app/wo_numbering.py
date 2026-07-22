"""Numeración consecutiva de órdenes de trabajo (OT-YY-NNNN)."""
from datetime import date, datetime
from typing import Optional, Tuple

from sqlalchemy import func

from app import db
from app.models import WorkOrder


def formato_numero_ot(anio: int, secuencia: int) -> str:
    yy = anio % 100
    return f"OT-{yy:02d}-{secuencia:04d}"


def siguiente_folio(empresa_id: Optional[int], anio: Optional[int] = None) -> Tuple[str, int, int]:
    """Devuelve (numero, folio_anio, folio_seq) para la siguiente OT de la empresa y año."""
    folio_anio = anio or date.today().year
    q = db.session.query(func.coalesce(func.max(WorkOrder.folio_seq), 0)).filter(
        WorkOrder.folio_anio == folio_anio
    )
    if empresa_id is not None:
        q = q.filter(WorkOrder.empresa_id == empresa_id)
    else:
        q = q.filter(WorkOrder.empresa_id.is_(None))
    seq = int(q.scalar() or 0) + 1
    return formato_numero_ot(folio_anio, seq), folio_anio, seq


def asignar_numero_ot(wo: WorkOrder, anio: Optional[int] = None) -> str:
    if wo.numero:
        return wo.numero
    numero, folio_anio, folio_seq = siguiente_folio(wo.empresa_id, anio)
    wo.numero = numero
    wo.folio_anio = folio_anio
    wo.folio_seq = folio_seq
    from app.integrations.emitters import emit_work_order_created

    emit_work_order_created(wo)
    return numero


def backfill_work_order_numeros() -> None:
    """Asigna número a OT existentes sin folio (migración)."""
    from collections import defaultdict

    from sqlalchemy import inspect, or_

    insp = inspect(db.engine)
    if "work_orders" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("work_orders")}
    if "numero" not in cols:
        return

    pendientes = (
        WorkOrder.query.filter(or_(WorkOrder.numero.is_(None), WorkOrder.numero == ""))
        .order_by(WorkOrder.empresa_id, WorkOrder.created_at, WorkOrder.id)
        .all()
    )
    if not pendientes:
        return

    contadores: dict[tuple[Optional[int], int], int] = defaultdict(int)
    for wo in WorkOrder.query.filter(WorkOrder.folio_seq.isnot(None)).all():
        if wo.folio_anio:
            key = (wo.empresa_id, wo.folio_anio)
            contadores[key] = max(contadores[key], wo.folio_seq or 0)

    for wo in pendientes:
        ref = wo.created_at or datetime.utcnow()
        anio = wo.folio_anio or (ref.year if hasattr(ref, "year") else date.today().year)
        key = (wo.empresa_id, anio)
        contadores[key] += 1
        seq = contadores[key]
        wo.folio_anio = anio
        wo.folio_seq = seq
        wo.numero = formato_numero_ot(anio, seq)
    db.session.commit()
