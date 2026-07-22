"""API REST multi-tenant — legacy `/api/*` y contrato MAG `/api/v1/*`."""

from __future__ import annotations

from datetime import datetime
from functools import wraps
from typing import Any, Callable

from flask import Blueprint, current_app, g, jsonify, make_response, request

from app import limiter
from app.integrations.authorization import scope_required
from app.public_api.contract import (
    PUBLIC_API_LIMIT,
    ApiContractError,
    api_error,
    api_rate_key,
    iso_utc,
    pagination_meta,
    parse_datetime_parameter,
    parse_pagination,
    success,
)
from app.models import Empresa, Machine, User, WorkOrder
from app.modules import MODULO_MANTENIMIENTO, modulos_activos_de, modulos_mag_de
from app.permissions import normalize_rol
from app.tenancy.decorators import rol_required, tenant_required
from app.tenancy.jwt_auth import generar_token
from app.tenancy.queries import query_tenant, verificar_pertenencia

tenancy_api_bp = Blueprint("tenancy_api", __name__)

JWT_EXPIRES_SECONDS = 86400

_ASSET_STATUS_MAG = {
    "operativo": "operational",
    "mantenimiento": "maintenance",
    "falla": "failure",
}

_WO_STATUS_MAG = {
    "programada": "scheduled",
    "abierta": "open",
    "en_proceso": "in_progress",
    "vencida": "overdue",
    "completado": "completed",
    "cerrada": "closed",
}


def _legacy_deprecation(successor: str):
    """Cabeceras MAG-07 solo en rutas legacy."""

    def decorator(view: Callable):
        @wraps(view)
        def wrapped(*args, **kwargs):
            result = view(*args, **kwargs)
            if isinstance(result, tuple):
                resp = make_response(result[0], result[1])
            else:
                resp = make_response(result)
            resp.headers["Deprecation"] = "true"
            resp.headers["Link"] = f'<{successor}>; rel="successor-version"'
            return resp

        return wrapped

    return decorator


def _empresa_actual() -> Empresa | None:
    if not g.empresa_id:
        return None
    return Empresa.query.get(g.empresa_id)


def _require_maintenance_module():
    emp = _empresa_actual()
    if emp is None or MODULO_MANTENIMIENTO not in modulos_activos_de(emp):
        if request.path.startswith("/api/v1"):
            return api_error("MODULE_REQUIRED", "Módulo maintenance no activo para este tenant.", 403)
        return jsonify({"error": "Módulo maintenance no activo para este tenant"}), 403
    return None


def _asset_legacy_item(m: Machine) -> dict[str, Any]:
    return {
        "id": m.id,
        "codigo": m.codigo,
        "nombre": m.nombre,
        "status": m.status,
        "ubicacion": m.ubicacion,
        "es_critico": m.es_critico,
    }


def _asset_mag_item(m: Machine) -> dict[str, Any]:
    st = (m.status or "").strip().lower()
    return {
        "asset_id": m.id,
        "asset_code": m.codigo,
        "name": m.nombre,
        "status": _ASSET_STATUS_MAG.get(st, st),
        "critical": bool(m.es_critico),
        "location": m.ubicacion or "",
        "criticality": m.criticidad or "media",
        "area": m.area or "",
        "created_at": iso_utc(m.created_at),
        "updated_at": iso_utc(m.updated_at),
    }


def _pagination_meta(total: int, page: int = 1, page_size: int | None = None) -> dict:
    ps = page_size if page_size is not None else max(total, 1)
    return {"pagination": {"page": page, "page_size": ps, "total": total}}


def _work_order_mag_item(wo: WorkOrder) -> dict[str, Any]:
    st = (wo.status or "").strip().lower()
    return {
        "work_order_id": wo.id,
        "asset_id": wo.machine_id,
        "number": wo.numero,
        "title": wo.titulo,
        "type": wo.tipo,
        "status": _WO_STATUS_MAG.get(st, st),
        "priority": wo.prioridad,
        "scheduled_date": wo.fecha_programada.isoformat() if wo.fecha_programada else None,
        "created_at": iso_utc(wo.created_at),
        "updated_at": iso_utc(wo.updated_at),
    }


def _login_impl():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    empresa_slug = (data.get("empresa_slug") or data.get("empresa") or "").strip()
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    from app.user_service import buscar_usuario_login, mensaje_login_ambiguo

    user = buscar_usuario_login(username, empresa_slug=empresa_slug or None)
    if user is None:
        if User.query.filter_by(username=username.strip().lower()).count() > 1:
            return jsonify({"error": mensaje_login_ambiguo(username)}), 400
        return jsonify({"error": "Credenciales inválidas"}), 401
    if not user.check_password(password) or not user.is_active:
        return jsonify({"error": "Credenciales inválidas"}), 401
    if not user.empresa_id or not user.empresa:
        return jsonify({"error": "Usuario sin empresa asignada"}), 403
    if not user.empresa.email_verificado:
        return jsonify(
            {
                "error": "Confirma el correo de la empresa antes de ingresar.",
                "codigo": "email_no_verificado",
            }
        ), 403
    if not user.empresa.slug:
        return jsonify({"error": "Empresa sin slug configurado"}), 503

    token = generar_token(
        user_id=user.id,
        empresa_id=user.empresa_id,
        empresa_slug=user.empresa.slug,
        rol=normalize_rol(user.rol),
        secret=current_app.config["SECRET_KEY"],
    )
    return jsonify(
        {
            "token": token,
            "expires_in": JWT_EXPIRES_SECONDS,
            "empresa_id": user.empresa_id,
            "empresa_slug": user.empresa.slug,
            "rol": normalize_rol(user.rol),
            "username": user.username,
            "modules": modulos_mag_de(user.empresa),
        }
    )


@tenancy_api_bp.route("/api/v1/auth/login", methods=["POST"])
@limiter.limit("5 per 15 minutes")
def login_v1():
    return _login_impl()


@tenancy_api_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per 15 minutes")
@_legacy_deprecation("/api/v1/auth/login")
def login():
    return _login_impl()


def _me_data():
    emp = _empresa_actual()
    data = {
        "identity_type": getattr(g, "auth_type", None),
        "user_id": g.user_id,
        "empresa_id": g.empresa_id,
        "empresa_slug": g.empresa_slug,
        "rol": g.user_rol,
        "modules": modulos_mag_de(emp),
    }
    if getattr(g, "auth_type", None) == "api_key":
        data["credential_id"] = g.integration_credential_id
        data["scopes"] = list(g.api_scopes)
    return data


@tenancy_api_bp.route("/api/v1/me", methods=["GET"])
@tenant_required
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def me_v1():
    return success(_me_data())


@tenancy_api_bp.route("/api/me", methods=["GET"])
@tenant_required
@_legacy_deprecation("/api/v1/me")
def me():
    return jsonify(_me_data())


@tenancy_api_bp.route("/api/v1/maintenance/assets", methods=["GET"])
@tenant_required
@scope_required("maintenance.assets:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def listar_assets_v1():
    denied = _require_maintenance_module()
    if denied:
        return denied
    page, page_size = parse_pagination({"status", "criticality", "area", "updated_since"})
    query = query_tenant(Machine)
    if request.args.get("status"):
        reverse = {value: key for key, value in _ASSET_STATUS_MAG.items()}
        value = request.args["status"].strip().lower()
        query = query.filter(Machine.status == reverse.get(value, value))
    if request.args.get("criticality"):
        query = query.filter(Machine.criticidad == request.args["criticality"].strip().lower())
    if request.args.get("area"):
        query = query.filter(Machine.area == request.args["area"].strip())
    since = parse_datetime_parameter(request.args.get("updated_since"), "updated_since")
    if since:
        query = query.filter(Machine.updated_at >= since)
    total = query.count()
    items = query.order_by(Machine.updated_at.desc(), Machine.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success(
        [_asset_mag_item(item) for item in items],
        pagination=pagination_meta(total, page, page_size),
    )


@tenancy_api_bp.route("/api/activos", methods=["GET"])
@tenant_required
@_legacy_deprecation("/api/v1/maintenance/assets")
def listar_activos():
    denied = _require_maintenance_module()
    if denied:
        return denied
    machines = query_tenant(Machine).order_by(Machine.codigo).all()
    return jsonify(
        {
            "total": len(machines),
            "items": [_asset_legacy_item(m) for m in machines],
        }
    )


@tenancy_api_bp.route("/api/v1/maintenance/assets/<int:asset_id>", methods=["GET"])
@tenant_required
@scope_required("maintenance.assets:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def detalle_asset_v1(asset_id: int):
    denied = _require_maintenance_module()
    if denied:
        return denied
    machine = query_tenant(Machine).filter_by(id=asset_id).first()
    if not machine or not verificar_pertenencia(machine):
        raise ApiContractError("RESOURCE_NOT_FOUND", "Activo no encontrado.", 404)
    return success(_asset_mag_item(machine))


@tenancy_api_bp.route("/api/activos/<int:activo_id>", methods=["GET"])
@tenant_required
@_legacy_deprecation("/api/v1/maintenance/assets/{id}")
def detalle_activo(activo_id: int):
    denied = _require_maintenance_module()
    if denied:
        return denied
    machine = query_tenant(Machine).filter_by(id=activo_id).first()
    if not machine or not verificar_pertenencia(machine):
        return jsonify({"error": "Activo no encontrado"}), 404
    return jsonify(
        {
            "id": machine.id,
            "codigo": machine.codigo,
            "nombre": machine.nombre,
            "status": machine.status,
            "criticidad": machine.criticidad,
        }
    )


@tenancy_api_bp.route("/api/v1/maintenance/work-orders", methods=["GET"])
@tenant_required
@scope_required("maintenance.work_orders:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def listar_work_orders_v1():
    denied = _require_maintenance_module()
    if denied:
        return denied
    page, page_size = parse_pagination(
        {"status", "priority", "type", "asset_id", "updated_since", "date_from", "date_to"}
    )
    query = query_tenant(WorkOrder)
    if request.args.get("status"):
        reverse = {value: key for key, value in _WO_STATUS_MAG.items()}
        value = request.args["status"].strip().lower()
        query = query.filter(WorkOrder.status == reverse.get(value, value))
    if request.args.get("priority"):
        query = query.filter(WorkOrder.prioridad == request.args["priority"].strip().lower())
    if request.args.get("type"):
        query = query.filter(WorkOrder.tipo == request.args["type"].strip().lower())
    if request.args.get("asset_id"):
        try:
            query = query.filter(WorkOrder.machine_id == int(request.args["asset_id"]))
        except ValueError as exc:
            raise ApiContractError("INVALID_PARAMETER", "asset_id debe ser entero.") from exc
    since = parse_datetime_parameter(request.args.get("updated_since"), "updated_since")
    if since:
        query = query.filter(WorkOrder.updated_at >= since)
    for arg, operator in (("date_from", "ge"), ("date_to", "le")):
        if request.args.get(arg):
            try:
                value = datetime.fromisoformat(request.args[arg]).date()
            except ValueError as exc:
                raise ApiContractError("INVALID_PARAMETER", f"{arg} debe usar YYYY-MM-DD.") from exc
            query = query.filter(
                WorkOrder.fecha_programada >= value if operator == "ge" else WorkOrder.fecha_programada <= value
            )
    total = query.count()
    items = query.order_by(WorkOrder.updated_at.desc(), WorkOrder.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success(
        [_work_order_mag_item(item) for item in items],
        pagination=pagination_meta(total, page, page_size),
    )


def _resumen_admin_impl():
    denied = _require_maintenance_module()
    if denied:
        return denied
    total = query_tenant(Machine).count()
    wo_total = query_tenant(WorkOrder).count()
    return jsonify(
        {
            "empresa_id": g.empresa_id,
            "assets": total,
            "work_orders": wo_total,
            "activos": total,
        }
    )


@tenancy_api_bp.route("/api/v1/admin/summary", methods=["GET"])
@tenant_required
@rol_required("superadmin", "admin")
def resumen_admin_v1():
    return _resumen_admin_impl()


@tenancy_api_bp.route("/api/admin/resumen", methods=["GET"])
@tenant_required
@rol_required("superadmin", "admin")
@_legacy_deprecation("/api/v1/admin/summary")
def resumen_admin():
    return _resumen_admin_impl()
