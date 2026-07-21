# MPA-02-ECO · Ecosistema Roustix

**Código:** MPA-02-ECO · Sprint 6.2

> Mapa oficial de producto. No es un diagrama de marketing: es la **taxonomía** que el equipo usa para nombrar módulos, priorizar roadmap y evitar duplicar capacidades.

---

## 1 · Vista general

```
                 ROUSTIX

          Enterprise Platform
                    │
    ────────────────────────────────────
    │                                  │
 Maintenance    Inventory         (hoy)
    │                                  │
    └──────────┬───────────────────────┘
               │
    ────────────────────────────────────
    Purchasing · CRM · Sales · Finance
    BI · IAM · AI · API · Mobile
    ────────────────────────────────────
```

**Regla:** todo lo que aparece en este mapa es un **módulo o capacidad de plataforma**, no un producto con marca propia.

---

## 2 · Capas del ecosistema

| Capa | Qué es | Ejemplos |
|------|--------|----------|
| **Plataforma** | Núcleo compartido por todos los tenants | Tenancy, auth, planes, onboarding, dashboard base |
| **Módulos operativos** | Dominios de negocio activables | Maintenance, Inventory, Purchasing… |
| **Capacidades transversales** | Servicios que cruzan módulos | PDF, Excel, correo, auditoría, KPIs |
| **Canales** | Cómo accede el usuario | Web app · API · Mobile (futuro) |
| **Inteligencia** | Análisis y asistencia | BI, Analytics, AI Assistant (futuro) |

---

## 3 · Módulos · Estado actual

| Módulo | Clave técnica | Blueprint / área | Estado |
|--------|---------------|------------------|--------|
| **Maintenance** | `mantenimiento` | `main.*` | ✅ Producción |
| **Inventory** | `inventario` | `inv_comercial.*` | ✅ Producción |
| **Purchasing** | — | — | 📋 Planificado |
| **CRM** | — | — | 📋 Planificado |
| **Sales** | — | parcial en Inventory | 🟡 Evolución a Sales Pro |
| **Finance** | — | — | 📋 Planificado |
| **BI / Analytics** | — | dashboards actuales | 🟡 KPIs por módulo hoy |

### Maintenance · capacidades hoy

- Activos (`machines`) con tipos y campos personalizados por sector
- Órdenes de trabajo (correctivas, preventivas)
- Calendario y planeación preventiva
- Inventario técnico de repuestos
- Proveedores de servicio
- Incidencias y reportes
- Dashboard con KPIs operativos

### Inventory · capacidades hoy

- Catálogo de productos y ubicaciones
- Compras a proveedores comerciales
- Ventas y clientes
- Cuentas por pagar
- Importación / exportación Excel
- Dashboard comercial

---

## 4 · Capacidades de plataforma (no módulos)

| Capacidad | Estado | Referencia |
|-----------|--------|------------|
| **IAM** | Roles por empresa + superadmin plataforma | MPA-04-SAAS |
| **API** | JWT tenancy API · admin API | MAG (07) |
| **Mobile** | — | Roadmap 2030 |
| **AI** | — | Roadmap 2030 |
| **Marketplace** | — | Largo plazo |

---

## 5 · Sectores vs módulos

**Los sectores no son módulos.** Son **plantillas de configuración** sobre la misma plataforma:

- Categorías de activo por sector (`sector_templates.py`)
- Campos personalizados (`campos_personalizados`)
- KPIs y dashboard JSON (`plantillas_dashboard`)

Sectores disponibles hoy: `comercio`, `manufactura`, `logistica`, `salud`, `mineria`, `alimentos`, `construccion`, `educacion`.

→ Detalle técnico: [arquitectura-sectores.md](../../arquitectura-sectores.md)  
→ Narrativa comercial: [MCM-05-SECT](/mcm/chapters/05-sectores.md)

---

## 6 · Documentación alineada al ecosistema

| Pilar | Doc | Pregunta que responde |
|-------|-----|----------------------|
| Marca | MBB (01) | ¿Quiénes somos? |
| Diseño | MDL (02) | ¿Cómo se ve? |
| Experiencia | MUX (03) | ¿Cómo se usa? |
| Comercial | MCM (04) | ¿Cómo se vende? |
| **Plataforma** | **MPA (05)** | **¿Cómo está construido?** |
| Reportes | MRL (06) | ¿Cómo se imprime? |
| API | MAG (07) | ¿Cómo se integra? |

---

## Siguiente

→ [MPA-03-MOD · Arquitectura modular](03-arquitectura-modular.md)
