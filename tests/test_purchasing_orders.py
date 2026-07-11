"""Sprint 16.2 · órdenes de compra y DOC-006."""

from __future__ import annotations

import unittest

from app import create_app, db
from app.models import Empresa, InvProducto, InvProveedor, PurSolicitud, PurSolicitudLinea, User
from app.purchasing.mrl_exports import export_orden_compra_pdf
from app.purchasing.service import crear_orden_desde_solicitud, registrar_recepcion, transicionar_orden


class TestPurchasingOrders(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.empresa = Empresa(razon_social="Acme & Cía", nit="900-1", moneda="COP", zona_horaria="America/Bogota")
        db.session.add(self.empresa); db.session.flush()
        self.user = User(empresa_id=self.empresa.id, username="admin", password_hash="x", rol="admin", onboarding_completado=True)
        self.provider = InvProveedor(empresa_id=self.empresa.id, nombre="Proveedor Uno", nit="800-1", activo=True)
        self.product = InvProducto(empresa_id=self.empresa.id, sku="SKU-1", nombre="Rodamiento", unidad="pza", activo=True)
        db.session.add_all([self.user, self.provider, self.product]); db.session.flush()
        self.request = PurSolicitud(empresa_id=self.empresa.id, numero="SC-2026-0001", solicitante_id=self.user.id, estado="aprobada", justificacion="Reposición")
        self.request.lineas.append(PurSolicitudLinea(producto=self.product, cantidad=2, unidad="pza", costo_estimado=10))
        db.session.add(self.request); db.session.commit()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def test_conversion_totals_state_and_unique_source(self):
        line = self.request.lineas[0]
        order = crear_orden_desde_solicitud(self.empresa.id, self.user.id, self.request, {"proveedor_id": self.provider.id, "moneda": "COP"}, {line.id: ("100", "19")})
        db.session.commit()
        self.assertEqual(order.subtotal, 200)
        self.assertEqual(order.monto_iva, 38)
        self.assertEqual(order.total, 238)
        self.assertEqual(self.request.estado, "convertida")
        self.assertEqual(len(order.eventos), 1)
        with self.assertRaisesRegex(ValueError, "aprobada"):
            crear_orden_desde_solicitud(self.empresa.id, self.user.id, self.request, {"proveedor_id": self.provider.id}, {})

    def test_transitions_and_doc006_pdf(self):
        line = self.request.lineas[0]
        order = crear_orden_desde_solicitud(self.empresa.id, self.user.id, self.request, {"proveedor_id": self.provider.id, "moneda": "COP"}, {line.id: ("50", "0")})
        db.session.flush()
        draft, name = export_orden_compra_pdf(self.empresa, order, usuario=self.user)
        self.assertTrue(draft.startswith(b"%PDF-")); self.assertTrue(name.startswith("DOC-006-OC-"))
        transicionar_orden(order, self.user.id, "emitida"); transicionar_orden(order, self.user.id, "enviada")
        self.assertEqual(order.estado, "enviada")

    def _sent_order(self):
        line = self.request.lineas[0]
        order = crear_orden_desde_solicitud(self.empresa.id, self.user.id, self.request, {"proveedor_id": self.provider.id, "moneda": "COP"}, {line.id: ("50", "0")})
        db.session.flush(); transicionar_orden(order, self.user.id, "emitida"); transicionar_orden(order, self.user.id, "enviada"); db.session.flush()
        return order

    def test_partial_then_total_receipt_updates_stock_once(self):
        order = self._sent_order(); line = order.lineas[0]
        first = registrar_recepcion(self.empresa.id, self.user.id, order, {"idempotency_key": "receipt-1", "fecha": __import__("datetime").date(2026, 7, 11)}, {line.id: (1, 0, "")})
        db.session.commit()
        self.assertEqual(first.estado, "confirmada"); self.assertEqual(order.estado, "parcial"); self.assertEqual(self.product.stock, 1)
        same = registrar_recepcion(self.empresa.id, self.user.id, order, {"idempotency_key": "receipt-1", "fecha": __import__("datetime").date(2026, 7, 11)}, {line.id: (1, 0, "")})
        self.assertEqual(same.id, first.id); self.assertEqual(self.product.stock, 1)
        second = registrar_recepcion(self.empresa.id, self.user.id, order, {"idempotency_key": "receipt-2", "fecha": __import__("datetime").date(2026, 7, 11)}, {line.id: (1, 0, "")})
        db.session.commit()
        self.assertEqual(second.estado, "confirmada"); self.assertEqual(order.estado, "recibida"); self.assertEqual(self.product.stock, 2)

    def test_rejection_requires_reason_and_does_not_touch_stock(self):
        order = self._sent_order(); line = order.lineas[0]
        with self.assertRaisesRegex(ValueError, "motivo"):
            registrar_recepcion(self.empresa.id, self.user.id, order, {"idempotency_key": "reject-bad", "fecha": __import__("datetime").date(2026, 7, 11)}, {line.id: (0, 1, "")})
        self.assertEqual(len(order.recepciones), 0)
        receipt = registrar_recepcion(self.empresa.id, self.user.id, order, {"idempotency_key": "reject-ok", "fecha": __import__("datetime").date(2026, 7, 11)}, {line.id: (0, 1, "Daño visible")})
        db.session.commit()
        self.assertEqual(receipt.estado, "rechazada"); self.assertEqual(order.estado, "parcial"); self.assertEqual(self.product.stock, 0)


if __name__ == "__main__":
    unittest.main()
