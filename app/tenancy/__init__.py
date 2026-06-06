"""Multi-tenancy MVP: una BD (mantenimiento.db) + empresa_id + JWT."""

from app.tenancy.context import current_empresa_id
from app.tenancy.db import close_db, get_db
from app.tenancy.decorators import rol_required, tenant_required
from app.tenancy.jwt_auth import generar_token, verificar_token
from app.tenancy.middleware import register_tenancy_middleware
from app.tenancy.queries import insertar_tenant, query_tenant, verificar_pertenencia

__all__ = [
    "close_db",
    "current_empresa_id",
    "generar_token",
    "get_db",
    "get_tenant_or_404",
    "insertar_tenant",
    "query_tenant",
    "register_tenancy_middleware",
    "rol_required",
    "tenant_required",
    "verificar_pertenencia",
    "verificar_token",
]
