# Sprint 23.2 · Hardening de identidad y plataforma

## Objetivo

Cerrar brechas de seguridad de configuración, autenticación privilegiada y
tokens antes de incorporar clientes reales, reutilizando la gestión de sesiones
tenant implementada en Sprint 18.

## Alcance

- Configuración productiva fail-fast para secretos, PostgreSQL, correo y S3.
- Confianza explícita en el proxy de Render y validación de hosts permitidos.
- Encabezados defensivos adicionales y protección fuerte de Flask-Login.
- MFA TOTP obligatorio cuando el panel de plataforma está habilitado en producción.
- Timeout corto, absoluto y por inactividad para la sesión de plataforma.
- Comparación constante de la clave privilegiada y auditoría de accesos.
- JWT vinculado a `auth_version`, usuario activo, empresa y rol actuales.
- Pruebas de revocación, tenant, configuración y acceso privilegiado.

## Fuera de alcance

- SSO/SAML empresarial.
- MFA por usuario tenant y recuperación de códigos; requiere un flujo de
  enrolamiento independiente.
- WAF, SIEM y almacenamiento distribuido de rate limits, cubiertos por 23.3–23.4.
- Eliminación de `unsafe-inline` del CSP; requiere migrar scripts y estilos de
  plantillas a archivos con nonce o hash.

## Reglas

1. Producción no arranca con SQLite, almacenamiento local ni secretos débiles.
2. Un panel de plataforma habilitado en producción no opera sin TOTP.
3. Cambiar contraseña, bloquear o desactivar un usuario invalida web y JWT.
4. Tenant y rol de un JWT se revalidan contra la base en cada petición.
5. Los fallos no revelan si una identidad existe.
6. Los eventos privilegiados quedan auditados sin persistir secretos ni códigos.

## Definition of Done

- [x] Existe validación fail-fast de configuración productiva.
- [x] Render se procesa mediante proxy confiable y hosts permitidos.
- [x] El acceso de plataforma exige MFA en producción y expira automáticamente.
- [x] Los JWT son revocables y tenant-safe después de cambios de identidad.
- [x] La auditoría cubre login, MFA, logout y expiración de plataforma.
- [x] Existen pruebas focalizadas para todos los controles anteriores.
- [x] La suite completa y las migraciones vigentes pasan.
