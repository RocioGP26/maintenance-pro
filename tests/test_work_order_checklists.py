"""Sprint 19.2 · checklist ejecutable dentro de la OT."""

import unittest
from datetime import date, datetime

from app import create_app, db
from app.maintenance_execution.models import CHECKLIST_COMPLETED, CHECKLIST_IN_PROGRESS
from app.maintenance_execution.service import (
    assign_checklist,
    can_access_checklist,
    checklist_completion_error,
    create_procedure,
    publish_version,
    review_checklist,
    save_checklist_responses,
    save_draft_version,
)
from app.models import Empresa, Machine, MachineType, PlanSuscripcion, Technician, User, WorkOrder


class TestWorkOrderChecklists(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context(); self.ctx.push(); db.create_all()
        self.company = Empresa(razon_social="Uno", slug="uno", email_verified_at=datetime.utcnow())
        self.other_company = Empresa(razon_social="Dos", slug="dos", email_verified_at=datetime.utcnow())
        db.session.add_all([self.company, self.other_company]); db.session.flush()
        self.admin = self._user(self.company, "admin", "admin")
        self.tech_user = self._user(self.company, "tech", "tecnico")
        self.other_user = self._user(self.other_company, "other", "admin")
        self.tech = Technician(empresa_id=self.company.id, user_id=self.tech_user.id, nombre="Técnico", activo=True)
        machine_type = MachineType(empresa_id=self.company.id, clave="motor", nombre="Motor", prefijo="M19")
        db.session.add_all([
            self.tech,
            machine_type,
            PlanSuscripcion(empresa_id=self.company.id, plan="professional", fecha_inicio=date.today(), activo=True, estado_ciclo="activa"),
        ]); db.session.flush()
        machine = Machine(empresa_id=self.company.id, codigo="M19-001", nombre="Motor 1", machine_type_id=machine_type.id)
        db.session.add(machine); db.session.flush()
        self.order = WorkOrder(empresa_id=self.company.id, numero="OT-19-2", titulo="Inspección", machine_id=machine.id, technician_id=self.tech.id, status="abierta")
        db.session.add(self.order); db.session.flush()
        procedure, self.version = create_procedure(self.company.id, self.admin.id, {"code":"PM-MOTOR", "name":"Rutina motor", "machine_type_id":machine_type.id})
        save_draft_version(self.version, self.company.id, self.admin.id, {}, [
            {"code":"STEP-001", "title":"Confirmar limpieza", "response_type":"confirmation", "required":"1", "config_json":"{}"},
            {"code":"STEP-002", "title":"Registrar presión", "response_type":"measurement", "required":"1", "config_json":"{}"},
            {"code":"STEP-003", "title":"Observación", "response_type":"text", "required":"0", "config_json":"{}"},
        ])
        publish_version(self.version, self.company.id, self.admin.id)
        db.session.commit()

    def tearDown(self):
        db.session.remove(); db.drop_all(); db.engine.dispose(); self.ctx.pop()

    def _user(self, company, username, role):
        user = User(empresa_id=company.id, username=username, rol=role, activo=True, onboarding_completado=True)
        user.set_password("Clave-Segura-123!")
        db.session.add(user); db.session.flush(); return user

    def test_assignment_progress_completion_and_delegated_authorship(self):
        checklist = assign_checklist(self.order, self.version.id, self.admin.id)
        db.session.commit()
        self.assertEqual(checklist.procedure_code_snapshot, "PM-MOTOR")
        self.assertTrue(can_access_checklist(checklist, self.tech_user))
        self.assertFalse(can_access_checklist(checklist, self.other_user))

        first, second, _third = self.version.steps
        save_checklist_responses(checklist, self.admin.id, {f"step_{first.id}": "done"})
        db.session.commit()
        self.assertEqual(checklist.status, CHECKLIST_IN_PROGRESS)
        self.assertIn("1/2", checklist_completion_error(self.order))
        response = checklist.responses[0]
        self.assertEqual(response.performed_by_user_id, self.tech_user.id)
        self.assertEqual(response.recorded_by_user_id, self.admin.id)

        save_checklist_responses(checklist, self.tech_user.id, {f"step_{second.id}": "5.4"})
        db.session.commit()
        self.assertEqual(checklist.status, CHECKLIST_COMPLETED)
        self.assertEqual(checklist.progress_percent, 100)
        self.assertIn("requiere revisión", checklist_completion_error(self.order))
        review_checklist(checklist, self.admin.id, {"review_notes": "Ejecución verificada"})
        db.session.commit()
        self.assertIsNone(checklist_completion_error(self.order))

    def test_assignment_rejects_other_tenant_and_duplicate(self):
        with self.assertRaisesRegex(ValueError, "empresa activa"):
            assign_checklist(self.order, self.version.id, self.other_user.id)
        assign_checklist(self.order, self.version.id, self.admin.id)
        db.session.commit()
        with self.assertRaisesRegex(ValueError, "ya tiene"):
            assign_checklist(self.order, self.version.id, self.admin.id)

    def test_routes_hide_unassigned_checklist_from_technician(self):
        client = self.app.test_client()
        client.post("/login", data={"username":self.tech_user.username, "empresa_slug":self.company.slug, "password":"Clave-Segura-123!"})
        response = client.get(f"/maintenance/procedures/work-orders/{self.order.id}/checklist")
        self.assertEqual(response.status_code, 404)
        client.post("/logout")
        client.post("/login", data={"username":self.admin.username, "empresa_slug":self.company.slug, "password":"Clave-Segura-123!"})
        response = client.get(f"/maintenance/procedures/work-orders/{self.order.id}/checklist")
        self.assertEqual(response.status_code, 200)
        self.assertIn("PM-MOTOR", response.get_data(as_text=True))

    def test_incomplete_checklist_prevents_work_order_closure(self):
        assign_checklist(self.order, self.version.id, self.admin.id)
        db.session.commit()
        client = self.app.test_client()
        client.post("/login", data={"username":self.admin.username, "empresa_slug":self.company.slug, "password":"Clave-Segura-123!"})
        response = client.post(
            f"/ordenes/{self.order.id}/editar",
            data={
                "titulo": self.order.titulo,
                "tipo": "correctivo",
                "prioridad": "media",
                "machine_id": str(self.order.machine_id),
                "status_manual": "cerrada",
                "ejecucion_tipo": "interno",
                "technician_id": str(self.tech.id),
                "jornadas_json": "[]",
                "repuestos_json": "[]",
            },
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.order)
        self.assertEqual(self.order.status, "en_proceso")


if __name__ == "__main__":
    unittest.main()
