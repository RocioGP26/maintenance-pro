# Changelog · Maintix Application

Todos los cambios relevantes de la aplicación se registran en este archivo. El
formato sigue *Keep a Changelog* y las versiones siguen SemVer 2.0.0.

La suite documental mantiene un ciclo independiente en
[`docs/changelog.md`](docs/changelog.md).

## [Unreleased]

### Added

- Espacio reservado para cambios aún no publicados.

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

[Unreleased]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.3...HEAD
[1.0.0]: https://github.com/RocioGP26/maintenance-pro/releases/tag/v1.0.0
[1.0.1]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.0...v1.0.1
[1.0.2]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.1...v1.0.2
[1.0.3]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.2...v1.0.3
