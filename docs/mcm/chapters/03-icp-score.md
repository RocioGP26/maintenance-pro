# MCM-03-ICP · Cliente ideal e ICP Score

**Código:** MCM-03-ICP · Sprint 5.3  
**Frase de marca:** Toda la operación. Una sola plataforma.

> No basta con describir al cliente ideal en abstracto.  
> Necesitamos una **herramienta** para calificar a cualquier prospecto y saber **qué tan buena oportunidad comercial** representa.

**Prerequisitos:** [MCM-01 · Posicionamiento](01-posicionamiento.md) · [MCM-02 · Propuesta de valor](02-propuesta-de-valor.md)

---

## Enfoque de este capítulo

Hasta ahora hablamos del cliente ideal en términos generales: **empresa en crecimiento**, Excel ya no alcanza, operación por encima de industria.

En este capítulo construimos el **ICP Score de Roustix** — una matriz de puntuación que permite:

- Priorizar prospectos al llegar un lead
- Enfocar demos según el perfil real
- Dirigir campañas de marketing hacia empresas con mayor probabilidad de conversión
- Informar decisiones de producto (qué dolores resolver primero)

**ICP** = quién es el cliente ideal.  
**ICP Score** = cuánto se parece *este* prospecto a ese ideal.

---

## 1 · Perfil del cliente ideal (resumen)

Roustix no vende por industria. **Vende por operación.**

| Dimensión | Cliente ideal |
|-----------|---------------|
| Tamaño | PYME en crecimiento · orientativo **10–500 empleados** |
| Madurez | Nivel 1–2 de [Madurez operativa](02-propuesta-de-valor.md) — Excel, WhatsApp, procesos manuales |
| Dolor | Información dispersa · decisiones tardías · dependencia de personas clave |
| Geografía | **Latinoamérica** |
| Entrada | **Maintenance** (activos) o **Inventory** (comercial) según prioridad |
| No es | Enterprise con consultoría de 12 meses · microempresa sin dolor operativo |

---

## 2 · ICP Score · Matriz de calificación

**Puntuación core:** hasta **100 puntos** (6 criterios positivos).

**Score neto** = core + complementarios − criterios negativos · **mínimo 0**.

Califica cada prospecto en la **primera conversación** o al recibir el lead.

### Criterios core (positivos)

| # | Criterio | Puntos | Cómo verificarlo |
|---|----------|--------|------------------|
| 1 | Usa **Excel** (o hojas de cálculo) como sistema principal de operación | **+20** | «¿Dónde llevan hoy stock, OTs o cartera?» |
| 2 | Tiene **más de una sede** o punto de operación | **+15** | «¿Operan en un solo lugar o en varios?» |
| 3 | Tiene **más de 20 empleados** | **+15** | Dato básico de calificación |
| 4 | Maneja **inventario o activos** de forma relevante para el negocio | **+20** | Bodega, planta, flota, maquinaria, catálogo comercial |
| 5 | Ya tiene **procesos definidos** (aunque sean manuales) | **+10** | «¿Tienen forma establecida de hacer X, aunque sea en papel?» |
| 6 | **Busca digitalización** activamente o reconoce que Excel ya no alcanza | **+20** | «¿Han evaluado cambiar de herramienta este año?» |

**Total core posible:** 100 puntos.

### Criterios negativos

No todos los prospectos suman. Algunos **restan** — así evitas invertir tiempo en oportunidades con pocas probabilidades de éxito.

| Criterio | Puntos | Cómo detectarlo |
|----------|--------|-----------------|
| **Solo busca precio** — sin hablar de operación ni transformación | **−15** | «¿Cuánto cuesta?» como primera y única pregunta |
| **No tiene responsable del proyecto** — nadie dueño interno del cambio | **−10** | Reunión sin gerente, dueño o líder operativo |
| Quiere desarrollo **completamente a medida** | **−20** | «Necesitamos que lo programen solo para nosotros» |
| **No utiliza procesos definidos** — operación caótica sin rutina estable | **−10** | Mutuamente excluyente con «procesos definidos +10» |

*Si aplica «procesos definidos +10», no apliques «no utiliza procesos −10».*

**Total negativo posible:** −55 puntos.

### Criterios complementarios (opcional · v1.1)

Usar cuando necesites afinar empates o priorizar dentro de la misma banda.

| Criterio | Puntos | Notas |
|----------|--------|-------|
| Gerente o dueño con **poder de decisión** en la reunión | +10 | Acelera cierre |
| Operación en **Latinoamérica** | +5 | Mercado objetivo |
| Nivel de madurez **1 o 2** (operación manual u organizada) | +10 | Encaja con transformación MCM-02 |
| Menciona **WhatsApp** como canal operativo crítico | +5 | Señal fuerte de dolor disperso |
| Ya probó otro software y **no adoptó** | +5 | Conoce el problema; necesita mejor fit |

*Los complementarios no sustituyen los core. Máximo recomendado con complementarios: 130 puntos antes de negativos.*

---

## 3 · Indicadores complementarios al score

El ICP Score mide **afinidad**. Estos tres campos miden **probabilidad y momento** de cierre — regístralos en CRM junto al score.

### Urgencia

Una empresa puede ser perfecta en afinidad pero **no comprar este año**.

| Nivel | Significado | Pregunta guía |
|-------|-------------|---------------|
| **Alta** | Necesitan resolver el dolor en semanas o meses | «¿Para cuándo necesitan tener esto funcionando?» |
| **Media** | Evaluando activamente · horizonte trimestral | «¿Están comparando opciones ahora?» |
| **Baja** | Exploración · sin fecha · «algún día» | «¿Es prioridad este año?» |

**Prioridad en CRM:** Band A + Urgencia **Alta** → tope del pipeline. Band A + Urgencia **Baja** → nurturing activo, no abandono.

### Champion

En ventas B2B casi siempre hay una persona que **impulsa el proyecto** dentro de la empresa.

| Campo | Valor |
|-------|-------|
| **Champion identificado** | ☐ Sí · ☐ No |

Ver **Champion Strength** (🟢 Fuerte · 🟡 Medio · 🔴 Débil) en [MCM-04-DMU](04-buyer-personas-dmu.md).

Sin champion, la venta suele ser **más lenta o fallar** — aunque el score sea alto. Si No: objetivo de la siguiente reunión = **identificar al champion**.

### Matriz de priorización rápida

| ICP Score | Urgencia | Champion | Prioridad pipeline |
|-----------|----------|----------|-------------------|
| A | Alta | Sí | 🔥 Máxima |
| A | Media | Sí | Alta |
| A | Baja | Sí | Seguimiento programado |
| B | Alta | Sí | Alta |
| B | cualquiera | No | Identificar champion primero |
| C / D | cualquiera | — | Nurturing o pausa |

---

## 4 · Bandas de interpretación

| Puntuación (score neto) | Banda | Significado | Acción comercial |
|-------------------------|-------|-------------|------------------|
| **80 – 100** | 🟢 **A · Prioritaria** | Prospecto muy alineado con Roustix | Respuesta en &lt;24 h · demo personalizada · trial activo desde día 1 |
| **60 – 79** | 🔵 **B · Sólida** | Buena oportunidad con algún gap | Demo estándar · trial 15 días · seguimiento semanal |
| **40 – 59** | 🟡 **C · Nurturing** | Interés real pero no es el momento ideal | Email educativo · caso de uso · recontacto en 30–60 días |
| **0 – 39** | 🔴 **D · Proceso diferente** | Bajo fit o prematuro | No priorizar ventas activas · lista de espera o derivar a partner |

### Tiempo estimado de cierre

Ayuda a planificar el pipeline comercial. Ajustar según Urgencia y Champion.

| Banda | Tiempo esperado de cierre |
|-------|---------------------------|
| **A** | **15 – 30 días** |
| **B** | **30 – 60 días** |
| **C** | **60 – 120 días** |
| **D** | Sin estimación |

*Urgencia Baja en Band A puede mover el cierre hacia el rango de B.*

### Señales de alerta (revisar aunque el score sea alto)

| Señal | Qué hacer |
|-------|-----------|
| Busca **ERP corporativo** con implementación de 6–12 meses | No es ICP · proceso diferente |
| **Menos de 5 empleados** sin dolor claro | Banda D o C — el costo de cambio puede superar el beneficio |
| Solo compara **precio** sin hablar de operación | Volver a MCM-02 (transformación) o depriorizar |
| Sin dueño/gerente involucrado | Pausar hasta tener decisor |
| No maneja inventario **ni** activos | Roustix no encaja hoy |

---

## 5 · Operational Maturity Index (OMI)

**No reemplaza el ICP Score. Lo complementa.**

| Herramienta | Mide |
|-------------|------|
| **ICP Score** | Qué tan buena oportunidad comercial es el prospecto |
| **OMI** | En qué nivel de madurez operativa está hoy — y hasta dónde puede llegar con Roustix |

Relacionado con [Madurez operativa](02-propuesta-de-valor.md) (MCM-02), pero **OMI es la métrica comercial** para CRM, demos y roadmap.

| Nivel | Estado | Señales típicas |
|-------|--------|-----------------|
| **1** | Excel | Hojas de cálculo, cuadernos, información dispersa |
| **2** | Procesos manuales | Rutinas definidas en papel o memoria — aún sin sistema |
| **3** | Digitalización parcial | Algún software o módulo aislado que no integra la operación |
| **4** | Operación integrada | Datos conectados, equipos en la misma plataforma |
| **5** | Operación basada en datos | Indicadores, alertas, decisiones con confianza en los números |

```
Nivel 1  Excel
    ↓
Nivel 2  Procesos manuales
    ↓
Nivel 3  Digitalización parcial
    ↓
Nivel 4  Operación integrada
    ↓
Nivel 5  Operación basada en datos
```

**Roustix acompaña ese recorrido** — desde Nivel 1–2 (cliente típico de entrada) hacia 3, 4 y 5 sin cambiar de plataforma.

| OMI actual | Mensaje comercial |
|------------|-------------------|
| 1–2 | «Empiezas donde estás hoy — sin consultoría de meses.» |
| 3 | «Unificamos lo que hoy está fragmentado.» |
| 4–5 | «Activas el siguiente módulo; los datos ya viven en Roustix.» |

Registrar **OMI actual** y **OMI objetivo** en cada prospecto.

---

## 6 · Puerta de entrada según el prospecto

El ICP Score no reemplaza la elección de módulo. La define el **dolor dominante**:

| Si el dolor principal es… | Puerta | Puntos de demo MUX |
|---------------------------|--------|---------------------|
| Activos, OTs, planta, disponibilidad | **Roustix Maintenance** | Laura + Carlos |
| Stock, ventas, cartera, compras | **Roustix Inventory** | Valentina + Roberto |
| Ambos con igual urgencia | Empezar por el más doloroso · segundo módulo en expansión | Combinar perfiles |

**Regla:** un prospecto Band A con Inventory no recibe demo de Maintenance solo porque «tenemos ese módulo».

---

## 7 · Cómo usar el ICP Score

### Ventas

1. Recibir lead → aplicar matriz en **5 minutos** (formulario, llamada corta o CRM)
2. Calcular **score neto** · asignar banda A/B/C/D
3. Registrar **Urgencia**, **Champion** y **OMI**
4. Estimar **tiempo de cierre** según banda
5. Elegir puerta de entrada y perfil MUX para la demo
6. Registrar todo en CRM para medir conversión por banda

**Meta v1:** los cierres deben concentrarse en bandas **A y B**. Si cierras mucho en D, el mensaje o el canal están mal.

### Demostraciones

| Banda | Enfoque demo |
|-------|--------------|
| A | Transformación MCM-02 + trial inmediato · 2 criterios con más puntos del prospecto |
| B | Demo 20 min estándar · un antes/después + puerta correcta |
| C | Video o demo grupal · educación antes de producto |
| D | No demo individual · material self-service |

### Marketing

| Banda objetivo | Canal sugerido |
|----------------|----------------|
| A y B | LinkedIn · referidos · contenido «Excel ya no alcanza» |
| C | Webinars · email nurturing · casos de éxito |
| D | No invertir CAC alto |

**Copy alineado a criterios con más peso:** Excel (+20), inventario/activos (+20), digitalización (+20).

### Producto

El ICP Score también informa desarrollo:

| Criterio frecuente en prospectos A | Implicación producto |
|-----------------------------------|----------------------|
| Excel como sistema principal | Importación Excel impecable · onboarding rápido |
| Multi-sede | Reportes por sede · permisos por ubicación |
| +20 empleados | Roles MUX · multi-usuario estable |
| Inventario o activos | Profundizar módulo de entrada según puerta |
| Procesos definidos | Plantillas y flujos preconfigurados |
| Busca digitalización | Trial 15 días sin fricción · TTFAV &lt;3 min (MUX) |

---

## 8 · Ficha rápida de calificación

Copiar en CRM, Notion o hoja de reunión:

```
Prospecto: _______________________
Fecha: ___________________________
Calificado por: ___________________

CRITERIOS CORE (positivos)              SÍ    PUNTOS
[ ] Excel como sistema principal        ___   +20
[ ] Más de una sede                     ___   +15
[ ] Más de 20 empleados                 ___   +15
[ ] Maneja inventario o activos         ___   +20
[ ] Procesos definidos                  ___   +10
[ ] Busca digitalización                ___   +20
                              Subtotal: ___

CRITERIOS NEGATIVOS                     SÍ    PUNTOS
[ ] Solo busca precio                   ___   -15
[ ] Sin responsable del proyecto        ___   -10
[ ] Quiere desarrollo a medida          ___   -20
[ ] No utiliza procesos definidos       ___   -10
                              Negativo: ___

                         SCORE NETO: ___ / 100 (mín. 0)

Banda: [ ] A  [ ] B  [ ] C  [ ] D
Tiempo cierre est.: _______________
Urgencia: [ ] Alta  [ ] Media  [ ] Baja
Champion: [ ] Sí  [ ] No
Champion Strength: [ ] 🟢 Fuerte  [ ] 🟡 Medio  [ ] 🔴 Débil
OMI actual: [ ] 1  [ ] 2  [ ] 3  [ ] 4  [ ] 5
OMI objetivo: ___
Puerta: [ ] Maintenance  [ ] Inventory
Perfil MUX demo: _________________
Próxima acción: __________________
```

---

## 9 · Ejemplos de calificación

### Ejemplo 1 · Tornillería · Band A (95 pts)

| Criterio | ¿Aplica? | Puntos |
|----------|----------|--------|
| Excel principal | Sí — stock y ventas | +20 |
| Multi-sede | Sí — bodega + mostrador | +15 |
| +20 empleados | Sí — 35 | +15 |
| Inventario o activos | Sí — inventario comercial | +20 |
| Procesos definidos | Sí — recepción y despacho | +10 |
| Busca digitalización | Sí — «Excel ya no da» | +20 |
| **Total** | | **100** |

→ Demo **Inventory** · Urgencia **Alta** · Champion **Sí** (dueño) · OMI 1→3 · cierre **15–30 días**.

---

### Ejemplo 2 · Fábrica mediana · Band B (75 pts neto)

| Criterio | ¿Aplica? | Puntos |
|----------|----------|--------|
| Excel principal | Sí | +20 |
| Multi-sede | No — una planta | 0 |
| +20 empleados | Sí — 48 | +15 |
| Inventario o activos | Sí — activos y repuestos | +20 |
| Procesos definidos | Sí — OT en papel | +10 |
| Busca digitalización | Parcial — «evaluando opciones» | +10* |
| **Total** | | **75** |

*Ajuste honesto si el interés en digitalizar no es activo aún: +10 en lugar de +20.*

→ Demo **Maintenance** · Urgencia **Media** · Champion **Sí** (jefe de planta) · OMI 2→4 · cierre **30–60 días**.

---

### Ejemplo 3 · Micro comercio · Band D (25 pts neto)

| Criterio | ¿Aplica? | Puntos |
|----------|----------|--------|
| Excel principal | Sí | +20 |
| Multi-sede | No | 0 |
| +20 empleados | No — 8 personas | 0 |
| Inventario o activos | Sí — stock básico | +20 |
| Procesos definidos | No | 0 |
| Busca digitalización | No — «solo preguntando precio» | 0 |
| Solo busca precio | Sí | **−15** |
| **Total neto** | | **25** |

→ Band **D** · Urgencia **Baja** · Champion **No** · sin estimación de cierre · material self-service.

---

### Ejemplo 4 · Score alto con alertas · Band B (70 pts neto)

| Criterio | ¿Aplica? | Puntos |
|----------|----------|--------|
| Core positivos | Varios | +90 |
| Quiere desarrollo a medida | Sí | **−20** |
| **Total neto** | | **70** |

→ Afinidad alta pero **proceso diferente** en expectativas · reencuadrar hacia SaaS modular o depriorizar.

---

## Conexión con capítulos anteriores

| Capítulo | Aporta al ICP Score |
|----------|-------------------|
| MCM-01 | Quién es el cliente ideal · puertas de entrada |
| MCM-02 | Madurez operativa · transformaciones · preguntas de descubrimiento |
| MCM-03 | **ICP Score + OMI + Urgencia + Champion** — de teoría a pipeline |

---

> **Frase del capítulo:** El ICP Score convierte la intuición comercial en **criterio compartido**. Todo el equipo — ventas, marketing y producto — prioriza con la misma brújula.

**Próximo capítulo:** MCM-04 · Buyer Personas y DMU (Sprint 5.4)

---

*MCM-03 · Roustix Commercial Manual · 2026*
