from markupsafe import Markup

from app.text_encoding import texto_legible


def test_corrige_acentos_reemplazados_por_interrogacion():
    assert texto_legible("L?nea de producci?n A") == "Línea de producción A"
    assert texto_legible("Ubicaci?n y t?cnico") == "Ubicación y técnico"


def test_corrige_mojibake_utf8_y_conserva_markup():
    assert texto_legible("InformaciÃ³n") == "Información"
    resultado = texto_legible(Markup("<strong>Ubicaci?n</strong>"))
    assert isinstance(resultado, Markup)
    assert resultado == Markup("<strong>Ubicación</strong>")
