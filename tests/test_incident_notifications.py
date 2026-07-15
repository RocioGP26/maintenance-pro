from datetime import date, datetime
from uuid import uuid4
import unittest

from app import create_app, db
from app.incident_notifications import (
    authorized_unread_notifications,
    create_incident_notifications,
    create_reporter_status_notification,
)
from app.models import (
    Empresa,
    Incident,
    IncidentHistory,
    IncidentNotification,
    PlanSuscripcion,
    User,
)


class TestIncidentNotifications(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.company = Empresa(
            razon_social="Áreas SAS",
            slug="areas-sas",
            email_verified_at=datetime.utcnow(),
        )
        other_company = Empresa(
            razon_social="Otro Tenant SAS",
            slug="otro-tenant",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add_all([self.company, other_company])
        db.session.flush()
        self.maintenance_supervisor = self._user(
            self.company, "supervisor_mant", "supervisor", "Mantenimiento"
        )
        self.maintenance_technician = self._user(
            self.company, "tecnico_mant", "tecnico", "MANTENIMIENTO"
        )
        self.tic_coordinator = self._user(
            self.company, "coord_tic", "admin", "Sistemas"
        )
        self.other_area_admin = self._user(
            self.company, "admin_calidad", "admin", "Calidad"
        )
        self.read_only_same_area = self._user(
            self.company, "lector_mant", "usuario", "Mantenimiento"
        )
        self.inactive_technician = self._user(
            self.company, "inactivo_mant", "tecnico", "Mantenimiento", activo=False
        )
        self.reporter = self._user(
            self.company, "reportante", "solicitante", "Producción"
        )
        self.other_tenant_user = self._user(
            other_company, "supervisor_otro", "supervisor", "Mantenimiento"
        )
        db.session.add_all(
            [
                PlanSuscripcion(
                    empresa_id=self.company.id,
                    plan="professional",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=other_company.id,
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
        self.ctx.pop()

    def _user(self, company, username, role, area, activo=True):
        user = User(
            empresa_id=company.id,
            username=username,
            nombre_visible=username.replace("_", " ").title(),
            rol=role,
            area=area,
            activo=activo,
            onboarding_completado=True,
        )
        user.set_password(self.PASSWORD)
        db.session.add(user)
        return user

    def _login(self, username="supervisor_mant", slug="areas-sas"):
        client = self.app.test_client()
        response = client.post(
            "/login",
            data={"username": username, "empresa_slug": slug, "password": self.PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        return client

    def _incident(self, area="Mantenimiento"):
        item = Incident(
            empresa_id=self.company.id,
            numero=f"INC-26-{Incident.query.count() + 1:04d}",
            titulo="Equipo detenido",
            descripcion="Prueba de notificación",
            area="Producción",
            area_responsable=area,
            reportado_por="Ana López",
            ubicacion="Laboratorio de Calidad",
            prioridad="alta",
        )
        db.session.add(item)
        db.session.flush()
        return item

    def test_creation_respects_tenant_area_role_active_and_unique_contract(self):
        incident = self._incident("Mantenimiento")
        created = create_incident_notifications(incident)
        db.session.commit()

        self.assertEqual(
            {item.user_id for item in created},
            {self.maintenance_supervisor.id, self.maintenance_technician.id},
        )
        self.assertNotIn(self.other_area_admin.id, {item.user_id for item in created})
        self.assertNotIn(self.read_only_same_area.id, {item.user_id for item in created})
        self.assertNotIn(self.inactive_technician.id, {item.user_id for item in created})
        self.assertNotIn(self.other_tenant_user.id, {item.user_id for item in created})

        self.assertEqual(create_incident_notifications(incident), [])
        db.session.commit()
        self.assertEqual(IncidentNotification.query.count(), 2)

    def test_tic_alias_routes_only_to_authorized_tic_users(self):
        incident = self._incident("TIC / Sistemas")
        created = create_incident_notifications(incident)
        db.session.commit()

        self.assertEqual([item.user_id for item in created], [self.tic_coordinator.id])

    def test_area_change_hides_old_delivery_and_notifies_new_area(self):
        incident = self._incident("Mantenimiento")
        create_incident_notifications(incident)
        db.session.flush()
        incident.area_responsable = "TIC / Sistemas"
        created = create_incident_notifications(incident)
        db.session.commit()

        self.assertEqual([item.user_id for item in created], [self.tic_coordinator.id])
        self.assertEqual(
            authorized_unread_notifications(self.maintenance_supervisor), []
        )
        self.assertEqual(
            [item.user_id for item in authorized_unread_notifications(self.tic_coordinator)],
            [self.tic_coordinator.id],
        )

    def test_incident_form_creates_notifications_and_audit(self):
        client = self._login("reportante")
        response = client.post(
            "/incidencia",
            data={
                "idempotency_key": str(uuid4()),
                "reportado_por": "Ana López",
                "cargo_reportante": "Analista",
                "telefono_contacto": "3000000000",
                "area": "Producción",
                "area_responsable": "Mantenimiento",
                "ubicacion": "Laboratorio",
                "titulo": "Falla de prueba",
                "machine_id": "",
                "tipo": "otro",
                "descripcion": "Descripción completa del incidente",
                "prioridad": "alta",
                "fecha_evento": date.today().isoformat(),
                "hora_evento": "08:42",
            },
        )

        self.assertEqual(response.status_code, 302)
        incident = Incident.query.filter_by(titulo="Falla de prueba").one()
        self.assertEqual(
            {item.user_id for item in incident.notifications.all()},
            {self.maintenance_supervisor.id, self.maintenance_technician.id},
        )
        audit = IncidentHistory.query.filter_by(
            incident_id=incident.id, accion="notificaciones_creadas"
        ).one()
        self.assertIn("2 usuario(s)", audit.comentario)

    def test_seen_keeps_badge_and_read_clears_it_with_audit(self):
        incident = self._incident()
        create_incident_notifications(incident)
        db.session.commit()
        notification = IncidentNotification.query.filter_by(
            incident_id=incident.id, user_id=self.maintenance_supervisor.id
        ).one()
        client = self._login()

        unread = client.get("/api/incidents/notifications/unread")
        self.assertEqual(unread.status_code, 200)
        self.assertEqual(unread.get_json()["count"], 1)
        self.assertFalse(unread.get_json()["items"][0]["shown"])

        seen = client.post(f"/api/incidents/notifications/{notification.id}/seen")
        self.assertEqual(seen.status_code, 200)
        self.assertEqual(seen.get_json()["count"], 1)
        db.session.refresh(notification)
        self.assertIsNotNone(notification.shown_at)
        self.assertIsNone(notification.read_at)

        read = client.post(
            f"/api/incidents/notifications/{notification.id}/read",
            json={"action": "read"},
        )
        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.get_json()["count"], 0)
        db.session.refresh(notification)
        self.assertIsNotNone(notification.read_at)
        self.assertIsNone(notification.accessed_at)
        self.assertEqual(
            IncidentHistory.query.filter_by(
                incident_id=incident.id,
                user_id=self.maintenance_supervisor.id,
                accion="notificacion_leida",
            ).count(),
            1,
        )

    def test_other_tenant_cannot_mutate_notification(self):
        incident = self._incident()
        create_incident_notifications(incident)
        db.session.commit()
        notification = IncidentNotification.query.filter_by(
            incident_id=incident.id, user_id=self.maintenance_supervisor.id
        ).one()

        other_client = self._login("supervisor_otro", "otro-tenant")
        denied = other_client.post(
            f"/api/incidents/notifications/{notification.id}/read",
            json={"action": "access"},
        )
        self.assertEqual(denied.status_code, 404)

    def test_access_is_audited(self):
        incident = self._incident()
        create_incident_notifications(incident)
        db.session.commit()
        notification = IncidentNotification.query.filter_by(
            incident_id=incident.id, user_id=self.maintenance_supervisor.id
        ).one()
        client = self._login()
        opened = client.post(
            f"/api/incidents/notifications/{notification.id}/read",
            json={"action": "access"},
        )
        self.assertEqual(opened.status_code, 200)
        db.session.refresh(notification)
        self.assertIsNotNone(notification.accessed_at)
        self.assertEqual(
            IncidentHistory.query.filter_by(
                incident_id=incident.id,
                user_id=self.maintenance_supervisor.id,
                accion="acceso_desde_notificacion",
            ).count(),
            1,
        )

    def test_authorized_layout_contains_modal_and_polling_contract(self):
        client = self._login()
        html = client.get("/dashboard").get_data(as_text=True)

        self.assertIn('id="incidentNotificationModal"', html)
        self.assertIn("/api/incidents/notifications/unread", html)
        self.assertIn("window.setInterval(poll, 45000)", html)

    def test_status_changes_create_distinct_notifications_for_reporter(self):
        incident = self._incident()
        incident.user_id = self.reporter.id
        first = create_reporter_status_notification(
            incident,
            previous_status="reportado",
            new_status="recibido",
            action="recibido",
            actor_user_id=self.maintenance_supervisor.id,
        )
        second = create_reporter_status_notification(
            incident,
            previous_status="recibido",
            new_status="asignado",
            action="tecnico_asignado",
            actor_user_id=self.maintenance_supervisor.id,
        )
        db.session.commit()

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertNotEqual(first.event_key, second.event_key)
        self.assertEqual(first.audience, "reporter")
        self.assertIn("Reportado → Recibido", first.message)
        self.assertIn("Recibido → Asignado", second.message)
        self.assertEqual(
            IncidentNotification.query.filter_by(
                incident_id=incident.id, user_id=self.reporter.id
            ).count(),
            2,
        )

    def test_closed_ticket_uses_explicit_reporter_message(self):
        incident = self._incident()
        incident.user_id = self.reporter.id
        item = create_reporter_status_notification(
            incident,
            previous_status="resuelto",
            new_status="cerrado",
            action="cerrado",
            actor_user_id=self.maintenance_supervisor.id,
        )
        db.session.commit()

        self.assertEqual(item.title, "Tu ticket fue cerrado")
        self.assertEqual(item.status_snapshot, "cerrado")
        self.assertIn("Resuelto → Cerrado", item.message)

    def test_reporter_does_not_receive_notification_for_own_transition(self):
        incident = self._incident()
        incident.user_id = self.reporter.id

        item = create_reporter_status_notification(
            incident,
            previous_status="resuelto",
            new_status="cerrado",
            action="cerrado",
            actor_user_id=self.reporter.id,
        )

        self.assertIsNone(item)

    def test_real_receive_transition_notifies_reporter(self):
        incident = self._incident()
        incident.user_id = self.reporter.id
        db.session.commit()
        client = self._login()

        response = client.post(
            f"/incidencias/{incident.id}/accion",
            data={"accion": "recibir", "prioridad_confirmada": "alta"},
        )

        self.assertEqual(response.status_code, 302)
        item = IncidentNotification.query.filter_by(
            incident_id=incident.id,
            user_id=self.reporter.id,
            audience="reporter",
        ).one()
        self.assertEqual(item.status_snapshot, "recibido")
        self.assertEqual(item.title, "Tu ticket cambió de estado")

    def test_reporter_can_poll_show_and_read_status_notification(self):
        incident = self._incident()
        incident.user_id = self.reporter.id
        item = create_reporter_status_notification(
            incident,
            previous_status="reportado",
            new_status="resuelto",
            action="resuelto",
            actor_user_id=self.maintenance_supervisor.id,
        )
        db.session.commit()
        notification_id = item.id
        client = self._login("reportante")

        page = client.get("/incidencias")
        self.assertEqual(page.status_code, 200)
        self.assertIn('id="incidentNotificationModal"', page.get_data(as_text=True))
        unread = client.get("/api/incidents/notifications/unread")
        self.assertEqual(unread.status_code, 200)
        payload = unread.get_json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["items"][0]["event_title"], "Tu ticket fue resuelto")

        seen = client.post(f"/api/incidents/notifications/{notification_id}/seen")
        self.assertEqual(seen.status_code, 200)
        self.assertEqual(seen.get_json()["count"], 1)
        read = client.post(
            f"/api/incidents/notifications/{notification_id}/read",
            json={"action": "access"},
        )
        self.assertEqual(read.status_code, 200)
        self.assertEqual(read.get_json()["count"], 0)


if __name__ == "__main__":
    unittest.main()
