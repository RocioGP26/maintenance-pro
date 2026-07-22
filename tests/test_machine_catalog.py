"""Catálogo creatable de marca / modelo / fabricante en activos."""

from datetime import datetime
import unittest

from app import create_app, db
from app.machine_catalog import (
    eliminar_valor_catalogo,
    listar_valores_catalogo,
    upsert_valor_catalogo,
)
from app.models import Empresa, Machine, MachineCatalogValue, MachineType, PlanSuscripcion, User


class TestMachineCatalogCreatable(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        empresa = Empresa(
            razon_social="Catalogo SAS",
            slug="catalogo-sas",
            email_verified_at=datetime.utcnow(),
        )
        db.session.add(empresa)
        db.session.flush()
        user = User(
            empresa_id=empresa.id,
            username="admincat",
            nombre_visible="Admin Catálogo",
            rol="superadmin",
            activo=True,
            onboarding_completado=True,
        )
        user.set_password("Clave-Segura-123!")
        tipo = MachineType(
            empresa_id=empresa.id,
            clave="general_cat",
            nombre="Equipo general",
            prefijo="CT",
        )
        db.session.add_all([user, tipo])
        db.session.flush()
        db.session.add(
            Machine(
                empresa_id=empresa.id,
                codigo="CT-001",
                machine_type_id=tipo.id,
                nombre="Bomba",
                marca="Siemens",
            )
        )
        db.session.add(
            PlanSuscripcion(
                empresa_id=empresa.id,
                plan="professional",
                fecha_inicio=datetime.utcnow().date(),
                activo=True,
                estado_ciclo="activa",
            )
        )
        db.session.commit()
        self.empresa_id = empresa.id
        self.client = self.app.test_client()
        login = self.client.post(
            "/login",
            data={
                "username": "admincat",
                "empresa_slug": "catalogo-sas",
                "password": "Clave-Segura-123!",
            },
        )
        self.assertEqual(login.status_code, 302)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_seed_list_create_and_delete(self):
        items = listar_valores_catalogo(self.empresa_id, "marca")
        self.assertTrue(any(i["valor"] == "Siemens" for i in items))

        created = upsert_valor_catalogo(self.empresa_id, "marca", "ABB")
        db.session.commit()
        self.assertIsNotNone(created)
        self.assertEqual(created.valor, "ABB")

        ok, _msg, usos = eliminar_valor_catalogo(self.empresa_id, "marca", "ABB")
        db.session.commit()
        self.assertTrue(ok)
        self.assertEqual(usos, 0)
        self.assertIsNone(
            MachineCatalogValue.query.filter_by(
                empresa_id=self.empresa_id, campo="marca", valor_norm="abb"
            ).first()
        )

    def test_form_exposes_creatable_select_markup(self):
        response = self.client.get("/activos/nuevo")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('class="creatable-select"', html)
        self.assertIn('data-campo="marca"', html)
        self.assertIn('data-campo="modelo"', html)
        self.assertIn('data-campo="fabricante"', html)
        self.assertIn('data-campo="area"', html)
        self.assertIn('data-campo="ubicacion"', html)
        self.assertIn('name="sede_id"', html)
        self.assertIn("— Sin sede —", html)
        self.assertIn('name="manual_archivo"', html)
        self.assertIn('name="ficha_archivo"', html)
        self.assertIn("Manual técnico (PDF)", html)
        self.assertNotIn('data-campo="planta" data-store="id"', html)
        self.assertIn("creatable-select-chips", html)
        self.assertIn("Crear «", html)
        self.assertIn("initCreatableSelects", html)

    def test_api_create_area_and_planta(self):
        area = self.client.post(
            "/activos/api/catalogo/area",
            json={"valor": "Producción"},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.assertEqual(area.status_code, 200)
        self.assertEqual(area.get_json()["item"]["valor"], "Producción")

        planta = self.client.post(
            "/activos/api/catalogo/planta",
            json={"valor": "Planta Norte"},
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.assertEqual(planta.status_code, 200)
        data = planta.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["item"]["valor"], "Planta Norte")


if __name__ == "__main__":
    unittest.main()
