# Sprint 23.5 · Dominio, correo y preparación para comercialización

## Objetivo

Certificar la identidad pública de Roustix, la entregabilidad de sus correos,
la aceptación técnica del servicio y los controles necesarios para iniciar la
comercialización general de manera responsable.

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

### 4. Aceptación técnica del servicio

- Ejecutar registro, verificación, inicio de sesión y recuperación.
- Crear empresa, sede, área, usuarios y activos.
- Recorrer incidencia → asignación → OT → jornadas → repuestos → cierre.
- Validar hoja de vida, PDF, documentos, imagen, auditoría y almacenamiento.
- Probar límites del plan, alertas de capacidad, add-on y suspensión controlada.
- Ejecutar pruebas con roles reales y aislamiento entre empresas.

### 5. Preparación comercial

- Capacidad de nuevas empresas controlada mediante métricas de infraestructura,
  almacenamiento, concurrencia y soporte; sin un límite comercial fijo.
- Onboarding documentado y responsable asignado para cada cliente.
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
- [x] Buzones o alias corporativos disponibles.
- [x] SPF, DKIM y DMARC publicados y validados.
- [ ] SMTP corporativo configurado en web, worker y GitHub Actions.
- [ ] Entregabilidad aprobada en Gmail y Outlook.
- [x] Aceptación técnica funcional y de aislamiento aprobada.
- [ ] Documentación legal, comercial y soporte listos para clientes.
- [ ] Decisión de habilitación comercial registrada.

## Evidencia de correo corporativo · 2026-08-09

- Responsable: Gladis Rocio Gelves Pabon.
- Proveedor: Namecheap Private Email.
- Buzón remitente y receptor: `contacto@roustix.com`.
- Canal operativo alterno conservado: `soporte.roustix@hotmail.com`.
- MX autoritativos: `mx1.privateemail.com` y `mx2.privateemail.com`.
- SPF: `v=spf1 include:spf.privateemail.com ~all`.
- DKIM: selector `privateemail`, publicado y visible.
- DMARC: `v=DMARC1; p=none; rua=mailto:contacto@roustix.com`.
- SMTP autenticado configurado y probado en la aplicación y el worker.
- `/health/ready`: `status=ok`, versión `1.1.3`; base de datos,
  migraciones, Redis y heartbeat del worker en verde.
- Alerta operativa enviada y recepción/respuesta del buzón corporativo
  confirmadas por la responsable.

Queda pendiente confirmar los secretos SMTP de GitHub Actions y documentar la
entregabilidad cruzada en Gmail y Outlook antes de cerrar completamente el gate.
