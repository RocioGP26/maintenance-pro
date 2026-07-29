"""Tests · alerta storage ≥80% y upsell +2 GB (portal cliente)."""

from types import SimpleNamespace
from unittest.mock import patch

from app.platform_service import STORAGE_WARN_PCT, _storage_uso_pct, storage_uso_tenant


def test_storage_uso_pct_warn_threshold():
    quota_mb = 1024  # 1 GB
    used_79 = int(quota_mb * 1024 * 1024 * 0.79)
    used_80 = int(quota_mb * 1024 * 1024 * 0.80)
    assert _storage_uso_pct(used_79, quota_mb) == 79
    assert _storage_uso_pct(used_80, quota_mb) == 80
    assert STORAGE_WARN_PCT == 80


def test_storage_uso_tenant_none_without_empresa():
    assert storage_uso_tenant(None) is None


def test_storage_uso_tenant_warn_and_addon_copy():
    empresa = SimpleNamespace(id=42, plan_activo=SimpleNamespace(plan="basico"))
    used = int(1024 * 1024 * 1024 * 0.85)  # 85% de 1 GB
    with (
        patch("app.platform_service.plan_meta", return_value={"storage_mb": 1024}),
        patch("app.platform_service.storage_bytes_empresa", return_value=used),
    ):
        uso = storage_uso_tenant(empresa)
    assert uso is not None
    assert uso["warn"] is True
    assert uso["pct"] == 85
    assert uso["addon_sku"] == "ADD-STG-2G"
    assert uso["addon_label"] == "+2 GB"
    assert "100.000" in uso["addon_price_label"]


def test_storage_uso_tenant_no_warn_below_threshold():
    empresa = SimpleNamespace(id=7, plan_activo=SimpleNamespace(plan="grow"))
    used = int(5 * 1024 * 1024 * 1024 * 0.5)  # 50% de 5 GB
    with (
        patch("app.platform_service.plan_meta", return_value={"storage_mb": 5 * 1024}),
        patch("app.platform_service.storage_bytes_empresa", return_value=used),
    ):
        uso = storage_uso_tenant(empresa)
    assert uso is not None
    assert uso["warn"] is False
    assert uso["pct"] == 50
