"""DOC-001 · Orden de Trabajo de referencia."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.maintenance.mrl_exports import export_orden_trabajo_pdf


class TestDoc001(unittest.TestCase):
    def test_generates_work_order_pdf_without_flask_context(self) -> None:
        empresa = SimpleNamespace(id=7, razon_social="Acme & Cía", nit="900-1", zona_horaria="America/Bogota", moneda="COP")
        machine = SimpleNamespace(codigo="EQ-001", nombre="Compresor", area="Planta", ubicacion="Norte")
        order = SimpleNamespace(
            id=42, numero="OT-2026-0042", titulo="Revisión & ajuste", descripcion="Inspección general",
            status="cerrada", tipo="correctivo", prioridad="alta", tiempo_gastado_label="2 h 30 min",
            machine=machine, area="", ubicacion="", fecha_programada=None, fecha_inicio=None, fecha_cierre=None,
            ejecucion_label="Interna", technician=SimpleNamespace(nombre="Ana"), es_ejecucion_externa=False,
            jornadas=[], repuestos=[], autorizado_por="Jefe", recibido_por="Operador", supervisor=None,
        )
        content, filename = export_orden_trabajo_pdf(empresa, order, usuario="tester")
        self.assertTrue(content.startswith(b"%PDF-"))
        self.assertGreater(len(content), 1500)
        self.assertTrue(filename.startswith("DOC-001-OT-2026-0042-"))

    def test_adapter_does_not_put_business_imports_in_mrl_engine(self) -> None:
        import app.mrl.pdf.exporter as engine
        with open(engine.__file__, encoding="utf-8") as source:
            self.assertNotIn("WorkOrder", source.read())


if __name__ == "__main__":
    unittest.main()
