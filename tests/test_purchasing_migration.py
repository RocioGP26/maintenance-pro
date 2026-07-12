"""Sprint 16.5 · migración legacy idempotente."""

import unittest
from datetime import date

from app import create_app, db
from app.models import Empresa, InvCompra, InvCompraLinea, InvProducto, InvProveedor, PurOrdenCompra, PurRecepcion, PurSolicitud, User
from app.purchasing.migration import migrate_legacy_purchases


class TestPurchasingMigration(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing"); self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        company = Empresa(razon_social="Legacy Co", nit="1", moneda="COP"); db.session.add(company); db.session.flush()
        user = User(empresa_id=company.id, username="admin", password_hash="x", rol="admin", activo=True); provider = InvProveedor(empresa_id=company.id, nombre="Proveedor", activo=True); product = InvProducto(empresa_id=company.id, sku="SKU", nombre="Producto", stock=7, unidad="pza", activo=True)
        db.session.add_all([user, provider, product]); db.session.flush()
        purchase = InvCompra(empresa_id=company.id, proveedor_id=provider.id, numero="FAC-OLD", moneda_factura="COP", tipo_iva="con_iva", subtotal=100, monto_iva=19, total=119, fecha=date(2026, 1, 1), fecha_factura=date(2026, 1, 1), fecha_vencimiento=date(2026, 2, 1), estado_pago="pendiente", monto_pagado=0)
        purchase.lineas.append(InvCompraLinea(producto=product, cantidad=2, precio_unitario=50, subtotal=100, tasa_iva=19, monto_iva=19)); db.session.add(purchase); db.session.commit()
        self.product_id = product.id; self.purchase_id = purchase.id

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def test_dry_run_apply_and_idempotency_without_stock_change(self):
        self.assertEqual(migrate_legacy_purchases(dry_run=True)["migrated"], 1)
        self.assertEqual(PurSolicitud.query.count(), 0)
        first = migrate_legacy_purchases(dry_run=False)
        self.assertEqual(first["migrated"], 1); self.assertEqual(PurSolicitud.query.count(), 1); self.assertEqual(PurOrdenCompra.query.count(), 1); self.assertEqual(PurRecepcion.query.count(), 1)
        self.assertEqual(db.session.get(InvProducto, self.product_id).stock, 7)
        receipt = PurRecepcion.query.one(); self.assertEqual(receipt.inv_compra_id, self.purchase_id); self.assertEqual(receipt.orden.estado, "cerrada")
        second = migrate_legacy_purchases(dry_run=False)
        self.assertEqual(second["migrated"], 0); self.assertEqual(second["linked"], 1); self.assertEqual(PurRecepcion.query.count(), 1); self.assertEqual(db.session.get(InvProducto, self.product_id).stock, 7)


if __name__ == "__main__":
    unittest.main()
