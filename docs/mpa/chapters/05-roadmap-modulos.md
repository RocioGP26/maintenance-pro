# MPA-05-ROAD · Roadmap de módulos

**Código:** MPA-05-ROAD · Sprint 6.5

> El futuro de Roustix **como plataforma**, no como lista de features sueltas. Cada módulo nuevo debe encajar en el stack Tenant → Módulos → Permisos → Datos → Dashboards.

---

## 1 · Hoy · Producción

| Módulo | Clave | Entrada típica |
|--------|-------|----------------|
| ✅ **Maintenance** | `mantenimiento` | Manufactura, logística, salud, plantas |
| ✅ **Inventory** | `inventario` | Comercio, retail, distribución, agro |
| ✅ **Purchasing** | `purchasing` | Abastecimiento, recepción y CxP |

**Capacidades transversales activas:** tenancy, roles, onboarding sectorial, dashboards, reportes PDF, import/export Excel (Inventory), auditoría plataforma, backups.

---

## 2 · Próximo · 12–18 meses

| Módulo | Propósito | Dependencias |
|--------|-----------|--------------|
| **Maintenance Execution** | Sprint 19 ✅ · procedimientos, checklist, evidencia, bitácora y medidores | Maintenance, MRG, MUX |
| **Maintenance Automation** | Sprint 20 ✅ · disparadores por lecturas, avisos y creación gobernada de OT | Maintenance Execution, IAM |
| **Asset Health** | Sprint 21 ✅ · puntaje explicable, confianza, señales e historial | Maintenance Execution, Automation |
| **API pública y Webhooks** | Sprint 22.0–22.5 ✅ completo | MAG, tenancy, IAM, planes |
| **CRM** | Clientes, pipeline, seguimiento comercial | Inventory |
| **Sales Pro** | Cotizaciones, pedidos, facturación ligera | Inventory, CRM |
| **Analytics** | KPIs cruzados, tendencias, export BI | Datos de todos los módulos activos |

### Criterios para priorizar

1. ¿Resuelve dolor de operación ya validado en MCM?
2. ¿Reutiliza tenancy y permisos existentes?
3. ¿Se puede activar por módulo sin romper tenants actuales?
4. ¿Tiene puerta de entrada clara en comercial (MCM-05)?

---

## 3 · Medio plazo

| Módulo / capacidad | Descripción |
|--------------------|-------------|
| **Finance** | CxC/CxP consolidado, conciliación, centros de costo |
| **IAM avanzado** | SSO, SCIM, políticas por sede |
| **Webhooks** | Sprint 22 · outbox, firma HMAC, entregas y reintentos |
| **API pública** | Sprint 22 · credenciales, scopes y contratos estables MAG |

---

## 4 · Largo plazo

| Módulo / capacidad | Descripción |
|--------------------|-------------|
| **Marketplace** | Módulos o integraciones de terceros |
| **AI Assistant** | Consultas operativas, sugerencias preventivas |
| **Mobile** | App nativa o PWA offline-first para técnicos y vendedores |
| **Integraciones ERP** | Conectores SAP, Siigo, Alegra, etc. |

---

## 5 · Lo que no haremos

| Anti-roadmap | Por qué |
|--------------|---------|
| Fork por país | Un código, configuración por tenant |
| Producto separado «Roustix CMMS» | Maintenance es módulo |
| ERP monolítico en un sprint | Finance llega cuando la operación esté consolidada |
| Features sin módulo definido | Todo entra en el mapa MPA-02 |

---

## 6 · Relación con planes comerciales

| Plan (MCM-06) | Módulos típicos |
|---------------|-----------------|
| Start | 1 módulo (Maintenance **o** Inventory) |
| Grow | 2+ módulos |
| Scale | Todos los disponibles + límites enterprise |

Los módulos futuros se **añaden al catálogo**, no a planes nuevos con otra marca.

---

## Siguiente

→ [MPA-06-INT · Integraciones](06-integraciones.md)  
→ Visión extendida: [MPA-10-2030](10-roadmap-2030.md)
