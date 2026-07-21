# Sprint 19 · Maintenance Execution Foundation

**Estado:** Sprint 19 completo ✅ · 19.0–19.5 implementados  
**Fecha de inicio:** 2026-07-21  
**Módulo propietario:** Maintenance

## 1 · Objetivo

Estandarizar la ejecución del mantenimiento para que cada orden de trabajo pueda
indicar qué procedimiento debía seguirse, qué pasos se realizaron, qué evidencia
se obtuvo, quién ejecutó el trabajo y quién registró la información.

El sprint también crea la bitácora contextual y el historial de lecturas que
alimentarán automatizaciones, indicadores de salud e integraciones posteriores.

## 2 · Problema que resuelve

Roustix ya administra OT, jornadas, repuestos, costos e incidencias, pero todavía
no dispone de un contrato común para:

- exigir pasos técnicos antes de completar una OT;
- conservar la versión exacta del procedimiento aplicado;
- registrar una conversación operativa dentro del contexto correcto;
- diferenciar al técnico ejecutor del administrador que transcribe el formato;
- mantener series históricas de horómetros, kilometraje, presión o temperatura.

Sin estos datos, una automatización futura tomaría decisiones sobre información
incompleta o no comparable.

## 3 · Alcance

### Incluido

- Plantillas de procedimientos por tenant.
- Versiones borrador, publicadas y retiradas.
- Pasos ordenados, obligatorios u opcionales.
- Tipos de respuesta: confirmación, texto, número, selección, medición, evidencia y firma.
- Instancia de checklist asociada a una OT.
- Ejecución directa por técnico o registro delegado por administrador/supervisor.
- No conformidades, justificación y revisión.
- Bitácora de comentarios y eventos para OT, incidencia o activo.
- Alertas personales por entradas nuevas de bitácora, sin notificar al autor y
  respetando tenant, visibilidad y participantes del contexto.
- Fotografías y archivos adjuntos con metadata y permisos.
- Medidores acumulativos y de valor instantáneo.
- Lecturas manuales, históricas, auditables e idempotentes.
- Tenancy, permisos, auditoría, pruebas y documentación MRG/MUX.

### Fuera de alcance

- Generación automática de OT por umbral.
- Motor evento–condición–acción.
- WebSockets, presencia en línea o indicador “escribiendo”.
- Mensajería SMS o WhatsApp.
- Ingesta IoT continua.
- Cálculo compuesto de Asset Health.
- API pública de escritura y webhooks.
- Restricciones comerciales por plan.

Estos puntos pertenecen a Sprints 20–22.

## 4 · Flujos principales

### Procedimiento y checklist

```text
Supervisor crea procedimiento
        ↓
Publica versión inmutable
        ↓
OT selecciona procedimiento
        ↓
Roustix crea checklist histórico
        ↓
Técnico ejecuta o administrador registra en su nombre
        ↓
Validación de pasos obligatorios y no conformidades
        ↓
Técnico solicita completar → supervisor revisa/cierra
```

`Completada` no equivale a cierre administrativo: deja la OT visible en la
campana como pendiente de cierre. Solo `Cerrada` finaliza el flujo y puede cerrar
el ticket de origen.

### Bitácora

```text
OT / Incidencia / Activo
        ↓
Entrada contextual + autor + visibilidad
        ↓
Adjuntos opcionales
        ↓
Auditoría y notificación a usuarios relacionados
```

### Medidores

```text
Activo → Medidor → Lectura fechada → validación → historial
                                              ↓
                         evento disponible para Sprint 20
```

## 5 · Regla de autoría delegada

Todo registro de ejecución debe conservar dos identidades cuando corresponda:

- `performed_by_user_id`: técnico o responsable que realizó físicamente el trabajo;
- `recorded_by_user_id`: usuario autenticado que digitó la información.

Si el técnico registra su propia actividad, ambos campos contienen el mismo
usuario. Si un administrador transcribe un formato físico, los campos son
diferentes y la auditoría debe mostrarlo explícitamente.

Nunca se permitirá que un administrador suplante silenciosamente al técnico.

## 6 · Entregables por sub-sprint

| Sub-sprint | Entregables |
|---|---|
| 19.0 | Charter, arquitectura, contratos, permisos, eventos y migración |
| 19.1 | Modelos, migración Alembic, catálogo, pasos y publicación de versiones |
| 19.2 | Asignación a OT, ejecución, progreso y validaciones |
| 19.3 | Evidencias, firma, no conformidades, revisión y auditoría |
| 19.4 | Bitácora, visibilidad, adjuntos, notificaciones y timeline |
| 19.5 | Medidores, lecturas, migración de horas, pruebas y cierre |

## 7 · Definition of Done · Sprint 19.0

- [x] Alcance y límites definidos.
- [x] Modelos y ownership documentados.
- [x] Estados y transiciones definidos.
- [x] Matriz de permisos definida.
- [x] Autoría delegada definida.
- [x] Eventos preparados para Sprint 20.
- [x] Matriz de compatibilidad con datos actuales definida.
- [x] Sub-sprints y Definition of Done general definidos.
- [x] MRG y MPA referencian el nuevo bloque.
- [x] No se implementó lógica de negocio en 19.0.

## 8 · Definition of Done · Sprint 19 completo

- [x] Existen procedimientos versionados tenant-safe.
- [x] Una versión publicada no puede modificarse.
- [x] La OT conserva su checklist histórico.
- [x] Los pasos obligatorios bloquean la solicitud de cierre cuando están pendientes.
- [x] Las no conformidades requieren resolución o justificación revisada.
- [x] Técnico y registrador quedan diferenciados y auditados.
- [x] La bitácora funciona para OT, incidencia y activo sin fugas entre tenants.
- [x] Los adjuntos validan tipo, tamaño, ownership y acceso.
- [x] Existen medidores acumulativos e instantáneos con historial de lecturas.
- [x] Las lecturas inválidas o regresivas se rechazan o justifican explícitamente.
- [x] Las OT antiguas continúan funcionando sin checklist obligatorio retroactivo.
- [x] Existen migraciones y pruebas de permisos, tenant y estados para 19.1–19.2.
- [x] Documentación, MRG, MUX y changelog están alineados.

## 9 · Definition of Done · Sprint 19.1

- [x] Existen catálogo, versiones, pasos y eventos de auditoría.
- [x] Código de procedimiento único por empresa.
- [x] Estados `draft`, `published` y `retired` protegidos por contrato y base de datos.
- [x] Una nueva versión clona la última versión publicada sin modificar su historia.
- [x] Publicar una versión retira automáticamente la publicada anterior.
- [x] Solo administradores y supervisores gestionan o publican; técnicos consultan publicadas.
- [x] La UI permite crear, editar metadata, ordenar pasos, publicar y retirar.
- [x] Migración Alembic aditiva disponible.
- [x] Pruebas de tenant, permisos, inmutabilidad, auditoría y rutas funcionando.
- [x] La asociación y ejecución dentro de la OT permanece expresamente en Sprint 19.2.

## 10 · Definition of Done · Sprint 19.2

- [x] Una OT puede recibir una versión publicada aplicable a su tipo de activo.
- [x] El checklist conserva código, nombre y número de versión como snapshot.
- [x] El técnico asignado ejecuta únicamente su checklist.
- [x] Administrador o supervisor registra en nombre del técnico sin suplantación.
- [x] Cada respuesta conserva ejecutor y registrador.
- [x] El progreso se calcula en servidor sobre los pasos obligatorios.
- [x] La OT permanece en proceso mientras el checklist esté incompleto.
- [x] Una OT finalizada conserva el checklist en modo histórico.
- [x] Existen auditoría, migración Alembic y pruebas tenant-safe.
- [x] Evidencias, firmas, no conformidades y revisión permanecen en Sprint 19.3.

## 11 · Dependencias desbloqueadas

- Sprint 20 · Disparadores de mantenimiento y automatizaciones configurables.
- Sprint 21 · Asset Health avanzado y analítica de condición.
- Sprint 22 · API pública, webhooks y derechos técnicos por plan.

## 12 · Definition of Done · Sprint 19.3

- [x] Evidencias privadas PDF o imagen, con límite de 5 MB y firma de contenido.
- [x] Metadata, checksum SHA-256, tenant y usuario cargador quedan auditados.
- [x] Las descargas revalidan empresa y relación con la OT.
- [x] “No conforme” y “No aplica” requieren justificación.
- [x] Una no conformidad bloquea el checklist hasta registrar su resolución.
- [x] La firma solo puede confirmarla el técnico desde su propia sesión.
- [x] Supervisor o administrador revisa y aprueba la ejecución.
- [x] La OT solo puede cerrarse con checklist en estado `reviewed`.
- [x] Accesos a evidencias y decisiones de revisión generan auditoría.
- [x] Migración y pruebas cubren evidencia, autoría, firma y resolución.

## 13 · Definition of Done · Sprint 19.4

- [x] Existe una bitácora común para OT, incidencia y activo.
- [x] Cada entrada apunta exactamente a un contexto y tenant.
- [x] Técnicos solo acceden a contextos relacionados con su trabajo.
- [x] El reportante solo ve entradas de su incidencia marcadas `requester`.
- [x] Solo supervisor o administrador publica información al reportante.
- [x] Autor y ejecutor pueden diferenciarse sin suplantación silenciosa.
- [x] Las entradas son inmutables y las correcciones conservan el original.
- [x] Adjuntos privados validan contenido, tamaño, checksum y acceso.
- [x] Creación, carga y descarga quedan auditadas.
- [x] Migración y pruebas cubren tenant, visibilidad, relación y adjuntos.

## 14 · Definition of Done · Sprint 19.5

- [x] Cada medidor pertenece a un activo y tenant, con código único por activo.
- [x] Existen medidores acumulativos e instantáneos con unidad y precisión definidas.
- [x] Las lecturas conservan fecha de medición, ejecutor, registrador, origen y OT opcional.
- [x] Una lectura acumulativa regresiva requiere reinicio, reemplazo, rollover o ajuste justificado.
- [x] Una lectura instantánea fuera del rango requiere confirmación y justificación.
- [x] Las correcciones crean una nueva lectura vinculada y no sobrescriben el original.
- [x] Técnicos registran únicamente en activos relacionados; supervisores y administradores pueden registrar de forma delegada.
- [x] `Machine.horas_operacion` siembra un horómetro y lectura inicial de manera idempotente.
- [x] Los eventos de lectura quedan disponibles para los disparadores del Sprint 20.
- [x] Migración, pruebas, MRG, MUX, changelog e índices documentales quedan alineados.
