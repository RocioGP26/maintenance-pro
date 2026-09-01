"""
Suscripciones SaaS — piloto con facturación y pago manual.

Flujo:
  registro → crear_suscripcion_trial()
  trial vence → verificar_vencimientos() → factura pendiente + mora
  pago manual → marcar_factura_pagada() → activa
  sin pago en gracia → suspendida
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
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
TERMINOS_COMERCIALES_VERSION = "RTX-COM-01-v1.3.2"


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
    """Alta de tenant: trial configurable (15 días por defecto) sin tarjeta."""
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
    """Suscripción de plan de pago para el flujo manual del piloto."""
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


def cambiar_plan_manual(
    empresa: Empresa,
    plan_key: str,
    *,
    hoy: date | None = None,
) -> tuple[PlanSuscripcion, str, bool]:
    """Asigna un plan comercial durante el piloto, sin generar una factura."""
    from app.platform_config_service import PLANES_COMERCIALES_PILOTO

    key = (plan_key or "").strip().lower()
    if key not in PLANES_COMERCIALES_PILOTO:
        raise ValueError("El plan no pertenece a la oferta comercial del piloto.")

    hoy = hoy or date.today()
    sub = empresa.plan_activo
    anterior = sub.plan if sub else "sin_plan"
    if sub and anterior == key and sub.estado_ciclo == SuscripcionEstado.ACTIVA.value:
        return sub, anterior, False

    if not sub:
        sub = crear_suscripcion_pagada(empresa, key)
        sub.fecha_inicio = hoy
        sub.fecha_fin = hoy + timedelta(days=dias_periodo_pago())
    else:
        reiniciar_ciclo = (
            anterior == PlanTipo.TRIAL.value
            or sub.estado_ciclo != SuscripcionEstado.ACTIVA.value
            or not sub.fecha_fin
            or sub.fecha_fin < hoy
        )
        sub.plan = key
        sub.activo = True
        sub.estado_ciclo = SuscripcionEstado.ACTIVA.value
        if reiniciar_ciclo:
            sub.fecha_inicio = hoy
            sub.fecha_fin = hoy + timedelta(days=dias_periodo_pago())

    empresa.suspendida = False
    return sub, anterior, True


def registrar_aceptacion_terminos(
    sub: PlanSuscripcion,
    *,
    user_id: int,
    ip_address: str = "",
) -> PlanSuscripcion:
    """Records an auditable, versioned acceptance without activating billing."""
    sub.terminos_version = TERMINOS_COMERCIALES_VERSION
    sub.terminos_aceptados_en = datetime.utcnow()
    sub.terminos_aceptados_por_id = user_id
    sub.terminos_aceptados_ip = (ip_address or "")[:45]
    return sub


def terminos_vigentes_aceptados(sub: PlanSuscripcion | None) -> bool:
    return bool(
        sub
        and sub.terminos_aceptados_en
        and sub.terminos_version == TERMINOS_COMERCIALES_VERSION
    )


def preparar_conversion_comercial(
    empresa: Empresa,
    plan_key: str,
    *,
    hoy: date | None = None,
) -> tuple[PlanSuscripcion, FacturaEmpresa, str, bool]:
    """Selects the paid plan and creates its invoice; activation waits for payment."""
    from app.platform_config_service import PLANES_COMERCIALES_PILOTO

    key = (plan_key or "").strip().lower()
    if key not in PLANES_COMERCIALES_PILOTO:
        raise ValueError("El plan no pertenece a la oferta comercial vigente.")
    if empresa.es_prueba:
        raise ValueError("Las empresas de prueba están excluidas de facturación.")

    sub = empresa.plan_activo
    if not sub:
        raise ValueError("La empresa no tiene una suscripción para convertir.")
    if not terminos_vigentes_aceptados(sub):
        raise ValueError(
            "La empresa debe aceptar los términos comerciales vigentes antes de convertir el trial."
        )

    hoy = hoy or date.today()
    anterior = sub.plan
    pendiente = (
        FacturaEmpresa.query.filter_by(
            empresa_id=empresa.id,
            suscripcion_id=sub.id,
            estado=FacturaEstado.PENDIENTE.value,
        )
        .order_by(FacturaEmpresa.id.desc())
        .first()
    )
    changed = anterior != key
    sub.plan = key
    sub.activo = True
    sub.estado_ciclo = SuscripcionEstado.MORA.value
    empresa.suspendida = False
    if pendiente:
        pendiente.concepto = f"Suscripción {plan_meta(key)['short_label']} — {_periodo_hoy(hoy)}"
        pendiente.monto = _monto_plan(key)
        pendiente.periodo = _periodo_hoy(hoy)
        factura = pendiente
    else:
        factura = _crear_factura_suscripcion(empresa, sub, hoy=hoy)
    return sub, factura, anterior, changed


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
    if empresa.es_prueba:
        raise ValueError("Las empresas de prueba están excluidas de facturación.")
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
        if sub.fecha_fin and sub.fecha_fin <= hoy:
            return SuscripcionEstado.MORA.value
        return SuscripcionEstado.TRIAL.value
    if sub.fecha_fin and sub.fecha_fin <= hoy:
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
    stats = {
        "avisos_trial": 0,
        "avisos_fallidos": 0,
        "trials_a_mora": 0,
        "facturas_vencidas": 0,
        "suspensiones": 0,
    }

    trials_para_aviso = PlanSuscripcion.query.join(Empresa).filter(
        Empresa.es_prueba.is_(False),
        PlanSuscripcion.activo.is_(True),
        PlanSuscripcion.estado_ciclo == SuscripcionEstado.TRIAL.value,
    ).all()
    for sub in trials_para_aviso:
        dia = (hoy - sub.fecha_inicio).days
        if dia not in {7, 12, 15} or not sub.empresa:
            continue
        empresa = sub.empresa
        recipient = (empresa.email or "").strip()
        if not recipient:
            from app.models import User

            admin = (
                User.query.filter(
                    User.empresa_id == empresa.id,
                    User.activo.is_(True),
                    User.rol.in_(["superadmin", "admin"]),
                    User.email != "",
                )
                .order_by(User.id.asc())
                .first()
            )
            recipient = (admin.email or "").strip() if admin else ""
        if not recipient:
            continue
        try:
            from app.email_service import EmailDeliveryError, send_templated_email

            send_templated_email(
                empresa_id=empresa.id,
                recipient=recipient,
                subject=(
                    "Tu periodo de prueba Roustix finaliza hoy"
                    if dia == 15
                    else "Información sobre tu periodo de prueba Roustix"
                ),
                template_name="trial_expiry",
                context={
                    "empresa": empresa,
                    "dia_trial": dia,
                    "dias_restantes": max(15 - dia, 0),
                    "fecha_fin": sub.fecha_fin,
                },
                idempotency_key=f"trial-expiry:{sub.id}:day:{dia}",
            )
            stats["avisos_trial"] += 1
        except EmailDeliveryError:
            stats["avisos_fallidos"] += 1

    trials_vencidos = PlanSuscripcion.query.join(Empresa).filter(
        Empresa.es_prueba.is_(False),
        PlanSuscripcion.activo.is_(True),
        PlanSuscripcion.estado_ciclo == SuscripcionEstado.TRIAL.value,
        PlanSuscripcion.fecha_fin.isnot(None),
        PlanSuscripcion.fecha_fin <= hoy,
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

    facturas_impagas = FacturaEmpresa.query.join(Empresa).filter(
        Empresa.es_prueba.is_(False),
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

    suscripciones_mora_vencidas = PlanSuscripcion.query.join(Empresa).filter(
        Empresa.es_prueba.is_(False),
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
    Piloto: pago manual desde SuperAdmin. La pasarela queda diferida a postpiloto.
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
    if empresa.es_prueba:
        return 0.0
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
    if empresa.es_prueba:
        raise ValueError("Las empresas de prueba están excluidas de facturación.")
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
