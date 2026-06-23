"""Facturación SaaS por tenant — delega en subscription_service (Etapa 1)."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from sqlalchemy import func, or_

from app import db
from app.models import (
    FACTURA_ESTADO_LABELS,
    FacturaEmpresa,
    FacturaEstado,
    Empresa,
)
from app.platform_service import estado_ciclo_empresa
from app.subscription_service import crear_factura_mensual, marcar_factura_pagada, monto_suscripcion_empresa, verificar_vencimientos


def mrr_empresa(empresa: Empresa, hoy: date | None = None) -> float:
    """MRR real: factura pagada del mes; si no, catálogo si está activa."""
    hoy = hoy or date.today()
    periodo = f"{hoy.year:04d}-{hoy.month:02d}"
    factura = (
        FacturaEmpresa.query.filter_by(
            empresa_id=empresa.id,
            periodo=periodo,
            estado=FacturaEstado.PAGADA.value,
        )
        .order_by(FacturaEmpresa.id.desc())
        .first()
    )
    if factura:
        return float(factura.monto)
    ultima_pagada = (
        FacturaEmpresa.query.filter_by(empresa_id=empresa.id, estado=FacturaEstado.PAGADA.value)
        .order_by(FacturaEmpresa.fecha_pago.desc(), FacturaEmpresa.id.desc())
        .first()
    )
    if ultima_pagada and estado_ciclo_empresa(empresa, hoy) == "activa":
        return float(ultima_pagada.monto)
    if estado_ciclo_empresa(empresa, hoy) == "activa":
        return monto_suscripcion_empresa(empresa)
    return 0.0


def facturas_empresa(empresa_id: int, limit: int = 24) -> list[FacturaEmpresa]:
    return (
        FacturaEmpresa.query.filter_by(empresa_id=empresa_id)
        .order_by(FacturaEmpresa.fecha_emision.desc(), FacturaEmpresa.id.desc())
        .limit(limit)
        .all()
    )


def registrar_pago_factura(
    factura: FacturaEmpresa,
    *,
    metodo: str = "",
    referencia: str = "",
    fecha_pago: Optional[date] = None,
    notas: str = "",
    pasarela_payment_id: str = "",
) -> FacturaEmpresa:
    return marcar_factura_pagada(
        factura,
        metodo=metodo,
        referencia=referencia,
        fecha_pago=fecha_pago,
        notas=notas,
        pasarela_payment_id=pasarela_payment_id,
    )


def actualizar_facturas_vencidas() -> int:
    """Compatibilidad: delega en verificar_vencimientos."""
    return verificar_vencimientos().get("facturas_vencidas", 0)


def factura_estado_label(estado: str) -> str:
    return FACTURA_ESTADO_LABELS.get((estado or "").strip().lower(), estado or "—")


FACTURA_ESTADO_CHOICES = (
    ("", "Todos los estados"),
    (FacturaEstado.PENDIENTE.value, "Pendientes"),
    (FacturaEstado.PAGADA.value, "Pagadas"),
    (FacturaEstado.VENCIDA.value, "Vencidas"),
    (FacturaEstado.ANULADA.value, "Anuladas"),
)


def listar_facturas_platform(
    *,
    estado: str = "",
    q: str = "",
    limit: int = 200,
) -> list[FacturaEmpresa]:
    query = (
        FacturaEmpresa.query.join(Empresa, FacturaEmpresa.empresa_id == Empresa.id)
        .order_by(FacturaEmpresa.fecha_emision.desc(), FacturaEmpresa.id.desc())
    )
    if estado:
        query = query.filter(FacturaEmpresa.estado == estado)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Empresa.razon_social.ilike(like),
                Empresa.nit.ilike(like),
                FacturaEmpresa.numero.ilike(like),
            )
        )
    return query.limit(limit).all()


def kpis_facturacion() -> dict[str, Any]:
    hoy = date.today()
    periodo = f"{hoy.year:04d}-{hoy.month:02d}"
    pendientes = FacturaEmpresa.query.filter_by(estado=FacturaEstado.PENDIENTE.value).count()
    vencidas = FacturaEmpresa.query.filter_by(estado=FacturaEstado.VENCIDA.value).count()
    pagadas_mes = FacturaEmpresa.query.filter(
        FacturaEmpresa.estado == FacturaEstado.PAGADA.value,
        FacturaEmpresa.periodo == periodo,
    ).count()
    cobrado_mes = (
        db.session.query(func.coalesce(func.sum(FacturaEmpresa.monto), 0))
        .filter(
            FacturaEmpresa.estado == FacturaEstado.PAGADA.value,
            FacturaEmpresa.periodo == periodo,
        )
        .scalar()
    )
    por_cobrar = (
        db.session.query(func.coalesce(func.sum(FacturaEmpresa.monto), 0))
        .filter(FacturaEmpresa.estado.in_((FacturaEstado.PENDIENTE.value, FacturaEstado.VENCIDA.value)))
        .scalar()
    )
    return {
        "pendientes": pendientes,
        "vencidas": vencidas,
        "pagadas_mes": pagadas_mes,
        "cobrado_mes": float(cobrado_mes or 0),
        "por_cobrar": float(por_cobrar or 0),
    }
