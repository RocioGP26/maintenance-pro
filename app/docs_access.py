"""Acceso híbrido a la suite documental Roustix Docs.

Política (MDO / Publishing):
  Público  → marca e integración (MBB, OpenAPI) + MAG/MSD HTML (/guide) + activos MKT + /guia
  Privado  → MAG/MSD .md fuente, MRG .md, MCM, Biblia MKT, arquitectura, diseño e ingeniería

Configuración:
  DOCS_ACCESS_POLICY=hybrid | open | locked
    hybrid (default prod/dev) — aplica la matriz pública/privada
    open   — todo abierto (útil en testing local)
    locked — todo requiere login (incluido lo público)
"""

from __future__ import annotations

from flask import current_app, flash, redirect, request, session, url_for
from flask_login import current_user

# Blueprints 100 % públicos (sin filtro de path)
PUBLIC_DOC_BLUEPRINTS = frozenset({
    "brand_book",
    "openapi",
})

# Blueprints 100 % privados
PRIVATE_DOC_BLUEPRINTS = frozenset({
    "mdl",
    "mux",
    "mcm",
    "mpa",
    "mrl",
    "mdo",
    "mrg",  # fuente interna; vista cliente = /guia
})

# MKT, MAG y MSD son híbridos: ver is_*_path_public

# Prefijos de path bajo /docs/ que son públicos (además del índice).
_PUBLIC_DOCS_HUB_PREFIXES = (
    "css/",
    "release-notes/",
    "ecosystem/",
    "brandbook/",
    # MAG / MSD: solo índice/css públicos vía hub; chapters .md privados
    "mag/css/",
    "msd/css/",
    # Solo activos públicos de MKT (no capítulos ni índice del manual)
    "mkt/assets/",
    "mkt/mtx-case/",
    # Material de integración expuesto vía MSD
    "api/collections/",
)

_PUBLIC_DOCS_HUB_FILES = frozenset({
    "README.md",
    "NOMENCLATURE.md",
    "VERSIONS.md",
    "VERSIONING.md",
    "changelog.md",
    "CROSS-REFERENCES.md",
    "DOCUMENTATION-PRODUCT.md",
    "api/README.md",
    "api/openapi.v1.yaml",
    "api/integrator-guide.md",
    "api/webhooks.md",
    "api/api-contract.md",
    "api/examples.md",
    "api/changelog.md",
    "api/collections/README.md",
})

_PUBLIC_DOCS_HUB_FILE_PREFIXES = (
    "RELEASE-v",
)

# Prefijos bajo /docs/ siempre privados (ingeniería / secreto comercial).
_PRIVATE_DOCS_HUB_PREFIXES = (
    "developer/",
    "handbook/",
    "madr/",
    "security/",
    "alignment/",
    "maintenance-execution/",
    "maintenance-automation/",
    "asset-health/",
    "publishing/",  # blueprint despliegue / DevOps (MkDocs · SSO · checklists)
    "mcm/",
    "mdl/",
    "mux/",
    "mpa/",
    "mrl/",
    "mdo/",
    "mrg/",
    "mag/chapters/",
    "msd/chapters/",
    # Biblia MKT y capítulos normativos (vía hub)
    "mkt/chapters/",
    "mkt/css/",
)


def docs_access_policy() -> str:
    raw = (current_app.config.get("DOCS_ACCESS_POLICY") or "hybrid").strip().lower()
    if raw in ("hybrid", "open", "locked"):
        return raw
    return "hybrid"


def _has_docs_credentials() -> bool:
    if getattr(current_user, "is_authenticated", False):
        return True
    if session.get("platform_admin"):
        return True
    return False


def is_mkt_path_public(rel_path: str | None = None, *, endpoint: str | None = None) -> bool:
    """Activos de captación públicos; capítulos y portal MKT privados.

    Público: /mkt/assets/* · /mkt/mtx-case/*
    Privado: /mkt/ · /mkt/chapters/* · /mkt/css/* · README, strategy, etc.
    """
    ep = endpoint or ""
    if ep in ("mkt.assets", "mkt.mtx_case"):
        return True
    if ep in ("mkt.index", "mkt.index_no_slash", "mkt.css", "mkt.chapters"):
        return False
    if ep == "mkt.docs_file":
        p = (rel_path or "").replace("\\", "/").lstrip("/")
        # Fail-closed: solo metadatos no se exponen; el manual es interno
        return False
    # Fallback por path si se llama sin endpoint
    p = (rel_path or "").replace("\\", "/").lstrip("/")
    if p.startswith("assets/") or p.startswith("mtx-case/"):
        return True
    return False


def is_docs_hub_path_public(rel_path: str) -> bool:
    """True si el archivo bajo /docs/<rel_path> puede servirse sin login."""
    p = (rel_path or "").replace("\\", "/").lstrip("/")
    if not p:
        return True
    for prefix in _PRIVATE_DOCS_HUB_PREFIXES:
        if p.startswith(prefix):
            return False
    # Meta MKT / MAG fuente bajo hub
    if p == "mkt" or p.startswith("mkt/"):
        if p.startswith("mkt/assets/") or p.startswith("mkt/mtx-case/"):
            return True
        return False
    if p == "mag" or p.startswith("mag/"):
        if p == "mag/index.html" or p.startswith("mag/css/"):
            return True
        return False
    if p == "msd" or p.startswith("msd/"):
        if p == "msd/index.html" or p.startswith("msd/css/"):
            return True
        return False
    for prefix in _PUBLIC_DOCS_HUB_PREFIXES:
        if p.startswith(prefix):
            return True
    if p in _PUBLIC_DOCS_HUB_FILES:
        return True
    for prefix in _PUBLIC_DOCS_HUB_FILE_PREFIXES:
        if p.startswith(prefix):
            return True
    if p.startswith("api/") and "SPRINT" in p.upper():
        return False
    if p.startswith("api/"):
        private_api = (
            "architecture.md",
            "charter.md",
            "roadmap.md",
            "permissions-plans.md",
        )
        if any(p.endswith(name) or p == f"api/{name}" for name in private_api):
            return False
        return True
    return False


def blueprint_requires_auth(blueprint_name: str | None) -> bool:
    """Decide si el blueprint documental exige login según la política."""
    policy = docs_access_policy()
    if policy == "open":
        return False
    if policy == "locked":
        if blueprint_name in PUBLIC_DOC_BLUEPRINTS or blueprint_name in PRIVATE_DOC_BLUEPRINTS:
            return True
        if blueprint_name in ("docs_hub", "mkt", "mag", "msd"):
            return True
        return False

    if blueprint_name in PRIVATE_DOC_BLUEPRINTS:
        return True
    if blueprint_name in PUBLIC_DOC_BLUEPRINTS:
        return False
    # mkt, mag, msd y docs_hub se resuelven por path/endpoint
    return False


def docs_hub_requires_auth(rel_path: str) -> bool:
    policy = docs_access_policy()
    if policy == "open":
        return False
    if policy == "locked":
        return True
    return not is_docs_hub_path_public(rel_path)


def is_mag_path_public(rel_path: str | None = None, *, endpoint: str | None = None) -> bool:
    """Índice + guía HTML públicos; .md crudo solo con sesión (la vista redirige).

    Público: /mag/ · /mag/css/* · /mag/guide/<slug>
             /mag/chapters/* también pasa el gate (la ruta redirige a /guide)
    Privado efectivo: contenido Markdown (solo tras login en la vista)
    """
    ep = endpoint or ""
    if ep in (
        "mag.index",
        "mag.index_no_slash",
        "mag.css",
        "mag.guide",
        "mag.chapters",  # redirige a guide si no hay sesión
    ):
        return True
    if ep == "mag.docs_file":
        return False
    p = (rel_path or "").replace("\\", "/").lstrip("/")
    if p.startswith("css/") or p == "index.html" or not p:
        return True
    if p.startswith("guide/") or p.startswith("chapters/"):
        return True
    return False


def mkt_requires_auth(*, endpoint: str, rel_path: str | None = None) -> bool:
    policy = docs_access_policy()
    if policy == "open":
        return False
    if policy == "locked":
        return True
    return not is_mkt_path_public(rel_path, endpoint=endpoint)


def mag_requires_auth(*, endpoint: str, rel_path: str | None = None) -> bool:
    policy = docs_access_policy()
    if policy == "open":
        return False
    if policy == "locked":
        return True
    return not is_mag_path_public(rel_path, endpoint=endpoint)


def is_msd_path_public(rel_path: str | None = None, *, endpoint: str | None = None) -> bool:
    """Índice + guía HTML públicos; .md / strategy / NOMENCLATURE solo con sesión.

    Público: /msd/ · /msd/css/* · /msd/guide/<slug> · /msd/openapi · /msd/collections
             /msd/chapters/* pasa el gate (la ruta redirige a /guide)
    Privado efectivo: Markdown fuente y meta interna
    """
    ep = endpoint or ""
    if ep in (
        "msd.index",
        "msd.index_no_slash",
        "msd.css",
        "msd.guide",
        "msd.chapters",
        "msd.openapi_portal",
        "msd.collections_portal",
    ):
        return True
    if ep == "msd.docs_file":
        return False
    p = (rel_path or "").replace("\\", "/").lstrip("/")
    if p.startswith("css/") or p == "index.html" or not p:
        return True
    if p.startswith("guide/") or p.startswith("chapters/"):
        return True
    return False


def msd_requires_auth(*, endpoint: str, rel_path: str | None = None) -> bool:
    policy = docs_access_policy()
    if policy == "open":
        return False
    if policy == "locked":
        return True
    return not is_msd_path_public(rel_path, endpoint=endpoint)


def _login_redirect():
    flash("Esta documentación es interna. Inicia sesión para continuar.", "info")
    return redirect(url_for("main.login", next=request.url))


def enforce_docs_access():
    """Hook before_request para blueprints documentales."""
    endpoint = request.endpoint or ""
    if not endpoint or endpoint == "static":
        return None

    blueprint = endpoint.split(".", 1)[0] if "." in endpoint else None

    if blueprint == "docs_hub":
        if endpoint in ("docs_hub.index", "docs_hub.index_no_slash", "docs_hub.css"):
            if docs_access_policy() == "locked" and not _has_docs_credentials():
                return _login_redirect()
            return None
        if endpoint == "docs_hub.docs_file":
            rel = (request.view_args or {}).get("filename") or ""
            if docs_hub_requires_auth(rel) and not _has_docs_credentials():
                return _login_redirect()
            return None
        return None

    # MKT híbrido: assets + MTX-CASE públicos; capítulos e índice privados
    if blueprint == "mkt":
        rel = (request.view_args or {}).get("filename")
        if mkt_requires_auth(endpoint=endpoint, rel_path=rel) and not _has_docs_credentials():
            return _login_redirect()
        return None

    # MAG híbrido: índice + /guide públicos; chapters .md privados
    if blueprint == "mag":
        rel = (request.view_args or {}).get("filename") or (request.view_args or {}).get("slug")
        if mag_requires_auth(endpoint=endpoint, rel_path=rel) and not _has_docs_credentials():
            return _login_redirect()
        return None

    # MSD híbrido: índice + /guide públicos; strategy / NOMENCLATURE / .md privados
    if blueprint == "msd":
        rel = (request.view_args or {}).get("filename") or (request.view_args or {}).get("slug")
        if msd_requires_auth(endpoint=endpoint, rel_path=rel) and not _has_docs_credentials():
            return _login_redirect()
        return None

    if blueprint in ("brand_book_legacy", "ux_legacy"):
        return None

    if not blueprint_requires_auth(blueprint):
        return None

    if not _has_docs_credentials():
        return _login_redirect()
    return None


def register_docs_access(app) -> None:
    """Registra el gate híbrido a nivel de aplicación."""
    app.before_request(enforce_docs_access)
