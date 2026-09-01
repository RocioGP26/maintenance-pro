"""Flujo comercial del piloto: asignación manual y catálogo oficial."""

from __future__ import annotations

import time
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from app import create_app, db
from app.models import (
    Empresa,
    EmailOutbox,
    FacturaEmpresa,
    FacturaEstado,
    PlanSuscripcion,
    PlanTipo,
    PlatformAuditLog,
    SuscripcionEstado,
    TenantActivityLog,
    User,
)
from app.platform_billing import kpis_facturacion, listar_facturas_platform
from app.platform_service import kpis_platform, listar_empresas_platform
from app.platform_config_service import PLANES_COMERCIALES_PILOTO
from app.subscription_service import (
    TERMINOS_COMERCIALES_VERSION,
    cambiar_plan_manual,
    crear_factura_mensual,
    marcar_factura_pagada,
    preparar_conversion_comercial,
    registrar_aceptacion_terminos,
    verificar_vencimientos,
)
from app.user_entitlements import UserLimitExceeded, usuarios_facturables, validar_cupo_usuario


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

    def _crear_admin(self, username: str) -> User:
        user = User(
            empresa_id=self.empresa.id,
            username=username,
            email=f"{username}@piloto.test",
            nombre_visible="Administrador comercial",
            area="Administración",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        user.set_password("Clave-Segura-123!")
        db.session.add(user)
        db.session.flush()
        return user

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
        aceptante = self._crear_admin("aceptante-ruta")
        self.sub.terminos_version = TERMINOS_COMERCIALES_VERSION
        self.sub.terminos_aceptados_en = datetime.utcnow()
        self.sub.terminos_aceptados_por_id = aceptante.id
        db.session.commit()
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
        self.assertEqual(self.sub.estado_ciclo, SuscripcionEstado.MORA.value)
        self.assertEqual(FacturaEmpresa.query.count(), 1)
        audit = PlatformAuditLog.query.filter_by(accion="plan_change").one()
        activity = TenantActivityLog.query.filter_by(tipo="plan_changed").one()
        self.assertEqual(audit.empresa_id, self.empresa.id)
        self.assertIn("Trial → Business", audit.detalle)
        self.assertIn("factura", activity.detalle)
        self.assertIn("pendiente", activity.detalle)

    def test_conversion_requiere_aceptacion_y_activa_solo_con_pago(self):
        with self.assertRaisesRegex(ValueError, "aceptar los términos"):
            preparar_conversion_comercial(self.empresa, PlanTipo.BASICO.value)

        aceptante = self._crear_admin("aceptante-servicio")
        registrar_aceptacion_terminos(
            self.sub, user_id=aceptante.id, ip_address="127.0.0.1"
        )
        sub, factura, anterior, changed = preparar_conversion_comercial(
            self.empresa, PlanTipo.BASICO.value
        )
        self.assertTrue(changed)
        self.assertEqual(anterior, PlanTipo.TRIAL.value)
        self.assertEqual(sub.estado_ciclo, SuscripcionEstado.MORA.value)
        self.assertEqual(factura.estado, FacturaEstado.PENDIENTE.value)

        marcar_factura_pagada(factura, metodo="transferencia", referencia="TRX-1")
        self.assertEqual(sub.estado_ciclo, SuscripcionEstado.ACTIVA.value)
        self.assertEqual(sub.plan, PlanTipo.BASICO.value)
        self.assertEqual(factura.estado, FacturaEstado.PAGADA.value)

    def test_dia_15_pasa_a_consulta_factura_y_envia_aviso(self):
        hoy = date(2026, 9, 1)
        self.empresa.email = "admin@piloto.test"
        self.sub.fecha_inicio = hoy - timedelta(days=15)
        self.sub.fecha_fin = hoy
        self.app.config["MAIL_DEFAULT_SENDER"] = "noreply@roustix.test"
        db.session.commit()

        stats = verificar_vencimientos(hoy=hoy)

        self.assertEqual(stats["avisos_trial"], 1)
        self.assertEqual(stats["trials_a_mora"], 1)
        self.assertEqual(self.sub.estado_ciclo, SuscripcionEstado.MORA.value)
        self.assertFalse(self.empresa.suspendida)
        self.assertEqual(FacturaEmpresa.query.count(), 1)
        self.assertEqual(EmailOutbox.query.count(), 1)

    def test_solicitantes_no_consumen_cupo_del_plan(self):
        for idx in range(20):
            user = User(
                empresa_id=self.empresa.id,
                username=f"usuario-{idx}",
                rol="tecnico",
                activo=True,
            )
            user.set_password("Clave-Segura-123!")
            db.session.add(user)
        requester = User(
            empresa_id=self.empresa.id,
            username="reportante",
            rol="solicitante",
            activo=True,
        )
        requester.set_password("Clave-Segura-123!")
        db.session.add(requester)
        db.session.commit()

        self.assertEqual(usuarios_facturables(self.empresa.id), 20)
        validar_cupo_usuario(self.empresa, rol="solicitante", activo=True)
        with self.assertRaises(UserLimitExceeded):
            validar_cupo_usuario(self.empresa, rol="tecnico", activo=True)

    def test_mora_permite_consulta_bloquea_escritura_y_acepta_terminos(self):
        self.empresa.email_verified_at = datetime.utcnow()
        self.sub.estado_ciclo = SuscripcionEstado.MORA.value
        admin = User(
            empresa_id=self.empresa.id,
            username="admin-comercial",
            email="admin@piloto.test",
            nombre_visible="Admin Comercial",
            area="Administración",
            rol="admin",
            activo=True,
            onboarding_completado=True,
        )
        admin.set_password("Clave-Segura-123!")
        db.session.add(admin)
        db.session.commit()

        client = self.app.test_client()
        with client.session_transaction() as session:
            session["_user_id"] = admin.get_id()
            session["_fresh"] = True

        page = client.get("/suscripcion")
        self.assertEqual(page.status_code, 200)
        self.assertIn("modo consulta", page.get_data(as_text=True))

        blocked = client.post("/equipo/nuevo", data={})
        self.assertEqual(blocked.status_code, 302)
        self.assertTrue(blocked.location.endswith("/suscripcion"))

        accepted = client.post("/suscripcion/aceptar-terminos", data={"acepto": "1"})
        self.assertEqual(accepted.status_code, 302)
        db.session.refresh(self.sub)
        self.assertEqual(self.sub.terminos_version, TERMINOS_COMERCIALES_VERSION)
        self.assertEqual(self.sub.terminos_aceptados_por_id, admin.id)

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

    def test_filtro_superadmin_muestra_solo_planes_oficiales(self):
        client = self.app.test_client()
        now = int(time.time())
        with client.session_transaction() as session:
            session["platform_admin"] = True
            session["platform_started_at"] = now
            session["platform_last_activity_at"] = now

        response = client.get("/platform/empresas")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Start", body)
        self.assertIn("Business", body)
        self.assertIn("Enterprise", body)
        self.assertNotIn(">Grow<", body)
        self.assertNotIn(">Scale<", body)

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

    def test_empresa_prueba_no_cuenta_como_cliente_y_se_puede_filtrar(self):
        self.empresa.es_prueba = True
        cliente = Empresa(
            razon_social="Cliente Real SAS", slug="cliente-real", sector="manufactura"
        )
        db.session.add(cliente)
        db.session.flush()
        db.session.add(
            PlanSuscripcion(
                empresa_id=cliente.id,
                plan=PlanTipo.BASICO.value,
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=30),
                activo=True,
                estado_ciclo=SuscripcionEstado.ACTIVA.value,
            )
        )
        db.session.commit()

        todas = listar_empresas_platform()
        kpis = kpis_platform(todas)
        pruebas = listar_empresas_platform(tipo="pruebas")
        clientes = listar_empresas_platform(tipo="clientes")

        self.assertEqual(kpis["total"], 1)
        self.assertEqual(kpis["pruebas"], 1)
        self.assertEqual(kpis["visible"], 2)
        self.assertEqual([f.empresa.slug for f in pruebas], ["piloto-sas"])
        self.assertEqual([f.empresa.slug for f in clientes], ["cliente-real"])
        self.assertEqual(
            next(f for f in todas if f.empresa.slug == "piloto-sas").mrr,
            0.0,
        )

    def test_empresa_prueba_no_genera_factura_ni_mora_automatica(self):
        self.empresa.es_prueba = True
        self.sub.fecha_fin = date.today() - timedelta(days=1)
        db.session.commit()

        stats = verificar_vencimientos(hoy=date.today())

        db.session.refresh(self.sub)
        self.assertEqual(stats["trials_a_mora"], 0)
        self.assertEqual(self.sub.estado_ciclo, SuscripcionEstado.TRIAL.value)
        self.assertEqual(FacturaEmpresa.query.count(), 0)
        with self.assertRaisesRegex(ValueError, "excluidas de facturación"):
            crear_factura_mensual(self.empresa)

    def test_factura_historica_de_prueba_no_contamina_resumen_comercial(self):
        self.empresa.es_prueba = True
        factura = FacturaEmpresa(
            empresa_id=self.empresa.id,
            suscripcion_id=self.sub.id,
            numero="FAC-TEST-001",
            concepto="Evidencia histórica",
            monto=250000,
            periodo=date.today().strftime("%Y-%m"),
            estado=FacturaEstado.PAGADA.value,
            fecha_emision=date.today(),
            fecha_pago=date.today(),
        )
        db.session.add(factura)
        db.session.commit()

        kpis = kpis_facturacion()

        self.assertEqual(kpis["pagadas_mes"], 0)
        self.assertEqual(kpis["cobrado_mes"], 0.0)
        self.assertEqual(listar_facturas_platform(), [])

    def test_superadmin_clasifica_empresa_de_prueba_y_audita(self):
        client = self.app.test_client()
        now = int(time.time())
        with client.session_transaction() as session:
            session["platform_admin"] = True
            session["platform_started_at"] = now
            session["platform_last_activity_at"] = now

        response = client.post(
            f"/platform/empresas/{self.empresa.id}/clasificacion",
            data={"es_prueba": "1"},
        )

        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.empresa)
        self.assertTrue(self.empresa.es_prueba)
        self.assertEqual(
            PlatformAuditLog.query.filter_by(
                accion="company_test_classification", empresa_id=self.empresa.id
            ).count(),
            1,
        )
        page = client.get("/platform/empresas?tipo=pruebas")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Pruebas", page.get_data(as_text=True))
        detail = client.get(f"/platform/empresas/{self.empresa.id}")
        self.assertIn("Facturación desactivada", detail.get_data(as_text=True))
        invoice = client.post(
            f"/platform/empresas/{self.empresa.id}/facturas/nueva",
            data={"periodo": date.today().strftime("%Y-%m"), "monto": "100000"},
        )
        self.assertEqual(invoice.status_code, 302)
        self.assertEqual(FacturaEmpresa.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
