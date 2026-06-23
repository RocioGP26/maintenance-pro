"""Bloque 6 — endpoints de ejemplo con decoradores de tenancy."""

from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request

from app import limiter
from app.models import Machine, User
from app.permissions import normalize_rol
from app.tenancy.decorators import rol_required, tenant_required
from app.tenancy.jwt_auth import generar_token
from app.tenancy.queries import query_tenant, verificar_pertenencia

tenancy_api_bp = Blueprint("tenancy_api", __name__)


@tenancy_api_bp.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per 15 minutes")
def login():
    """Login API: devuelve JWT con empresa_id firmado."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password) or not user.is_active:
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
            "empresa_id": user.empresa_id,
            "empresa_slug": user.empresa.slug,
            "rol": normalize_rol(user.rol),
            "username": user.username,
        }
    )


@tenancy_api_bp.route("/api/me", methods=["GET"])
@tenant_required
def me():
    """Contexto del tenant activo (JWT o sesión)."""
    return jsonify(
        {
            "user_id": g.user_id,
            "empresa_id": g.empresa_id,
            "empresa_slug": g.empresa_slug,
            "rol": g.user_rol,
        }
    )


@tenancy_api_bp.route("/api/activos", methods=["GET"])
@tenant_required
def listar_activos():
    """Listado de activos filtrado por empresa_id del contexto."""
    machines = query_tenant(Machine).order_by(Machine.codigo).all()
    return jsonify(
        {
            "total": len(machines),
            "items": [
                {
                    "id": m.id,
                    "codigo": m.codigo,
                    "nombre": m.nombre,
                    "status": m.status,
                    "ubicacion": m.ubicacion,
                    "es_critico": m.es_critico,
                }
                for m in machines
            ],
        }
    )


@tenancy_api_bp.route("/api/activos/<int:activo_id>", methods=["GET"])
@tenant_required
def detalle_activo(activo_id: int):
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


@tenancy_api_bp.route("/api/admin/resumen", methods=["GET"])
@tenant_required
@rol_required("superadmin", "admin")
def resumen_admin():
    """Solo admin/superadmin del tenant."""
    total = query_tenant(Machine).count()
    return jsonify({"empresa_id": g.empresa_id, "activos": total})
