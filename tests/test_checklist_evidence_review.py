"""Sprint 19.3 · evidencia, firma, no conformidad y revisión."""

import io
import unittest

from app import db
from app.maintenance_execution.models import CHECKLIST_BLOCKED, CHECKLIST_REVIEWED
from app.maintenance_execution.service import review_checklist, save_checklist_responses
from tests import test_work_order_checklists as checklist_base


class TestChecklistEvidenceReview(checklist_base.TestWorkOrderChecklists):
    def test_nonconformity_requires_resolution_before_review(self):
        checklist = self._assigned()
        first, second, _third = self.version.steps
        save_checklist_responses(checklist, self.tech_user.id, {
            f"step_{first.id}": "not_done",
            f"justification_{first.id}": "Fuga detectada",
            f"step_{second.id}": "5.4",
            f"conformity_{second.id}": "conforming",
        })
        db.session.commit()
        self.assertEqual(checklist.status, CHECKLIST_BLOCKED)
        with self.assertRaisesRegex(ValueError, "resolución"):
            review_checklist(checklist, self.admin.id, {})
        response = next(item for item in checklist.responses if item.step_id == first.id)
        review_checklist(checklist, self.admin.id, {
            f"resolution_{response.id}": "Se corrigió el sello y se verificó nuevamente.",
            "review_notes": "Aprobado después de corrección",
        })
        db.session.commit()
        self.assertEqual(checklist.status, CHECKLIST_REVIEWED)
        self.assertEqual(response.resolved_by_id, self.admin.id)

    def test_signature_cannot_be_delegated(self):
        self.version.steps[-1].response_type = "signature"
        self.version.steps[-1].required = True
        db.session.commit()
        checklist = self._assigned()
        signature = self.version.steps[-1]
        with self.assertRaisesRegex(ValueError, "firma debe confirmarla"):
            save_checklist_responses(checklist, self.admin.id, {f"step_{signature.id}": "confirmed"})
        db.session.rollback()
        checklist = self.order.execution_checklist
        save_checklist_responses(checklist, self.tech_user.id, {f"step_{signature.id}": "confirmed"})
        db.session.commit()
        response = next(item for item in checklist.responses if item.step_id == signature.id)
        self.assertEqual(response.signature_name_snapshot, self.tech_user.etiqueta())
        self.assertIsNotNone(response.signed_at)

    def test_evidence_upload_and_authorized_download(self):
        self.version.steps[-1].response_type = "evidence"
        self.version.steps[-1].required = True
        db.session.commit()
        checklist = self._assigned()
        client = self.app.test_client()
        client.post("/login", data={"username":self.tech_user.username, "empresa_slug":self.company.slug, "password":"Clave-Segura-123!"})
        step = self.version.steps[-1]
        response = client.post(
            f"/maintenance/procedures/work-orders/{self.order.id}/checklist/execute",
            data={f"evidence_{step.id}": (io.BytesIO(b"%PDF-1.4 test"), "evidence.pdf")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(checklist)
        evidence_response = next(item for item in checklist.responses if item.step_id == step.id)
        self.assertEqual(len(evidence_response.evidences), 1)
        evidence = evidence_response.evidences[0]
        page = client.get(f"/maintenance/procedures/work-orders/{self.order.id}/checklist")
        self.assertEqual(page.status_code, 200)
        self.assertIn("evidence.pdf", page.get_data(as_text=True))
        download = client.get(f"/maintenance/procedures/work-orders/{self.order.id}/checklist/evidence/{evidence.id}")
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.data, b"%PDF-1.4 test")
        download.close()
        from app.maintenance_execution.evidence import resolve_evidence_path
        resolve_evidence_path(evidence.storage_key).unlink(missing_ok=True)

    def _assigned(self):
        from app.maintenance_execution.service import assign_checklist
        checklist = assign_checklist(self.order, self.version.id, self.admin.id)
        db.session.commit()
        return checklist


if __name__ == "__main__":
    unittest.main()
