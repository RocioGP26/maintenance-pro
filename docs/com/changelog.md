# COM Changelog

## [1.4.0] — 2026-08-09 · Comercialización general

### Changed
- COM-01 y COM-02 pasan a oferta comercial general.
- Se elimina el límite comercial de tres empresas; la capacidad se controla
  mediante métricas operativas e infraestructura disponible.
- COM-03 queda archivado y fuera de la oferta vigente.
- Las plantillas exclusivas del piloto pasan al archivo histórico.

---

## [1.3.3] — 2026-08-01 · Piloto controlado

### Changed
- El cupo inicial se limita a un máximo de **3 empresas piloto reales**.
- Los tenants internos marcados como prueba no consumen el cupo comercial.
- El ingreso de nuevas empresas queda sujeto al gate UAT y a una decisión
  Go/No-Go documentada.

---

## [1.3.2] — 2026-07-29 · Storage conservador año 1

### Changed
- Almacenamiento incluido: Start **1 GB** · Business **5 GB** · Enterprise **20 GB** ampliables
- Justificación: capa free R2 (~10 GB) · upsell antes de pagar infra
- Roadmap v2: 2 / 10 / 50 GB cuando haya ingresos estables

### Added
- Monitor SuperAdmin `/platform/infraestructura` (BD, R2, SMTP, backups, workers, health)
- Barra de uso storage por tenant vs cuota del plan (alerta ≥ 80% → +2 GB)
- Alerta y upsell **+2 GB** en portal cliente (admins · banner global + Configuración empresa)

---

## [1.3.1] — 2026-07-29 · Business + Enterprise sin precio público


### Changed
- Nombre medio: **Business** (clave técnica `grow`)
- **Enterprise:** landing «Contactar para conocer el precio» (piso $2.5M solo interno)
- Start / Business siguen con precio público ($1M / $1.5M)

### Added (piloto)
- Protección de marcas `translate=no` / `notranslate` en landing · ver [i18n-roadmap.md](../mkt/i18n-roadmap.md)

---

## [1.3.0] — 2026-07-29 · Estrategia de precios final

### Changed
- Precios: Start **$1.000.000** · Grow **$1.500.000** · Enterprise **desde $2.500.000**
- Activos **ilimitados** en los tres planes

---

## [1.2.0] — 2026-07-29 · Business + precios públicos (supersedido)

---

## [1.1.0] — 2026-07-29 · Tres planes

---

## [1.0.0] — 2026-07-29 · Empaquetado inicial
