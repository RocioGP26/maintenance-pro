"""PDF imprimible de la Hoja de Vida de un activo."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from flask import current_app, has_app_context
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import machine_status_meta, wo_status_meta, wo_tipo_meta
from app.text_encoding import texto_legible


def _texto(valor) -> str:
    return texto_legible("" if valor is None else str(valor))


def _p(valor, estilo):
    texto = _texto(valor).replace("\n", "<br/>")
    return Paragraph(escape(texto).replace("&lt;br/&gt;", "<br/>"), estilo)


def _logo(empresa):
    if not has_app_context() or not (getattr(empresa, "logo", "") or "").strip():
        return ""
    valor = empresa.logo.strip().replace("\\", "/").lstrip("/")
    if valor.startswith("static/"):
        valor = valor[7:]
    ruta = (Path(current_app.static_folder) / valor).resolve()
    raiz = Path(current_app.static_folder).resolve()
    if raiz not in ruta.parents or not ruta.is_file():
        return ""
    imagen = Image(str(ruta), width=28 * mm, height=18 * mm)
    imagen.hAlign = "CENTER"
    return imagen


def _imagen_activo(machine):
    """Devuelve la fotografía local del activo sin deformarla."""
    valor = (getattr(machine, "foto_url", "") or "").strip()
    if not has_app_context() or not valor or valor.startswith(("http://", "https://")):
        return None
    valor = valor.replace("\\", "/").lstrip("/")
    if valor.startswith("static/"):
        valor = valor[7:]
    ruta = (Path(current_app.static_folder) / valor).resolve()
    raiz = Path(current_app.static_folder).resolve()
    if raiz not in ruta.parents or not ruta.is_file():
        return None
    imagen = Image(str(ruta))
    imagen._restrictSize(62 * mm, 42 * mm)
    imagen.hAlign = "CENTER"
    return imagen


def export_asset_life_pdf(
    empresa, machine, campos, valores, ordenes, incidentes, sector_label, avances_por_ot=None
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=13 * mm,
        bottomMargin=14 * mm,
        title=f"Hoja de Vida - {machine.codigo}",
        author=empresa.razon_social or "Empresa",
    )
    estilos = getSampleStyleSheet()
    normal = ParagraphStyle("hv-normal", parent=estilos["BodyText"], fontName="Helvetica", fontSize=8, leading=10)
    small = ParagraphStyle("hv-small", parent=normal, fontSize=7, leading=8.5, textColor=colors.HexColor("#475569"))
    center = ParagraphStyle("hv-center", parent=normal, alignment=TA_CENTER)
    title = ParagraphStyle("hv-title", parent=normal, fontName="Helvetica-Bold", fontSize=14, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#17365D"))
    subtitle = ParagraphStyle("hv-subtitle", parent=normal, fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.HexColor("#17365D"), spaceBefore=6, spaceAfter=5)
    header = ParagraphStyle("hv-header", parent=center, fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.white)
    label = ParagraphStyle("hv-label", parent=small, fontName="Helvetica-Bold")

    def tabla(datos, anchos=None, repeat=1):
        t = Table(datos, colWidths=anchos, repeatRows=repeat, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ]))
        return t

    empresa_nombre = (empresa.razon_social or "Empresa").upper()
    encabezado = Table([
        [_logo(empresa), _p(empresa_nombre, subtitle), _p("HOJA DE VIDA DEL ACTIVO", title)],
        ["", _p(f"NIT: {empresa.nit or '-'}", center), _p(f"{machine.codigo} - {machine.nombre}", center)],
    ], colWidths=[34 * mm, 63 * mm, 89 * mm], rowHeights=[20 * mm, 8 * mm])
    encabezado.setStyle(TableStyle([
        ("SPAN", (0, 0), (0, 1)), ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#17365D")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story = [encabezado, Spacer(1, 4 * mm)]

    foto_activo = _imagen_activo(machine)
    if foto_activo is not None:
        foto_tabla = Table(
            [[_p("IMAGEN DEL ACTIVO", subtitle)], [foto_activo]],
            colWidths=[186 * mm],
        )
        foto_tabla.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 1), (0, 1), 0.35, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 1), (0, 1), 5),
            ("BOTTOMPADDING", (0, 1), (0, 1), 5),
        ]))
        story.extend([foto_tabla, Spacer(1, 3 * mm)])

    estado = machine_status_meta(machine.status)["label"]
    generales = [
        ("Código", machine.codigo), ("Nombre", machine.nombre), ("Estado", estado),
        ("Tipo", machine.tipo_etiqueta), ("Sector", sector_label), ("Criticidad", machine.criticidad),
        ("Marca", machine.marca), ("Modelo", machine.modelo), ("Número de serie", machine.numero_serie),
        ("Fabricante", machine.fabricante), ("Sede", machine.sede.nombre if machine.sede else ""),
        ("Área", machine.area), ("Ubicación", machine.ubicacion), ("Responsable", machine.responsable_nombre),
        ("Proveedor", machine.proveedor_relacionado.nombre if machine.proveedor_relacionado else machine.proveedor),
        ("Factura", machine.numero_factura),
        ("Fecha de compra", machine.fecha_compra.strftime("%d/%m/%Y") if machine.fecha_compra else ""),
        ("Valor de compra", machine.valor_compra if machine.valor_compra is not None else ""),
        ("Garantía hasta", machine.garantia_hasta.strftime("%d/%m/%Y") if machine.garantia_hasta else ""),
    ]
    story.append(_p("INFORMACIÓN GENERAL", subtitle))
    filas = []
    for i in range(0, len(generales), 2):
        par = generales[i:i + 2]
        fila = []
        for etiqueta, valor in par:
            fila.extend([_p(etiqueta, label), _p(valor or "-", normal)])
        while len(fila) < 4:
            fila.extend(["", ""])
        filas.append(fila)
    general_table = Table(filas, colWidths=[29 * mm, 64 * mm, 29 * mm, 64 * mm])
    general_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F6")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EAF0F6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.extend([general_table, Spacer(1, 3 * mm)])

    if campos:
        story.append(_p(f"INFORMACIÓN ESPECÍFICA - {sector_label.upper()}", subtitle))
        datos = [[_p("Campo", header), _p("Valor", header)]]
        datos += [[_p(c.nombre, normal), _p(valores.get(c.id) or "-", normal)] for c in campos]
        story.extend([tabla(datos, [70 * mm, 116 * mm]), Spacer(1, 3 * mm)])

    story.append(_p("HISTORIAL DE ÓRDENES DE TRABAJO", subtitle))
    datos_ot = [[_p(x, header) for x in ["OT", "Fecha", "Tipo", "Estado", "Técnico", "Tiempo", "Repuestos"]]]
    for o in ordenes:
        datos_ot.append([
            _p(o.numero or f"#{o.id}", normal), _p(o.fecha_programada.strftime("%d/%m/%Y") if o.fecha_programada else "-", normal),
            _p(wo_tipo_meta(o.tipo)["label"], normal), _p(wo_status_meta(o.status)["label"], normal),
            _p(o.tecnicos_realizadores_label, normal), _p(o.tiempo_gastado_label, normal), _p(len(o.repuestos), center),
        ])
    if not ordenes:
        datos_ot.append([_p("Sin órdenes registradas", normal)] + [""] * 6)
    story.append(tabla(datos_ot, [21*mm, 22*mm, 25*mm, 25*mm, 45*mm, 24*mm, 24*mm]))

    avances_por_ot = avances_por_ot or {}
    story.extend([Spacer(1, 3 * mm), _p("AVANCES REALIZADOS EN LAS OT", subtitle)])
    for orden in ordenes:
        story.append(_p(f"{orden.numero or ('OT #' + str(orden.id))} - {orden.titulo or machine.nombre}", label))
        avances = avances_por_ot.get(orden.id, [])
        datos_avance = [[_p(x, header) for x in ["#", "Fecha / horario", "Técnico / proveedor", "Trabajo realizado", "Paro", "Recibido por", "Repuestos"]]]
        for avance in avances:
            jornada = avance["jornada"]
            repuestos = ", ".join(
                f"{linea.spare_part.nombre if linea.spare_part else 'Repuesto'} x {linea.cantidad}"
                for linea in avance["repuestos"]
            ) or "-"
            fecha_horario = (
                f"{avance['fecha'].strftime('%d/%m/%Y') if avance['fecha'] else '-'}\n"
                f"{avance['hora_inicio'] or '-'} - {avance['hora_fin'] or '-'} ({avance['duracion']})"
            )
            datos_avance.append([
                _p(jornada.orden or "-", center), _p(fecha_horario, normal),
                _p(jornada.tecnico_label, normal), _p(jornada.descripcion_avance or "-", normal),
                _p("Sí" if jornada.requirio_paro else "No", center),
                _p(jornada.recibido_por or "-", normal), _p(repuestos, normal),
            ])
        if not avances:
            datos_avance.append([_p("Sin avances registrados", normal)] + [""] * 6)
        story.extend([
            tabla(datos_avance, [8*mm, 30*mm, 32*mm, 52*mm, 13*mm, 25*mm, 26*mm]),
            Spacer(1, 2.5 * mm),
        ])

    story.extend([Spacer(1, 3 * mm), _p("HISTORIAL DE INCIDENCIAS", subtitle)])
    datos_inc = [[_p(x, header) for x in ["Reporte", "Fecha", "Descripción", "Prioridad", "Estado"]]]
    for inc in incidentes:
        datos_inc.append([
            _p(inc.numero or f"#{inc.id}", normal), _p(inc.reportado_en.strftime("%d/%m/%Y") if inc.reportado_en else "-", normal),
            _p(inc.titulo, normal), _p(inc.prioridad_meta["label"], normal), _p(inc.estado_label, normal),
        ])
    if not incidentes:
        datos_inc.append([_p("Sin incidencias registradas", normal)] + [""] * 4)
    story.append(tabla(datos_inc, [25*mm, 25*mm, 82*mm, 27*mm, 27*mm]))

    def pie(canvas, _doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.line(12 * mm, 10 * mm, A4[0] - 12 * mm, 10 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(12 * mm, 6 * mm, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0] - 12 * mm, 6 * mm, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(story, onFirstPage=pie, onLaterPages=pie)
    nombre = f"Hoja-de-Vida-{machine.codigo}.pdf".replace("/", "-").replace("\\", "-")
    return buffer.getvalue(), nombre
