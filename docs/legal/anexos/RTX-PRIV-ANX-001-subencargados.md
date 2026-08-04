# RTX-PRIV-ANX-001 · Lista de Subencargados

| Campo | Valor |
|-------|-------|
| **Código** | RTX-PRIV-ANX-001 |
| **Versión** | **0.2.0** |
| **Estado** | 🟡 Borrador operativo · regiones cloud por validar en consolas |
| **Padre** | [RTX-PRIV-001](../RTX-PRIV-001-politica-privacidad.md) |
| **Fecha** | 2026-08-03 |
| **Fuente** | `render.yaml` · `.env.example` · `docs/production-storage.md` · runbooks Sprint 23 |

---

## Propósito

Identificar proveedores que tratan o pueden tratar datos personales por cuenta de Roustix en la prestación del servicio SaaS.

---

## Lista vigente (operación documentada)

| Proveedor | Servicio | Datos / contexto | Región / país | Estado |
|-----------|----------|------------------|---------------|--------|
| **Render** | Hosting web (`mantis-app`), worker (`roustix-worker`) | Aplicación, sesiones, logs de runtime | No documentado en repo · validar en panel Render | Activo (prod) |
| **Neon** | PostgreSQL gestionado (+ PITR / backups) | Datos de Tenants, cuentas, operación | No documentado · hostname `*.aws.neon.tech` · validar región del proyecto | Activo (prod) |
| **Cloudflare R2** | Almacenamiento de objetos (S3-compatible) | Archivos / evidencias del Cliente | `STORAGE_REGION=auto` · jurisdicción por validar en Cloudflare | Activo (prod certificado) |
| **Render Key Value** | Redis (rate limits, locks, heartbeat) | Metadatos de sesión / límites · no contenido de negocio | No documentado · validar en Render | Activo (prod) |
| **Sentry** | Errores y trazas (`SENTRY_DSN`) | Telemetría; posible PII en mensajes de error (scrub aplicado) | No documentado · validar org/región Sentry | Activo (prod) |
| **SMTP (actual)** | Correo transaccional vía **Gmail SMTP** (`smtp.gmail.com`) | Destinatarios, asunto y cuerpo de correos del servicio | Global (Google) · **provisional** | Activo temporal |
| **GitHub Actions** | Jobs de backup Neon→R2, uptime monitor, CI, alertas | Credenciales en secrets; volcados/backups según workflow | No documentado (infra GitHub) | Activo (operación) |

### SMTP corporativo (objetivo)

| Proveedor | Servicio | Estado |
|-----------|----------|--------|
| Por definir (`soporte@` / `contacto@` en `roustix.com`) | Correo corporativo con SPF / DKIM / DMARC | Pendiente Sprint 23.5 · sustituirá Gmail como canal definitivo |

### Compatibles / no certificados como prod actual

Amazon S3 · Backblaze B2 (ver `docs/production-storage.md`) — no listar como subencargados activos hasta uso real.

---

## Notas de tratamiento

1. **Scrubbing:** `app/observability.py` intenta limpiar eventos antes de enviarlos a Sentry; no garantiza ausencia total de PII en stack traces.  
2. **Backups:** Neon PITR + `pg_dump` hacia R2 (workflow `backup.yml`).  
3. **Cambios:** actualizar esta tabla y notificar a clientes con DPA / Enterprise cuando cambie un proveedor material.  
4. **Regiones:** completar columna «Región / país» desde las consolas antes de publicar PRIV-001 como Vigente.

---

## Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Plantilla inicial |
| **0.2.0** | 2026-08-03 | Proveedores reales del stack prod documentado |

---

*RTX-PRIV-ANX-001 · v0.2.0*
