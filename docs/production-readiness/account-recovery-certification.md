# Certificación de recuperación de cuenta · Piloto Roustix

**Fecha de corte:** 2026-07-30

**Alcance:** solicitud anónima, entrega del enlace, expiración, uso único,
revocación de sesiones, protección contra enumeración y rate limiting.

## Veredicto

| Control | Estado | Evidencia |
|---------|--------|-----------|
| Acceso desde «¿Olvidaste tu contraseña?» | ✅ Aprobado | Enlace público y formulario cubiertos por prueba HTTP |
| Token seguro | ✅ Aprobado | Token aleatorio; PostgreSQL conserva únicamente SHA-256 |
| Expiración | ✅ Aprobado | Enlace expirado rechazado por servicio y formulario |
| Uso único | ✅ Aprobado | Un segundo consumo no modifica nuevamente la contraseña |
| Solicitud posterior | ✅ Aprobado | El token anterior se invalida al emitir uno nuevo |
| Revocación de sesiones | ✅ Aprobado | `auth_version` incrementa y las sesiones activas quedan revocadas |
| No enumeración | ✅ Aprobado | Cuenta conocida y desconocida reciben el mismo mensaje y recorrido HTTP |
| Rate limiting | ✅ Aprobado | Cinco solicitudes por 15 minutos; la sexta devuelve HTTP 429 |
| SMTP real | ✅ Aprobado | Recepción y consumo comprobados con una cuenta piloto en producción |

**Estado global:** certificación de recuperación de cuenta aprobada en
producción.

## Evidencia automatizada

Archivo: `tests/test_password_reset.py`.

Resultado focalizado al 2026-07-30:

```text
18 pruebas aprobadas (recuperación y versión)
```

La batería comprueba:

- acceso al flujo desde la pantalla de ingreso;
- igualdad de respuesta para correo conocido y desconocido;
- envío al outbox controlado y almacenamiento exclusivo del hash;
- restablecimiento completo por HTTP;
- aceptación de la nueva clave y rechazo de la anterior;
- expiración del enlace;
- invalidación del token previo ante una nueva solicitud;
- rechazo del segundo uso;
- revocación de una sesión administrada que estaba abierta;
- límite de cinco solicitudes en 15 minutos y HTTP 429 en la sexta.

## Gate remoto SMTP · Ejecutado

El responsable del piloto ejecutó el recorrido con una cuenta de producción y
confirmó los siguientes controles:

1. Abrir `/login` y seleccionar **¿Olvidaste tu contraseña?**.
2. Solicitar recuperación con el correo corporativo de la cuenta piloto.
3. Confirmar que la interfaz muestra el mensaje genérico y no revela si la
   cuenta existe.
4. Registrar hora de solicitud y hora de recepción del correo.
5. Abrir el enlace recibido y establecer una contraseña nueva.
6. Confirmar que la contraseña anterior ya no permite ingresar.
7. Confirmar que la nueva contraseña permite ingresar.
8. Volver a abrir el mismo enlace y confirmar que es rechazado.
9. Si había otra sesión abierta, confirmar que solicita autenticación de nuevo.
10. Revisar logs: entrega SMTP exitosa, sin contraseña ni token crudo.

## Registro del gate remoto

| Campo | Valor |
|-------|-------|
| Fecha y hora Colombia | 2026-07-30; hora exacta no registrada |
| Responsable | Gladis Rocio Gelves Pabon |
| Commit desplegado | `805d14a` · Roustix v1.0.37 |
| Cuenta piloto | Cuenta de producción; identificador reservado |
| Tiempo de entrega SMTP | Correo recibido correctamente; tiempo exacto no medido |
| Cambio de contraseña | ✅ Aprobado |
| Reutilización rechazada | ✅ Aprobado |
| Sesión anterior revocada | ✅ Aprobado |
| Logs revisados | ✅ Render confirmó entrega, consumo único y revocación sin exponer secretos |
| Veredicto final | ✅ Gate SMTP aprobado en producción |

No incluir en la evidencia capturas del enlace completo, el token, la contraseña
ni secretos SMTP.
