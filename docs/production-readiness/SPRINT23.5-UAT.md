# Sprint 23.5 · Gate UAT del piloto

## Propósito

Demostrar que una empresa puede comenzar y completar su operación esencial sin
intervención de desarrollo. El gate se ejecuta primero con un tenant marcado
como **Pruebas** y después, de forma abreviada, con cada empresa piloto real.

## Datos de la ejecución

| Campo | Evidencia |
| --- | --- |
| Fecha y hora Colombia | 2026-08-01, 15:49–21:45 aprox. |
| Responsable | Gladis Rocio Gelves Pabon |
| Versión y commit | v1.0.46 · `100e206` |
| Tenant de prueba | Empresa de Prueba |
| Plan | Start · tenant clasificado como Pruebas |
| Navegador / dispositivo | Navegador de escritorio · Windows |
| Resultado final | GO CONDICIONADO |

No registrar contraseñas, códigos de verificación, tokens, cookies ni datos
personales innecesarios en las capturas o en este documento.

## 1. Identidad y acceso

- [x] Registrar una empresa con un correo nuevo: Empresa de Prueba.
- [x] Recibir y consumir el código de verificación. El correo transaccional fue
  recibido y el código habilitó correctamente la cuenta.
- [x] Confirmar el correo de bienvenida, recibido después de la verificación.
- [x] Iniciar y cerrar sesión con el administrador del tenant y con el
  supervisor de Mantenimiento.
- [x] Recuperar la contraseña y rechazar la reutilización del enlace. El gate
  SMTP real aprobó el cambio y el enlace consumido dejó de ser reutilizable.
- [x] Confirmar que una sesión anterior queda revocada después del cambio.
- [x] Verificar que un correo inexistente no pueda enumerarse; la respuesta
  pública conserva el mismo mensaje genérico.

## 2. Configuración de empresa

- [x] Completar datos generales, sector Manufactura y zona America/Bogota.
- [x] Crear sede y área, utilizadas por los usuarios y activos del recorrido.
- [x] Crear usuarios con área y cargo obligatorios: solicitante, técnico y
  supervisor activos para Mantenimiento.
- [x] Confirmar permisos por rol y acceso al menú correspondiente: reportante,
  técnico, supervisor y administrador participaron en el recorrido.
- [x] Verificar que otro tenant no pueda consultar ni modificar estos datos.
  El aislamiento cruzado devolvió HTTP 403 y las consultas permanecieron
  filtradas por empresa.

## 3. Activos y hoja de vida

- [x] Crear y reabrir un activo con responsable, proveedor registrado, número
  de factura e imagen; los cuatro datos permanecieron guardados.
- [x] Completar y reabrir la ficha técnica con marca, modelo, serie, fabricante
  y campos de la plantilla sectorial de Manufactura; la información permaneció
  guardada y visible en la ficha.
- [x] Abrir la hoja de vida y confirmar la información general del activo, el
  historial de incidencias, OT y demás registros operativos relacionados.
- [x] Descargar la hoja de vida en PDF. La versión `v1.0.46` corrigió el
  sello de generación para usar la zona horaria de la empresa; el PDF de la
  Hoja de Vida fue descargado y revalidado correctamente en producción.
- [x] Verificar aislamiento de imagen y documentos desde otro tenant. El gate
  R2 confirmó HTTP 403 para una empresa distinta.

## 4. Incidencia y orden de trabajo

- [x] Crear una incidencia como usuario reportante (`INC-26-0001`).
- [x] Confirmar notificación en la campana. `INC-26-0002` notificó a 2
  responsables autorizados; Pedro Pérez recibió el modal, abrió el detalle y
  la campana pasó de 1 a 0. El historial registró `notificacion leida` y
  `acceso desde notificacion` el 01/08/2026 a las 16:58.
- [x] Asignar técnico y crear la OT desde el incidente. Se validaron
  `INC-26-0001` → `OT-26-0002` y `INC-26-0002` → `OT-26-0003`.
- [x] Seleccionar libremente el tipo de OT (se eligió Preventiva).
- [x] Registrar jornada interna con horas, sin paro y recibido por.
- [x] Registrar jornada externa con proveedor y técnico del proveedor.
  `OT-26-0003` registró dos jornadas con `Proveedor UAT 23.5`, técnico
  `Técnico externo UAT`, recibido por Pedro Perez y sin paro. La lista mostró
  el técnico y el proveedor en líneas separadas y acumuló 20 minutos.
- [x] Instalar un repuesto y confirmar jornada, hora y técnico. En la OT
  controlada `OT-26-0004`, el repuesto `UAT-235-001` bajó de 2 a 1 unidad una
  sola vez; la tabla mostró 01/08/2026, 14:30–14:45 y Luis Martinez.
- [x] Repetir el consumo del mismo repuesto en una jornada posterior. Tras la
  corrección `v1.0.44`, la tabla **Repuestos instalados** conservó la primera
  línea de `UAT-235-001` (14:30–14:45) y agregó una segunda línea independiente
  (18:15–18:30), ambas con cantidad 1 y técnico Luis Martinez.
- [x] Adjuntar informe técnico. `OT-26-0003` recibió
  `uat-informe-tecnico.doc`, descripción `Informe técnico controlado UAT
  23.5`, cargado el 01/08/2026 a las 17:14 por Pedro Perez.
- [x] Completar la OT y confirmar el cierre del incidente asociado. El hallazgo
  inicial fue corregido en v1.0.40 y revalidado en producción: `OT-26-0002`
  cerró automáticamente `INC-26-0001` el 01/08/2026 a las 16:07, con historial
  `cerrado por ot` y motivo de cierre registrado.
- [x] Repetir el cierre automático con el segundo recorrido. Al completar
  `OT-26-0003` con dos jornadas e informe técnico, `INC-26-0002` apareció como
  `Cerrado` en la lista de incidencias.
- [x] Abrir el PDF de `OT-26-0002` desde el enlace disponible en el detalle de
  `INC-26-0001`; el visor recibió correctamente el documento en producción.

## 5. Almacenamiento y capacidad

- [x] Cargar una imagen en un campo vacío del activo. El uso pasó de
  `577.4 KB` a `587.5 KB` bajo la cuota Start de 1 GB.
- [x] Reemplazar y visualizar la imagen. El uso cambió a `589.2 KB`, reflejando
  solamente la diferencia neta del archivo nuevo; tras `v1.0.45` el navegador
  mostró inmediatamente la imagen reemplazada.
- [x] Visualizar y eliminar el archivo reemplazado. La imagen desapareció del
  activo y el uso regresó al nivel previo a la carga controlada.
- [x] Confirmar que el uso del tenant cambia una sola vez por operación. La
  carga sumó el archivo inicial, el reemplazo contabilizó solo la diferencia
  neta y la eliminación liberó el objeto vigente.
- [x] Verificar alerta al 80 % y bloqueo al 100 % en un entorno controlado.
  Evidencia cruzada: `storage-capacity-certification.md`, umbral exacto, banner
  y hard limit aprobados sin cargar artificialmente 800 MB en producción.
- [x] Activar y retirar el add-on de almacenamiento según el procedimiento.
  El gate previo confirmó 1 GB → 3 GB → 1 GB, auditoría y conservación de
  archivos.
- [x] Confirmar que una indisponibilidad de R2 falla de forma controlada.
  `storage-certification.md` y `tests/test_file_storage.py` verifican que las
  fallas de lectura/escritura se propagan, generan alerta y que la limpieza
  posterior al commit es tolerante a fallos y alertable.

## 6. Operación y soporte

- [x] Confirmar `/health/ready` en verde durante la ejecución. El endpoint
  reportó aplicación, PostgreSQL, migraciones, Redis y worker saludables.
- [x] Verificar worker, Redis, SMTP, R2, Sentry y backups en infraestructura.
  El panel operativo quedó en verde y el heartbeat del worker estable.
- [x] Generar una alerta controlada y comprobar auditoría y recepción. El
  evento `ops_alert_test` apareció en Sentry y la alerta operativa fue recibida
  por correo.
- [x] Registrar una solicitud de soporte y medir el tiempo de respuesta. Envío
  controlado a las 09:04, recibido en soporte a las 09:05; respuesta enviada a
  las 09:07 y recibida en el mismo minuto. Tiempo de primera respuesta: 3 min.
  Se abrió un hallazgo independiente porque el correo recibido mostró 02:04
  a. m. en el cliente, en lugar de la hora Colombia.
- [x] Confirmar que el tenant de prueba no genera MRR ni factura. Empresa de
  Prueba conserva límites Start, aparece como **Excluida** en MRR y no genera
  facturación.

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

**Decisión:** `GO CONDICIONADO`

El recorrido integral del tenant **Empresa de Prueba** quedó aprobado sin
hallazgos críticos o altos abiertos. Antes de incorporar empresas piloto
reales se mantienen como condiciones de salida:

- configurar y certificar el correo corporativo de Roustix con SPF, DKIM y
  DMARC;
- completar y publicar la documentación legal aplicable;
- ejecutar el recorrido UAT abreviado para cada empresa piloto real, con un
  máximo de tres empresas durante esta fase.
