"""Tests del motor PDF MRL · Sprint 15.3."""

from __future__ import annotations

import unittest

from app.mrl import BasePdfExporter, PdfExporter
from app.mrl.metadata import build_sample_metadata


class TestMRLPdfEngine(unittest.TestCase):
    def test_generates_valid_pdf_with_all_base_blocks(self) -> None:
        exporter = BasePdfExporter(build_sample_metadata(), watermark="Borrador")
        exporter.add_title("Resumen operativo")
        exporter.add_kpis([("Activos", 12), ("Disponibilidad", "98 %")])
        exporter.add_spacer()
        exporter.add_table(["Código", "Estado"], [["EQ-001", "Operativo"]])
        content, filename = exporter.save()

        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertGreater(len(content), 1000)
        self.assertEqual(filename, "DOC-010-BATCH-20260710-20260710.pdf")

    def test_public_alias(self) -> None:
        self.assertIs(PdfExporter, BasePdfExporter)

    def test_engine_has_no_business_imports(self) -> None:
        import app.mrl.pdf.exporter as module

        with open(module.__file__, encoding="utf-8") as source:
            text = source.read()
        self.assertNotIn("inventario_comercial", text)
        self.assertNotIn("app.models", text)


if __name__ == "__main__":
    unittest.main()
