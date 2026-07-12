"""Sprint 16.1 · solicitudes y aprobación simple."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from app.permissions import can_approve_purchase_request, can_create_purchase_request
from app.models import PurSolicitud
from app.purchasing.service import transicionar


class FakeSession:
    def __init__(self):
        self.added = []

    def add(self, item):
        self.added.append(item)


class TestPurchasingRequests(unittest.TestCase):
    def test_permission_contract(self):
        user = SimpleNamespace(is_authenticated=True, rol="usuario")
        admin = SimpleNamespace(is_authenticated=True, rol="admin")
        self.assertTrue(can_create_purchase_request(user))
        self.assertFalse(can_approve_purchase_request(user))
        self.assertTrue(can_approve_purchase_request(admin))

    def test_transition_happy_path_and_audit(self):
        import app.purchasing.service as service

        original = service.db.session
        fake = FakeSession()
        service.db.session = fake
        try:
            item = PurSolicitud(id=1, empresa_id=9, numero="SC-2026-0001", solicitante_id=3, estado="borrador")
            transicionar(item, 3, "enviada")
            transicionar(item, 4, "aprobada", detalle="Presupuesto disponible")
            self.assertEqual(item.estado, "aprobada")
            self.assertEqual(item.aprobador_id, 4)
            self.assertEqual(len(fake.added), 2)
            self.assertEqual(fake.added[-1].estado_anterior, "enviada")
        finally:
            service.db.session = original

    def test_rejection_requires_reason(self):
        item = PurSolicitud(id=1, empresa_id=9, numero="SC-2026-0001", solicitante_id=3, estado="enviada")
        with self.assertRaisesRegex(ValueError, "motivo"):
            transicionar(item, 4, "rechazada")

    def test_invalid_state_jump_is_rejected(self):
        item = PurSolicitud(id=1, empresa_id=9, numero="SC-2026-0001", solicitante_id=3, estado="borrador")
        with self.assertRaises(ValueError):
            transicionar(item, 4, "aprobada")


if __name__ == "__main__":
    unittest.main()
