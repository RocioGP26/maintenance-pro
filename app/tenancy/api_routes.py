"""API REST multi-tenant — legacy `/api/*` y contrato MAG `/api/v1/*`."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import Blueprint, current_app, g, jsonify, make_response, request

from app import limiter
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


def _me_impl():
    emp = _empresa_actual()
    return jsonify(
        {
            "user_id": g.user_id,
            "empresa_id": g.empresa_id,
            "empresa_slug": g.empresa_slug,
            "rol": g.user_rol,
            "modules": modulos_mag_de(emp),
        }
    )


@tenancy_api_bp.route("/api/v1/me", methods=["GET"])
@tenant_required
def me_v1():
    return _me_impl()


@tenancy_api_bp.route("/api/me", methods=["GET"])
@tenant_required
@_legacy_deprecation("/api/v1/me")
def me():
    return _me_impl()


@tenancy_api_bp.route("/api/v1/maintenance/assets", methods=["GET"])
@tenant_required
def listar_assets_v1():
    denied = _require_maintenance_module()
    if denied:
        return denied
    machines = query_tenant(Machine).order_by(Machine.codigo).all()
    page = max(1, int(request.args.get("page", 1) or 1))
    page_size = min(200, max(1, int(request.args.get("page_size", 50) or 50)))
    total = len(machines)
    start = (page - 1) * page_size
    chunk = machines[start : start + page_size]
    return jsonify(
        {
            "data": [_asset_mag_item(m) for m in chunk],
            "meta": _pagination_meta(total, page, page_size),
        }
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
def detalle_asset_v1(asset_id: int):
    denied = _require_maintenance_module()
    if denied:
        return denied
    machine = query_tenant(Machine).filter_by(id=asset_id).first()
    if not machine or not verificar_pertenencia(machine):
        return jsonify({"error": "Activo no encontrado"}), 404
    return jsonify({"data": _asset_mag_item(machine)})


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
def listar_work_orders_v1():
    denied = _require_maintenance_module()
    if denied:
        return denied
    page = max(1, int(request.args.get("page", 1) or 1))
    page_size = min(200, max(1, int(request.args.get("page_size", 50) or 50)))
    q = query_tenant(WorkOrder).order_by(WorkOrder.created_at.desc())
    total = q.count()
    start = (page - 1) * page_size
    orders = q.offset(start).limit(page_size).all()
    return jsonify(
        {
            "data": [_work_order_mag_item(wo) for wo in orders],
            "meta": _pagination_meta(total, page, page_size),
        }
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
