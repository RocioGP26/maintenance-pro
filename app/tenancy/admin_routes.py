"""Admin de plataforma: crear empresas en mantenimiento.db."""

from __future__ import annotations

import os
from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from app import db
from app.models import Empresa, PLAN_CATALOG, PlanSuscripcion, PlanTipo, Sede
from app.tenancy.slug import slug_unico_empresa, slugify_empresa

admin_bp = Blueprint("admin", __name__)


def _verificar_clave_plataforma() -> bool:
    clave = os.environ.get("PLATFORM_ADMIN_KEY", "").strip()
    if not clave:
        return False
    return request.headers.get("X-Platform-Key", "").strip() == clave


@admin_bp.route("/admin/empresas", methods=["POST"])
def crear_empresa():
    """
    Registra empresa en mantenimiento.db (misma BD que web y API).
    Requiere header X-Platform-Key = PLATFORM_ADMIN_KEY.
    """
    if not _verificar_clave_plataforma():
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json(silent=True) or {}
    razon_social = (data.get("razon_social") or "").strip()
    if not razon_social:
        return jsonify({"error": "razon_social es obligatoria"}), 400

    slug = (data.get("slug") or "").strip() or slugify_empresa(razon_social)
    slug = slug_unico_empresa(slug)

    plan_key = (data.get("plan") or PlanTipo.TRIAL.value).strip()
    meta = PLAN_CATALOG.get(plan_key, PLAN_CATALOG[PlanTipo.TRIAL.value])

    empresa = Empresa(
        razon_social=razon_social,
        slug=slug,
        nit=data.get("nit", ""),
        sector=data.get("sector", "manufactura"),
        email=data.get("email", ""),
        telefono=data.get("telefono", ""),
        moneda=data.get("moneda", "COP"),
        zona_horaria=data.get("zona_horaria", "America/Bogota"),
    )
    db.session.add(empresa)
    db.session.flush()

    db.session.add(
        Sede(
            empresa_id=empresa.id,
            nombre=data.get("sede_nombre") or "Sede principal",
            es_principal=True,
        )
    )

    inicio = date.today()
    fin = inicio + timedelta(days=int(meta["dias"])) if meta.get("dias") else None
    db.session.add(
        PlanSuscripcion(
            empresa_id=empresa.id,
            plan=plan_key,
            fecha_inicio=inicio,
            fecha_fin=fin,
            activo=True,
        )
    )
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "empresa_id": empresa.id,
            "slug": slug,
        }
    ), 201


@admin_bp.route("/admin/empresas", methods=["GET"])
def listar_empresas():
    if not _verificar_clave_plataforma():
        return jsonify({"error": "No autorizado"}), 403

    empresas = Empresa.query.order_by(Empresa.razon_social).all()
    return jsonify(
        {
            "total": len(empresas),
            "items": [
                {
                    "id": e.id,
                    "razon_social": e.razon_social,
                    "slug": e.slug,
                }
                for e in empresas
            ],
        }
    )
