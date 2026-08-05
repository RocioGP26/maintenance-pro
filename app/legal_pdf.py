"""Exportación PDF de documentos legales públicos (ReportLab · marca Roustix)."""

from __future__ import annotations

import re
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.public_legal import get_legal_page, load_legal_markdown
from app.timezone_utils import DEFAULT_TZ, timezone_obj


def _legal_today() -> date:
    """Fecha civil en zona Colombia (evita desfase UTC del servidor)."""
    return datetime.now(timezone_obj(tz_name=DEFAULT_TZ)).date()

_ROOT = Path(__file__).resolve().parents[1]
# Mismo arte del paquete piloto DOCX, aplanado sobre blanco (ReportLab no maneja bien RGBA)
_CORPORATE_LOGO = _ROOT / "static" / "img" / "roustix-logo-pdf.png"
_CORPORATE_LOGO_SOURCE = _ROOT / "static" / "img" / "roustix-logo-docx.png"

# Paleta alineada al paquete documental DOCX (build_pilot_linkage_act)
_NAVY = colors.HexColor("#0A2540")
_BLUE = colors.HexColor("#185FA5")
_LIGHT_BLUE = colors.HexColor("#E8EEF5")
_PALE_BLUE = colors.HexColor("#F3F7FB")
_GRAY = colors.HexColor("#5B6472")
_BORDER = colors.HexColor("#D8DEE7")
_BLACK = colors.HexColor("#1D2733")
_GOLD = colors.HexColor("#8A6400")
_WARN_BG = colors.HexColor("#FFF8E8")
_SOFT = colors.HexColor("#F8FAFC")

_CONTENT_WIDTH = 178 * mm
_HEADER_LABEL = "ROUSTIX  ·  PAQUETE DOCUMENTAL"


class _LegalPageCanvas(Canvas):
    """Canvas que imprime cabecera de marca y «Página Y de X»."""

    def __init__(self, *args, footer_left: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._footer_left = footer_left
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_chrome(total)
            super().showPage()
        super().save()

    def _draw_chrome(self, total: int) -> None:
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(_GRAY)
        self.drawRightString(A4[0] - 16 * mm, A4[1] - 10 * mm, _HEADER_LABEL)
        underline_w = self.stringWidth("ROUSTIX", "Helvetica-Bold", 8)
        full_w = self.stringWidth(_HEADER_LABEL, "Helvetica-Bold", 8)
        x_start = (A4[0] - 16 * mm) - full_w
        self.setStrokeColor(_BLUE)
        self.setLineWidth(0.7)
        self.line(x_start, A4[1] - 11 * mm, x_start + underline_w, A4[1] - 11 * mm)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(_GRAY)
        self.drawString(16 * mm, 8 * mm, self._footer_left)
        self.drawRightString(
            A4[0] - 16 * mm,
            8 * mm,
            f"Página {self._pageNumber} de {total}",
        )
        self.restoreState()


def export_legal_pdf(slug: str) -> tuple[bytes, str]:
    page = get_legal_page(slug)
    if page is None:
        raise ValueError(f"Documento legal desconocido: {slug}")

    md = load_legal_markdown(slug)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"{page.code} · {page.title}",
        author="Roustix",
        subject=page.description,
    )
    styles = _styles()
    story: list = []
    story.extend(_branded_cover(page, styles))
    story.extend(_markdown_to_flowables(md, styles))
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=_BORDER))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        escape(
            f"Generado desde roustix.com · {_legal_today().isoformat()} · "
            f"{page.code} v{page.version}"
        ),
        styles["footer"],
    ))

    footer_left = f"{page.code} · Versión {page.version}"

    def _canvas_maker(filename_or_buffer, **kwargs):
        return _LegalPageCanvas(filename_or_buffer, footer_left=footer_left, **kwargs)

    doc.build(story, canvasmaker=_canvas_maker)
    filename = f"Roustix-{page.code}-{page.slug}-v{page.version}.pdf"
    return buffer.getvalue(), filename


def _branded_cover(page, styles: dict) -> list:
    """Portada alineada al paquete documental Word (logo + meta + callouts)."""
    blocks: list = []

    logo = _logo_image()
    if logo is not None:
        blocks.append(logo)
        blocks.append(Spacer(1, 4 * mm))
    else:
        blocks.append(Paragraph(escape("roustix"), styles["wordmark"]))
        blocks.append(Paragraph(escape("GESTIÓN INTELIGENTE DE ACTIVOS"), styles["tagline"]))
        blocks.append(Spacer(1, 3 * mm))

    blocks.append(Paragraph(escape(page.title), styles["title"]))
    blocks.append(Paragraph(escape(page.description), styles["subtitle"]))
    blocks.append(Spacer(1, 4 * mm))
    blocks.append(_meta_table(page, styles))
    blocks.append(Spacer(1, 3 * mm))
    blocks.append(_callout(
        "Propósito",
        "Documento oficial del Sistema Documental Legal de Roustix. "
        "Regula el uso de la plataforma o el tratamiento de datos según el código indicado. "
        "Debe completarse la identificación del prestador y revisarse jurídicamente antes de exigirse como vigente.",
        styles,
        fill=_PALE_BLUE,
        accent=_BLUE,
    ))
    if page.is_draft:
        blocks.append(Spacer(1, 2.5 * mm))
        blocks.append(_callout(
            "Advertencia",
            "Borrador · no vigente. Roustix es actualmente un nombre comercial. "
            "Este texto está en revisión jurídica e identificación del responsable; "
            "no constituye aún el documento aplicable al servicio. "
            "En la versión 1.0 Vigente, esta advertencia se reemplazará por la "
            "identificación jurídica definitiva del Prestador.",
            styles,
            fill=_WARN_BG,
            accent=_GOLD,
        ))
    blocks.append(Spacer(1, 5 * mm))
    return blocks


def _logo_image() -> Image | None:
    logo_path = _ensure_pdf_logo()
    if logo_path is None:
        return None
    from reportlab.lib.utils import ImageReader

    # Forzar proporción real: ReportLab, si solo recibe width, usa
    # imageHeight en puntos y estira el logo en vertical.
    px_w, px_h = ImageReader(str(logo_path)).getSize()
    width = 66 * mm  # ~2.6 in, igual que el paquete DOCX piloto
    height = width * (float(px_h) / float(px_w))
    img = Image(str(logo_path), width=width, height=height)
    img.hAlign = "LEFT"
    return img


def _ensure_pdf_logo() -> Path | None:
    """Usa PNG del piloto aplanado a RGB; regenera si falta o está desactualizado."""
    if _CORPORATE_LOGO.is_file():
        if (
            not _CORPORATE_LOGO_SOURCE.is_file()
            or _CORPORATE_LOGO.stat().st_mtime >= _CORPORATE_LOGO_SOURCE.stat().st_mtime
        ):
            return _CORPORATE_LOGO
    if not _CORPORATE_LOGO_SOURCE.is_file():
        return _CORPORATE_LOGO if _CORPORATE_LOGO.is_file() else None
    try:
        from PIL import Image as PILImage
    except ImportError:
        # Fallback: ReportLab con mask auto sobre el PNG del piloto
        return _CORPORATE_LOGO_SOURCE

    src = PILImage.open(_CORPORATE_LOGO_SOURCE).convert("RGBA")
    # 2× para nitidez en PDF
    src = src.resize((src.width * 2, src.height * 2), PILImage.Resampling.LANCZOS)
    canvas = PILImage.new("RGB", src.size, (255, 255, 255))
    canvas.paste(src, mask=src.split()[3])
    _CORPORATE_LOGO.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(_CORPORATE_LOGO, "PNG", optimize=True)
    return _CORPORATE_LOGO


def _meta_table(page, styles: dict) -> Table:
    label = styles["meta_label"]
    value = styles["meta_value"]
    data = [
        [
            Paragraph("Código", label),
            Paragraph(escape(page.code), value),
            Paragraph("Versión", label),
            Paragraph(escape(page.version), value),
        ],
        [
            Paragraph("Estado", label),
            Paragraph(escape(page.status_label), value),
            Paragraph("Fecha", label),
            Paragraph(escape(_legal_today().strftime("%d / %m / %Y")), value),
        ],
    ]
    table = Table(data, colWidths=[28 * mm, 61 * mm, 28 * mm, 61 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _LIGHT_BLUE),
        ("BACKGROUND", (2, 0), (2, -1), _LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, _BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _callout(title: str, body: str, styles: dict, *, fill, accent) -> KeepTogether:
    inner = Paragraph(
        f"<b>{escape(title)}</b><br/>{_inline_pdf(body)}",
        styles["callout"],
    )
    table = Table([[inner]], colWidths=[_CONTENT_WIDTH])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#1D2733")),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([table])


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "wordmark": ParagraphStyle(
            "leg-wordmark",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=_NAVY,
            alignment=TA_LEFT,
            spaceAfter=1,
        ),
        "tagline": ParagraphStyle(
            "leg-tagline",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            textColor=_BLUE,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "title": ParagraphStyle(
            "leg-title",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=_NAVY,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "subtitle": ParagraphStyle(
            "leg-subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=_GRAY,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "meta_label": ParagraphStyle(
            "leg-meta-label",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=_NAVY,
        ),
        "meta_value": ParagraphStyle(
            "leg-meta-value",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=_BLACK,
        ),
        "callout": ParagraphStyle(
            "leg-callout",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=_BLACK,
        ),
        "h1": ParagraphStyle(
            "leg-h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=_NAVY,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "h2": ParagraphStyle(
            "leg-h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=_NAVY,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "h3": ParagraphStyle(
            "leg-h3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=_NAVY,
            spaceBefore=6,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "leg-body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_JUSTIFY,
            textColor=_BLACK,
            spaceAfter=5,
        ),
        "quote": ParagraphStyle(
            "leg-quote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=_GRAY,
            leftIndent=6,
            spaceAfter=6,
        ),
        "li": ParagraphStyle(
            "leg-li",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11.5,
            alignment=TA_LEFT,
            textColor=_BLACK,
        ),
        "th": ParagraphStyle(
            "leg-th",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=_NAVY,
        ),
        "td": ParagraphStyle(
            "leg-td",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9.5,
            textColor=_BLACK,
        ),
        "footer": ParagraphStyle(
            "leg-footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7,
            textColor=_GRAY,
            alignment=TA_CENTER,
        ),
        "code": ParagraphStyle(
            "leg-code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=9.5,
            backColor=_SOFT,
            spaceAfter=5,
        ),
        "header_right": ParagraphStyle(
            "leg-header-right",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=_GRAY,
            alignment=TA_RIGHT,
        ),
    }



def _markdown_to_flowables(md: str, styles: dict) -> list:
    lines = md.splitlines()
    story: list = []
    i = 0
    para: list[str] = []
    in_code = False
    code_buf: list[str] = []

    def flush_para() -> None:
        if not para:
            return
        raw = " ".join(s.strip() for s in para)
        story.append(Paragraph(_inline_pdf(raw), styles["body"]))
        para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            if in_code:
                story.append(Paragraph(escape("\n".join(code_buf)).replace("\n", "<br/>"), styles["code"]))
                code_buf.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            flush_para()
            table_lines = [stripped]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(_table_flowable(table_lines, styles))
            story.append(Spacer(1, 2 * mm))
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            flush_para()
            level = len(heading.group(1))
            key = "h1" if level <= 1 else ("h2" if level == 2 else "h3")
            story.append(Paragraph(_inline_pdf(heading.group(2)), styles[key]))
            i += 1
            continue

        if stripped.startswith("> "):
            flush_para()
            quote = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            story.append(Paragraph(_inline_pdf(" ".join(quote)), styles["quote"]))
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            story.append(ListFlowable(
                [ListItem(Paragraph(_inline_pdf(it), styles["li"]), leftIndent=8, bulletColor=_NAVY) for it in items],
                bulletType="bullet",
                start="•",
                leftIndent=12,
                bulletFontSize=8,
                spaceAfter=4,
            ))
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            story.append(ListFlowable(
                [ListItem(Paragraph(_inline_pdf(it), styles["li"]), leftIndent=8) for it in items],
                bulletType="1",
                leftIndent=14,
                spaceAfter=4,
            ))
            continue

        if stripped == "---":
            flush_para()
            story.append(Spacer(1, 1 * mm))
            story.append(HRFlowable(width="100%", thickness=0.4, color=_BORDER))
            story.append(Spacer(1, 2 * mm))
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return story


def _table_flowable(rows: list[str], styles: dict) -> Table:
    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip("|").split("|")]

    header = cells(rows[0])
    body = [cells(r) for r in rows[1:]]
    cols = len(header)
    usable = 178 * mm
    col_w = usable / max(cols, 1)

    data = [[Paragraph(_inline_pdf(c), styles["th"]) for c in header]]
    for row in body:
        while len(row) < cols:
            row.append("")
        data.append([Paragraph(_inline_pdf(c), styles["td"]) for c in row[:cols]])

    table = Table(data, colWidths=[col_w] * cols, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _SOFT),
        ("GRID", (0, 0), (-1, -1), 0.35, _BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def _inline_pdf(text: str) -> str:
    """Markdown inline → markup ReportLab (<b>, <i>, <font name="Courier">)."""
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', text)
    # Enlaces: solo conservar la etiqueta visible
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text
