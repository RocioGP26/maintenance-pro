"""Sprint 19.4 · bitácora contextual y adjuntos."""

import io

from app import db
from app.maintenance_execution.log_service import (
    can_view_log, can_write_log, create_log_entry, entries_for_context,
)
from app.maintenance_execution.log_storage import resolve_log_file
from app.maintenance_execution.models import (
    MaintenanceLogAttachment,
    MaintenanceLogEntry,
    MaintenanceLogEvent,
    MaintenanceLogNotification,
)
from app.models import Incident
from tests import test_work_order_checklists as checklist_base


class TestContextLog(checklist_base.TestWorkOrderChecklists):
    def setUp(self):
        super().setUp()
        self.requester = self._user(self.company, "requester", "solicitante")
        self.incident = Incident(
            empresa_id=self.company.id, user_id=self.requester.id,
            numero="INC-LOG", titulo="Falla reportada", machine_id=self.order.machine_id,
            area_responsable="Mantenimiento", estado="reportado",
        )
        db.session.add(self.incident); db.session.commit()

    def test_internal_and_requester_visibility_are_separated(self):
        internal = create_log_entry(self.admin, "incident", self.incident, {
            "entry_type":"diagnosis", "visibility":"internal", "body":"Diagnóstico interno",
        })
        public = create_log_entry(self.admin, "incident", self.incident, {
            "entry_type":"action", "visibility":"requester", "body":"Estamos atendiendo tu solicitud",
        })
        db.session.commit()
        self.assertTrue(can_view_log(self.requester, "incident", self.incident))
        self.assertFalse(can_write_log(self.requester, "incident", self.incident))
        visible = entries_for_context(self.requester, "incident", self.incident)
        self.assertEqual([item.id for item in visible], [public.id])
        self.assertNotIn(internal.id, [item.id for item in visible])

    def test_technician_only_writes_related_context(self):
        self.assertTrue(can_write_log(self.tech_user, "work_order", self.order))
        entry = create_log_entry(self.tech_user, "work_order", self.order, {
            "entry_type":"action", "body":"Se inspeccionó el motor", "visibility":"internal",
        })
        db.session.commit()
        self.assertEqual(entry.author_id, self.tech_user.id)
        self.assertEqual(entry.work_order_id, self.order.id)
        self.assertTrue(MaintenanceLogEvent.query.filter_by(entry_id=entry.id, event="log_entry_created").first())
        manager_notice = MaintenanceLogNotification.query.filter_by(
            entry_id=entry.id, user_id=self.admin.id
        ).first()
        self.assertIsNotNone(manager_notice)
        self.assertIsNone(manager_notice.read_at)
        self.assertFalse(MaintenanceLogNotification.query.filter_by(
            entry_id=entry.id, user_id=self.tech_user.id
        ).first())
        with self.assertRaisesRegex(ValueError, "permiso"):
            create_log_entry(self.other_user, "work_order", self.order, {"body":"Cruce de tenant"})

    def test_requester_is_notified_only_for_public_incident_entry(self):
        internal = create_log_entry(self.admin, "incident", self.incident, {
            "body":"Diagnóstico reservado", "visibility":"internal",
        })
        public = create_log_entry(self.admin, "incident", self.incident, {
            "body":"Actualización para el reportante", "visibility":"requester",
        })
        db.session.commit()
        self.assertFalse(MaintenanceLogNotification.query.filter_by(
            entry_id=internal.id, user_id=self.requester.id
        ).first())
        self.assertTrue(MaintenanceLogNotification.query.filter_by(
            entry_id=public.id, user_id=self.requester.id
        ).first())

    def test_private_attachment_upload_render_and_download(self):
        client = self.app.test_client()
        client.post("/login", data={"username":self.admin.username, "empresa_slug":self.company.slug, "password":"Clave-Segura-123!"})
        response = client.post(
            f"/maintenance/procedures/context/work_order/{self.order.id}/log",
            data={
                "entry_type":"observation", "visibility":"internal", "body":"Adjunto inspección visual",
                "attachments":(io.BytesIO(b"%PDF-1.4 bitacora"), "inspection.pdf"),
            }, content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 302)
        attachment = MaintenanceLogAttachment.query.one()
        page = client.get(f"/maintenance/procedures/context/work_order/{self.order.id}/log")
        self.assertEqual(page.status_code, 200)
        self.assertIn("inspection.pdf", page.get_data(as_text=True))
        download = client.get(f"/maintenance/procedures/context/log/attachment/{attachment.id}")
        self.assertEqual(download.status_code, 200); self.assertEqual(download.data, b"%PDF-1.4 bitacora")
        download.close(); resolve_log_file(attachment.storage_key).unlink(missing_ok=True)
        self.assertTrue(MaintenanceLogEvent.query.filter_by(entry_id=attachment.entry_id, event="log_attachment_downloaded").first())

    def test_entries_are_immutable_and_corrections_reference_original(self):
        original = create_log_entry(self.admin, "work_order", self.order, {"body":"Valor 10", "visibility":"internal"})
        db.session.commit()
        correction = create_log_entry(self.admin, "work_order", self.order, {
            "body":"Corrección: valor 12", "visibility":"internal", "correction_of_id":str(original.id),
        })
        db.session.commit()
        self.assertEqual(correction.correction_of_id, original.id)
        self.assertEqual(original.body, "Valor 10")
        self.assertEqual(correction.entry_type, "correction")
