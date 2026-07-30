"""Flujo comercial del piloto: asignación manual y catálogo oficial."""

from __future__ import annotations

import time
import unittest
from datetime import date, timedelta
from pathlib import Path

from app import create_app, db
from app.models import (
    Empresa,
    PlanSuscripcion,
    PlanTipo,
    PlatformAuditLog,
    SuscripcionEstado,
    TenantActivityLog,
)
from app.platform_config_service import PLANES_COMERCIALES_PILOTO
from app.subscription_service import cambiar_plan_manual


class TestCommercialPilot(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.empresa = Empresa(
            razon_social="Piloto SAS",
            slug="piloto-sas",
            nit="900123",
            sector="industrial",
        )
        db.session.add(self.empresa)
        db.session.flush()
        self.sub = PlanSuscripcion(
            empresa_id=self.empresa.id,
            plan=PlanTipo.TRIAL.value,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=15),
            activo=True,
            estado_ciclo=SuscripcionEstado.TRIAL.value,
        )
        db.session.add(self.sub)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_catalogo_asignable_excluye_trial_y_scale_legacy(self):
        self.assertEqual(
            PLANES_COMERCIALES_PILOTO,
            ("basico", "grow", "enterprise"),
        )
        self.assertEqual(PlanTipo.BUSINESS.value, "grow")
        self.assertNotIn(PlanTipo.PROFESIONAL.value, PLANES_COMERCIALES_PILOTO)

    def test_trial_a_business_abre_ciclo_activo(self):
        hoy = date(2026, 7, 29)
        sub, anterior, changed = cambiar_plan_manual(
            self.empresa,
            PlanTipo.BUSINESS.value,
            hoy=hoy,
        )

        self.assertTrue(changed)
        self.assertEqual(anterior, PlanTipo.TRIAL.value)
        self.assertEqual(sub.plan, PlanTipo.BUSINESS.value)
        self.assertEqual(sub.estado_ciclo, SuscripcionEstado.ACTIVA.value)
        self.assertEqual(sub.fecha_inicio, hoy)
        self.assertEqual(sub.fecha_fin, hoy + timedelta(days=30))
        self.assertFalse(self.empresa.suspendida)

    def test_upgrade_activo_preserva_vencimiento(self):
        vencimiento = date.today() + timedelta(days=12)
        self.sub.plan = PlanTipo.BASICO.value
        self.sub.estado_ciclo = SuscripcionEstado.ACTIVA.value
        self.sub.fecha_fin = vencimiento

        sub, anterior, changed = cambiar_plan_manual(
            self.empresa,
            PlanTipo.ENTERPRISE.value,
        )

        self.assertTrue(changed)
        self.assertEqual(anterior, PlanTipo.BASICO.value)
        self.assertEqual(sub.plan, PlanTipo.ENTERPRISE.value)
        self.assertEqual(sub.fecha_fin, vencimiento)

    def test_scale_legacy_no_es_asignable(self):
        with self.assertRaisesRegex(ValueError, "oferta comercial"):
            cambiar_plan_manual(self.empresa, PlanTipo.PROFESIONAL.value)

    def test_ruta_superadmin_cambia_plan_y_audita(self):
        client = self.app.test_client()
        now = int(time.time())
        with client.session_transaction() as session:
            session["platform_admin"] = True
            session["platform_actor"] = "QA Roustix"
            session["platform_started_at"] = now
            session["platform_last_activity_at"] = now

        response = client.post(
            f"/platform/empresas/{self.empresa.id}/plan",
            data={"plan": PlanTipo.BUSINESS.value},
        )

        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.sub)
        self.assertEqual(self.sub.plan, PlanTipo.BUSINESS.value)
        audit = PlatformAuditLog.query.filter_by(accion="plan_change").one()
        activity = TenantActivityLog.query.filter_by(tipo="plan_changed").one()
        self.assertEqual(audit.empresa_id, self.empresa.id)
        self.assertIn("Trial → Business", audit.detalle)
        self.assertIn("no genera factura", activity.detalle)

    def test_detalle_superadmin_muestra_solo_planes_oficiales(self):
        client = self.app.test_client()
        now = int(time.time())
        with client.session_transaction() as session:
            session["platform_admin"] = True
            session["platform_started_at"] = now
            session["platform_last_activity_at"] = now

        response = client.get(f"/platform/empresas/{self.empresa.id}")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Plan comercial del piloto", body)
        self.assertIn("Start", body)
        self.assertIn("Business", body)
        self.assertIn("Enterprise", body)
        self.assertNotIn("Scale (legacy)", body)

    def test_materiales_publicos_no_ofrecen_grow_ni_scale(self):
        public_files = [
            Path("docs/mkt/assets/brochure-corporativo.html"),
            Path("docs/mkt/assets/one-pager.html"),
            *Path("docs/mkt/mtx-case").glob("*.md"),
        ]
        for path in public_files:
            content = path.read_text(encoding="utf-8")
            self.assertNotRegex(content, r"\bGrow\b", str(path))
            self.assertNotRegex(content, r"\bScale\b", str(path))


if __name__ == "__main__":
    unittest.main()
