from datetime import date, datetime
from decimal import Decimal
import unittest

from app import create_app, db
from app.models import (
    Empresa,
    Machine,
    MachineType,
    PlanSuscripcion,
    Technician,
    User,
    WorkOrder,
    WorkOrderEjecucionTipo,
    WorkOrderJornada,
    WorkOrderRepuesto,
)
from app.routes import _parse_tarifa_hora_equipo


class TestLaborCosts(unittest.TestCase):
    def test_journey_uses_current_user_rate_for_legacy_rows(self):
        user = User(username="tecnico", password_hash="x", tarifa_hora=Decimal("24000.00"))
        technician = Technician(nombre="Técnico", user=user)
        journey = WorkOrderJornada(
            fecha_inicio=datetime(2026, 7, 14, 8, 0),
            fecha_fin=datetime(2026, 7, 14, 9, 30),
            technician=technician,
            tarifa_hora_aplicada=None,
        )

        self.assertEqual(journey.tarifa_hora_efectiva, 24000.0)
        self.assertEqual(journey.costo_mano_obra, 36000.0)

    def test_snapshot_does_not_change_when_user_rate_changes(self):
        user = User(username="tecnico", password_hash="x", tarifa_hora=Decimal("40000.00"))
        technician = Technician(nombre="Técnico", user=user)
        journey = WorkOrderJornada(
            fecha_inicio=datetime(2026, 7, 14, 8, 0),
            fecha_fin=datetime(2026, 7, 14, 10, 0),
            technician=technician,
            tarifa_hora_aplicada=Decimal("25000.00"),
        )

        self.assertEqual(journey.costo_mano_obra, 50000.0)

    def test_work_order_total_combines_all_cost_components(self):
        order = WorkOrder(
            titulo="Costo completo",
            machine_id=1,
            ejecucion_tipo=WorkOrderEjecucionTipo.EXTERNO.value,
            costo_real=30000,
        )
        order.jornadas.append(
            WorkOrderJornada(
                fecha_inicio=datetime(2026, 7, 14, 8, 0),
                fecha_fin=datetime(2026, 7, 14, 10, 0),
                tarifa_hora_aplicada=Decimal("25000.00"),
                costo_herramientas=Decimal("12000.00"),
            )
        )
        order.repuestos.append(
            WorkOrderRepuesto(
                spare_part_id=1,
                cantidad=2,
                costo_unitario_aplicado=Decimal("8000.00"),
            )
        )

        self.assertEqual(order.costo_mano_obra_total, 50000.0)
        self.assertEqual(order.costo_repuestos_total, 16000.0)
        self.assertEqual(order.costo_herramientas_total, 12000.0)
        self.assertEqual(order.costo_servicio_externo, 30000.0)
        self.assertEqual(order.costo_total_mantenimiento, 108000.0)

    def test_spare_part_snapshot_preserves_historical_cost(self):
        line = WorkOrderRepuesto(
            spare_part_id=1,
            cantidad=3,
            costo_unitario_aplicado=Decimal("7500.00"),
        )

        self.assertEqual(line.costo_total_linea, 22500.0)

    def test_rate_parser_respects_company_currency_format(self):
        empresa = type("EmpresaStub", (), {"moneda": "COP"})()
        value, error = _parse_tarifa_hora_equipo({"tarifa_hora": "25.500,50"}, empresa)
        self.assertIsNone(error)
        self.assertEqual(value, 25500.50)

    def test_rate_parser_rejects_negative_values(self):
        empresa = type("EmpresaStub", (), {"moneda": "USD"})()
        _, error = _parse_tarifa_hora_equipo({"tarifa_hora": "-5"}, empresa)
        self.assertIsNotNone(error)

class TestLaborCostReport(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        empresa = Empresa(
            razon_social="Costos SAS",
            slug="costos-sas",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(empresa)
        db.session.flush()
        user = User(
            empresa_id=empresa.id,
            username="admincostos",
            nombre_visible="Técnico de costos",
            rol="superadmin",
            activo=True,
            onboarding_completado=True,
            tarifa_hora=Decimal("25000.00"),
        )
        user.set_password("Clave-Segura-123!")
        machine_type = MachineType(
            empresa_id=empresa.id,
            clave="general_costos",
            nombre="Equipo general",
            prefijo="CT",
        )
        db.session.add_all([user, machine_type])
        db.session.flush()
        technician = Technician(
            empresa_id=empresa.id,
            user_id=user.id,
            nombre=user.nombre_visible,
            activo=True,
        )
        machine = Machine(
            empresa_id=empresa.id,
            codigo="CT-001",
            machine_type_id=machine_type.id,
            nombre="Equipo prueba",
        )
        db.session.add_all([technician, machine])
        db.session.flush()
        order = WorkOrder(
            empresa_id=empresa.id,
            titulo="OT con mano de obra",
            machine_id=machine.id,
            fecha_programada=date.today(),
        )
        order.jornadas.append(
            WorkOrderJornada(
                orden=1,
                fecha_inicio=datetime.combine(date.today(), datetime.min.time()).replace(hour=8),
                fecha_fin=datetime.combine(date.today(), datetime.min.time()).replace(hour=10),
                technician_id=technician.id,
                tarifa_hora_aplicada=Decimal("25000.00"),
                costo_herramientas=Decimal("12000.00"),
                recibido_por="Supervisor",
            )
        )
        db.session.add_all(
            [
                order,
                PlanSuscripcion(
                    empresa_id=empresa.id,
                    plan="professional",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_cost_report_includes_labor(self):
        login = self.client.post(
            "/login",
            data={
                "username": "admincostos",
                "empresa_slug": "costos-sas",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(login.status_code, 302)

        response = self.client.get("/mantenimiento/analisis-costos")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Mano de obra", response.get_data(as_text=True))
        self.assertIn("$50.000", response.get_data(as_text=True))
        self.assertIn("Herramientas", response.get_data(as_text=True))
        self.assertIn("$12.000", response.get_data(as_text=True))
        self.assertIn("$62.000", response.get_data(as_text=True))

    def test_work_order_modal_exposes_tool_cost_and_main_form_is_summary_only(self):
        self.client.post(
            "/login",
            data={
                "username": "admincostos",
                "empresa_slug": "costos-sas",
                "password": "Clave-Segura-123!",
            },
        )
        order = WorkOrder.query.filter_by(titulo="OT con mano de obra").one()
        response = self.client.get(f"/ordenes/{order.id}/editar")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('id="jornadaCostoHerramientas"', html)
        self.assertNotIn('name="costo_herramientas"', html)
        self.assertIn("se acumulan desde las jornadas", html)

    def test_asset_life_includes_cost_breakdown(self):
        self.client.post(
            "/login",
            data={
                "username": "admincostos",
                "empresa_slug": "costos-sas",
                "password": "Clave-Segura-123!",
            },
        )
        machine = Machine.query.filter_by(codigo="CT-001").one()
        response = self.client.get(f"/activos/{machine.id}/hoja-vida")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Costo total de mantenimiento", html)
        self.assertIn("Costo repuestos", html)
        self.assertIn("$62.000", html)

        pdf_response = self.client.get(f"/activos/{machine.id}/hoja-vida/pdf")
        self.assertEqual(pdf_response.status_code, 200)
        self.assertTrue(pdf_response.data.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
