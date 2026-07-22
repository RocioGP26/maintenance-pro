"""Envelope, errores, paginación, request ID e idempotencia de API v1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import secrets

from flask import g, jsonify, request
from app import db
from app.models import ApiIdempotencyRecord


API_VERSION = "v1"
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{8,100}$")
_IDEMPOTENCY_RE = re.compile(r"^[\x21-\x7E]{8,120}$")


def public_api_limit() -> str:
    """Límite dinámico por entitlement del tenant (fallback 120/min)."""
    from flask import g, request

    from app.integrations.entitlements import entitlement_int
    from app.models import IntegrationCredential

    empresa_id = getattr(g, "empresa_id", None)
    if not empresa_id:
        auth = (request.headers.get("Authorization") or "").strip()
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            if token.startswith(("rtx_test_", "rtx_live_")) and "." in token:
                prefix = token.split(".", 1)[0]
                cred = IntegrationCredential.query.filter_by(key_prefix=prefix).first()
                if cred is not None:
                    empresa_id = cred.empresa_id
    rpm = entitlement_int(empresa_id, "public_api.requests_per_minute", 120)
    return f"{max(10, rpm)} per minute"


# Flask-Limiter acepta callables; se mantiene el nombre histórico.
PUBLIC_API_LIMIT = public_api_limit


@dataclass(frozen=True)
class ApiContractError(Exception):
    code: str
    message: str
    status: int = 400
    details: dict | None = None


def request_id() -> str:
    value = getattr(g, "request_id", None)
    if value:
        return value
    value = f"req_{secrets.token_hex(12)}"
    g.request_id = value
    return value


def meta(*, pagination: dict | None = None) -> dict:
    result = {"request_id": request_id(), "api_version": API_VERSION}
    if pagination is not None:
        result["pagination"] = pagination
    return result


def success(data, *, status: int = 200, pagination: dict | None = None):
    return jsonify({"data": data, "meta": meta(pagination=pagination)}), status


def api_error(code: str, message: str, status: int, *, details: dict | None = None):
    return jsonify(
        {
            "error": {
                "code": code.upper(),
                "message": message,
                "details": details or {},
                "request_id": request_id(),
            }
        }
    ), status


def register_public_api_contract(app) -> None:
    @app.before_request
    def _assign_public_request_id():
        if not request.path.startswith("/api/v1"):
            return None
        supplied = (request.headers.get("X-Request-Id") or "").strip()
        g.request_id = supplied if _REQUEST_ID_RE.fullmatch(supplied) else f"req_{secrets.token_hex(12)}"
        return None

    @app.after_request
    def _public_api_headers(response):
        if request.path.startswith("/api/v1"):
            response.headers["X-Request-Id"] = request_id()
            response.headers["X-Roustix-Api-Version"] = API_VERSION
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(ApiContractError)
    def _contract_error(exc: ApiContractError):
        return api_error(exc.code, exc.message, exc.status, details=exc.details)

    for status, code, message in (
        (404, "RESOURCE_NOT_FOUND", "Recurso no encontrado."),
        (405, "METHOD_NOT_ALLOWED", "Método no permitido."),
        (429, "RATE_LIMIT_EXCEEDED", "Se excedió el límite de solicitudes."),
    ):
        def handler(exc, _status=status, _code=code, _message=message):
            if request.path.startswith("/api/v1"):
                return api_error(_code, _message, _status)
            return exc.get_response()
        app.register_error_handler(status, handler)


def api_rate_key() -> str:
    credential_id = getattr(g, "integration_credential_id", None)
    if credential_id:
        return f"credential:{credential_id}"
    user_id = getattr(g, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    # Flask-Limiter evalúa su key antes que el middleware tenant. Se deriva una
    # identidad opaca del header sin almacenar ni registrar el secreto.
    auth = (request.headers.get("Authorization") or "").strip()
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
        if token.startswith(("rtx_test_", "rtx_live_")) and "." in token:
            return f"credential-prefix:{token.split('.', 1)[0]}"
        if token:
            return f"bearer:{hashlib.sha256(token.encode('utf-8')).hexdigest()[:24]}"
    return f"ip:{request.remote_addr or 'unknown'}"


def parse_pagination(allowed_params: set[str]) -> tuple[int, int]:
    unknown = set(request.args).difference(allowed_params | {"page", "page_size"})
    if unknown:
        raise ApiContractError(
            "INVALID_PARAMETER",
            "La solicitud contiene parámetros no reconocidos.",
            details={"parameters": sorted(unknown)},
        )
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 50))
    except (TypeError, ValueError) as exc:
        raise ApiContractError("INVALID_PARAMETER", "page y page_size deben ser enteros.") from exc
    if page < 1 or page_size < 1 or page_size > 200:
        raise ApiContractError(
            "INVALID_PARAMETER", "page debe ser >= 1 y page_size debe estar entre 1 y 200."
        )
    return page, page_size


def pagination_meta(total: int, page: int, page_size: int) -> dict:
    return {"page": page, "page_size": page_size, "total": int(total)}


def parse_datetime_parameter(value: str | None, name: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApiContractError("INVALID_PARAMETER", f"{name} debe usar formato ISO 8601.") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def iso_utc(value: datetime | None) -> str | None:
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if value else None


def _actor_key() -> tuple[str, int | None]:
    credential_id = getattr(g, "integration_credential_id", None)
    if credential_id:
        return f"credential:{credential_id}", int(credential_id)
    user_id = getattr(g, "user_id", None)
    if user_id:
        return f"user:{user_id}", None
    raise ApiContractError("AUTHENTICATION_REQUIRED", "Autenticación requerida.", 401)


def payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def idempotency_lookup(operation: str, payload: dict):
    key = (request.headers.get("Idempotency-Key") or "").strip()
    if not _IDEMPOTENCY_RE.fullmatch(key):
        raise ApiContractError(
            "IDEMPOTENCY_KEY_REQUIRED",
            "Idempotency-Key es obligatorio y debe tener entre 8 y 120 caracteres ASCII.",
        )
    actor_key, credential_id = _actor_key()
    digest = payload_hash(payload)
    record = ApiIdempotencyRecord.query.filter_by(
        empresa_id=g.empresa_id,
        actor_key=actor_key,
        operation=operation,
        idempotency_key=key,
    ).first()
    if record and record.request_hash != digest:
        raise ApiContractError(
            "IDEMPOTENCY_CONFLICT",
            "La misma Idempotency-Key fue usada con un cuerpo diferente.",
            409,
        )
    return record, key, digest, actor_key, credential_id


def replay_idempotency(record: ApiIdempotencyRecord):
    return success(json.loads(record.response_json), status=record.status_code)


def store_idempotency(
    *, operation: str, key: str, digest: str, actor_key: str,
    credential_id: int | None, resource_type: str, resource_id: int,
    response_data: dict, status_code: int = 201,
) -> ApiIdempotencyRecord:
    record = ApiIdempotencyRecord(
        empresa_id=g.empresa_id,
        credential_id=credential_id,
        actor_key=actor_key,
        operation=operation,
        idempotency_key=key,
        request_hash=digest,
        resource_type=resource_type,
        resource_id=resource_id,
        response_json=json.dumps(response_data, ensure_ascii=False, sort_keys=True),
        status_code=status_code,
    )
    db.session.add(record)
    return record
