# COM-01 · Planes y Licenciamiento Roustix

| Campo | Valor |
|-------|-------|
| **Código** | COM-01 |
| **Versión** | **1.4.0** |
| **Estado** | ✅ Estrategia comercial vigente |
| **Vigencia** | 2026-08-09 |
| **Moneda** | COP |
| **Fuente** | `PLANES_SEED` · [MCM-04](../mcm/chapters/04-planes-saas.md) |

> Start / Business publican precio. Enterprise: contactar.  
> **Almacenamiento año 1 (conservador):** 1 GB · 5 GB · 20 GB ampliables.

---

## 1 · Matriz oficial

| Característica | Start | Business | Enterprise |
|----------------|------:|---------:|------------|
| **Precio mensual** | **$1.000.000** | **$1.500.000** | Desde $2.500.000 *(interno)* |
| **Usuarios** | 20 | 50 | Personalizado |
| **Sedes** | 1 | 3 | Personalizadas |
| **Módulos** | 1 principal a elegir | Hasta 2 principales | Todos disponibles |
| **Activos** | Ilimitados | Ilimitados | Ilimitados |
| **Almacenamiento** | **1 GB** | **5 GB** | **20 GB ampliables** |
| **Soporte** | Email | Chat | Dedicado |

```
Start  →  Business  →  Enterprise
```

### Por qué estos cupos de storage (año 1)

La capacidad contratada se controla por tenant y la infraestructura debe
escalar conforme crezca el almacenamiento comercial comprometido.

| Escenario | Consumo teórico incluido |
|-----------|--------------------------|
| 5 clientes Start | 5 GB |
| 2 clientes Business | 2 × 5 GB = 10 GB |
| 1 cliente Enterprise | Desde 20 GB · validar capacidad antes de activar |

La capacidad disponible se revisa antes de activar planes Enterprise o
ampliaciones relevantes. Es más fácil **aumentar** cupos en 6–12 meses que
reducir beneficios ya contratados.

Complemento comercial: **+2 GB · $100.000/mes** ([COM-02](COM-02-servicios-adicionales.md)).

---

## 2 · Roadmap · Versión 2 de storage *(ingresos estables)*

| Plan | Storage v2 (anunciar como mejora) |
|------|-----------------------------------|
| Start | 2 GB |
| Business | 10 GB |
| Enterprise | 50 GB |

No reducir los cupos vigentes de COM-01 v1.4.0; solo ampliar y comunicar como
beneficio.

---

## 3 · Uso dinámico (producto)

| Capacidad | Estado |
|-----------|--------|
| Medición por tenant | ✅ SuperAdmin (barra uso / cuota) |
| Alerta ≥ 80% | ✅ Panel plataforma · oferta +2 GB |
| Alerta en portal cliente | ✅ Banner admin (≥80%) + barra en Configuración empresa · mismo umbral · CTA +2 GB |
| Monitor BD + R2 + servicios | ✅ `/platform/infraestructura` |

---

## 4 · Precios y publicación

| Plan | Mensual | Landing |
|------|--------:|---------|
| Start | 1.000.000 | ✅ Visible |
| Business | 1.500.000 | ✅ Visible |
| Enterprise | 2.500.000 *(piso)* | ❌ Contactar |

---

## 5 · Todos los planes incluyen

Plataforma SaaS · actualizaciones · backups · HTTPS · roles · auditoría · BD por empresa · multi-dispositivo · soporte según plan.

---

## 6 · Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **1.4.0** | 2026-08-09 | Oferta comercial general; retirado el enfoque y límite del piloto |
| **1.3.2** | 2026-07-29 | Storage año 1: 1 / 5 / 20 GB · roadmap v2 · monitor infra |
| **1.3.1** | 2026-07-29 | Business · Enterprise sin precio público |
| **1.3.0** | 2026-07-29 | Precios 1M / 1.5M / desde 2.5M |

---

*COM-01 · v1.4.0 · 2026*
