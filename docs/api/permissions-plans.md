# Autenticación, permisos y derechos técnicos

## Dos identidades, un contrato

| Identidad | Uso | Credencial |
|---|---|---|
| Usuario | clientes interactivos y pruebas autorizadas | JWT Bearer |
| Integración | ERP, BI, automatizaciones y conectores | API key Bearer |

El header es siempre `Authorization: Bearer <credential>`. El prefijo
`rtx_live_` o `rtx_test_` permite enrutar API keys sin exponer su hash. Una key
pertenece a exactamente una empresa y no puede cambiar de tenant.

## Quién puede gestionar API keys (UI y admin REST)

| Rol / perfil | Acceso |
|---|---|
| Superadministrador | Sí — total |
| Administrador con área **TI / TIC / Sistemas / Infraestructura** | Sí — crear, rotar, revocar |
| Administrador operativo (Mantenimiento u otras áreas) | No |
| Supervisor / Técnico / Operario | No |

Las API keys dan acceso a datos sin pasar por la UI. Por eso solo el área de
Sistemas / TIC (o Superadmin) debe emitirlas. El permiso de producto es
`can_manage_integrations` (`perm.integraciones` en plantillas).

## Ciclo de vida de API keys

1. Un administrador de Sistemas / TIC (o Superadmin) asigna nombre, ambiente, scopes y expiración.
2. Roustix muestra el secreto completo una sola vez.
3. Solo se persisten prefijo identificable y hash resistente a ataques offline.
4. Cada uso válido actualiza `last_used_at` de manera acotada.
5. Rotar crea una key nueva y permite una ventana breve de convivencia.
6. Revocar tiene efecto inmediato y queda auditado.

La interfaz nunca permite recuperar el secreto original.

## Scopes iniciales

```text
maintenance.assets:read
maintenance.incidents:read
maintenance.incidents:write
maintenance.work_orders:read
maintenance.meters:read
maintenance.meters:write
webhooks:read
webhooks:manage
```

No existe `*` para credenciales ordinarias. Los scopes administrativos de
webhooks se usan desde sesión web; habilitarlos para API keys requiere derecho
Enterprise explícito y queda fuera del MVP.

## Evaluación de autorización

```text
credencial válida
  → empresa activa
  → suscripción vigente
  → módulo activo
  → entitlement habilitado
  → scope requerido
  → recurso del mismo tenant
  → operación permitida
```

Fallar en cualquier punto detiene la solicitud. La pertenencia del recurso se
evalúa al final como `404` para no filtrar datos entre empresas.

## Derechos técnicos

Sprint 22 no codifica reglas como `if plan == enterprise`. Introduce claves de
capacidad resolubles desde el catálogo o una asignación por tenant:

| Entitlement | Unidad |
|---|---|
| `public_api.enabled` | booleano |
| `public_api.requests_per_minute` | entero |
| `public_api.credentials_max` | entero |
| `public_api.write_enabled` | booleano |
| `webhooks.enabled` | booleano |
| `webhooks.endpoints_max` | entero |
| `webhooks.retention_days` | entero |
| `webhooks.manual_retry` | booleano |

La asignación comercial a Trial, Start, Grow, Scale y Enterprise está definida
en la matriz de entitlements de Sprint 22.4 (`app/integrations/entitlements.py`).

## Revocación automática

Las credenciales se invalidan cuando la empresa se suspende o elimina. Cambiar
la contraseña de un usuario revoca sus sesiones/JWT, pero no una API key de
servicio independiente. Revocar el usuario que creó la key no la elimina de
forma implícita: genera una alerta administrativa para reasignar propietario o
revocarla, evitando interrupciones accidentales.
