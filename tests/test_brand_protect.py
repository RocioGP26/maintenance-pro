"""Tests · protección de marcas (translate=no)."""

from app.brand_protect import protect_brands, wrap_notranslate


def test_wrap_notranslate_attrs():
    html = str(wrap_notranslate("Start"))
    assert 'translate="no"' in html
    assert 'class="notranslate"' in html
    assert ">Start<" in html


def test_protect_brands_keeps_long_module_names():
    html = str(protect_brands("Activa Roustix Maintenance o Roustix Inventory"))
    assert "Roustix Maintenance" in html
    assert "Roustix Inventory" in html
    assert html.count('translate="no"') >= 2


def test_protect_brands_planes_label():
    html = str(protect_brands("Sección Planes de la landing"))
    assert ">Planes<" in html
    assert 'translate="no"' in html
