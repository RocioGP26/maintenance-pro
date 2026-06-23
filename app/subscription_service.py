"""
Suscripciones SaaS — Etapa 1 (sin pasarela real).

Flujo:
  registro → crear_suscripcion_trial()
  trial vence → verificar_vencimientos() → factura pendiente + mora
  pago manual / futuro webhook → marcar_factura_pagada() → activa
  sin pago en gracia → suspendida
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from app import db
from app.models import (
    Empresa,
    FacturaEmpresa,
    FacturaEstado,
    PLAN_CATALOG,
    PlanSuscripcion,
    PlanTipo,
    SuscripcionEstado,
)
from app.platform_config_service import (
    dias_gracia_mora,
    dias_periodo_pago,
    plan_tras_trial,
    trial_dias,
)
from app.platform_service import plan_meta

PLAN_TRAS_TRIAL = PlanTipo.BASICO.value  # fallback; usar plan_tras_trial()


def _periodo_hoy(hoy: date | None = None) -> str:
    hoy = hoy or date.today()
    return f"{hoy.year:04d}-{hoy.month:02d}"


def siguiente_numero_factura(empresa_id: int) -> str:
    anio = date.today().year
    prefijo = f"FAC-{anio}-"
    ultima = (
        FacturaEmpresa.query.filter(
            FacturaEmpresa.empresa_id == empresa_id,
            FacturaEmpresa.numero.like(f"{prefijo}%"),
        )
        .order_by(FacturaEmpresa.id.desc())
        .first()
    )
    if not ultima:
        return f"{prefijo}001"
    try:
        seq = int(ultima.numero.rsplit("-", 1)[-1]) + 1
    except ValueError:
        seq = 1
    return f"{prefijo}{seq:03d}"


def crear_suscripcion_trial(
    empresa: Empresa,
    plan_key: str = PlanTipo.TRIAL.value,
) -> PlanSuscripcion:
    """Alta de tenant: trial 14 días sin tarjeta."""
    if plan_key != PlanTipo.TRIAL.value:
        return crear_suscripcion_pagada(empresa, plan_key)
    inicio = date.today()
    sub = PlanSuscripcion(
        empresa_id=empresa.id,
        plan=PlanTipo.TRIAL.value,
        fecha_inicio=inicio,
        fecha_fin=inicio + timedelta(days=trial_dias()),
        activo=True,
        estado_ciclo=SuscripcionEstado.TRIAL.value,
    )
    db.session.add(sub)
    return sub


def crear_suscripcion_pagada(empresa: Empresa, plan_key: str) -> PlanSuscripcion:
    """Suscripción de plan de pago (sin pasarela; se factura manualmente)."""
    inicio = date.today()
    sub = PlanSuscripcion(
        empresa_id=empresa.id,
        plan=plan_key,
        fecha_inicio=inicio,
        fecha_fin=inicio + timedelta(days=dias_periodo_pago()),
        activo=True,
        estado_ciclo=SuscripcionEstado.ACTIVA.value,
    )
    db.session.add(sub)
    return sub


def _plan_facturable(sub: PlanSuscripcion) -> str:
    if sub.plan == PlanTipo.TRIAL.value:
        return plan_tras_trial()
    return sub.plan


def _monto_plan(plan_key: str) -> float:
    return float(plan_meta(plan_key).get("precio_mensual", 0) or 0)


def _crear_factura_suscripcion(
    empresa: Empresa,
    sub: PlanSuscripcion,
    *,
    hoy: date | None = None,
    concepto: str = "",
    periodo: str | None = None,
) -> FacturaEmpresa:
    hoy = hoy or date.today()
    plan_key = _plan_facturable(sub)
    meta = plan_meta(plan_key)
    fac = FacturaEmpresa(
        empresa_id=empresa.id,
        suscripcion_id=sub.id,
        numero=siguiente_numero_factura(empresa.id),
        concepto=concepto or f"Suscripción {meta['short_label']} — {_periodo_hoy(hoy)}",
        monto=_monto_plan(plan_key),
        moneda=empresa.moneda or "COP",
        periodo=periodo or _periodo_hoy(hoy),
        estado=FacturaEstado.PENDIENTE.value,
        fecha_emision=hoy,
        fecha_vencimiento=hoy + timedelta(days=dias_gracia_mora()),
    )
    db.session.add(fac)
    return fac


def _inferir_estado_ciclo_legacy(sub: PlanSuscripcion, hoy: date) -> str:
    if sub.plan == PlanTipo.TRIAL.value:
        if sub.fecha_fin and sub.fecha_fin < hoy:
            return SuscripcionEstado.MORA.value
        return SuscripcionEstado.TRIAL.value
    if sub.fecha_fin and sub.fecha_fin < hoy:
        return SuscripcionEstado.MORA.value
    return SuscripcionEstado.ACTIVA.value


def backfill_estado_ciclo_suscripciones() -> int:
    """Migración: estado_ciclo en suscripciones existentes."""
    hoy = date.today()
    n = 0
    for sub in PlanSuscripcion.query.filter_by(activo=True).all():
        if (sub.estado_ciclo or "").strip():
            continue
        sub.estado_ciclo = _inferir_estado_ciclo_legacy(sub, hoy)
        if sub.estado_ciclo == SuscripcionEstado.MORA.value and sub.empresa:
            sub.empresa.suspendida = False
        n += 1
    if n:
        db.session.commit()
    return n


def verificar_vencimientos(hoy: date | None = None) -> dict[str, int]:
    """
    Cron diario (Etapa 1):
    - Trials vencidos → factura pendiente + mora
    - Facturas impagas tras gracia → vencida + suscripción suspendida
    """
    hoy = hoy or date.today()
    stats = {"trials_a_mora": 0, "facturas_vencidas": 0, "suspensiones": 0}

    trials_vencidos = PlanSuscripcion.query.filter(
        PlanSuscripcion.activo.is_(True),
        PlanSuscripcion.estado_ciclo == SuscripcionEstado.TRIAL.value,
        PlanSuscripcion.fecha_fin.isnot(None),
        PlanSuscripcion.fecha_fin < hoy,
    ).all()
    for sub in trials_vencidos:
        empresa = sub.empresa
        if not empresa:
            continue
        pendiente = (
            FacturaEmpresa.query.filter_by(
                empresa_id=empresa.id,
                suscripcion_id=sub.id,
                estado=FacturaEstado.PENDIENTE.value,
            )
            .first()
        )
        if not pendiente:
            _crear_factura_suscripcion(
                empresa,
                sub,
                hoy=hoy,
                concepto=f"Primera suscripción tras periodo de prueba — {plan_meta(_plan_facturable(sub))['short_label']}",
            )
        sub.estado_ciclo = SuscripcionEstado.MORA.value
        stats["trials_a_mora"] += 1

    facturas_impagas = FacturaEmpresa.query.filter(
        FacturaEmpresa.estado == FacturaEstado.PENDIENTE.value,
        FacturaEmpresa.fecha_vencimiento.isnot(None),
        FacturaEmpresa.fecha_vencimiento < hoy,
    ).all()
    for fac in facturas_impagas:
        fac.estado = FacturaEstado.VENCIDA.value
        stats["facturas_vencidas"] += 1
        empresa = fac.empresa
        if not empresa:
            continue
        sub = (
            PlanSuscripcion.query.get(fac.suscripcion_id)
            if fac.suscripcion_id
            else empresa.plan_activo
        )
        if sub:
            sub.estado_ciclo = SuscripcionEstado.SUSPENDIDA.value
        empresa.suspendida = True
        stats["suspensiones"] += 1

    suscripciones_mora_vencidas = PlanSuscripcion.query.filter(
        PlanSuscripcion.activo.is_(True),
        PlanSuscripcion.estado_ciclo == SuscripcionEstado.MORA.value,
        PlanSuscripcion.fecha_fin.isnot(None),
        PlanSuscripcion.fecha_fin < hoy,
    ).all()
    for sub in suscripciones_mora_vencidas:
        tiene_pendiente = (
            FacturaEmpresa.query.filter_by(
                empresa_id=sub.empresa_id,
                suscripcion_id=sub.id,
                estado=FacturaEstado.PENDIENTE.value,
            )
            .first()
        )
        if not tiene_pendiente:
            _crear_factura_suscripcion(sub.empresa, sub, hoy=hoy)

    if any(stats.values()) or trials_vencidos or facturas_impagas:
        db.session.commit()
    return stats


def marcar_factura_pagada(
    factura: FacturaEmpresa,
    *,
    metodo: str = "",
    referencia: str = "",
    fecha_pago: Optional[date] = None,
    notas: str = "",
    pasarela_payment_id: str = "",
) -> FacturaEmpresa:
    """
    Etapa 1: pago manual desde superadmin.
    Etapa 2+: el webhook de la pasarela llamará aquí con pasarela_payment_id.
    """
    fecha_pago = fecha_pago or date.today()
    factura.estado = FacturaEstado.PAGADA.value
    factura.fecha_pago = fecha_pago
    factura.metodo_pago = (metodo or "manual").strip()
    factura.referencia_pago = (referencia or "").strip()
    if notas:
        factura.notas = notas.strip()
    if pasarela_payment_id:
        factura.pasarela_payment_id = pasarela_payment_id.strip()

    empresa = factura.empresa
    sub = (
        PlanSuscripcion.query.get(factura.suscripcion_id)
        if factura.suscripcion_id
        else (empresa.plan_activo if empresa else None)
    )
    if sub:
        sub.estado_ciclo = SuscripcionEstado.ACTIVA.value
        if sub.plan == PlanTipo.TRIAL.value:
            sub.plan = _plan_facturable(sub)
        sub.fecha_fin = fecha_pago + timedelta(days=dias_periodo_pago())
    if empresa:
        empresa.suspendida = False
    return factura


def monto_suscripcion_empresa(empresa: Empresa) -> float:
    sub = empresa.plan_activo
    key = _plan_facturable(sub) if sub else PlanTipo.TRIAL.value
    return _monto_plan(key)


def crear_factura_mensual(
    empresa: Empresa,
    *,
    periodo: Optional[str] = None,
    monto: Optional[float] = None,
) -> FacturaEmpresa:
    """Factura manual adicional desde el panel (fuera del cron)."""
    sub = empresa.plan_activo
    if not sub:
        raise ValueError("La empresa no tiene suscripción activa.")
    hoy = date.today()
    plan_key = _plan_facturable(sub)
    fac = FacturaEmpresa(
        empresa_id=empresa.id,
        suscripcion_id=sub.id,
        numero=siguiente_numero_factura(empresa.id),
        concepto=f"Suscripción {plan_meta(plan_key)['short_label']} — {periodo or _periodo_hoy(hoy)}",
        monto=monto if monto is not None else _monto_plan(plan_key),
        moneda=empresa.moneda or "COP",
        periodo=periodo or _periodo_hoy(hoy),
        estado=FacturaEstado.PENDIENTE.value,
        fecha_emision=hoy,
        fecha_vencimiento=hoy + timedelta(days=dias_gracia_mora()),
    )
    db.session.add(fac)
    return fac
