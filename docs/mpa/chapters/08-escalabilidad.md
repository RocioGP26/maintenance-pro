# MPA-08-SCALE · Escalabilidad

**Código:** MPA-08-SCALE · Sprint 6.8

> Cómo Roustix puede crecer de **10 usuarios a 10.000 empresas** sin reescribir la plataforma.

---

## 1 · Dimensiones de escala

| Dimensión | Pregunta |
|-----------|----------|
| **Usuarios** | ¿Cuántas personas usan la app simultáneamente? |
| **Tenants** | ¿Cuántas empresas en la misma instancia? |
| **Datos** | ¿Cuántos activos, productos, OT por tenant? |
| **Módulos** | ¿Cuántos dominios activos por empresa? |
| **Geografía** | ¿LatAm multi-país, zonas horarias? |

---

## 2 · Escenarios de referencia

### Usuarios concurrentes (una empresa)

| Escala | Perfil | Infraestructura |
|--------|--------|-----------------|
| **10** | PyME, 1 sede | App single instance · DB compartida |
| **100** | Mediana, varias sedes | Connection pooling · índices por `empresa_id` |
| **1 000** | Enterprise tenant | Read replicas · cache KPIs · colas async |

### Empresas en plataforma

| Escala | Perfil | Enfoque |
|--------|--------|---------|
| **100 empresas** | Early SaaS | Monolito modular bien indexado |
| **1 000** | Growth | Particionar jobs pesados (reportes, imports) |
| **10 000** | Scale | Evaluar sharding por tenant tier, CDN estáticos |

---

## 3 · Palancas técnicas actuales

| Palanca | Estado |
|---------|--------|
| Multi-tenant lógico | ✅ |
| PostgreSQL (Neon) en producción | ✅ |
| Índices en `empresa_id` | ✅ En modelos principales |
| Stateless app (sesión/JWT) | ✅ Horizontal scaling ready |
| Cache de dashboards | 🟡 Evolución |
| Cola de trabajos (Celery/RQ) | 📋 Para imports y reportes pesados |

---

## 4 · Cuellos de botella previsibles

| Área | Riesgo | Mitigación |
|------|--------|------------|
| Dashboard KPIs | Queries agregadas pesadas | Materializar KPIs · cache TTL |
| Import Excel | CPU y memoria en request | Job async + notificación |
| Reportes PDF | Bloqueo de worker | Cola dedicada |
| Listados sin paginar | O(n) en tablas grandes | Paginación obligatoria (MUX) |

---

## 5 · Escalabilidad organizacional

La plataforma también escala **equipo de desarrollo**:

| Práctica | Beneficio |
|----------|-----------|
| MPA como handbook | Onboarding técnico en días, no meses |
| MUX Laws | Calidad consistente sin revisión heroica |
| MDL | UI uniforme sin debates por pantalla |
| Módulos acotados | Equipos pueden ownership por dominio |

---

## 6 · Límites por plan

Los planes comerciales (`CatalogoPlan`) son el primer **throttle** de escala:

- Máximo de activos / usuarios / storage
- Upgrade de plan antes de optimización infra

Esto protege la plataforma en etapa growth.

---

## Siguiente

→ [MPA-09-PHIL · Filosofía técnica](09-filosofia-tecnica.md)
