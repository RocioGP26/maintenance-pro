# MCM · Decisiones estratégicas (fundación comercial)

Documento de referencia para todos los capítulos MCM.  
**Aprobado:** Sprint 5 · Capítulo 1 · 2026-07-10

---

## Modelo de negocio

| Decisión | Valor |
|----------|-------|
| Modelo | **SaaS por suscripción mensual** |
| Alcance | Aplica a **todos** los tipos de cliente |
| Prueba gratuita | **15 días** sin compromiso |
| Mercado | **Latinoamérica** desde el primer día |

Mensaje landing: *«Comienza hoy. Prueba Maintix durante 15 días sin compromiso.»*

---

## Dos puertas de entrada · Una plataforma

| Puerta | Para quién |
|--------|------------|
| **Maintix Maintenance** | Prioridad: gestión de activos y mantenimiento |
| **Maintix Inventory** | Prioridad: control comercial e inventarios |

**Ambas puertas conducen a la misma plataforma.**

**Comparten la misma plataforma:** usuarios, autenticación, dashboard, reportes, configuración, SuperAdmin, facturación SaaS.

El cliente activa el módulo según su necesidad. Mañana incorpora más **sin migrar de sistema**.

**Cliente ideal:** empresas **en crecimiento** — no gigantes ni micro; las que sienten que Excel ya no alcanza.

---

## Origen auténtico (no cambiar por narrativa corporativa)

### Problema 1 · Mantenimiento (Colombia)

Experiencia en entorno industrial (INR): activos, OT, preventivos, disponibilidad, indicadores.  
→ Nació el **módulo de Mantenimiento**.

### Problema 2 · Inventario (Venezuela)

Dos negocios familiares (agropecuaria y tornillería): mismo dolor — stock, compras, ventas, cartera, sin control unificado.  
→ Nació el **módulo de Inventario Comercial**.

**Conclusión comercial:** Maintix no vende por industria. **Vende por operación.**  
El ICP no es un sector — es cualquier empresa que necesita **controlar su operación diaria**.

---

## Respuesta oficial «¿Por qué desarrollaron Maintix?»

> Porque vimos el mismo problema en dos empresas, en dos países y en sectores completamente diferentes. El verdadero desafío no era solo el mantenimiento ni solo el inventario: era la **falta de control sobre la operación**. Construimos una sola plataforma para resolver ambos.

---

## ICP Score (MCM-03)

**Score neto** = criterios positivos (hasta 100) − criterios negativos (hasta −55) · mínimo 0.

| Positivo | Pts | Negativo | Pts |
|----------|-----|----------|-----|
| Excel principal | +20 | Solo busca precio | −15 |
| Multi-sede | +15 | Sin responsable proyecto | −10 |
| +20 empleados | +15 | Desarrollo a medida | −20 |
| Inventario o activos | +20 | Sin procesos definidos | −10 |
| Procesos definidos | +10 | | |
| Busca digitalización | +20 | | |

**Bandas:** A (80–100) · B (60–79) · C (40–59) · D (0–39)  
**Cierre:** A 15–30 d · B 30–60 d · C 60–120 d · D sin estimación  
**CRM:** Urgencia (Alta/Media/Baja) · Champion (Sí/No) · **OMI** (1–5)

Ver [chapters/03-icp-score.md](chapters/03-icp-score.md)

---

## Buyer Personas y DMU (MCM-04-DMU)

| Concepto | Definición |
|----------|------------|
| **Buyer Persona** | Evalúa, recomienda o usa Maintix (MUX) |
| **DMU** | Conjunto que participa en la compra |
| **Influencia** | Gerente ⭐⭐⭐⭐⭐ → Bodega ⭐ |
| **Riesgo** | Bloqueadores: Finanzas, TI, Compras |
| **Champion Strength** | 🟢 Fuerte · 🟡 Medio · 🔴 Débil |

Ver [chapters/04-buyer-personas-dmu.md](chapters/04-buyer-personas-dmu.md) · [NOMENCLATURE.md](NOMENCLATURE.md)

---

## Sectores (MCM-05-SECT)

Patrón de **6 bloques** por sector: problema · puerta · transformación · KPIs · historia demo.

Sectores v1: Manufactura · Comercio · Agro · Servicios · Distribución · Operación mixta.

Por sector: madurez digital · prioridad KPIs · tiempo impl. · módulos futuros.

**Pilar de marca · Crecimiento** (Landing · MCM · Folleto · Demo · Bienvenida): *La transformación comienza con un módulo. El crecimiento ocurre dentro de una sola plataforma.*

Ver [chapters/05-sectores.md](chapters/05-sectores.md) · [materials/folleto-comercial.md](materials/folleto-comercial.md) · [materials/pilar-crecimiento.md](materials/pilar-crecimiento.md)

---

## Planes comerciales (MCM-06-PLAN)

**Filosofía:** hoja de ruta por etapa — no tabla de features quitadas.

| Plan | Perfil ideal | Resultado esperado |
|------|--------------|-------------------|
| **Start** | Reemplaza Excel | Digitalizado en &lt; 1 semana |
| **Grow** | Ya digitalizó una parte | Unificar módulos en una plataforma |
| **Scale** | Varias sedes | Control multisede centralizado |
| **Enterprise** | Procesos complejos | Plataforma central de operación |

**Qué no cambia:** misma plataforma, MUX, MDL y arquitectura — solo cambia la capacidad de acompañar el crecimiento.

Ver [chapters/06-planes-comerciales.md](chapters/06-planes-comerciales.md)

---

## Demo comercial (MCM-07-DEMO)

**Filosofía:** experiencia repetible — no listado de pantallas.

| Código | Fase | Tiempo |
|--------|------|--------|
| PLAY-001 | Preparación | Antes |
| PLAY-002 | Apertura | 3 min |
| PLAY-003 | Operación | 10–15 min |
| PLAY-004 | KPIs | 3 min |
| PLAY-005 | Cierre | 5 min |

**Exit Criteria:** demo exitosa = ≥1 acción con evidencia (trial, segunda reunión, champion, etc.).

**Debrief:** 24 h post-demo — qué funcionó, objeciones, próxima PLAY-003.

Ver [chapters/07-demo-comercial.md](chapters/07-demo-comercial.md) · [NOMENCLATURE.md](NOMENCLATURE.md#playbook--códigos-play)

---

## Objeciones (MCM-08-OBJ)

**Filosofía:** entender el riesgo de fondo — no memorizar respuestas.

Plantilla por ficha: objeción · **riesgo** · **quién responde** · **momento típico** · guion · evidencia · error · siguiente pregunta.

Códigos **OBJ-001** a **OBJ-010** (precio, tiempo, riesgo, confianza, proceso, técnico).

Alimentado por **Debrief** MCM-07.

Ver [chapters/08-objeciones.md](chapters/08-objeciones.md) · [NOMENCLATURE.md](NOMENCLATURE.md#objeciones--códigos-obj)

---

## Casos de éxito (MCM-09-CASE)

**Filosofía:** casos de **transformación** — no testimonios inventados hasta tener clientes reales.

Estructura **MTX-CASE**: Antes · Después · KPIs · Historia · **evidencia A–D** · fecha · matching · **cross refs**.

Migración: reemplazar genérico por cliente documentado **sin cambiar la ficha**.

Ver [chapters/09-casos-exito.md](chapters/09-casos-exito.md) · [NOMENCLATURE.md](NOMENCLATURE.md#casos--códigos-mtx-case)

---

## Go To Market (MCM-10-GTM)

**Puente** entre el MCM y el lanzamiento real.

| Sección | Contenido |
|---------|-----------|
| Mercado inicial | LatAm · Colombia · Venezuela |
| Puertas | Maintenance · Inventory |
| Canales | Landing · contenido · demos · referidos · alianzas |
| Embudo | Visitante → Lead → ICP → Demo → Trial → Cliente → Expansión |
| KPIs | CAC · conversiones · activación · retención · expansión |
| Ciclo | Cliente → Caso → Referido → Nuevo cliente |

Ver [chapters/10-gtm.md](chapters/10-gtm.md)

---

**Sprint 5 · Maintix Commercial Manual — completo.**

## Propuesta de valor (MCM-02)

**Pregunta central:** ¿Qué cambia en la vida de una empresa después de implementar Maintix?

No frases de marketing — **transformación** en seis dimensiones: certeza, anticipación, flujo, crecimiento, gobernanza, procesos.

Concepto **Madurez operativa** (Niveles 1–5). Infografía futura para landing.

Ver [chapters/02-propuesta-de-valor.md](chapters/02-propuesta-de-valor.md)

---

Ver [chapters/01-posicionamiento.md](chapters/01-posicionamiento.md)
