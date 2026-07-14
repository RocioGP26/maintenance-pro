# Sprint 18 · Seguridad e Identidad

## Objetivo

Evitar sesiones web indefinidas y proporcionar controles empresariales de
expiración, revocación y auditoría antes de operar con clientes reales.

## Entregables

- [x] Expiración por inactividad configurable.
- [x] Duración máxima absoluta configurable.
- [x] “Recordarme” opcional y desactivado por defecto.
- [x] Advertencia previa con renovación por interacción explícita.
- [x] Registro servidor de sesiones activas.
- [x] Cierre remoto individual y cierre de las demás sesiones propias.
- [x] Auditoría de login, logout, expiración, revocación y cambio de contraseña.
- [x] Revocación por credenciales, bloqueo de usuario y suspensión de tenant.
- [x] Política administrable por empresa dentro de rangos seguros.
- [x] Migración Alembic y pruebas automatizadas.

## Decisiones de seguridad

- Las sesiones sin “Recordarme” usan cookie de navegador.
- “Recordarme” sólo se acepta si el tenant lo habilitó.
- La actividad automática de una pestaña abierta no mantiene viva la sesión; el
  ping se produce por interacción del usuario y se limita a uno por minuto.
- El límite absoluto prevalece aunque exista actividad continua.
- `auth_version` permite invalidar la identidad firmada sin almacenar contraseñas
  ni tokens sensibles en texto plano.

## Fuera de alcance

- Geolocalización de IP mediante proveedores externos.
- MFA, SSO/SAML y políticas adaptativas por riesgo.
- Reautenticación parcial para operaciones críticas.

## Verificación

La suite cubre creación de sesión administrada, política de “Recordarme”, timeout
por inactividad, timeout absoluto, revocación remota, versión de identidad y
acceso al panel administrativo.
