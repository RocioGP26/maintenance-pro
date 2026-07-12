"""PDF imprimible de control de actividades para entregar al técnico."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
import re
from xml.sax.saxutils import escape

from flask import current_app, has_app_context
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, TableStyle


class _PageCountCanvas(Canvas):
    """Canvas que imprime Página X de Y."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont("Helvetica", 8)
            self.drawCentredString(landscape(A4)[0] / 2, 5 * mm, f"Página {self._pageNumber} de {total}")
            super().showPage()
        super().save()


_REEMPLAZOS_ACENTOS = {
    "inspecci?n": "inspección",
    "l?nea": "línea",
    "producci?n": "producción",
    "ubicaci?n": "ubicación",
    "descripci?n": "descripción",
    "observaci?n": "observación",
    "observaciones": "observaciones",
    "t?cnico": "técnico",
    "t?cnica": "técnica",
    "m?quina": "máquina",
    "el?ctrico": "eléctrico",
    "el?ctrica": "eléctrica",
    "lubricaci?n": "lubricación",
    "revisi?n": "revisión",
    "ejecuci?n": "ejecución",
    "correcci?n": "corrección",
    "v?lvula": "válvula",
    "v?lvulas": "válvulas",
    "m?ndez": "méndez",
}


def _normalizar_texto(value) -> str:
    text = "" if value is None else str(value)
    if "Ã" in text or "Â" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    for incorrecto, correcto in _REEMPLAZOS_ACENTOS.items():
        def reemplazar(match):
            original = match.group(0)
            if original.isupper():
                return correcto.upper()
            if original[:1].isupper():
                return correcto[:1].upper() + correcto[1:]
            return correcto

        text = re.sub(re.escape(incorrecto), reemplazar, text, flags=re.IGNORECASE)
    return text


def _p(value, style):
    return Paragraph(escape(_normalizar_texto(value)), style)


def _logo_empresa(empresa):
    if not has_app_context() or not (getattr(empresa, "logo", "") or "").strip():
        return ""
    value = empresa.logo.strip().replace("\\", "/").lstrip("/")
    if value.startswith("static/"):
        value = value[7:]
    path = (Path(current_app.static_folder) / value).resolve()
    static_root = Path(current_app.static_folder).resolve()
    if static_root not in path.parents or not path.is_file():
        return ""
    image = Image(str(path), width=23 * mm, height=13 * mm)
    image.hAlign = "CENTER"
    return image


def _fecha_hora(value) -> str:
    return value.strftime("%d/%m/%Y %H:%M") if value else ""


def export_control_actividades_pdf(empresa, orders, *, periodo_label: str = "") -> tuple[bytes, str]:
    """Genera el listado horizontal 71-MT-43 con las OT filtradas."""
    page = landscape(A4)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page,
        leftMargin=5 * mm,
        rightMargin=5 * mm,
        topMargin=5 * mm,
        bottomMargin=10 * mm,
        title="Control de actividades de mantenimiento",
        author=(empresa.razon_social or "Empresa"),
    )
    normal = ParagraphStyle("control-normal", fontName="Helvetica", fontSize=7.2, leading=8.5, alignment=TA_LEFT)
    center = ParagraphStyle("control-center", parent=normal, alignment=TA_CENTER)
    bold = ParagraphStyle("control-bold", parent=center, fontName="Helvetica-Bold", fontSize=8.5, leading=10)
    title = ParagraphStyle("control-title", parent=center, fontName="Helvetica-Bold", fontSize=10, leading=12)
    company = ParagraphStyle("control-company", parent=center, fontName="Helvetica-Bold", fontSize=10, leading=12)
    header = ParagraphStyle("control-header", parent=center, fontName="Helvetica-Bold", fontSize=7.4, leading=8.5)

    widths = [8, 23, 23, 16, 34, 30, 16, 21, 37, 36, 43]
    widths = [w * mm for w in widths]
    logo = _logo_empresa(empresa)
    empresa_nombre = (empresa.razon_social or "Empresa").upper()
    periodo = periodo_label or datetime.now().strftime("%B %Y")
    edition = "12/07/2026"

    data = [
        [logo, "", _p(empresa_nombre, company), "", "", _p("CONTROL DE ACTIVIDADES DE MANTENIMIENTO", title), "", "", "", _p(periodo, title), _p("Código", bold)],
        ["", "", "", "", "", "", "", "", "", "", _p("", center)],
        ["", "", "", "", "", "", "", "", "", "", _p("Edición", bold)],
        ["", "", "", "", "", "", "", "", "", "", _p(edition, center)],
        [""] * 11,
        [_p(v, header) for v in ["N°", "Fec./Hor. Inic.", "Fec./Hor. Fin", "Código", "Nombre Máquina", "Ubicación", "Tipo", "Técnico", "Actividad", "Observaciones", "Recibido por"]],
    ]

    for index, order in enumerate(orders, start=1):
        machine = order.machine
        jornadas = list(order.jornadas or [])
        inicio = jornadas[0].fecha_inicio if jornadas else order.fecha_inicio
        fin = jornadas[-1].fecha_fin if jornadas else order.fecha_cierre
        tecnico = getattr(order, "tecnicos_realizadores_label", "") or (
            order.technician.nombre if order.technician else ""
        )
        recibido = next((j.recibido_por for j in reversed(jornadas) if j.recibido_por), "")
        observaciones = "\n".join(
            j.descripcion_avance.strip() for j in jornadas if (j.descripcion_avance or "").strip()
        )
        actividad = (order.titulo or "").strip()
        if (order.descripcion or "").strip() and order.descripcion.strip() != actividad:
            actividad = f"{actividad}\n{order.descripcion.strip()}".strip()
        values = [
            index,
            _fecha_hora(inicio),
            _fecha_hora(fin),
            machine.codigo if machine else "",
            machine.nombre if machine else "",
            order.ubicacion or getattr(machine, "ubicacion", "") or order.area or getattr(machine, "area", "") or "",
            (order.tipo or "").capitalize(),
            "" if tecnico == "—" else tecnico,
            actividad,
            observaciones,
            recibido,
        ]
        data.append([_p(v, center if i in (0, 1, 2, 3, 6, 7) else normal) for i, v in enumerate(values)])

    if not orders:
        data.append([_p("Sin órdenes para los filtros seleccionados", center)] + [""] * 10)

    row_heights = [4 * mm, 4 * mm, 4 * mm, 4 * mm, 2.5 * mm, 9 * mm] + [None] * (len(data) - 6)
    table = Table(
        data,
        colWidths=widths,
        rowHeights=row_heights,
        repeatRows=6,
        hAlign="CENTER",
    )
    commands = [
        ("SPAN", (0, 0), (1, 3)),
        ("SPAN", (2, 0), (4, 3)),
        ("SPAN", (5, 0), (8, 3)),
        ("SPAN", (9, 0), (9, 3)),
        ("GRID", (0, 0), (-1, 3), 0.55, colors.black),
        ("GRID", (0, 5), (-1, -1), 0.55, colors.black),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#D2D2D2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 3), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 3), 0),
        ("TOPPADDING", (0, 5), (-1, 5), 5),
        ("BOTTOMPADDING", (0, 5), (-1, 5), 5),
        ("TOPPADDING", (0, 6), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 6), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]
    for row in range(7, len(data), 2):
        commands.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor("#F3F3F3")))
    if not orders:
        commands.append(("SPAN", (0, 6), (10, 6)))
    table.setStyle(TableStyle(commands))
    doc.build([table], canvasmaker=_PageCountCanvas)

    stamp = datetime.now().strftime("%Y%m%d")
    return buffer.getvalue(), f"71-MT-43-Control-Actividades-{stamp}.pdf"
