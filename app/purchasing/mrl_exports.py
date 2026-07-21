"""Documentos MRL de Purchasing."""

from datetime import datetime, timezone

from app.mrl.metadata import MRLDocumentMeta
from app.mrl.pdf.exporter import BasePdfExporter
from app.mrl.excel.exporter import BaseExcelExporter
from app.timezone_utils import resolve_timezone_name


def export_orden_compra_pdf(empresa, orden, *, usuario=None):
    meta = MRLDocumentMeta(doc_code="DOC-006", instance_code=orden.numero, module="Purchasing", title=f"Orden de Compra · {orden.numero}", empresa_id=empresa.id, empresa_nombre=empresa.razon_social, empresa_nit=empresa.nit or None, generated_at=datetime.now(timezone.utc), timezone_name=resolve_timezone_name(empresa), usuario=str(getattr(usuario, "username", usuario) or "Sistema · Roustix"), template="MRL-TPL-004")
    pdf = BasePdfExporter(meta, watermark="BORRADOR" if orden.estado == "borrador" else None)
    pdf.add_title("Orden de Compra")
    pdf.add_kpis([("Estado", orden.estado.title()), ("Moneda", orden.moneda), ("Total", f"{orden.total:,.2f}"), ("Solicitud", orden.solicitud.numero)])
    pdf.add_spacer()
    p = orden.proveedor
    pdf.add_table(["Proveedor", "Identificación", "Contacto", "Entrega prevista"], [[p.nombre, p.nit or "—", p.contacto_email or p.contacto_telefono or "—", orden.entrega_prevista.strftime("%d/%m/%Y") if orden.entrega_prevista else "—"]])
    pdf.add_spacer()
    pdf.add_table(["Descripción", "Cantidad", "Unidad", "Precio", "IVA %", "Subtotal", "Total"], [[l.descripcion_snapshot, f"{l.cantidad_ordenada:g}", l.unidad, f"{l.precio_unitario:,.2f}", f"{l.tasa_iva:g}", f"{l.subtotal:,.2f}", f"{l.total:,.2f}"] for l in orden.lineas])
    pdf.add_spacer()
    pdf.add_table(["Subtotal", "IVA", "Total"], [[f"{orden.subtotal:,.2f} {orden.moneda}", f"{orden.monto_iva:,.2f} {orden.moneda}", f"{orden.total:,.2f} {orden.moneda}"]])
    if orden.condiciones_pago or orden.direccion_entrega or orden.notas:
        pdf.add_spacer(); pdf.add_title("Condiciones")
        pdf.add_paragraph(f"Entrega: {orden.direccion_entrega or 'Por acordar'} · Pago: {orden.condiciones_pago or 'Por acordar'} · Notas: {orden.notas or 'Sin notas'}")
    return pdf.save()


def export_cxp_excel(empresa, compras, *, usuario=None):
    meta = MRLDocumentMeta(doc_code="DOC-010", instance_code=f"PUR-CXP-{datetime.now(timezone.utc):%Y%m%d}", module="Purchasing", title="Cuentas por pagar · Purchasing", empresa_id=empresa.id, empresa_nombre=empresa.razon_social, empresa_nit=empresa.nit or None, generated_at=datetime.now(timezone.utc), timezone_name=resolve_timezone_name(empresa), usuario=str(getattr(usuario, "username", usuario) or "Sistema · Roustix"))
    headers = ["Documento", "Recepción", "Proveedor", "Fecha", "Vencimiento", "Moneda", "Total", "Pagado", "Saldo", "Estado", "Días al vencimiento"]
    today = datetime.now(timezone.utc).date()
    rows = [[c.numero, c.recepcion.numero if getattr(c, "recepcion", None) else "—", c.proveedor.nombre if c.proveedor else "—", c.fecha, c.fecha_vencimiento, c.moneda_factura, float(c.total or 0), float(c.monto_pagado or 0), c.saldo_pendiente, c.estado_pago_label, (c.fecha_vencimiento - today).days if c.fecha_vencimiento else None] for c in compras]
    exporter = BaseExcelExporter(meta); exporter.add_sheet("CxP").write_table(headers, rows, column_formats=[None, None, None, "date", "date", None, "currency", "currency", "currency", None, "integer"])
    return exporter.save()
