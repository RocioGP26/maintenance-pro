# MCM · Nomenclatura de documentos

Códigos oficiales para búsqueda y mantenimiento del manual comercial.

| Código | Capítulo | Archivo |
|--------|----------|---------|
| **MCM-01-POS** | Posicionamiento | [chapters/01-posicionamiento.md](chapters/01-posicionamiento.md) |
| **MCM-02-VALUE** | Propuesta de valor | [chapters/02-propuesta-de-valor.md](chapters/02-propuesta-de-valor.md) |
| **MCM-03-ICP** | Cliente ideal e ICP Score | [chapters/03-icp-score.md](chapters/03-icp-score.md) |
| **MCM-04-DMU** | Buyer Personas y DMU | [chapters/04-buyer-personas-dmu.md](chapters/04-buyer-personas-dmu.md) |
| **MCM-05-SECT** | Sectores | [chapters/05-sectores.md](chapters/05-sectores.md) |
| **MCM-06-PLAN** | Planes comerciales | [chapters/06-planes-comerciales.md](chapters/06-planes-comerciales.md) |
| **MCM-07-DEMO** | La demo comercial | [chapters/07-demo-comercial.md](chapters/07-demo-comercial.md) |
| **MCM-08-OBJ** | Objeciones | [chapters/08-objeciones.md](chapters/08-objeciones.md) |
| **MCM-09-CASE** | Casos de éxito | [chapters/09-casos-exito.md](chapters/09-casos-exito.md) |
| **MCM-10-GTM** | Go To Market | [chapters/10-gtm.md](chapters/10-gtm.md) |

Formato: `MCM-{NN}-{SLUG}` · Sprint 5.{N} · **Sprint 5 completo**

---

## Playbook · Códigos PLAY

Códigos internos del **playbook de demo** (MCM-07-DEMO). Permiten referenciar fases sin citar capítulos completos.

```
MCM-07-DEMO
│
├── PLAY-001 · Preparación
├── PLAY-002 · Apertura
├── PLAY-003 · Operación
├── PLAY-004 · KPIs
└── PLAY-005 · Cierre
```

| Código | Fase | Tiempo | Capítulo |
|--------|------|--------|----------|
| **PLAY-001** | Preparación | Antes de reunión | [07-demo-comercial.md](chapters/07-demo-comercial.md#play-001--preparación) |
| **PLAY-002** | Apertura | 3 min | [07-demo-comercial.md](chapters/07-demo-comercial.md#play-002--apertura-3-minutos) |
| **PLAY-003** | Operación | 10–15 min | [07-demo-comercial.md](chapters/07-demo-comercial.md#play-003--operación-1015-minutos) |
| **PLAY-004** | KPIs | 3 min | [07-demo-comercial.md](chapters/07-demo-comercial.md#play-004--kpis-3-minutos) |
| **PLAY-005** | Cierre | 5 min | [07-demo-comercial.md](chapters/07-demo-comercial.md#play-005--cierre-5-minutos) |

Formato: `PLAY-{NNN}` · pertenece a **MCM-07-DEMO**

**Ejemplo de uso:** *«Revisa PLAY-003 antes de hacer la demo.»* en lugar de *«Lee el capítulo 7.»*

---

## Objeciones · Códigos OBJ

Códigos de **fichas de objeción** (MCM-08-OBJ).

| Código | Objeción | Riesgo | Mejor responde | Momento |
|--------|----------|--------|----------------|---------|
| **OBJ-001** | Es muy caro | 🟡 | Comercial | Cierre |
| **OBJ-002** | No tenemos tiempo | 🟡 | Comercial | Calificación |
| **OBJ-003** | Queremos a medida | 🔴 | Comercial + Producto | Discovery |
| **OBJ-004** | No lo van a usar | 🟢 | Comercial | Demo |
| **OBJ-005** | Excel nos funciona | 🟡 | Comercial | Apertura |
| **OBJ-006** | Más cotizaciones | 🟢 | Comercial | Cierre |
| **OBJ-007** | ¿Y si desaparecen? | 🔴 | Fundador / Com. Senior | Follow-up |
| **OBJ-008** | Sector muy específico | 🟡 | Comercial | Apertura |
| **OBJ-009** | No es prioridad | 🟡 | Comercial | Calificación |
| **OBJ-010** | ¿Integran con ERP? | 🟢 | Preventa / TI | Post-demo |

Formato: `OBJ-{NNN}` · pertenece a **MCM-08-OBJ**

**Ejemplo de uso:** *«En el debrief salió OBJ-004 — revisa la ficha antes del follow-up.»*

---

## Casos · Códigos MTX-CASE

Códigos de **casos de transformación** (MCM-09-CASE). Hoy: narrativas genéricas por sector. Mañana: mismos códigos con cliente real.

| Código | Sector | Evidencia | Empleados ref. | País ref. |
|--------|--------|-----------|----------------|-----------|
| **MTX-CASE-001** | Manufactura | D | 40–80 | Colombia |
| **MTX-CASE-002** | Comercio | D | 20–50 | LatAm |
| **MTX-CASE-003** | Agropecuaria | D | 30–70 | LatAm |
| **MTX-CASE-004** | Servicios | D | 25–60 | LatAm |
| **MTX-CASE-005** | Distribución | D | 40–100 | LatAm |
| **MTX-CASE-006** | Operación mixta | D | 50–120 | LatAm |

### Nivel de evidencia (por caso)

| Nivel | Estado |
|-------|--------|
| **A** | Cliente documentado + métricas + cita |
| **B** | Cliente documentado sin cifras públicas |
| **C** | Caso validado internamente |
| **D** | Caso genérico |

Campos adicionales por caso: **fecha publicación** · **cross references** (OBJ · MCM · PLAY · Landing · Folleto).

Formato: `MTX-CASE-{NNN}` · pertenece a **MCM-09-CASE**

**Ejemplo de uso:** *«Usa MTX-CASE-002 en OBJ-001 para comercio.»*
