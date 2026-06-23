"""Utilidades para validación de URLs de redirección."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse


def is_safe_redirect(target: str, host_url: str) -> bool:
    if not target:
        return False
    ref = urlparse(host_url)
    test = urlparse(urljoin(host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc
