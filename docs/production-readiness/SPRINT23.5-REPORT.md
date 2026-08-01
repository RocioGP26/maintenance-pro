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

## Próximo gate

1. Seleccionar o confirmar el proveedor del correo corporativo.
2. Crear los buzones o alias de contacto y soporte.
3. Obtener los registros SPF, DKIM y DMARC del proveedor.
4. Publicarlos en la zona DNS de `roustix.com`.
5. Actualizar secretos de web, worker y GitHub Actions.
6. Ejecutar y documentar las pruebas de entregabilidad.

No se deben publicar valores de contraseñas, claves DKIM privadas, tokens ni
credenciales SMTP en este documento o en el repositorio.

