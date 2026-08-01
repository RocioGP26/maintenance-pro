# Sprint 23.5 · Dominio, correo, UAT y salida controlada

## Objetivo

Certificar la identidad pública de Roustix, la entregabilidad de sus correos y
el recorrido completo de un cliente piloto antes de iniciar una operación
comercial controlada de máximo tres empresas.

## Estado inicial · 2026-08-01

- `roustix.com` sirve la aplicación productiva mediante HTTPS.
- La aplicación publica `contacto@roustix.com` como dirección comercial.
- El correo transaccional y operativo funciona mediante una cuenta temporal.
- La responsable dispone de `soporte.roustix@hotmail.com`, pero aún no de un
  buzón autenticado bajo el dominio `roustix.com`.
- Verificación, bienvenida, recuperación e idempotencia de correo ya fueron
  certificadas funcionalmente en el Sprint 23.4.

## Alcance

### 1. Dominio e identidad de correo

- Crear o verificar los buzones o alias `contacto@roustix.com` y
  `soporte@roustix.com`.
- Elegir un proveedor de correo que permita envío SMTP autenticado y DKIM.
- Mantener alineados remitente visible, dominio autenticado y Return-Path.
- Conservar un canal alterno de recuperación operativa fuera del dominio.

### 2. Entregabilidad

- Publicar y validar SPF sin superar el límite de una política SPF por dominio.
- Activar DKIM con las claves entregadas por el proveedor.
- Iniciar DMARC en modo observación y definir el buzón de reportes.
- Probar recepción en Gmail y Outlook sin exponer códigos ni tokens.
- Confirmar que alertas, verificación, bienvenida y recuperación usan la
  identidad aprobada.

### 3. Configuración productiva

- Actualizar `MAIL_USERNAME`, `MAIL_PASSWORD` y `MAIL_DEFAULT_SENDER` en web y
  worker con valores coherentes.
- Actualizar `OPS_ALERT_EMAIL` y los secretos SMTP de GitHub Actions.
- Verificar el panel de infraestructura, el worker y `/health/ready`.
- Rotar las credenciales temporales cuando la nueva identidad quede aprobada.

### 4. UAT del piloto

- Ejecutar registro, verificación, inicio de sesión y recuperación.
- Crear empresa, sede, área, usuarios y activos.
- Recorrer incidencia → asignación → OT → jornadas → repuestos → cierre.
- Validar hoja de vida, PDF, documentos, imagen, auditoría y almacenamiento.
- Probar límites del plan, alertas de capacidad, add-on y suspensión controlada.
- Ejecutar pruebas con roles reales y aislamiento entre empresas.

### 5. Salida controlada

- Máximo tres empresas piloto reales; los tenants marcados como prueba no
  consumen ese cupo.
- Onboarding asistido y responsable asignado para cada empresa.
- Canal, horario y tiempos de respuesta de soporte documentados.
- Política de escalamiento, respaldo, restauración e incidentes comunicada.
- Revisión legal de privacidad, tratamiento de datos, términos y servicio SaaS.

## Gate de correo corporativo

El gate no puede aprobarse hasta contar con acceso al proveedor de correo y a
la zona DNS de `roustix.com`. La evidencia mínima debe incluir:

1. Buzones o alias corporativos operativos.
2. SPF, DKIM y DMARC visibles mediante consulta DNS pública.
3. Remitente y dominio alineados en un mensaje real.
4. Recepción en Gmail y Outlook, incluida revisión de correo no deseado.
5. Verificación de alertas operativas y correos transaccionales.
6. Fecha, responsable, proveedor, capturas y resultado del gate.

## Definition of Done

- [x] Dominio productivo con HTTPS.
- [ ] Buzones o alias corporativos disponibles.
- [ ] SPF, DKIM y DMARC publicados y validados.
- [ ] SMTP corporativo configurado en web, worker y GitHub Actions.
- [ ] Entregabilidad aprobada en Gmail y Outlook.
- [ ] UAT funcional y de aislamiento aprobado.
- [ ] Documentación legal y soporte listos para el piloto.
- [ ] Decisión Go/No-Go registrada para máximo tres empresas.

