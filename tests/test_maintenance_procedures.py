"""Sprint 19.1 · catálogo y versionado de procedimientos."""

from __future__ import annotations

import unittest
from datetime import date, datetime

from app import create_app, db
from app.maintenance_execution.models import (
    MaintenanceProcedureEvent,
    PROCEDURE_VERSION_PUBLISHED,
    PROCEDURE_VERSION_RETIRED,
)
from app.maintenance_execution.service import (
    create_draft_version,
    create_procedure,
    publish_version,
    save_draft_version,
    update_procedure,
)
from app.models import Empresa, MachineType, PlanSuscripcion, User
from app.permissions import (
    can_manage_maintenance_procedures,
    can_view_maintenance_procedures,
)


class TestMaintenanceProcedures(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.company = Empresa(
            razon_social="Industria Uno",
            slug="industria-uno",
            email_verified_at=datetime.utcnow(),
        )
        self.other_company = Empresa(
            razon_social="Industria Dos",
            slug="industria-dos",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add_all([self.company, self.other_company])
        db.session.flush()
        self.admin = self._user(self.company, "admin", "admin")
        self.technician = self._user(self.company, "tecnico", "tecnico")
        self.other_admin = self._user(self.other_company, "admin", "admin")
        self.machine_type = MachineType(
            empresa_id=self.company.id,
            clave="compresores",
            nombre="Compresor",
            prefijo="CMP",
        )
        self.other_machine_type = MachineType(
            empresa_id=self.other_company.id,
            clave="bombas",
            nombre="Bomba",
            prefijo="BMB",
        )
        db.session.add_all(
            [
                self.machine_type,
                self.other_machine_type,
                PlanSuscripcion(
                    empresa_id=self.company.id,
                    plan="professional",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=self.other_company.id,
                    plan="professional",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def _user(self, company, username, role):
        user = User(
            empresa_id=company.id,
            username=username,
            nombre_visible=username.title(),
            rol=role,
            activo=True,
            onboarding_completado=True,
        )
        user.set_password(self.PASSWORD)
        db.session.add(user)
        db.session.flush()
        return user

    def _draft(self, *, company=None, actor=None, code="PM-CMP-001"):
        company = company or self.company
        actor = actor or self.admin
        procedure, version = create_procedure(
            company.id,
            actor.id,
            {
                "code": code,
                "name": "Inspección preventiva",
                "description": "Rutina estandarizada",
                "machine_type_id": (
                    self.machine_type.id
                    if company.id == self.company.id
                    else self.other_machine_type.id
                ),
                "change_notes": "Versión inicial",
            },
        )
        save_draft_version(
            version,
            company.id,
            actor.id,
            {"change_notes": "Versión inicial"},
            [
                {
                    "code": "STEP-001",
                    "title": "Verificar nivel",
                    "instructions": "Compare contra el rango permitido.",
                    "response_type": "measurement",
                    "required": "1",
                    "config_json": '{"unit":"bar","min":4,"max":6}',
                },
                {
                    "code": "STEP-002",
                    "title": "Confirmar ausencia de fugas",
                    "response_type": "confirmation",
                    "required": "1",
                    "config_json": "{}",
                },
            ],
        )
        db.session.commit()
        return procedure, version

    def test_publish_clone_and_replace_version_without_mutating_history(self):
        procedure, first = self._draft()
        publish_version(first, self.company.id, self.admin.id)
        db.session.commit()
        self.assertEqual(first.status, PROCEDURE_VERSION_PUBLISHED)
        self.assertEqual(len(first.steps), 2)

        with self.assertRaisesRegex(ValueError, "inmutable"):
            save_draft_version(
                first,
                self.company.id,
                self.admin.id,
                {},
                [{"title": "Intento de cambio"}],
            )

        second = create_draft_version(procedure, self.company.id, self.admin.id)
        db.session.flush()
        self.assertEqual(second.version, 2)
        self.assertEqual([item.code for item in second.steps], ["STEP-001", "STEP-002"])
        save_draft_version(
            second,
            self.company.id,
            self.admin.id,
            {"change_notes": "Ajuste de seguridad"},
            [
                {
                    "code": "STEP-001",
                    "title": "Verificar presión y nivel",
                    "response_type": "measurement",
                    "required": "1",
                    "config_json": '{"unit":"bar"}',
                }
            ],
        )
        publish_version(second, self.company.id, self.admin.id)
        db.session.commit()

        self.assertEqual(first.status, PROCEDURE_VERSION_RETIRED)
        self.assertEqual(first.steps[0].title, "Verificar nivel")
        self.assertEqual(second.status, PROCEDURE_VERSION_PUBLISHED)
        self.assertEqual(procedure.published_version.id, second.id)
        events = {
            item.event for item in MaintenanceProcedureEvent.query.filter_by(
                procedure_id=procedure.id
            )
        }
        self.assertTrue(
            {"procedure_created", "draft_saved", "version_published", "version_retired"}
            <= events
        )

    def test_tenant_boundaries_cover_codes_actors_and_machine_types(self):
        own, _version = self._draft(code="PM-SHARED")
        other, _other_version = self._draft(
            company=self.other_company,
            actor=self.other_admin,
            code="PM-SHARED",
        )
        self.assertNotEqual(own.id, other.id)

        with self.assertRaisesRegex(ValueError, "empresa activa"):
            create_draft_version(own, self.company.id, self.other_admin.id)
        with self.assertRaisesRegex(ValueError, "no pertenece"):
            create_procedure(
                self.company.id,
                self.admin.id,
                {
                    "code": "PM-FOREIGN",
                    "name": "Tipo de activo externo",
                    "machine_type_id": self.other_machine_type.id,
                },
            )
        with self.assertRaisesRegex(ValueError, "Ya existe"):
            create_procedure(
                self.company.id,
                self.admin.id,
                {"code": "PM-SHARED", "name": "Duplicado local"},
            )

    def test_catalog_metadata_is_editable_and_audited(self):
        procedure, _version = self._draft()
        update_procedure(
            procedure,
            self.company.id,
            self.admin.id,
            {
                "code": "PM-CMP-002",
                "name": "Inspección anual de compresor",
                "description": "Nueva descripción",
                "machine_type_id": "",
                "active": "0",
            },
        )
        db.session.commit()
        self.assertEqual(procedure.code, "PM-CMP-002")
        self.assertFalse(procedure.active)
        self.assertIsNone(procedure.machine_type_id)
        self.assertTrue(
            MaintenanceProcedureEvent.query.filter_by(
                procedure_id=procedure.id, event="procedure_updated"
            ).first()
        )

    def test_permissions_and_catalog_route_respect_role_and_tenant(self):
        own, own_version = self._draft(code="PM-OWN")
        publish_version(own_version, self.company.id, self.admin.id)
        inactive, inactive_version = self._draft(code="PM-INACTIVE")
        publish_version(inactive_version, self.company.id, self.admin.id)
        update_procedure(
            inactive,
            self.company.id,
            self.admin.id,
            {
                "code": inactive.code,
                "name": inactive.name,
                "description": inactive.description,
                "machine_type_id": inactive.machine_type_id,
                "active": "0",
            },
        )
        other, _other_version = self._draft(
            company=self.other_company,
            actor=self.other_admin,
            code="PM-OTHER",
        )
        db.session.commit()
        self.assertTrue(can_view_maintenance_procedures(self.technician))
        self.assertFalse(can_manage_maintenance_procedures(self.technician))
        self.assertTrue(can_manage_maintenance_procedures(self.admin))

        client = self.app.test_client()
        login = client.post(
            "/login",
            data={
                "username": self.admin.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(login.status_code, 302)
        listing = client.get("/maintenance/procedures/")
        html = listing.get_data(as_text=True)
        self.assertEqual(listing.status_code, 200)
        self.assertIn("PM-OWN", html)
        self.assertNotIn("PM-OTHER", html)
        self.assertEqual(
            client.get(f"/maintenance/procedures/{own.id}").status_code, 200
        )
        self.assertEqual(client.get("/maintenance/procedures/new").status_code, 200)
        self.assertEqual(
            client.get(f"/maintenance/procedures/{own.id}/edit").status_code, 200
        )
        self.assertEqual(
            client.get(
                f"/maintenance/procedures/{own.id}/versions/{own_version.id}/edit"
            ).status_code,
            302,
        )
        self.assertEqual(
            client.get(f"/maintenance/procedures/{other.id}").status_code, 404
        )

        client.post("/logout")
        client.post(
            "/login",
            data={
                "username": self.technician.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        technician_listing = client.get("/maintenance/procedures/")
        technician_html = technician_listing.get_data(as_text=True)
        self.assertEqual(technician_listing.status_code, 200)
        self.assertIn("PM-OWN", technician_html)
        self.assertNotIn("PM-INACTIVE", technician_html)
        self.assertIn("Procedimientos", technician_html)
        self.assertNotIn("Nuevo procedimiento", technician_html)


if __name__ == "__main__":
    unittest.main()
