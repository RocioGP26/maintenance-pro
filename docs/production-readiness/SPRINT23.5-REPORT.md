# Sprint 23.5 · Reporte en curso

Fecha de inicio: 2026-08-01  
Estado: **iniciado · gate de correo corporativo pendiente**

## Evidencia de entrada

- Sprint 23.4 cerrado con observabilidad, workers, outbox, monitor y prueba de
  carga certificados.
- Producción saludable en Roustix `1.0.39`.
- Capacidad piloto aprobada: 10 usuarios concurrentes sobre la instancia actual.
- Límite comercial: máximo tres empresas piloto reales.

## Auditoría inicial de identidad

| Elemento | Estado | Observación |
| --- | --- | --- |
| `roustix.com` | Operativo | Aplicación productiva bajo HTTPS |
| `contacto@roustix.com` | Pendiente de validar | Publicado en la aplicación y material comercial |
| `soporte@roustix.com` | Pendiente | Recomendado para atención y alertas |
| `soporte.roustix@hotmail.com` | Disponible | Canal temporal, no autentica el dominio Roustix |
| SMTP transaccional | Operativo temporal | Gates funcionales aprobados con cuenta externa |
| SPF / DKIM / DMARC | Pendiente | Requiere proveedor de correo y acceso DNS |

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

## Próximo gate

1. Seleccionar o confirmar el proveedor del correo corporativo.
2. Crear los buzones o alias de contacto y soporte.
3. Obtener los registros SPF, DKIM y DMARC del proveedor.
4. Publicarlos en la zona DNS de `roustix.com`.
5. Actualizar secretos de web, worker y GitHub Actions.
6. Ejecutar y documentar las pruebas de entregabilidad.

## Hallazgo legal inicial

- El footer público todavía presenta **Privacidad · próximamente**.
- No existen páginas públicas vigentes para privacidad, tratamiento de datos y
  términos del servicio.
- Antes de redactarlas se requieren como mínimo la identidad legal del
  responsable, NIT, domicilio, canal de atención de titulares, política de
  conservación, subencargados relevantes y condiciones comerciales aprobadas.
- Los textos deberán someterse a revisión legal antes de publicarse.

## Gate UAT

El recorrido reproducible quedó definido en `SPRINT23.5-UAT.md`. Se ejecutará
primero con la empresa marcada como **Pruebas**, sin consumir el cupo máximo de
tres empresas piloto reales.

No se deben publicar valores de contraseñas, claves DKIM privadas, tokens ni
credenciales SMTP en este documento o en el repositorio.
