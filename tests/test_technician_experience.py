from datetime import date, datetime
import re
import unittest

from app import create_app, db
from app.incident_notifications import (
    authorized_unread_notifications,
    create_technician_assignment_notification,
)
from app.models import (
    Empresa,
    Incident,
    Machine,
    MachineType,
    PlanSuscripcion,
    Technician,
    User,
    WorkOrder,
)


class TestTechnicianExperience(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.company = Empresa(
            razon_social="Servicio Tecnico SAS",
            slug="servicio-tecnico",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(self.company)
        db.session.flush()
        self.user = User(
            empresa_id=self.company.id,
            username="tecnico1",
            nombre_visible="Carlos Técnico",
            rol="tecnico",
            area="Mantenimiento",
            activo=True,
            onboarding_completado=True,
        )
        self.user.set_password(self.PASSWORD)
        other_user = User(
            empresa_id=self.company.id,
            username="tecnico2",
            nombre_visible="Laura Técnica",
            rol="tecnico",
            area="Mantenimiento",
            activo=True,
            onboarding_completado=True,
        )
        other_user.set_password(self.PASSWORD)
        machine_type = MachineType(
            empresa_id=self.company.id,
            clave="equipos_test",
            nombre="Equipo",
            prefijo="EQ",
        )
        db.session.add_all([self.user, other_user, machine_type])
        db.session.flush()
        self.technician = Technician(
            empresa_id=self.company.id,
            user_id=self.user.id,
            nombre="Carlos Técnico",
            activo=True,
        )
        other_technician = Technician(
            empresa_id=self.company.id,
            user_id=other_user.id,
            nombre="Laura Técnica",
            activo=True,
        )
        db.session.add_all([self.technician, other_technician])
        db.session.flush()
        self.own_machine = Machine(
            empresa_id=self.company.id,
            codigo="EQ-001",
            machine_type_id=machine_type.id,
            nombre="Compresor asignado",
        )
        other_machine = Machine(
            empresa_id=self.company.id,
            codigo="EQ-002",
            machine_type_id=machine_type.id,
            nombre="Equipo ajeno",
        )
        db.session.add_all([self.own_machine, other_machine])
        db.session.flush()
        self.own_order = WorkOrder(
            empresa_id=self.company.id,
            numero="OT-OWN",
            titulo="Preventivo propio",
            machine_id=self.own_machine.id,
            technician_id=self.technician.id,
            tipo="preventivo",
            prioridad="alta",
            status="abierta",
            fecha_programada=date.today(),
        )
        self.other_order = WorkOrder(
            empresa_id=self.company.id,
            numero="OT-OTHER",
            titulo="Correctivo ajeno",
            machine_id=other_machine.id,
            technician_id=other_technician.id,
            status="abierta",
            fecha_programada=date.today(),
        )
        self.own_incident = Incident(
            empresa_id=self.company.id,
            numero="INC-OWN",
            titulo="Incidencia asignada",
            tecnico_asignado_id=self.technician.id,
            area_responsable="Mantenimiento",
            estado="asignado",
        )
        self.other_incident = Incident(
            empresa_id=self.company.id,
            numero="INC-OTHER",
            titulo="Incidencia de otro técnico",
            tecnico_asignado_id=other_technician.id,
            area_responsable="Mantenimiento",
            estado="asignado",
        )
        db.session.add_all([
            self.own_order,
            self.other_order,
            self.own_incident,
            self.other_incident,
            PlanSuscripcion(
                empresa_id=self.company.id,
                plan="professional",
                fecha_inicio=date.today(),
                activo=True,
                estado_ciclo="activa",
            ),
        ])
        db.session.commit()
        self.client = self.app.test_client()
        response = self.client.post("/login", data={
            "username": self.user.username,
            "empresa_slug": self.company.slug,
            "password": self.PASSWORD,
        })
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_dashboard_and_menu_are_operational(self):
        response = self.client.get("/dashboard")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Buenos días, Carlos Técnico", html)
        self.assertIn("Preventivo propio", html)
        self.assertNotIn("Correctivo ajeno", html)
        self.assertIn("Mis órdenes de trabajo", html)
        self.assertIn("Mis incidencias", html)
        self.assertIn("Mis activos", html)
        self.assertIn('href="/notificaciones"', html)
        self.assertNotIn("Administración", html)
        self.assertNotIn("Compras", html)
        self.assertNotIn("Análisis", html)

    def test_bell_only_counts_logged_in_technician_assignments(self):
        response = self.client.get("/dashboard")
        html = response.get_data(as_text=True)
        self.assertIn("Mis alertas", html)
        self.assertIn("Mis OT programadas hoy", html)
        self.assertIn("Mis incidencias pendientes", html)
        programmed = re.search(
            r"Mis OT programadas hoy.*?header-alert-badge[^>]*>\s*(\d+)",
            html,
            re.S,
        )
        incidents = re.search(
            r"Mis incidencias pendientes.*?header-alert-badge[^>]*>\s*(\d+)",
            html,
            re.S,
        )
        self.assertIsNotNone(programmed)
        self.assertIsNotNone(incidents)
        self.assertEqual(int(programmed.group(1)), 1)
        self.assertEqual(int(incidents.group(1)), 1)

    def test_lists_and_direct_access_only_show_assignments(self):
        orders = self.client.get("/ordenes").get_data(as_text=True)
        incidents = self.client.get("/incidencias").get_data(as_text=True)
        assets = self.client.get("/activos").get_data(as_text=True)
        self.assertIn("OT-OWN", orders)
        self.assertNotIn("OT-OTHER", orders)
        self.assertIn("INC-OWN", incidents)
        self.assertNotIn("INC-OTHER", incidents)
        self.assertIn("Compresor asignado", assets)
        self.assertNotIn("Equipo ajeno", assets)
        own_detail = self.client.get(f"/ordenes/{self.own_order.id}/editar")
        self.assertEqual(own_detail.status_code, 200)
        self.assertIn("El cierre definitivo corresponde al supervisor", own_detail.get_data(as_text=True))
        self.assertEqual(self.client.get(f"/ordenes/{self.other_order.id}/editar").status_code, 404)
        self.assertEqual(self.client.get(f"/incidencias/{self.other_incident.id}").status_code, 404)

    def test_management_routes_are_blocked(self):
        response = self.client.get("/analisis", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/dashboard"))

    def test_profile_allows_personal_data_but_protects_employment_fields(self):
        page = self.client.get("/mi-perfil")
        html = page.get_data(as_text=True)
        self.assertEqual(page.status_code, 200)
        self.assertIn("Puedes cambiar nombre, correo, teléfono y contraseña", html)

        original_rate = self.user.tarifa_hora
        response = self.client.post(
            "/mi-perfil",
            data={
                "username": "usuario-alterado",
                "nombre_visible": "Carlos Actualizado",
                "area": "Gerencia",
                "cargo": "Administrador",
                "sede_id": "",
                "email": self.user.email or "",
                "telefono": "3001234567",
                "rol": "admin",
                "tarifa_hora": "999999",
                "password": "",
                "password2": "",
                "activo": "1",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/mi-perfil"))
        db.session.refresh(self.user)
        self.assertEqual(self.user.nombre_visible, "Carlos Actualizado")
        self.assertEqual(self.user.telefono, "3001234567")
        self.assertEqual(self.user.username, "tecnico1")
        self.assertEqual(self.user.area, "Mantenimiento")
        self.assertEqual(self.user.cargo, "")
        self.assertEqual(self.user.rol, "tecnico")
        self.assertEqual(self.user.tarifa_hora, original_rate)

    def test_technician_cannot_change_master_data_or_close_order(self):
        response = self.client.post(
            f"/ordenes/{self.own_order.id}/editar",
            data={
                "titulo": "Título alterado",
                "prioridad": "baja",
                "status_manual": "cerrada",
                "jornada_estado_ot": "completado",
                "tiempo_manual": "1",
                "tiempo_horas": "1",
                "tiempo_minutos": "0",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.own_order)
        self.assertEqual(self.own_order.titulo, "Preventivo propio")
        self.assertEqual(self.own_order.prioridad, "alta")
        self.assertNotIn(self.own_order.status, ("cerrada", "completado"))

    def test_assignment_notification_is_only_visible_to_assigned_technician(self):
        item = create_technician_assignment_notification(
            self.own_incident, technician_user=self.user
        )
        db.session.commit()
        self.assertIsNotNone(item)
        self.assertEqual([row.id for row in authorized_unread_notifications(self.user)], [item.id])
        center = self.client.get("/notificaciones")
        center_html = center.get_data(as_text=True)
        self.assertEqual(center.status_code, 200)
        self.assertIn("Centro personal de notificaciones", center_html)
        self.assertIn("Nueva incidencia asignada", center_html)
        self.assertIn("INC-OWN", center_html)

        read = self.client.post(
            f"/notificaciones/{item.id}/accion",
            data={"action": "read"},
            follow_redirects=False,
        )
        self.assertEqual(read.status_code, 302)
        db.session.refresh(item)
        self.assertTrue(item.read)


if __name__ == "__main__":
    unittest.main()
