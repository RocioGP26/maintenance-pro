# Sprint 23.3 · CI PostgreSQL, E2E y controles de seguridad

## Objetivo

Convertir la validación de Roustix en un gate repetible de entrega que pruebe la
aplicación sobre PostgreSQL, recorra flujos HTTP críticos en un servidor real y
bloquee dependencias vulnerables, código de alta severidad o secretos
versionados antes de llegar a `main`.

## Alcance

- Suite unitaria rápida sobre SQLite.
- Suite completa de integración sobre PostgreSQL 18.
- Migraciones Alembic desde una base vacía y verificación de cabeza única.
- Smoke E2E externo contra Gunicorn y PostgreSQL.
- Login tenant, sesión administrada, logout y MFA de plataforma.
- Auditoría de dependencias con `pip-audit`.
- Análisis estático de alta severidad con Bandit.
- Detección de secretos con Gitleaks.
- Revisión de cambios de dependencias en pull requests.
- Evidencia del log E2E cuando el gate falla.

## Fuera de alcance

- Pruebas visuales de todos los navegadores y dispositivos.
- Pruebas de carga, estrés o caos.
- Servicios externos reales de correo, Neon, R2 o webhooks.
- WAF, rate limits distribuidos y observabilidad operacional, cubiertos por 23.4.

## Reglas

1. Las pruebas nunca usan la base de producción ni variables de producción.
2. `TEST_DATABASE_URL` es la única vía para sustituir SQLite en modo testing.
3. El E2E genera credenciales aleatorias por ejecución y no las versiona.
4. PostgreSQL y la semilla E2E nacen vacíos en cada job.
5. Una vulnerabilidad conocida, una migración divergente o un flujo crítico roto bloquea CI.
6. Los logs E2E no imprimen contraseñas, secretos TOTP ni tokens.

## Definition of Done

- [x] CI conserva el gate SQLite.
- [x] CI ejecuta migraciones y suite completa en PostgreSQL 18.
- [x] Existe smoke HTTP contra Gunicorn con identidad tenant y plataforma.
- [x] Existen gates de dependencias, análisis estático y secretos.
- [x] Las credenciales E2E son efímeras.
- [x] Las dependencias vulnerables detectadas durante el sprint fueron corregidas.
- [ ] El workflow remoto completo queda verde en GitHub Actions.
