from datetime import date, datetime, timedelta
import unittest

from app import create_app, db
from app.models import Empresa, Machine, MachineType, PlanSuscripcion, User, WorkOrder


class TestDashboardAnalysisSeparation(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        empresa = Empresa(
            razon_social="Operaciones SAS",
            slug="operaciones-sas",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(empresa)
        db.session.flush()
        user = User(
            empresa_id=empresa.id,
            username="adminops",
            nombre_visible="Administrador de operaciones",
            rol="superadmin",
            activo=True,
            onboarding_completado=True,
        )
        user.set_password("Clave-Segura-123!")
        machine_type = MachineType(
            empresa_id=empresa.id,
            clave="general_ops",
            nombre="Equipo general",
            prefijo="OP",
        )
        db.session.add_all([user, machine_type])
        db.session.flush()
        machine = Machine(
            empresa_id=empresa.id,
            codigo="OP-001",
            machine_type_id=machine_type.id,
            nombre="Equipo operativo",
            garantia_hasta=date.today() + timedelta(days=10),
        )
        db.session.add(machine)
        db.session.flush()
        db.session.add(
            WorkOrder(
                empresa_id=empresa.id,
                titulo="Preventivo del día",
                machine_id=machine.id,
                tipo="preventivo",
                status="abierta",
                fecha_programada=date.today(),
            )
        )
        db.session.add(
            PlanSuscripcion(
                empresa_id=empresa.id,
                plan="professional",
                fecha_inicio=date.today(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()
        self.client = self.app.test_client()
        login = self.client.post(
            "/login",
            data={
                "username": "adminops",
                "empresa_slug": "operaciones-sas",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(login.status_code, 302)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_home_is_operational_and_not_strategic(self):
        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Centro de Operaciones", html)
        self.assertIn("¿Qué requiere tu atención hoy?", html)
        self.assertIn("Preventivos de hoy", html)
        self.assertIn("Preventivo del día", html)
        self.assertIn("Garantías por vencer", html)
        self.assertNotIn("MTBF planta", html)
        self.assertNotIn("MTTR prom.", html)

    def test_analysis_summary_exposes_business_intelligence_modules(self):
        response = self.client.get("/analisis")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Inteligencia de negocio", html)
        self.assertIn("Costos de mantenimiento", html)
        self.assertIn("Reportes y exportaciones", html)

    def test_maintenance_analysis_keeps_kpis_and_its_own_filter_actions(self):
        response = self.client.get("/analisis/mantenimiento")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Análisis · Mantenimiento", html)
        self.assertIn("MTBF planta", html)
        self.assertIn("MTTR prom.", html)
        self.assertIn('action="/analisis/mantenimiento"', html)

    def test_sidebar_separates_start_and_analysis(self):
        response = self.client.get("/dashboard")
        html = response.get_data(as_text=True)

        self.assertIn("Inicio", html)
        self.assertIn("Inteligencia", html)
        self.assertIn("Análisis", html)


if __name__ == "__main__":
    unittest.main()
