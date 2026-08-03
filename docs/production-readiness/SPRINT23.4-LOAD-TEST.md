# Sprint 23.4 · Gate de carga

## Objetivo

Comprobar que Roustix mantiene disponibilidad y aislamiento bajo concurrencia
de lectura, sin crear incidencias, OT ni datos artificiales en producción.

El runner versionado es `scripts/load_test.py`. Sólo ejecuta `GET` después de
un único login web y un único login API, por lo que respeta el rate limiting de
autenticación. Nunca registra contraseñas, cookies, JWT ni cuerpos de respuesta.

## Escenarios

- `/health/live` y `/health/ready`;
- `/dashboard`;
- `/incidencias`;
- `/ordenes`;
- `/api/v1/me`;
- `/api/v1/maintenance/assets`;
- `/api/v1/maintenance/work-orders`.

## Umbrales

| Estado | Latencia p95 | Errores |
| --- | ---: | ---: |
| Verde | ≤ 2.500 ms | < 1 % |
| Amarillo | > 2.500 y ≤ 5.000 ms | ≥ 1 % y ≤ 3 % |
| Rojo | > 5.000 ms | > 3 % |

Un estado rojo bloquea el cierre del Sprint 23.4. Un estado amarillo exige
analizar el endpoint afectado y repetir el mismo escalón.

## Preparación

1. Crear una cuenta de carga exclusiva en una empresa piloto, sin privilegios
   de plataforma y sin reutilizar cuentas personales.
2. Confirmar `/health/ready` en verde y worker con heartbeat estable.
3. Abrir Render Metrics y Sentry para observar CPU, memoria, errores y reinicios.
4. Crear localmente `instance/load-test.env`. La carpeta `instance/` está
   excluida de Git; no enviar este archivo por chat ni adjuntarlo como evidencia:

```dotenv
LOAD_TEST_USERNAME=usuario-carga
LOAD_TEST_PASSWORD=valor-reservado
LOAD_TEST_EMPRESA_SLUG=empresa-piloto
```

## Ejecución escalonada

Realizarla en una ventana controlada y detenerse ante el primer rojo:

```powershell
python scripts/load_test.py --base-url https://roustix.com --env-file instance/load-test.env --users 1  --duration 30 --allow-production --output artifacts/load-01.json
python scripts/load_test.py --base-url https://roustix.com --env-file instance/load-test.env --users 5  --duration 60 --allow-production --output artifacts/load-05.json
python scripts/load_test.py --base-url https://roustix.com --env-file instance/load-test.env --users 10 --duration 60 --allow-production --output artifacts/load-10.json
python scripts/load_test.py --base-url https://roustix.com --env-file instance/load-test.env --users 20 --duration 60 --allow-production --output artifacts/load-20.json
```

El argumento `--allow-production` es obligatorio para cualquier destino remoto.
El máximo técnico del runner es 50 usuarios y cinco minutos por escalón.
Antes de iniciar la concurrencia, el runner toma una muestra de línea base por
ruta para evitar endpoints sin representación en escalones cortos.

El runner limita cada ruta API a 50 solicitudes por minuto de forma
predeterminada para no convertir el gate de capacidad en una prueba de abuso
contra el límite de 60 RPM del plan Start. El valor puede ajustarse con
`--api-rpm-per-path` cuando el tenant certificado tenga otro entitlement.

## Smoke público · 2026-07-31

- 1 usuario durante 5 segundos; sólo `/health/live` y `/health/ready`.
- 3 solicitudes, 0 errores y sin reinicios observados.
- p95 global: `3.154,87 ms` (**amarillo**).
- El muestreo aleatorio inicial no alcanzó liveness; el runner fue corregido
  para garantizar una línea base por endpoint antes del periodo concurrente.
- Repetición después de la corrección: 7 solicitudes, 0 errores, p95
  `1.216,98 ms`; liveness y readiness representados; veredicto **verde**.
- Este smoke valida el runner y no sustituye la prueba autenticada escalonada.

## Evidencia requerida

| Campo | Resultado |
| --- | --- |
| Fecha y responsable | 2026-07-31 · Gladis Rocio Gelves Pabon |
| Commit / versión | Producción `a04aeb3` · `1.0.37` |
| Cuenta y tenant de carga | Identificadores reservados y comprobados |
| Escalones ejecutados | 1 usuario · 30 s; dos repeticiones posteriores al despliegue |
| Resultado global | 26/27 solicitudes · 0 fallos · p95 2.496,31/2.209,95 ms |
| Endpoint con mayor p95 | `/dashboard` · 2.496,31/2.505,72 ms |
| Error rate máximo | 0 % |
| CPU / memoria Render | Pendiente |
| Errores Sentry | Pendiente |
| Reinicios / health fallidos | Pendiente |
| Veredicto | 1, 5 y 10 usuarios aprobados; 20 usuarios no aprobados en Starter |

## Primera etapa autenticada · 2026-07-31

- Responsable: Gladis Rocio Gelves Pabon.
- Cuenta y tenant: identificadores reservados en `instance/load-test.env`.
- Escalón: 1 usuario, 30 segundos, ocho rutas de solo lectura.
- Resultado: 23 solicitudes, 0 fallos y tasa de error `0 %`.
- p95 global: `8.227,86 ms`; veredicto **rojo**.
- Endpoint determinante: `/dashboard`, p95 `8.464,05 ms` y dos muestras
  entre `8.227,86` y `8.464,05 ms`.
- El registro de aplicación confirmó procesamiento interno de `/dashboard`
  entre `7.904,36` y `8.350,45 ms`; no fue latencia del cliente.
- Los otros siete endpoints no presentaron fallos; sus p95 quedaron entre
  `475,71` y `2.486,66 ms`.
- Decisión: detener el escalamiento antes de 5 usuarios.
- Hallazgo: Inicio ejecutaba también el bloque completo de KPI históricos de
  `/analisis/mantenimiento`, aunque su plantilla no los muestra.
- Corrección local: separar el contexto operativo del analítico y evitar 104
  sentencias SQL por carga (28 en Inicio frente a 132 en Análisis en la prueba
  controlada).

## Repetición posterior al despliegue · `a04aeb3`

- Render confirmó el deploy `live`; readiness aprobó PostgreSQL, migraciones,
  Redis y heartbeat del worker.
- Primera repetición: 26 solicitudes, 0 fallos, p95 global `2.496,31 ms` y
  veredicto **verde**. `/dashboard` bajó a `2.496,31 ms`.
- `/ordenes` tuvo una muestra aislada de `2.825,66 ms`; se repitió el escalón
  conforme a la regla del gate.
- Confirmación: 27 solicitudes, 0 fallos, p95 global `2.209,95 ms` y veredicto
  **verde**. `/ordenes` quedó en `1.951,83 ms`.
- `/dashboard` osciló entre `2.209,50` y `2.505,72 ms` en la confirmación;
  permanece cerca del umbral y debe observarse en el escalón de 5 usuarios.
- Mejora del p95 de `/dashboard` frente al hallazgo inicial: aproximadamente
  `70 %`, sin errores funcionales ni fallos de readiness.

Los JSON de evidencia no deben contener credenciales ni identificadores
personales. Antes de adjuntarlos, revisar el arreglo `failures` y conservar sólo
tipo de error, ruta, estado y latencia.

## Escalones concurrentes · 2026-08-01

- Responsable: Gladis Rocio Gelves Pabon.
- Producción inicial: `9a3d773`, versión `1.0.37`, readiness completamente
  verde.
- Primer escalón de 5 usuarios: 181 solicitudes, 0 fallos, p95 global
  `3.142,65 ms`; las tres vistas HTML quedaron rojas por cola de ejecución.
- Corrección: 8 hilos web, estados de OT delegados al worker y consultas
  agregadas para los resúmenes de OT e incidencias.
- Repetición de 5 usuarios: 228 solicitudes, 0 fallos, p95 global
  `2.493,92 ms` (**verde**). Confirmación: 234 solicitudes, 0 fallos y p95
  `1.782,03 ms` (**verde**).
- Primer escalón de 10 usuarios: las vistas de incidencias y OT superaron
  `5.000 ms`; el escalamiento se detuvo y se identificaron 8–9 consultas de la
  campana repetidas en cada página.
- Corrección: caché distribuida por tenant y usuario durante 15 segundos
  (`c9c98eb`). En prueba controlada, una recarga de OT bajó de 16 a 6
  sentencias SQL.
- Repetición sin tope API: incidencias `2.106,31 ms` y OT `2.412,98 ms`, sin
  fallos web. Los `429` restantes correspondieron al límite contractual del
  plan Start, no a errores de capacidad.
- Runner corregido en `5804654` para limitar cada ruta API a 50 RPM.
- Repetición de 10 usuarios con cuota respetada: 494 solicitudes, 0 fallos,
  p95 global `2.180,98 ms` (**verde**). API completamente verde; dashboard,
  incidencias y OT en amarillo, sin endpoints rojos.
- Confirmación de 10 usuarios: 507 solicitudes, 0 fallos y p95 global
  `2.052,03 ms` (**verde**). El resultado reproduce el patrón anterior sin
  respuestas `429` ni errores funcionales; se autoriza avanzar a 20 usuarios.
- Primer escalón de 20 usuarios: 770 solicitudes, 0 fallos y p95 global
  `2.686,48 ms` (**amarillo**). API y health verdes; `/incidencias` alcanzó
  p95 `5.646,84 ms` (**rojo**), por lo que el gate se detuvo. El patrón es de
  cola de ejecución con 20 usuarios sobre 8 hilos; se requiere ajustar la
  concurrencia y repetir este escalón antes de certificarlo.
- Repetición con 16 hilos: 926 solicitudes, 0 fallos y p95 global
  `1.845,20 ms` (**verde**). Health y API quedaron verdes; `/dashboard`
  alcanzó `5.437,23 ms` por ráfagas coincidentes con la expiración de la
  caché cada 15 segundos. Se amplía el TTL a 60 segundos y se exige una nueva
  confirmación del escalón de 20 usuarios.
- Confirmación con TTL de 60 segundos: 970 solicitudes, 0 fallos y p95 global
  `1.857,06 ms` (**verde**). `/dashboard` quedó amarillo, `/incidencias`
  verde y `/ordenes` alcanzó `7.274,91 ms` (**rojo**). El desplazamiento de la
  ráfaga entre vistas confirmó una estampida al renovar la caché distribuida.
- Corrección final `4f88bb6`: caché *stale-while-refresh*, renovación protegida
  por lock de Redis y reutilización temporal del valor anterior para las
  solicitudes concurrentes.
- Prueba definitiva de 20 usuarios: 981 solicitudes, 0 fallos, tasa de error
  `0 %` y p95 global `1.568,86 ms` (**verde**). Health y API quedaron verdes;
  `/dashboard` quedó amarillo con `3.275,33 ms`, pero `/incidencias` alcanzó
  `5.015,59 ms` y `/ordenes` `6.845,57 ms` (**rojo**).
- Veredicto de capacidad: la instancia web Starter actual queda certificada
  hasta **10 usuarios concurrentes** para el piloto. El escalón de 20 usuarios
  queda **no aprobado**; antes de repetirlo se requiere ampliar CPU/instancias
  o reducir el coste de las vistas de incidencias y órdenes. No se justifican
  más ajustes a ciegas sobre la misma infraestructura.
