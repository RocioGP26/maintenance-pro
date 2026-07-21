"""Smoke test MRL · Sprint 15.1 — sin generación de archivos."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

import app.mrl as mrl
from app.mrl import colors, constants, typography
from app.mrl.metadata import MRLDocumentMeta, build_sample_metadata
from app.mrl.styles import MRLStyle
from app.mrl.utils.dates import format_datetime_latam


class TestMRLSmoke(unittest.TestCase):
    def test_import_public_api(self) -> None:
        self.assertEqual(mrl.MRL_VERSION, "1.1")
        self.assertIs(mrl.colors, colors)
        self.assertIs(mrl.constants, constants)
        self.assertIs(mrl.typography, typography)
        self.assertIs(mrl.MRLStyle, MRLStyle)
        self.assertIs(mrl.ExcelExporter, mrl.BaseExcelExporter)
        self.assertIs(mrl.PdfExporter, mrl.BasePdfExporter)

    def test_colors_official_tokens(self) -> None:
        self.assertEqual(colors.PRIMARY, "#042C53")
        self.assertEqual(colors.HEADER, colors.PRIMARY)
        self.assertEqual(colors.SUCCESS, "#38A169")
        self.assertEqual(colors.DANGER, "#E53E3E")
        self.assertIn(colors.PRIMARY, colors.ALL_COLORS)

    def test_typography_families(self) -> None:
        self.assertEqual(typography.EXCEL_FONT_FAMILY, "Calibri")
        self.assertEqual(typography.PDF_FONT_FAMILY, "Helvetica")
        self.assertEqual(typography.PDF_FONT_SIZES.title, 16)
        self.assertEqual(typography.EXCEL_FONT_SIZES.title, 14)

    def test_constants_layout(self) -> None:
        self.assertEqual(constants.EXCEL_HEADER_ROW, 7)
        self.assertEqual(constants.EXCEL_DATA_START_ROW, 8)
        self.assertGreater(constants.LOGO_MAX_WIDTH_MM, 0)

    def test_metadata_creation_and_fields(self) -> None:
        meta = build_sample_metadata()
        self.assertIsInstance(meta, MRLDocumentMeta)
        self.assertEqual(meta.doc_code, "DOC-010")
        self.assertEqual(meta.tenant, meta.empresa_id)
        self.assertEqual(meta.documento, "DOC-010")
        self.assertEqual(meta.sistema, "Roustix")
        self.assertIn("Empresa Demo", meta.empresa_nombre)
        payload = meta.as_dict()
        self.assertEqual(payload["tenant"], 1)
        self.assertEqual(payload["generado_por"], "Roustix")

    def test_metadata_rejects_invalid_doc(self) -> None:
        with self.assertRaises(ValueError):
            MRLDocumentMeta(
                doc_code="INVALID",
                instance_code="X-1",
                module="Test",
                title="T",
                empresa_id=1,
                empresa_nombre="Co",
                generated_at=datetime.now(timezone.utc),
                timezone_name="America/Bogota",
            )

    def test_mrl_style_blocks_load(self) -> None:
        meta = build_sample_metadata()
        header = MRLStyle.header(meta)
        table = MRLStyle.table()
        kpi = MRLStyle.kpi()
        footer = MRLStyle.footer(meta)

        self.assertEqual(header.block_id, constants.BLOCK_HEADER)
        self.assertEqual(table.header_background, colors.PRIMARY)
        self.assertEqual(kpi.value_color, colors.PRIMARY)
        self.assertIn("MRL v", footer.mrl_version)

        bundle = MRLStyle.bundle(meta)
        self.assertIn("header", bundle)
        self.assertIn("meta", bundle)

    def test_semantic_status_colors(self) -> None:
        self.assertEqual(MRLStyle.semantic_status("ok"), colors.SUCCESS)
        self.assertEqual(MRLStyle.semantic_status("critico"), colors.DANGER)
        self.assertEqual(MRLStyle.semantic_status("advertencia"), colors.WARNING)

    def test_format_datetime_latam(self) -> None:
        dt = datetime(2026, 7, 10, 20, 30, tzinfo=timezone.utc)
        text = format_datetime_latam(dt, "America/Bogota")
        self.assertRegex(text, r"\d{2}/\d{2}/2026 \d{2}:\d{2}")

    def test_no_business_module_imports(self) -> None:
        import app.mrl.colors as mod_colors
        import app.mrl.metadata as mod_meta
        import app.mrl.styles as mod_styles

        sources = (
            mod_colors.__file__,
            mod_meta.__file__,
            mod_styles.__file__,
        )
        for path in sources:
            self.assertIsNotNone(path)
            with open(path, encoding="utf-8") as fh:
                source = fh.read()
            self.assertNotIn("inventario_comercial", source)
            self.assertNotIn("models", source)


if __name__ == "__main__":
    unittest.main()
