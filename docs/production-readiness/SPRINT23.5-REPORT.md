# Sprint 23.5 · Reporte en curso

Fecha de inicio: 2026-08-01  
Última actualización: 2026-08-09

Estado: **Preparación para comercialización · identidad de correo, GitHub
Actions y paquete comercial aprobados; revisión legal pendiente**

## Evidencia de entrada

- Sprint 23.4 cerrado con observabilidad, workers, outbox, monitor y prueba de
  carga certificados.
- Producción saludable en Roustix `1.0.46` (`100e206`).
- Prueba de capacidad aprobada: 10 usuarios concurrentes sobre la instancia
  evaluada; este resultado es una referencia operativa, no un límite comercial.

## Auditoría inicial de identidad

| Elemento | Estado | Observación |
| --- | --- | --- |
| `roustix.com` | Operativo | Aplicación productiva bajo HTTPS |
| `contacto@roustix.com` | Operativo | Buzón Namecheap Private Email con envío y recepción comprobados |
| `soporte@roustix.com` | Opcional futuro | `contacto@roustix.com` es el canal corporativo vigente |
| `soporte.roustix@hotmail.com` | Disponible | Canal externo de recuperación y alertas operativas |
| SMTP transaccional | Operativo corporativo | Namecheap Private Email configurado en web y worker |
| SPF / DKIM / DMARC | Aprobado | Registros visibles en DNS autoritativo el 2026-08-09 |

### Consulta DNS pública · 2026-08-01

- Los registros MX apuntan a `eforward1`–`eforward5.registrar-servers.com`,
  correspondientes al reenvío de correo del registrador.
- No se observó una política SPF utilizable ni un registro DMARC público.
- El reenvío permite recibir mensajes, pero no certifica el envío SMTP
  autenticado requerido por Roustix.
- Ruta recomendada: crear `soporte@roustix.com` como buzón Private Email y
  `contacto@roustix.com` como alias; los planes nuevos permiten recibir y enviar
  mediante el alias.
- La contratación y los cambios DNS requieren aprobación de la responsable.

## Gate de identidad y SMTP · 2026-08-09

- Proveedor seleccionado: Namecheap Private Email.
- MX corporativos publicados para `roustix.com`.
- SPF, DKIM y DMARC visibles mediante consulta al DNS autoritativo.
- DMARC inició en observación (`p=none`) y envía reportes a
  `contacto@roustix.com`.
- La aplicación y el worker usan `contacto@roustix.com` como identidad SMTP.
- La prueba operativa de envío, recepción y respuesta fue aprobada por Gladis
  Rocio Gelves Pabon.
- Producción respondió `status=ok` en `/health/ready`, versión `1.1.3`, con
  base de datos, migraciones, Redis y worker en verde.
- No se registraron contraseñas, claves privadas ni secretos SMTP en el
  repositorio.

## Próximo gate

1. Completar identidad jurídica y tributaria del Prestador.
2. Cerrar decisiones de precios, pagos, terminación y SLA.
3. Completar la revisión jurídica y contable del paquete.
4. Publicar Términos y Privacidad vigentes y activar aceptación trazable.

## Hallazgo legal inicial

- El footer público todavía presenta **Privacidad · próximamente**.
- No existen páginas públicas vigentes para privacidad, tratamiento de datos y
  términos del servicio.
- Antes de redactarlas se requieren como mínimo la identidad legal del
  responsable, NIT, domicilio, canal de atención de titulares, política de
  conservación, subencargados relevantes y condiciones comerciales aprobadas.
- Los textos deberán someterse a revisión legal antes de publicarse.

### Avance legal · 2026-08-01

- Roustix todavía no corresponde a una sociedad constituida y es desarrollado
  por dos socios personas naturales.
- Se prepararon en almacenamiento local privado borradores de política de
  tratamiento, aviso de privacidad, términos comerciales y acuerdo de
  transmisión de datos.
- Los borradores están excluidos de Git porque contienen datos personales y no
  pueden publicarse ni firmarse hasta completar la identificación de ambos
  socios y obtener revisión jurídica colombiana.

## Evidencia de aceptación técnica

El recorrido reproducible definido en `SPRINT23.5-UAT.md` fue ejecutado con la
empresa interna marcada como **Pruebas**. Se conserva como evidencia técnica y
no como requisito de un programa piloto.

Resultado: **GO CONDICIONADO**. Todos los pasos técnicos del tenant de prueba
quedaron aprobados en producción, incluida la descarga de la Hoja de Vida en PDF
con la zona horaria de la empresa. No quedaron hallazgos críticos o altos
abiertos.

Antes de activar cada cliente se deberá ejecutar el onboarding abreviado,
documentar responsables, soporte, plan contratado y capacidad disponible.

No se deben publicar valores de contraseñas, claves DKIM privadas, tokens ni
credenciales SMTP en este documento o en el repositorio.
