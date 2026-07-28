"""Smoke HTTP externo contra una instancia real de Roustix."""

from __future__ import annotations

import os
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

import pyotp


BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def _opener():
    return build_opener(HTTPCookieProcessor(CookieJar()))


def _request(opener, path: str, *, data: dict[str, str] | None = None):
    encoded = urlencode(data).encode("utf-8") if data is not None else None
    request = Request(
        urljoin(f"{BASE_URL}/", path.lstrip("/")),
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"} if encoded else {},
    )
    try:
        return opener.open(request, timeout=15)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise AssertionError(f"{request.full_url} respondió {exc.code}: {body[:300]}") from exc


def _body(response) -> str:
    return response.read().decode("utf-8", errors="replace")


def _assert_path(response, expected: str, context: str) -> None:
    actual = urlparse(response.geturl()).path
    if actual != expected:
        raise AssertionError(
            f"{context}: se esperaba la ruta {expected!r}, pero se obtuvo {actual!r} "
            f"({response.geturl()})"
        )


def run() -> None:
    user_password = os.environ.get("E2E_USER_PASSWORD", "")
    platform_key = os.environ.get("PLATFORM_ADMIN_KEY", "")
    totp_secret = os.environ.get("PLATFORM_ADMIN_TOTP_SECRET", "")
    if not all((user_password, platform_key, totp_secret)):
        raise RuntimeError("Faltan credenciales efímeras requeridas por el smoke E2E.")

    public = _request(_opener(), "/")
    public_html = _body(public)
    assert public.status == 200
    assert "Roustix" in public_html
    assert public.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert public.headers.get("X-Content-Type-Options") == "nosniff"
    assert public.headers.get("Content-Security-Policy")

    tenant = _opener()
    login_page = _request(tenant, "/login")
    assert login_page.status == 200
    assert "Ingresa tus credenciales" in _body(login_page)

    dashboard = _request(
        tenant,
        "/login",
        data={
            "username": "ci_admin",
            "empresa_slug": "ci-e2e",
            "password": user_password,
        },
    )
    dashboard_html = _body(dashboard)
    _assert_path(dashboard, "/dashboard", "Login tenant")
    assert dashboard.status == 200
    assert "Sesión iniciada correctamente" in dashboard_html

    session_state = _request(tenant, "/sesion/estado")
    assert session_state.status == 200
    assert '"authenticated":true' in _body(session_state).replace(" ", "")

    logout = _request(tenant, "/logout", data={})
    _assert_path(logout, "/", "Logout tenant")
    protected = _request(tenant, "/dashboard")
    _assert_path(protected, "/login", "Ruta protegida sin sesión")

    platform = _opener()
    challenge = _request(platform, "/platform/login", data={"clave": platform_key})
    challenge_html = _body(challenge)
    _assert_path(challenge, "/platform/login", "Desafío MFA de plataforma")
    assert "Código de 6 dígitos" in challenge_html

    privileged = _request(
        platform,
        "/platform/login",
        data={"action": "totp", "totp": pyotp.TOTP(totp_secret).now()},
    )
    _assert_path(privileged, "/platform/empresas", "Login MFA de plataforma")
    assert privileged.status == 200
    assert "Empresas" in _body(privileged)

    print("E2E aprobado: público, login tenant, sesión, logout y MFA de plataforma.")


if __name__ == "__main__":
    run()
