# Changelog · Maintix Application

Todos los cambios relevantes de la aplicación se registran en este archivo. El
formato sigue *Keep a Changelog* y las versiones siguen SemVer 2.0.0.

La suite documental mantiene un ciclo independiente en
[`docs/changelog.md`](docs/changelog.md).

## [Unreleased]

### Added

- Espacio reservado para cambios aún no publicados.

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

[Unreleased]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.1...HEAD
[1.0.0]: https://github.com/RocioGP26/maintenance-pro/releases/tag/v1.0.0
[1.0.1]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.0...v1.0.1
