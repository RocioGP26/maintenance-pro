"""PDF del cronograma anual de mantenimiento preventivo por activo.

Formato alineado al documento clásico 62-MT (matriz ENE–DIC · PROG/EJEC).
"""

from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from flask import current_app, has_app_context
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.maintenance.cronograma_preventivo import MESES_ES, CronogramaActivo

# Colores de celdas (como el formato físico)
_COLOR_L = colors.HexColor("#f9a8d4")  # lubricación
_COLOR_I = colors.HexColor("#c4b5fd")  # inspección
_COLOR_A = colors.HexColor("#fcd34d")
_COLOR_LZ = colors.HexColor("#93c5fd")
_COLOR_MG = colors.HexColor("#86efac")
_COLOR_R = colors.HexColor("#fdba74")
_COLOR_C = colors.HexColor("#67e8f9")
_COLOR_OK = colors.HexColor("#4ade80")
_COLOR_HEADER = colors.HexColor("#1e3a5f")
_COLOR_BORDER = colors.HexColor("#334155")
_COLOR_PROG_BG = colors.HexColor("#fff7ed")
_COLOR_EJEC_BG = colors.HexColor("#f0fdf4")

_TIPO_BG = {
    "L": _COLOR_L,
    "I": _COLOR_I,
    "A": _COLOR_A,
    "LZ": _COLOR_LZ,
    "MG": _COLOR_MG,
    "R": _COLOR_R,
    "C": _COLOR_C,
}

_FREQ_LABEL = {
    "S": "Sem.",
    "M": "Men.",
    "BI": "Bi.",
    "TR": "Tri.",
    "SE": "Semest.",
    "AN": "Anual",
}


class _PageCountCanvas(Canvas):
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
            self.setFont("Helvetica", 7)
            self.drawCentredString(
                landscape(A4)[0] / 2, 4 * mm, f"Página {self._pageNumber} de {total}"
            )
            super().showPage()
        super().save()


def _logo_empresa(empresa, width=24 * mm, height=14 * mm):
    if not has_app_context() or not (getattr(empresa, "logo", "") or "").strip():
        return ""
    value = empresa.logo.strip().replace("\\", "/").lstrip("/")
    from app.file_storage import key_from_reference, read_bytes

    storage_key = key_from_reference(value)
    if storage_key:
        try:
            image = Image(BytesIO(read_bytes(storage_key)), width=width, height=height)
            image.hAlign = "CENTER"
            return image
        except (FileNotFoundError, OSError):
            return ""
    if value.startswith("static/"):
        value = value[7:]
    path = (Path(current_app.static_folder) / value).resolve()
    static_root = Path(current_app.static_folder).resolve()
    if static_root not in path.parents or not path.is_file():
        return ""
    image = Image(str(path), width=width, height=height)
    image.hAlign = "CENTER"
    return image


def _styles():
    return {
        "title": ParagraphStyle(
            "cr_title",
            fontName="Helvetica-Bold",
            fontSize=9,
            alignment=TA_CENTER,
            leading=11,
            textColor=colors.black,
        ),
        "company": ParagraphStyle(
            "cr_company",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            alignment=TA_CENTER,
            leading=9,
            textColor=colors.black,
        ),
        "meta": ParagraphStyle(
            "cr_meta",
            fontName="Helvetica",
            fontSize=7,
            alignment=TA_LEFT,
            leading=9,
        ),
        "meta_c": ParagraphStyle(
            "cr_meta_c",
            fontName="Helvetica",
            fontSize=7,
            alignment=TA_CENTER,
            leading=9,
        ),
        "th": ParagraphStyle(
            "cr_th",
            fontName="Helvetica-Bold",
            fontSize=6,
            alignment=TA_CENTER,
            leading=7,
            textColor=colors.white,
        ),
        "td": ParagraphStyle(
            "cr_td",
            fontName="Helvetica",
            fontSize=5.5,
            alignment=TA_LEFT,
            leading=7,
        ),
        "td_c": ParagraphStyle(
            "cr_td_c",
            fontName="Helvetica-Bold",
            fontSize=6,
            alignment=TA_CENTER,
            leading=7,
        ),
        "pe": ParagraphStyle(
            "cr_pe",
            fontName="Helvetica-Bold",
            fontSize=5,
            alignment=TA_CENTER,
            leading=6,
        ),
        "small": ParagraphStyle(
            "cr_small",
            fontName="Helvetica",
            fontSize=6.5,
            alignment=TA_LEFT,
            leading=8,
        ),
        "box_title": ParagraphStyle(
            "cr_box_title",
            fontName="Helvetica-Bold",
            fontSize=7,
            alignment=TA_LEFT,
            leading=9,
        ),
    }


def _rich(html: str, style) -> Paragraph:
    """Paragraph con markup ReportLab (sin escapar tags propios)."""
    return Paragraph(html, style)


def _txt(value) -> str:
    return escape("" if value is None else str(value))


def _content_width() -> float:
    """Ancho útil compartido por encabezado y tablas."""
    return landscape(A4)[0] - 12 * mm


def _matrix_col_widths() -> list[float]:
    page_w = _content_width()
    fixed = 7 * mm + 48 * mm + 12 * mm + 9 * mm
    week_w = max(3.6 * mm, (page_w - fixed) / 48)
    return [7 * mm, 48 * mm, 12 * mm, 9 * mm] + [week_w] * 48


def _empresa_dos_lineas(empresa) -> tuple[str, str]:
    empresa_nombre = (
        getattr(empresa, "razon_social", None) or getattr(empresa, "nombre", "") or "Empresa"
    ).strip()
    partes = empresa_nombre.split()
    if len(partes) >= 4:
        mid = max(2, len(partes) // 2)
        return " ".join(partes[:mid]), " ".join(partes[mid:])
    if len(partes) >= 2:
        return " ".join(partes[:2]), " ".join(partes[2:])
    return empresa_nombre, ""


def _build_header(cronograma: CronogramaActivo, empresa, styles):
    """Encabezado plano (una sola Table + SPAN/GRID), mismo ancho que la matriz."""
    machine = cronograma.machine
    logo = _logo_empresa(empresa, width=26 * mm, height=14 * mm)
    if not logo:
        logo = _rich("<b>LOGO</b>", styles["meta_c"])

    linea1, linea2 = _empresa_dos_lineas(empresa)
    empresa_html = f"<b>{_txt(linea1.upper())}</b>"
    if linea2:
        empresa_html += f"<br/>{_txt(linea2.upper())}"

    edicion = date.today().strftime("%d/%b/%Y")
    page_w = _content_width()

    # 7 columnas: logo | empresa | cód.maq | nombre | aprobó | rótulo ctl | valor ctl
    w_logo = page_w * 0.11
    w_emp = page_w * 0.15
    w_cod = page_w * 0.16
    w_nom = page_w * 0.28
    w_apr = page_w * 0.14
    w_ctl_rest = page_w - (w_logo + w_emp + w_cod + w_nom + w_apr)
    w_ctl_lbl = w_ctl_rest * 0.42
    w_ctl_val = w_ctl_rest - w_ctl_lbl
    col_w = [w_logo, w_emp, w_cod, w_nom, w_apr, w_ctl_lbl, w_ctl_val]

    # 3 filas · 4 campos de control: Código | (vacío) / Edición | fecha
    data = [
        [
            logo,
            _rich(empresa_html, styles["company"]),
            _rich(
                "<b>CRONOGRAMA DE MANTENIMIENTO PREVENTIVO<br/>MÁQUINAS Y/O EQUIPOS</b>",
                styles["title"],
            ),
            "",  # span con título
            _rich("<b>Aprobó:</b><br/>Jefe de Mantenimiento", styles["meta_c"]),
            _rich("<b>Código</b>", styles["meta_c"]),
            _rich(" ", styles["meta_c"]),  # valor Código en blanco
        ],
        [
            "",
            "",
            _rich("<b>Código Máquina/Equipo</b>", styles["meta_c"]),
            _rich("<b>Nombre Máquina o Equipo</b>", styles["meta_c"]),
            "",
            "",  # span con Código
            "",  # span con valor Código
        ],
        [
            "",
            "",
            _rich(_txt(machine.codigo or ""), styles["meta_c"]),
            _rich(_txt(machine.nombre or ""), styles["meta_c"]),
            "",
            _rich("<b>Edición</b>", styles["meta_c"]),
            _rich(_txt(edicion), styles["meta_c"]),
        ],
    ]

    head = Table(data, colWidths=col_w, rowHeights=[10 * mm, 7 * mm, 8 * mm])
    head.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.1, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                # Logo y empresa a lo alto
                ("SPAN", (0, 0), (0, 2)),
                ("SPAN", (1, 0), (1, 2)),
                # Título sobre código+nombre
                ("SPAN", (2, 0), (3, 0)),
                # Aprobó a lo alto
                ("SPAN", (4, 0), (4, 2)),
                # Código / valor (filas 0-1) · Edición / fecha (fila 2)
                ("SPAN", (5, 0), (5, 1)),
                ("SPAN", (6, 0), (6, 1)),
                ("BACKGROUND", (2, 1), (3, 1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (5, 0), (5, 1), colors.HexColor("#f1f5f9")),
                ("BACKGROUND", (5, 2), (5, 2), colors.HexColor("#f1f5f9")),
            ]
        )
    )
    return [head, Spacer(1, 2.5 * mm)]


def _build_matrix(cronograma: CronogramaActivo, styles):
    """Matriz: N° | Instrucciones | F | PROG/EJEC | 48 semanas."""
    # Filas de encabezado
    row_meses = [
        _rich("<b>N°</b>", styles["th"]),
        _rich("<b>INSTRUCCIONES</b>", styles["th"]),
        _rich("<b>FREC.</b>", styles["th"]),
        _rich("<b></b>", styles["th"]),
    ]
    row_sem = ["", "", "", ""]
    for mes in MESES_ES:
        row_meses.append(_rich(f"<b>{mes}</b>", styles["th"]))
        row_meses.extend(["", "", ""])
        for s in (1, 2, 3, 4):
            row_sem.append(_rich(str(s), styles["th"]))

    data = [row_meses, row_sem]
    style_cmds: list = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 5.5),
        ("GRID", (0, 0), (-1, -1), 0.35, _COLOR_BORDER),
        ("BACKGROUND", (0, 0), (-1, 1), _COLOR_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        # Spans encabezado
        ("SPAN", (0, 0), (0, 1)),
        ("SPAN", (1, 0), (1, 1)),
        ("SPAN", (2, 0), (2, 1)),
        ("SPAN", (3, 0), (3, 1)),
    ]
    for i in range(12):
        c0 = 4 + i * 4
        style_cmds.append(("SPAN", (c0, 0), (c0 + 3, 0)))

    for idx, fila in enumerate(cronograma.filas):
        frec = _FREQ_LABEL.get(fila.frecuencia_codigo, fila.frecuencia_codigo)
        act_html = _txt(fila.actividad[:220])
        prog_row = [
            _rich(str(fila.numero), styles["td_c"]),
            _rich(act_html, styles["td"]),
            _rich(frec, styles["td_c"]),
            _rich("PROG", styles["pe"]),
        ]
        ejec_row = [
            "",
            "",
            "",
            _rich("EJEC", styles["pe"]),
        ]
        for m in range(1, 13):
            for s in range(1, 5):
                cel = fila.celdas[m][s]
                prog_row.append(_rich(_txt(cel.prog), styles["td_c"]) if cel.prog else "")
                ejec_row.append(_rich(_txt(cel.ejec), styles["td_c"]) if cel.ejec else "")

        r_prog = len(data)
        data.append(prog_row)
        data.append(ejec_row)
        r_ejec = r_prog + 1

        style_cmds.extend(
            [
                ("SPAN", (0, r_prog), (0, r_ejec)),
                ("SPAN", (1, r_prog), (1, r_ejec)),
                ("SPAN", (2, r_prog), (2, r_ejec)),
                ("BACKGROUND", (0, r_prog), (-1, r_prog), _COLOR_PROG_BG),
                ("BACKGROUND", (0, r_ejec), (-1, r_ejec), _COLOR_EJEC_BG),
                ("BACKGROUND", (3, r_prog), (3, r_prog), colors.HexColor("#ffedd5")),
                ("BACKGROUND", (3, r_ejec), (3, r_ejec), colors.HexColor("#dcfce7")),
                ("ALIGN", (1, r_prog), (1, r_ejec), "LEFT"),
                ("VALIGN", (1, r_prog), (1, r_ejec), "TOP"),
            ]
        )

        for m in range(1, 13):
            for s in range(1, 5):
                cel = fila.celdas[m][s]
                col = 4 + (m - 1) * 4 + (s - 1)
                if cel.prog:
                    bg = _TIPO_BG.get(cel.prog.upper(), colors.HexColor("#e2e8f0"))
                    style_cmds.append(("BACKGROUND", (col, r_prog), (col, r_prog), bg))
                if cel.ejec:
                    style_cmds.append(("BACKGROUND", (col, r_ejec), (col, r_ejec), _COLOR_OK))

    table = Table(data, colWidths=_matrix_col_widths(), repeatRows=2)
    table.setStyle(TableStyle(style_cmds))
    return table


def _build_cumplimiento(cronograma: CronogramaActivo, styles):
    cump = cronograma.cumplimiento
    header = [
        _rich("<b>SEGUIMIENTO AL CUMPLIMIENTO</b>", styles["th"]),
        _rich("<b>TOTAL</b>", styles["th"]),
    ]
    header.extend([_rich(f"<b>{m}</b>", styles["th"]) for m in MESES_ES])

    row_prog = [
        _rich("Mantenimiento programado", styles["td"]),
        _rich(str(cump["prog_total"]), styles["td_c"]),
    ]
    row_ejec = [
        _rich("Mantenimiento ejecutado", styles["td"]),
        _rich(str(cump["ejec_total"]), styles["td_c"]),
    ]
    row_pct = [
        _rich("% cumplimiento mes", styles["td"]),
        _rich(
            "—" if cump["pct_total"] is None else f"{cump['pct_total']}%",
            styles["td_c"],
        ),
    ]
    for m in range(1, 13):
        info = cump["por_mes"][m]
        row_prog.append(_rich(str(info["prog"]), styles["td_c"]))
        row_ejec.append(_rich(str(info["ejec"]), styles["td_c"]))
        row_pct.append(
            _rich("—" if info["pct"] is None else f"{info['pct']}%", styles["td_c"])
        )

    page_w = _content_width()
    label_w = 42 * mm
    total_w = 14 * mm
    mes_w = (page_w - label_w - total_w) / 12
    table = Table(
        [header, row_prog, row_ejec, row_pct],
        colWidths=[label_w, total_w] + [mes_w] * 12,
    )
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, _COLOR_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), _COLOR_HEADER),
                ("BACKGROUND", (0, 1), (-1, 1), _COLOR_PROG_BG),
                ("BACKGROUND", (0, 2), (-1, 2), _COLOR_EJEC_BG),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def _build_observaciones(cronograma: CronogramaActivo, styles):
    lines = []
    for o in cronograma.observaciones[:15]:
        f = o["fecha"].strftime("%d/%m/%Y") if o["fecha"] else "—"
        lines.append(f"<b>{_txt(f)}</b>: {_txt(o['texto'][:200])}")
    if not lines:
        lines = ["Sin observaciones de OT preventivas completadas en el año."]
    body = "<br/>".join(lines)
    content = Table(
        [
            [_rich("<b>OBSERVACIONES</b>", styles["box_title"])],
            [_rich(body, styles["small"])],
        ],
        colWidths=[_content_width()],
    )
    content.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, _COLOR_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return content


def _build_convenciones(styles):
    text = (
        "<b>CONVENCIONES:</b> "
        "PROG = Programado · EJEC = Ejecutado · "
        "I = Inspección · L = Lubricación · A = Ajuste · LZ = Limpieza · "
        "MG = Mantenimiento general · R = Revisión · C = Calibración · "
        "F = Frecuencia · S = Semanal · Men. = Mensual · BI = Bimensual · "
        "Tri. = Trimestral · SE = Semestral · AN = Anual · ok = Realizado"
    )
    box = Table(
        [[_rich(text, styles["small"])]],
        colWidths=[_content_width()],
    )
    box.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, _COLOR_BORDER),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return box


def _build_cronograma_flowables(cronograma: CronogramaActivo, empresa):
    styles = _styles()
    parts = []
    parts.extend(_build_header(cronograma, empresa, styles))
    parts.append(_build_matrix(cronograma, styles))
    parts.append(Spacer(1, 3 * mm))
    parts.append(_build_convenciones(styles))
    parts.append(Spacer(1, 2.5 * mm))
    parts.append(_build_observaciones(cronograma, styles))
    parts.append(Spacer(1, 2.5 * mm))
    parts.append(_build_cumplimiento(cronograma, styles))
    return [KeepTogether(parts)] if len(cronograma.filas) <= 3 else parts


def export_cronograma_pdf(empresa, cronograma: CronogramaActivo) -> tuple[bytes, str]:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=6 * mm,
        rightMargin=6 * mm,
        topMargin=6 * mm,
        bottomMargin=9 * mm,
        title=f"Cronograma preventivo {cronograma.machine.codigo}",
        author=getattr(empresa, "razon_social", "") or "Roustix",
    )
    flow = _build_cronograma_flowables(cronograma, empresa)
    if not cronograma.filas:
        styles = _styles()
        flow = _build_header(cronograma, empresa, styles) + [
            Spacer(1, 8 * mm),
            _rich(
                "<b>Sin actividades preventivas.</b> Aplique la plantilla del sector "
                "y genere las OT del año.",
                styles["meta"],
            ),
        ]
    doc.build(flow, canvasmaker=_PageCountCanvas)
    codigo = (cronograma.machine.codigo or "activo").replace("/", "-")
    return buffer.getvalue(), f"cronograma-preventivo-{codigo}-{cronograma.anio}.pdf"


def export_cronogramas_bulk_pdf(empresa, cronogramas: list[CronogramaActivo]) -> tuple[bytes, str]:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=6 * mm,
        rightMargin=6 * mm,
        topMargin=6 * mm,
        bottomMargin=9 * mm,
    )
    flow: list = []
    for i, cronograma in enumerate(cronogramas):
        if i:
            flow.append(PageBreak())
        chunk = _build_cronograma_flowables(cronograma, empresa)
        if not cronograma.filas:
            styles = _styles()
            chunk = _build_header(cronograma, empresa, styles) + [
                Spacer(1, 6 * mm),
                _rich("Sin actividades preventivas para este activo.", styles["meta"]),
            ]
        flow.extend(chunk)
    if not flow:
        styles = _styles()
        flow = [_rich("No hay activos con planes preventivos.", styles["meta"])]
    doc.build(flow, canvasmaker=_PageCountCanvas)
    anio = cronogramas[0].anio if cronogramas else date.today().year
    return buffer.getvalue(), f"cronogramas-preventivos-{anio}.pdf"
