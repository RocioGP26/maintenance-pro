"""Sprint 22.1 · credenciales de integración y autorización tenant-safe."""

from datetime import date, datetime, timedelta
import unittest

from app import create_app, db
from app.integrations.credentials import (
    CredentialError,
    authenticate_credential,
    issue_credential,
    revoke_credential,
    rotate_credential,
)
from app.models import (
    Empresa,
    IntegrationCredential,
    Machine,
    MachineType,
    PlanSuscripcion,
    TenantActivityLog,
    User,
)


class TestIntegrationCredentials(unittest.TestCase):
    PASSWORD = "Clave-Segura-123!"

    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.company = Empresa(
            razon_social="API Tenant SAS", slug="api-tenant", email_verified_at=datetime.utcnow()
        )
        self.other_company = Empresa(
            razon_social="Otro Tenant SAS", slug="otro-tenant", email_verified_at=datetime.utcnow()
        )
        db.session.add_all([self.company, self.other_company])
        db.session.flush()
        db.session.add_all(
            [
                PlanSuscripcion(
                    empresa_id=self.company.id,
                    plan="enterprise",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
                PlanSuscripcion(
                    empresa_id=self.other_company.id,
                    plan="enterprise",
                    fecha_inicio=date.today(),
                    activo=True,
                    estado_ciclo="activa",
                ),
            ]
        )
        self.admin = User(
            empresa_id=self.company.id,
            username="apiadmin",
            rol="admin",
            area="TIC",
            activo=True,
            onboarding_completado=True,
        )
        self.admin.set_password(self.PASSWORD)
        self.ops_admin = User(
            empresa_id=self.company.id,
            username="opsadmin",
            rol="admin",
            area="Mantenimiento",
            activo=True,
            onboarding_completado=True,
        )
        self.ops_admin.set_password(self.PASSWORD)
        own_type = MachineType(
            empresa_id=self.company.id, clave="api-own", nombre="Equipo API", prefijo="API"
        )
        other_type = MachineType(
            empresa_id=self.other_company.id, clave="api-other", nombre="Otro", prefijo="OTH"
        )
        db.session.add_all([self.admin, self.ops_admin, own_type, other_type])
        db.session.flush()
        self.own_asset = Machine(
            empresa_id=self.company.id,
            machine_type_id=own_type.id,
            codigo="API-001",
            nombre="Activo propio",
        )
        self.other_asset = Machine(
            empresa_id=self.other_company.id,
            machine_type_id=other_type.id,
            codigo="OTH-001",
            nombre="Activo ajeno",
        )
        db.session.add_all([self.own_asset, self.other_asset])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _issue(self, *scopes):
        issued = issue_credential(
            empresa_id=self.company.id,
            name="Integración pruebas",
            environment="test",
            scopes=list(scopes) or ["maintenance.assets:read"],
            created_by_id=self.admin.id,
        )
        db.session.commit()
        return issued

    def test_secret_is_shown_once_and_only_scrypt_hash_is_persisted(self):
        issued = self._issue()
        self.assertTrue(issued.secret.startswith("rtx_test_"))
        self.assertNotIn(issued.secret, issued.credential.secret_hash)
        self.assertTrue(issued.credential.secret_hash.startswith("scrypt:"))
        self.assertEqual(issued.credential.key_prefix, issued.secret.split(".", 1)[0])
        self.assertIs(authenticate_credential(issued.secret), issued.credential)

    def test_api_key_resolves_identity_and_never_leaks_other_tenant(self):
        issued = self._issue("maintenance.assets:read")
        client = self.app.test_client()
        headers = {"Authorization": f"Bearer {issued.secret}"}
        identity = client.get("/api/v1/me", headers=headers)
        self.assertEqual(identity.status_code, 200)
        me = identity.json["data"]
        self.assertEqual(me["identity_type"], "api_key")
        self.assertEqual(me["empresa_id"], self.company.id)
        self.assertEqual(me["credential_id"], issued.credential.id)

        response = client.get("/api/v1/maintenance/assets", headers=headers)
        self.assertEqual(response.status_code, 200)
        codes = [item["asset_code"] for item in response.json["data"]]
        self.assertIn(self.own_asset.codigo, codes)
        self.assertNotIn(self.other_asset.codigo, codes)
        self.assertEqual(
            client.get(
                f"/api/v1/maintenance/assets/{self.other_asset.id}", headers=headers
            ).status_code,
            404,
        )

    def test_missing_scope_is_denied_and_key_cannot_open_web_routes(self):
        issued = self._issue("maintenance.work_orders:read")
        headers = {"Authorization": f"Bearer {issued.secret}"}
        response = self.app.test_client().get("/api/v1/maintenance/assets", headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json["error"]["code"], "SCOPE_REQUIRED")
        web = self.app.test_client().get("/dashboard", headers=headers)
        self.assertEqual(web.status_code, 401)

    def test_revoked_and_expired_credentials_are_rejected(self):
        issued = self._issue()
        revoke_credential(issued.credential)
        db.session.commit()
        response = self.app.test_client().get(
            "/api/v1/me", headers={"Authorization": f"Bearer {issued.secret}"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"]["code"], "API_KEY_REVOKED")

        expired = self._issue()
        expired.credential.expires_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()
        response = self.app.test_client().get(
            "/api/v1/me", headers={"Authorization": f"Bearer {expired.secret}"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["error"]["code"], "API_KEY_EXPIRED")

    def test_rotation_copies_scopes_and_limits_old_key_grace_period(self):
        issued = self._issue("maintenance.assets:read", "maintenance.work_orders:read")
        before = datetime.utcnow()
        rotated = rotate_credential(issued.credential, created_by_id=self.admin.id, grace_minutes=10)
        db.session.commit()
        self.assertEqual(rotated.credential.rotated_from_id, issued.credential.id)
        self.assertEqual(rotated.credential.scopes, issued.credential.scopes)
        self.assertLessEqual(issued.credential.expires_at, before + timedelta(minutes=11))
        self.assertIsNotNone(authenticate_credential(rotated.secret))

    def test_validation_rejects_unknown_scope_and_past_expiration(self):
        with self.assertRaises(CredentialError):
            issue_credential(
                empresa_id=self.company.id,
                name="Inválida",
                environment="test",
                scopes=["admin:*"],
                created_by_id=self.admin.id,
            )
        with self.assertRaises(CredentialError):
            issue_credential(
                empresa_id=self.company.id,
                name="Expirada",
                environment="live",
                scopes=["maintenance.assets:read"],
                expires_at=datetime.utcnow() - timedelta(days=1),
                created_by_id=self.admin.id,
            )

    def test_admin_api_is_session_only_and_tenant_scoped(self):
        issued = self._issue()
        key_headers = {"Authorization": f"Bearer {issued.secret}"}
        denied = self.app.test_client().get(
            "/api/v1/admin/integration-credentials", headers=key_headers
        )
        self.assertEqual(denied.status_code, 403)

        client = self.app.test_client()
        login = client.post(
            "/login",
            data={
                "username": self.admin.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(login.status_code, 302)
        listed = client.get("/api/v1/admin/integration-credentials")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json["data"]), 1)
        self.assertNotIn("secret", listed.json["data"][0])

        page = client.get("/administracion/integraciones/credenciales")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Credenciales de integración", page.get_data(as_text=True))

        created = client.post(
            "/api/v1/admin/integration-credentials",
            json={
                "name": "Power BI",
                "environment": "live",
                "scopes": ["maintenance.assets:read"],
            },
        )
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.json["data"]["secret"].startswith("rtx_live_"))
        listed_again = client.get("/api/v1/admin/integration-credentials")
        self.assertNotIn("secret", listed_again.json["data"][0])
        self.assertTrue(
            TenantActivityLog.query.filter_by(
                empresa_id=self.company.id, tipo="integration_credential_created"
            ).first()
        )

    def test_maintenance_admin_cannot_manage_integration_credentials(self):
        from app.permissions import can_manage_integrations

        self.assertTrue(can_manage_integrations(self.admin))
        self.assertFalse(can_manage_integrations(self.ops_admin))

        client = self.app.test_client()
        login = client.post(
            "/login",
            data={
                "username": self.ops_admin.username,
                "empresa_slug": self.company.slug,
                "password": self.PASSWORD,
            },
        )
        self.assertEqual(login.status_code, 302)
        page = client.get("/administracion/integraciones/credenciales")
        self.assertEqual(page.status_code, 302)
        listed = client.get("/api/v1/admin/integration-credentials")
        self.assertEqual(listed.status_code, 403)


if __name__ == "__main__":
    unittest.main()
