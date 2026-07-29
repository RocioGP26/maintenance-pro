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


def test_set_addon_stg_2g_updates_quota():
    from app.storage_quota import (
        ADDON_STG_2G_MB,
        has_addon_stg_2g,
        quota_mb_efectiva,
        set_addon_stg_2g,
    )

    empresa = SimpleNamespace(
        id=3,
        plan_activo=SimpleNamespace(plan="basico"),
        storage_addon_mb=0,
    )
    with patch("app.platform_service.plan_meta", return_value={"storage_mb": 1024}):
        assert quota_mb_efectiva(empresa) == 1024
        set_addon_stg_2g(empresa, active=True)
        assert has_addon_stg_2g(empresa)
        assert empresa.storage_addon_mb == ADDON_STG_2G_MB
        assert quota_mb_efectiva(empresa) == 1024 + ADDON_STG_2G_MB
        set_addon_stg_2g(empresa, active=False)
        assert not has_addon_stg_2g(empresa)
        assert quota_mb_efectiva(empresa) == 1024


def test_storage_uso_tenant_warn_and_addon_copy():
    empresa = SimpleNamespace(
        id=42,
        razon_social="Empresa ABC",
        plan_activo=SimpleNamespace(plan="basico"),
        storage_addon_mb=0,
    )
    used = int(1024 * 1024 * 1024 * 0.85)  # 85% de 1 GB
    with (
        patch("app.storage_quota.quota_mb_efectiva", return_value=1024),
        patch("app.platform_service.storage_bytes_empresa", return_value=used),
        patch("app.platform_service.plan_meta", return_value={"label": "Start", "storage_mb": 1024}),
    ):
        uso = storage_uso_tenant(empresa)
    assert uso is not None
    assert uso["warn"] is True
    assert uso["pct"] == 85
    assert uso["empresa_nombre"] == "Empresa ABC"
    assert uso["plan_label"] == "Start"
    assert uso["quota_label"] == "1 GB"
    assert uso["addon_sku"] == "ADD-STG-2G"
    assert uso["addon_label"] == "+2 GB"
    assert "100.000" in uso["addon_price_label"]


def test_storage_uso_tenant_no_warn_below_threshold():
    empresa = SimpleNamespace(
        id=7,
        razon_social="Acme",
        plan_activo=SimpleNamespace(plan="grow"),
        storage_addon_mb=0,
    )
    used = int(5 * 1024 * 1024 * 1024 * 0.5)  # 50% de 5 GB
    with (
        patch("app.storage_quota.quota_mb_efectiva", return_value=5 * 1024),
        patch("app.platform_service.storage_bytes_empresa", return_value=used),
        patch("app.platform_service.plan_meta", return_value={"label": "Business", "storage_mb": 5120}),
    ):
        uso = storage_uso_tenant(empresa)
    assert uso is not None
    assert uso["warn"] is False
    assert uso["pct"] == 50
    assert uso["quota_label"] == "5 GB"


def test_format_quota_mb_friendly():
    from app.platform_service import _format_quota_mb

    assert _format_quota_mb(1024) == "1 GB"
    assert _format_quota_mb(5120) == "5 GB"
    assert _format_quota_mb(500) == "500 MB"
