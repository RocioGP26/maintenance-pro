# Sprint 23.5 · Gate UAT del piloto

## Propósito

Demostrar que una empresa puede comenzar y completar su operación esencial sin
intervención de desarrollo. El gate se ejecuta primero con un tenant marcado
como **Pruebas** y después, de forma abreviada, con cada empresa piloto real.

## Datos de la ejecución

| Campo | Evidencia |
| --- | --- |
| Fecha y hora Colombia | 2026-08-01, 15:49–16:00 aprox. |
| Responsable | Gladis Rocio Gelves Pabon |
| Versión y commit | v1.0.40 · `bc6c593` |
| Tenant de prueba | Empresa de Prueba |
| Plan | Start · tenant clasificado como Pruebas |
| Navegador / dispositivo | Navegador de escritorio · Windows |
| Resultado final | Pendiente |

No registrar contraseñas, códigos de verificación, tokens, cookies ni datos
personales innecesarios en las capturas o en este documento.

## 1. Identidad y acceso

- [ ] Registrar una empresa con un correo nuevo.
- [ ] Recibir y consumir el código de verificación.
- [ ] Confirmar el correo de bienvenida.
- [ ] Iniciar y cerrar sesión.
- [ ] Recuperar la contraseña y rechazar la reutilización del enlace.
- [ ] Confirmar que una sesión anterior queda revocada.
- [ ] Verificar que un correo inexistente no pueda enumerarse.

## 2. Configuración de empresa

- [ ] Completar datos generales, sector y zona horaria.
- [ ] Crear sede y área.
- [ ] Crear usuarios con área y cargo obligatorios.
- [ ] Confirmar permisos por rol y acceso al menú correspondiente.
- [ ] Verificar que otro tenant no pueda consultar ni modificar estos datos.

## 3. Activos y hoja de vida

- [ ] Crear un activo con responsable, proveedor, factura e imagen.
- [ ] Completar ficha técnica y campos de la plantilla sectorial.
- [ ] Abrir la hoja de vida y confirmar imagen, documentos e historial.
- [ ] Descargar la hoja de vida en PDF.
- [ ] Verificar aislamiento de imagen y documentos desde otro tenant.

## 4. Incidencia y orden de trabajo

- [x] Crear una incidencia como usuario reportante (`INC-26-0001`).
- [ ] Confirmar notificación en la campana. El tenant de prueba no tiene
  personal autorizado configurado en Mantenimiento y el reporte generó
  `0 usuario(s)` notificados; condición de configuración pendiente.
- [x] Asignar técnico y crear la OT desde el incidente (`OT-26-0002`).
- [x] Seleccionar libremente el tipo de OT (se eligió Preventiva).
- [x] Registrar jornada interna con horas, sin paro y recibido por.
- [ ] Registrar jornada externa con proveedor y técnico del proveedor.
- [ ] Instalar un repuesto y confirmar jornada, hora y técnico.
- [ ] Adjuntar informe técnico.
- [x] Completar la OT y confirmar el cierre del incidente asociado. El hallazgo
  inicial fue corregido en v1.0.40 y revalidado en producción: `OT-26-0002`
  cerró automáticamente `INC-26-0001` el 01/08/2026 a las 16:07, con historial
  `cerrado por ot` y motivo de cierre registrado.
- [x] Abrir el PDF de `OT-26-0002` desde el enlace disponible en el detalle de
  `INC-26-0001`; el visor recibió correctamente el documento en producción.

## 5. Almacenamiento y capacidad

- [ ] Cargar, reemplazar, descargar y eliminar un archivo.
- [ ] Confirmar que el uso del tenant cambia una sola vez por operación.
- [ ] Verificar alerta al 80 % y bloqueo al 100 % en un entorno controlado.
- [ ] Activar y retirar el add-on de almacenamiento según el procedimiento.
- [ ] Confirmar que una indisponibilidad de R2 falla de forma controlada.

## 6. Operación y soporte

- [ ] Confirmar `/health/ready` en verde durante la ejecución.
- [ ] Verificar worker, Redis, SMTP, R2, Sentry y backups en infraestructura.
- [ ] Generar una alerta controlada y comprobar auditoría y recepción.
- [ ] Registrar una solicitud de soporte y medir el tiempo de respuesta.
- [ ] Confirmar que el tenant de prueba no genera MRR ni factura.

## 7. Evidencia y decisión

Para cada hallazgo registrar: paso, resultado esperado, resultado observado,
captura saneada, severidad, responsable y estado de corrección.

### Criterio Go

- Cero hallazgos críticos o altos abiertos.
- Todos los recorridos esenciales aprobados.
- Aislamiento multiempresa aprobado.
- Correo corporativo y documentos legales disponibles.
- Capacidad dentro del límite certificado de 10 usuarios concurrentes.

### Criterio No-Go

Cualquier pérdida o exposición de datos, fallo de aislamiento, imposibilidad de
recuperar acceso, correo transaccional no entregable, backup no recuperable o
flujo esencial bloqueado impide incorporar una empresa piloto real.

## Resultado

**Decisión:** Pendiente · `GO` / `GO CONDICIONADO` / `NO-GO`
