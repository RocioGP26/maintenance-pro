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
| Veredicto | Escalón de 1 usuario aprobado; 5/10/20 usuarios pendientes |

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
