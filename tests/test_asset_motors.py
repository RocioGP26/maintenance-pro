"""Gestión y trazabilidad de motores asociados a activos."""

from datetime import datetime
import unittest

from app import create_app, db
from app.models import (
    AssetMotorAssignment,
    Empresa,
    Machine,
    MachineType,
    PlanSuscripcion,
    User,
)


class TestAssetMotors(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.company = Empresa(
            razon_social="Motores SAS",
            slug="motores-sas",
            email_verified_at=datetime.utcnow(),
        )
        self.other_company = Empresa(
            razon_social="Otra SAS",
            slug="otra-motores-sas",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add_all([self.company, self.other_company])
        db.session.flush()
        self.admin = User(
            empresa_id=self.company.id,
            username="adminmotor",
            nombre_visible="Admin Motores",
            rol="superadmin",
            activo=True,
            onboarding_completado=True,
        )
        self.admin.set_password("Clave-Segura-123!")
        general = MachineType(
            empresa_id=self.company.id,
            clave="equipo_motor_test",
            nombre="Equipo industrial",
            prefijo="AMT",
        )
        motor_type = MachineType(
            empresa_id=self.company.id,
            clave="motor_electrico_test",
            nombre="Motor eléctrico",
            prefijo="MOT",
        )
        other_type = MachineType(
            empresa_id=self.other_company.id,
            clave="motor_otro_test",
            nombre="Motor eléctrico",
            prefijo="OMT",
        )
        db.session.add_all([self.admin, general, motor_type, other_type])
        db.session.flush()
        self.asset = Machine(
            empresa_id=self.company.id,
            codigo="AMT-001",
            machine_type_id=general.id,
            nombre="Extrusora",
            tiene_motores=True,
        )
        self.motor = Machine(
            empresa_id=self.company.id,
            codigo="MOT-001",
            machine_type_id=motor_type.id,
            nombre="Motor principal",
            marca="WEG",
            modelo="W22",
            numero_serie="SER-001",
        )
        self.other_motor = Machine(
            empresa_id=self.other_company.id,
            codigo="OMT-001",
            machine_type_id=other_type.id,
            nombre="Motor ajeno",
        )
        db.session.add_all([self.asset, self.motor, self.other_motor])
        db.session.add(
            PlanSuscripcion(
                empresa_id=self.company.id,
                plan="professional",
                fecha_inicio=datetime.utcnow().date(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()
        self.client = self.app.test_client()
        login = self.client.post(
            "/login",
            data={
                "username": "adminmotor",
                "empresa_slug": "motores-sas",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(login.status_code, 302)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_associate_existing_motor_and_show_life_sheet(self):
        edit = self.client.get(f"/activos/{self.asset.id}/editar")
        self.assertEqual(edit.status_code, 200)
        edit_html = edit.get_data(as_text=True)
        self.assertIn("¿Tiene motores asociados?", edit_html)
        self.assertIn("Motores y Accionamientos", edit_html)
        self.assertIn('id="motorAddBtn"', edit_html)
        self.assertIn("como un activo independiente", edit_html)
        self.assertNotIn("Activo motor existente", edit_html)

        response = self.client.post(
            f"/activos/{self.asset.id}/motores",
            json={
                "action": "save",
                "nombre_funcion": "Motor principal",
                "source_type": "machine",
                "source_id": self.motor.id,
                "potencia": "15",
                "potencia_unidad": "kW",
                "rpm": "1750",
                "voltaje": "220/440 V",
                "amperaje": "42 A",
                "fecha_instalacion": "2026-08-09",
                "estado": "instalado",
            },
        )
        self.assertEqual(response.status_code, 200)
        row = AssetMotorAssignment.query.one()
        self.assertEqual(row.motor_machine_id, self.motor.id)
        self.assertEqual(row.identificador, "MOT-001")
        self.assertEqual(row.marca, "WEG")
        self.assertEqual(row.rpm, 1750)

        life = self.client.get(f"/activos/{self.asset.id}/hoja-vida")
        self.assertEqual(life.status_code, 200)
        html = life.get_data(as_text=True)
        self.assertIn("Motores y Accionamientos", html)
        self.assertIn("Motores: 1 asignados", html)
        self.assertIn("MOT-001", html)
        self.assertIn("15 kW", html)
        pdf = self.client.get(f"/activos/{self.asset.id}/hoja-vida/pdf")
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.data.startswith(b"%PDF"))

    def test_replacement_retires_previous_without_deleting_history(self):
        old = AssetMotorAssignment(
            empresa_id=self.company.id,
            asset_id=self.asset.id,
            motor_machine_id=self.motor.id,
            nombre_funcion="Motor principal",
            identificador="MOT-001",
            estado="mantenimiento",
            created_by_id=self.admin.id,
        )
        db.session.add(old)
        db.session.commit()

        response = self.client.post(
            f"/activos/{self.asset.id}/motores",
            json={
                "action": "save",
                "nombre_funcion": "Motor principal de reemplazo",
                "source_type": "new",
                "identificador": "MOT-TEMP-02",
                "potencia_unidad": "HP",
                "estado": "instalado",
                "fecha_instalacion": "2026-08-10",
                "reemplaza_asignacion_id": old.id,
            },
        )
        self.assertEqual(response.status_code, 200)
        db.session.refresh(old)
        new = AssetMotorAssignment.query.filter_by(identificador="MOT-TEMP-02").one()
        self.assertEqual(old.estado, "retirado")
        self.assertEqual(old.fecha_retiro.isoformat(), "2026-08-10")
        self.assertEqual(new.reemplaza_asignacion_id, old.id)
        self.assertEqual(AssetMotorAssignment.query.count(), 2)

    def test_embedded_motor_does_not_create_an_independent_asset(self):
        machine_count = Machine.query.filter_by(empresa_id=self.company.id).count()

        response = self.client.post(
            f"/activos/{self.asset.id}/motores",
            json={
                "action": "save",
                "nombre_funcion": "Motor de ventilación",
                "source_type": "new",
                "identificador": "MOT-COMP-01",
                "marca": "WEG",
                "modelo": "W22",
                "numero_serie": "COMP-001",
                "potencia": "5",
                "potencia_unidad": "HP",
                "rpm": "1750",
                "estado": "instalado",
            },
        )

        self.assertEqual(response.status_code, 200)
        row = AssetMotorAssignment.query.filter_by(identificador="MOT-COMP-01").one()
        self.assertEqual(row.asset_id, self.asset.id)
        self.assertIsNone(row.motor_machine_id)
        self.assertIsNone(row.spare_part_id)
        self.assertEqual(
            Machine.query.filter_by(empresa_id=self.company.id).count(),
            machine_count,
        )

    def test_rejects_motor_from_another_tenant(self):
        response = self.client.post(
            f"/activos/{self.asset.id}/motores",
            json={
                "action": "save",
                "nombre_funcion": "Motor ajeno",
                "source_type": "machine",
                "source_id": self.other_motor.id,
                "potencia_unidad": "kW",
                "estado": "instalado",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["ok"])
        self.assertEqual(AssetMotorAssignment.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
