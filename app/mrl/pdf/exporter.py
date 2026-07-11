"""Motor PDF MRL · bloques reutilizables sobre ReportLab."""

from __future__ import annotations

from io import BytesIO
from typing import Sequence
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.mrl import colors, constants, typography
from app.mrl.metadata import MRLDocumentMeta
from app.mrl.pdf.base import build_kpi_row, build_table, paragraph_styles, pdf_color
from app.mrl.utils.dates import format_datetime_latam


class BasePdfExporter:
    """Exportador PDF componible, deliberadamente ajeno al negocio."""

    def __init__(self, meta: MRLDocumentMeta, *, watermark: str | None = None) -> None:
        self.meta = meta
        self.watermark = (watermark or "").strip().upper() or None
        self._story: list[object] = []

    def add_title(self, text: str) -> None:
        self._story.append(Paragraph(escape(text), paragraph_styles()["title"]))

    def add_paragraph(self, text: str) -> None:
        self._story.append(Paragraph(escape(text), paragraph_styles()["body"]))

    def add_spacer(self, height_mm: float = 4) -> None:
        self._story.append(Spacer(1, height_mm * mm))

    def add_table(
        self, headers: Sequence[object], rows: Sequence[Sequence[object]], *,
        column_widths: Sequence[float] | None = None,
    ) -> None:
        self._story.append(build_table(headers, rows, column_widths=column_widths))

    def add_kpis(self, items: Sequence[tuple[str, object]]) -> None:
        if items:
            self._story.append(build_kpi_row(items))

    def save(self) -> tuple[bytes, str]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=constants.PDF_MARGIN_LEFT_MM * mm,
            rightMargin=constants.PDF_MARGIN_RIGHT_MM * mm,
            topMargin=(constants.PDF_MARGIN_TOP_MM + constants.PDF_HEADER_HEIGHT_MM) * mm,
            bottomMargin=(constants.PDF_MARGIN_BOTTOM_MM + constants.PDF_FOOTER_HEIGHT_MM) * mm,
            title=self.meta.title, author="Maintix",
            subject=self.meta.doc_code, creator=f"Maintix MRL v{self.meta.mrl_version}",
        )
        story = self._story or [Paragraph(self.meta.title, paragraph_styles()["title"])]
        doc.build(story, onFirstPage=self._draw_page, onLaterPages=self._draw_page)
        date = self.meta.generated_at.strftime("%Y%m%d")
        safe_instance = "".join(c if c.isalnum() or c in "-_" else "-" for c in self.meta.instance_code)
        return buffer.getvalue(), f"{self.meta.doc_code}-{safe_instance}-{date}.pdf"

    def _draw_page(self, canvas: Canvas, doc: SimpleDocTemplate) -> None:
        canvas.saveState()
        width, height = A4
        left = constants.PDF_MARGIN_LEFT_MM * mm
        right = width - constants.PDF_MARGIN_RIGHT_MM * mm
        canvas.setTitle(self.meta.title)
        canvas.setAuthor("Maintix")
        canvas.setCreator(f"Maintix MRL v{self.meta.mrl_version}")
        canvas.setSubject(self.meta.doc_code)

        canvas.setFillColor(pdf_color(colors.PRIMARY))
        canvas.setFont(f"{typography.PDF_FONT_FAMILY}-Bold", typography.PDF_FONT_SIZES.title)
        canvas.drawString(left, height - 22 * mm, self.meta.empresa_nombre)
        canvas.setFillColor(pdf_color(colors.BODY))
        canvas.setFont(typography.PDF_FONT_FAMILY, typography.PDF_FONT_SIZES.meta)
        canvas.drawString(left, height - 28 * mm, self.meta.title)
        canvas.setFillColor(pdf_color(colors.MUTED))
        canvas.drawRightString(right, height - 22 * mm, f"{self.meta.doc_code} · {self.meta.instance_code}")
        canvas.drawRightString(right, height - 28 * mm, f"Página {doc.page}")
        canvas.setStrokeColor(pdf_color(colors.PRIMARY))
        canvas.setLineWidth(0.7)
        canvas.line(left, height - 33 * mm, right, height - 33 * mm)

        footer_y = 12 * mm
        generated = format_datetime_latam(self.meta.generated_at, self.meta.timezone_name)
        canvas.setFillColor(pdf_color(colors.MUTED))
        canvas.setFont(typography.PDF_FONT_FAMILY, typography.PDF_FONT_SIZES.footer)
        canvas.drawString(left, footer_y, f"{constants.GENERATED_BY_LABEL} · {generated}")
        canvas.drawRightString(right, footer_y, f"MRL v{self.meta.mrl_version} · Página {doc.page}")

        if self.watermark:
            canvas.saveState()
            canvas.setFillColor(pdf_color(colors.MUTED), alpha=0.12)
            canvas.setFont(f"{typography.PDF_FONT_FAMILY}-Bold", 52)
            canvas.translate(width / 2, height / 2)
            canvas.rotate(35)
            canvas.drawCentredString(0, 0, self.watermark)
            canvas.restoreState()
        canvas.restoreState()


PdfExporter = BasePdfExporter

__all__ = ["BasePdfExporter", "PdfExporter"]
