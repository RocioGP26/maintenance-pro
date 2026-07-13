"""PDF de la Ficha Técnica de un activo."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.maintenance.asset_life_pdf import _imagen_activo, _logo
from app.models import machine_status_meta
from app.text_encoding import texto_legible


def export_asset_technical_pdf(empresa, machine, campos, valores, sector_label):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=12*mm, rightMargin=12*mm,
        topMargin=13*mm, bottomMargin=14*mm,
        title=f"Ficha Técnica - {machine.codigo}", author=empresa.razon_social or "Empresa",
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("ft-normal", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10)
    center = ParagraphStyle("ft-center", parent=normal, alignment=TA_CENTER)
    title = ParagraphStyle("ft-title", parent=center, fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#17365D"))
    section = ParagraphStyle("ft-section", parent=normal, fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.HexColor("#17365D"), spaceBefore=7, spaceAfter=5)
    label = ParagraphStyle("ft-label", parent=normal, fontName="Helvetica-Bold", textColor=colors.HexColor("#475569"))

    def p(value, style=normal):
        text = texto_legible("" if value is None else str(value))
        return Paragraph(escape(text).replace("\n", "<br/>"), style)

    def details(rows):
        data = []
        for i in range(0, len(rows), 2):
            pair = rows[i:i+2]
            row = []
            for key, value in pair:
                row.extend([p(key, label), p(value or "-")])
            while len(row) < 4:
                row.extend(["", ""])
            data.append(row)
        table = Table(data, colWidths=[29*mm, 64*mm, 29*mm, 64*mm])
        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EAF0F6")),
            ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#EAF0F6")),
            ("VALIGN", (0,0), (-1,-1), "TOP"), ("PADDING", (0,0), (-1,-1), 4),
        ]))
        return table

    header = Table([
        [_logo(empresa), p((empresa.razon_social or "Empresa").upper(), section), p("FICHA TÉCNICA DEL ACTIVO", title)],
        ["", p(f"NIT: {empresa.nit or '-'}", center), p(f"{machine.codigo} - {machine.nombre}", center)],
    ], colWidths=[34*mm, 63*mm, 89*mm], rowHeights=[20*mm, 8*mm])
    header.setStyle(TableStyle([
        ("SPAN", (0,0), (0,1)), ("GRID", (0,0), (-1,-1), .6, colors.HexColor("#17365D")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    story = [header, Spacer(1, 4*mm)]
    photo = _imagen_activo(machine)
    if photo:
        photo_table = Table([[photo]], colWidths=[186*mm])
        photo_table.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER"), ("BOX", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")), ("PADDING", (0,0), (-1,-1), 5)]))
        story.extend([photo_table, Spacer(1, 3*mm)])

    identification = [
        ("Código", machine.codigo), ("Nombre", machine.nombre),
        ("Tipo", machine.tipo_etiqueta), ("Estado", machine_status_meta(machine.status)["label"]),
        ("Sector", sector_label), ("Criticidad", machine.criticidad),
        ("Marca", machine.marca), ("Modelo", machine.modelo),
        ("Número de serie", machine.numero_serie), ("Fabricante", machine.fabricante),
        ("Fecha de fabricación", machine.fecha_fabricacion.strftime("%d/%m/%Y") if machine.fecha_fabricacion else ""),
        ("Fecha de instalación", machine.fecha_instalacion.strftime("%d/%m/%Y") if machine.fecha_instalacion else ""),
    ]
    operational = [
        ("Sede", machine.sede.nombre if machine.sede else ""), ("Ubicación", machine.ubicacion),
        ("Área", machine.area), ("Responsable", machine.responsable_nombre),
        ("Horas de operación", machine.horas_operacion),
        ("Vida útil", f"{machine.vida_util_anios} años" if machine.vida_util_anios else ""),
        ("Requiere mantenimiento", "Sí" if machine.requiere_mantenimiento else "No"),
        ("Frecuencia", machine.frecuencia_mantenimiento),
    ]
    story.extend([p("IDENTIFICACIÓN", section), details(identification), p("DATOS TÉCNICOS Y OPERATIVOS", section), details(operational)])
    if campos:
        story.append(p(f"ESPECIFICACIONES DEL SECTOR - {sector_label.upper()}", section))
        story.append(details([(c.nombre, valores.get(c.id) or "-") for c in campos]))
    documents = [("Manual técnico", machine.manual_url), ("Ficha del fabricante", machine.ficha_tecnica_url), ("Observaciones", machine.notas)]
    story.extend([p("DOCUMENTACIÓN", section), details(documents)])

    def footer(canvas, _doc):
        canvas.saveState(); canvas.setFont("Helvetica", 7); canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(12*mm, 6*mm, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0]-12*mm, 6*mm, f"Página {canvas.getPageNumber()}"); canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    safe_code = (machine.codigo or str(machine.id)).replace("/", "-").replace("\\", "-")
    return buffer.getvalue(), f"Ficha-Tecnica-{safe_code}.pdf"
