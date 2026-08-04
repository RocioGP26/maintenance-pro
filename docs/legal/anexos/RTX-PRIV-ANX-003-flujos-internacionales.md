# RTX-PRIV-ANX-003 · Registro de Flujos Internacionales

| Campo | Valor |
|-------|-------|
| **Código** | RTX-PRIV-ANX-003 |
| **Versión** | **0.2.0** |
| **Estado** | 🟡 Borrador · confirmar países/regiones en consolas de cada proveedor |
| **Padre** | [RTX-PRIV-001](../RTX-PRIV-001-politica-privacidad.md) |
| **Fecha** | 2026-08-03 |

---

## Propósito

Registrar transferencias o transmisiones internacionales de datos personales asociadas a la operación de Roustix (Ley 1581 / Decreto 1074).

**Origen operativo habitual:** Colombia (Clientes / Usuarios · operación comercial Bogotá).

---

## Registro

| # | Destino probable | Proveedor | Categoría de datos | Finalidad | Mecanismo / garantía | País/región confirmado |
|---|------------------|-----------|--------------------|-----------|----------------------|------------------------|
| 1 | Infra cloud del host | **Render** | Cuentas, Tenants, logs de app, sesiones | Operación SaaS | Contrato proveedor + controles técnicos | **Por validar** en panel Render |
| 2 | Cloud PostgreSQL (AWS subyacente típico) | **Neon** | Base de datos completa del servicio | Persistencia y consultas | Contrato + TLS (`sslmode=require`) | **Por validar** región del proyecto Neon |
| 3 | Object storage | **Cloudflare R2** | Archivos / evidencias | Almacenamiento | Credenciales S3-compatible + ACL | **Por validar** jurisdicción Cloudflare / bucket |
| 4 | Redis gestionado | **Render Key Value** | Metadatos de rate limit / locks | Estabilidad y seguridad | Servicio del mismo proveedor de host | **Por validar** |
| 5 | Observabilidad | **Sentry** | Eventos de error / traces (posible PII residual) | Monitoreo y diagnóstico | DSN + `before_send` scrub | **Por validar** org/región Sentry |
| 6 | Correo | **Google (Gmail SMTP)** — provisional | Destinatarios y contenido transaccional | Notificaciones del servicio | SMTP TLS · cuenta temporal | Global Google · **sustituir** por correo `@roustix.com` |
| 7 | CI / backups automatizados | **GitHub Actions** | Acceso a secrets; artefacto de backup según job | Continuidad operativa | Secrets cifrados · least privilege | **Por validar** (runners GitHub) |

---

## Constancia provisional

A la fecha de este borrador **existen flujos hacia infraestructura cloud fuera de Colombia** (o con ubicación no confirmada en el repositorio). No puede declararse «sin flujos internacionales» hasta validar regiones y actualizar este registro.

Cuando se confirmen los países:

1. Completar la columna «País/región confirmado».  
2. Evaluar con asesoría jurídica el mecanismo adecuado (cláusulas contractuales, declaración, etc.).  
3. Alinear con [RTX-PRIV-ANX-001](RTX-PRIV-ANX-001-subencargados.md).

---

## Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Plantilla inicial |
| **0.2.0** | 2026-08-03 | Flujos mapeados al stack prod (regiones pendientes de consola) |

---

*RTX-PRIV-ANX-003 · v0.2.0*
