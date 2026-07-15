from datetime import date, datetime
import unittest

from app import create_app, db
from app.models import Empresa, Incident, PlanSuscripcion, User


class TestRequesterAlerts(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        company = Empresa(
            razon_social="Solicitantes SAS",
            slug="solicitantes-sas",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(company)
        db.session.flush()
        self.requester = User(
            empresa_id=company.id,
            username="reportante",
            rol="solicitante",
            area="Producción",
            activo=True,
            onboarding_completado=True,
        )
        self.requester.set_password("Clave-Segura-123!")
        another = User(
            empresa_id=company.id,
            username="otro_reportante",
            rol="solicitante",
            area="Producción",
            activo=True,
            onboarding_completado=True,
        )
        another.set_password("Clave-Segura-123!")
        db.session.add_all([self.requester, another])
        db.session.flush()
        db.session.add_all(
            [
                Incident(
                    empresa_id=company.id,
                    user_id=self.requester.id,
                    numero="INC-26-0001",
                    titulo="Mi ticket pendiente",
                    descripcion="Pendiente",
                    area="Producción",
                    area_responsable="Mantenimiento",
                    resuelto=False,
                ),
                Incident(
                    empresa_id=company.id,
                    user_id=another.id,
                    numero="INC-26-0002",
                    titulo="Ticket de otra persona",
                    descripcion="Pendiente",
                    area="Producción",
                    area_responsable="Mantenimiento",
                    resuelto=False,
                ),
                PlanSuscripcion(
                    empresa_id=company.id,
                    plan="professional",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        db.session.commit()
        self.client = self.app.test_client()
        response = self.client.post(
            "/login",
            data={
                "username": "reportante",
                "empresa_slug": "solicitantes-sas",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_bell_only_contains_requesters_own_tickets(self):
        response = self.client.get("/incidencias")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Mis tickets", html)
        self.assertIn("Tickets pendientes", html)
        self.assertNotIn("Vencimientos", html)
        self.assertNotIn("Programados hoy", html)
        self.assertNotIn("En proceso", html)


if __name__ == "__main__":
    unittest.main()
