# Changelog · Roustix Application

Todos los cambios relevantes de la aplicación se registran en este archivo. El
formato sigue *Keep a Changelog* y las versiones siguen SemVer 2.0.0.

La suite documental mantiene un ciclo independiente en
[`docs/changelog.md`](docs/changelog.md).

## [Unreleased]

### Added

- Espacio reservado para cambios aún no publicados.

## [1.0.8] - 2026-07-22

### Changed

- feat: historial y OT pendientes en hoja de vida (#9).

## [1.0.7] - 2026-07-21

### Changed

- Favicon de Roustix optimizado para que la “R” permanezca legible en las
  pestañas del navegador.
- Hoja de vida de activos simplificada con información sectorial y avances de
  OT desplegables, enlaces directos desde números de OT e incidencia y tablas
  sin botones redundantes.

### Notes

- Sprint 22.0, favicon y mejoras de hoja de vida (#8).

## [1.0.6] - 2026-07-21

### Changed

- fix: sync develop → main (migración medidores PostgreSQL) (#7).

## [1.0.5] - 2026-07-21

### Added

- Asset Health avanzado por activo con puntaje 0–100, confianza de datos,
  factores explicables, razones accionables, bandas e historial de snapshots.
- Portafolio de salud con filtros, detalle por activo, integración en dashboard
  y alerta de activos en riesgo según el último diagnóstico persistido.
- Motor tenant-safe de automatizaciones de mantenimiento con reglas de umbral,
  control de cruce y enfriamiento, avisos internos, creación idempotente de OT
  e historial auditable de evaluaciones.
- Medidores acumulativos e instantáneos por activo, lecturas vinculables a OT,
  autoría delegada, validación de secuencia y rangos, correcciones inmutables y
  migración idempotente de horas de operación.
- Bitácora contextual para OT, incidencias y activos, con visibilidad interna o
  para el reportante y correcciones inmutables.
- Adjuntos privados de bitácora con checksum, validación binaria, control de
  acceso y auditoría de descarga.
- Evidencias privadas de checklist con validación de contenido, límite de 5 MB,
  checksum SHA-256 y descarga autorizada por tenant.
- Conformidad por paso, justificación de excepciones, resolución supervisada,
  firma personal del técnico y aprobación formal del checklist.
- Checklist ejecutable dentro de la OT, vinculado a una versión publicada del
  procedimiento y con snapshot histórico.
- Progreso de pasos obligatorios, autoría delegada técnico/registrador y
  auditoría de asignación y ejecución.
- Validación server-side que impide finalizar una OT con checklist incompleto.
- Catálogo tenant-safe de procedimientos de mantenimiento con versiones
  borrador, publicadas y retiradas.
- Pasos ordenados, tipos de respuesta configurables y publicación inmutable con
  retiro automático de la versión anterior.
- Auditoría del ciclo de vida, permisos por rol, UI de gestión y migración
  Alembic para Sprint 19.1.
- Alertas personales por nuevas entradas de bitácora, dirigidas únicamente a
  participantes autorizados y con lectura auditada.

### Changed

- Los timestamps UTC de Asset Health, automatizaciones, bitácora y
  procedimientos se muestran en la zona horaria configurada para la empresa.
- El gráfico “Estado de salud” deja de depender de OT del período y pasa a
  representar las bandas reales del motor Asset Health.
- El técnico puede marcar una OT como **Completada / pendiente de cierre**;
  administradores y supervisores reciben una alerta visual y conservan la
  responsabilidad exclusiva de cerrarla definitivamente.
- El ticket vinculado ya no se cierra al completar el trabajo técnico: espera
  el cierre definitivo de la OT.

- Marca principal actualizada de Maintix a **Roustix** en la aplicación, correos,
  exportaciones MRL, API, automatización de releases y suite documental.
- Recursos públicos y colecciones de API renombrados para usar la identidad
  Roustix, conservando identificadores técnicos heredados cuando su cambio podría
  romper compatibilidad.
- Logo y favicon oficiales de Roustix incorporados como SVG y enlazados en la
  aplicación operativa, landing, onboarding y panel de plataforma.

### Fixed

- La migración inicial de medidores enlaza valores booleanos tipados para que
  la carga de horas históricas funcione tanto en SQLite como en PostgreSQL.

### Notes

- Release: Roustix + Sprints 19-21 (ejecucion, automatizacion, Asset Health) (#6).

## [1.0.4] - 2026-07-16

### Changed

- feat: agregar asignacion rapida de OT a tecnicos (#5).

## [1.0.3] - 2026-07-16

### Added

- Dashboard operativo exclusivo para el rol Técnico con OT prioritarias, preventivos del día, incidencias asignadas, agenda y alertas.
- Notificación individual al técnico cuando una incidencia se asigna a su bandeja.
- Centro personal de notificaciones con alertas operativas, historial, estado leído y acceso a la incidencia.
- Asignación rápida de OT a un técnico sin exigir datos de jornada, horarios o costos.

### Changed

- El Técnico solo consulta sus OT, incidencias y activos vinculados; repuestos queda en modo consulta.
- La campana del Técnico calcula únicamente sus OT e incidencias asignadas y presenta contadores personales.
- La navegación técnica oculta administración, compras, ventas, proveedores, configuración, análisis y reportes generales.
- El Técnico registra jornadas, repuestos y diagnóstico, pero el cierre definitivo de OT e incidencias queda reservado al supervisor o responsable del flujo.
- Mi perfil permite autoservicio seguro al Técnico para nombre, correo, teléfono y contraseña, conservando los datos laborales bajo control administrativo.

### Notes

- feat: experiencia operativa y notificaciones para técnicos (#4).

## [1.0.2] - 2026-07-14

### Added

- Notificaciones individuales de incidencias por empresa, área responsable, rol y usuario activo, con modal no bloqueante, badge en la campana y polling ligero.
- Notificaciones de ciclo de vida al reportante cuando su ticket cambia de estado, es resuelto, cerrado o reabierto.
- Auditoría de entrega, primera visualización, lectura y acceso al detalle desde cada notificación de incidencia.
- Centro de Operaciones en Inicio con OT abiertas y vencidas, preventivos del día, incidencias nuevas, inventario bajo mínimo, activos fuera de servicio, garantías y actividad reciente.
- Módulo `Análisis` como acceso común a indicadores de mantenimiento, costos, reportes, inventario comercial y Purchasing.
- Tarifa por hora en usuarios para calcular mano de obra de Mantenimiento.
- Snapshot de tarifa por jornada para conservar costos históricos de las OT.
- Mano de obra en indicadores, activos, técnicos y detalle del análisis de costos.
- Costo de herramientas por jornada y desglose económico acumulado en la OT, análisis de costos y hoja de vida del activo.
- Cálculo visible de MDO y total de jornada en el modal de OT no correctivas.
- MDO editable por jornada cuando el mantenimiento lo realiza un proveedor externo.
- Resumen correctivo por jornada con herramientas, repuestos, MDO y total calculado.
- Snapshot del costo unitario de cada repuesto consumido para preservar el histórico de mantenimiento.

### Changed

- La campana del rol Solicitante/Reportante muestra únicamente sus propios tickets pendientes y oculta alertas operativas de OT.
- El antiguo Dashboard estratégico de Mantenimiento se mueve a `Análisis → Mantenimiento`; Inicio queda enfocado exclusivamente en decisiones operativas del día.
- La navegación principal se organiza en los niveles Operación, Inteligencia y Administración.

### Notes

- Actualizar main con Inicio operativo y módulo Análisis (#3).

## [1.0.1] - 2026-07-14

### Changed

- Automatizar versiones y releases (#2).

## [1.0.0] - 2026-07-14

### Added

- Primera línea base SemVer formal de la aplicación existente.
- Fuente única de verdad en `app/version.py`.
- Versión disponible en Flask, plantillas, CLI, logs y endpoints públicos seguros.
- Identificación opcional del build mediante `RENDER_GIT_COMMIT` o `GITHUB_SHA`.

### Changed

- `/health` deja de depender de `APP_VERSION` y usa la versión canónica del código.

### Notes

- Este release formaliza el versionado; no modifica funcionalidades de negocio.

[Unreleased]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.8...HEAD
[1.0.0]: https://github.com/RocioGP26/maintenance-pro/releases/tag/v1.0.0
[1.0.1]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.0...v1.0.1
[1.0.2]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.1...v1.0.2
[1.0.3]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.2...v1.0.3
[1.0.4]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.3...v1.0.4
[1.0.5]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.4...v1.0.5
[1.0.6]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.5...v1.0.6
[1.0.7]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.6...v1.0.7
[1.0.8]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.7...v1.0.8
