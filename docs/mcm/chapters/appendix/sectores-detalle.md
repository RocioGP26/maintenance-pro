# MCM-05-SECT · Sectores (detalle extendido)

> ⚠️ **Apéndice Sprint 5** — Matrices KPI · historias de demo · madurez digital. Capítulo principal: [MCM-03-MARKETS](../03-sectores-mercados.md).

**Código:** MCM-05-SECT · Sprint 5.5 *(legacy)*
**Frase de marca:** Toda la operación. Una sola plataforma.

> Roustix **no vende por industria** — vende por operación.
> Pero el vendedor **sí necesita hablar el idioma del sector** del prospecto.

**Prerequisitos:** [MCM-01-POS](01-posicionamiento.md) · [MCM-02-VALUE](02-propuesta-de-valor.md) · [MCM-03-ICP](03-icp-score.md) · [MCM-04-DMU](04-buyer-personas-dmu.md)

---

## Enfoque de este capítulo

Este capítulo puede convertirse en una de las **mayores ventajas competitivas** de Roustix: no listamos sectores como etiquetas vacías.

Cada sector sigue el **mismo patrón de seis bloques** — un guion que cualquier vendedor adapta en minutos y que cualquier sector nuevo replica en el futuro.

| Sección | Contenido |
|---------|-----------|
| **Sector** | Manufactura, Comercio, Servicios, Agro, etc. |
| **Problema principal** | ¿Qué suele ocurrir en ese tipo de empresa? |
| **Módulo de entrada** | Maintenance o Inventory |
| **Transformación** | ¿Qué cambia con Roustix? |
| **KPIs relevantes** | Métricas que ese sector entiende y valora |
| **Prioridad de KPIs** | Orden 1️⃣ 2️⃣ 3️⃣ — en qué enfocar la conversación |
| **Madurez digital típica** | ⭐ a ⭐⭐⭐⭐⭐ — ayuda para preparar la reunión *(no es juicio)* |
| **Tiempo típico de implementación** | Expectativa comercial *(no promesa contractual)* |
| **Módulos futuros** | Hoy → mañana — visualizar crecimiento en la plataforma |
| **Historia de demo** | Un caso sencillo y cercano para mostrar en reunión |

**Regla:** el sector **adapta el discurso**, no redefine el producto. La puerta de entrada la define el **dolor dominante** (MCM-01-POS), no el rubro del RUT.

---

## Plantilla · Agregar un sector nuevo

Copiar este bloque para cada sector que se incorpore al manual:

```markdown
### [Nombre del sector]

| Campo | Contenido |
|-------|-----------|
| **Sector** | |
| **Problema principal** | |
| **Módulo de entrada** | Maintenance · Inventory · Mixto |
| **Transformación** | |
| **KPIs relevantes** | |
| **Prioridad KPIs** | 1️⃣ · 2️⃣ · 3️⃣ |
| **Madurez digital típica** | ⭐⭐☆☆☆ |
| **Tiempo implementación** | X–Y semanas *(expectativa)* |
| **Módulos futuros** | Hoy → … → mañana |
| **Historia de demo** | |
| **MUX en demo** | Perfiles DMU a invitar |
| **ICP Score** | Criterios que suelen sumar más |
```

---

## 1 · Manufactura e industria

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Manufactura** — fábricas, plantas, líneas de producción, talleres industriales |
| **Problema principal** | Paradas no planificadas · OTs en papel o WhatsApp · sin historial por máquina · el gerente no sabe disponibilidad real hasta que alguien arma un Excel |
| **Módulo de entrada** | **Roustix Maintenance** |
| **Transformación** | La planta deja de ser una caja negra → OTs trazables, preventivos con alerta, dashboard de disponibilidad en segundos |
| **KPIs relevantes** | **Disponibilidad** de activos · **% cumplimiento** de OT preventivas · **MTTR** · OTs abiertas vs cerradas |
| **Prioridad KPIs** | 1️⃣ **Disponibilidad** · 2️⃣ **Preventivos** · 3️⃣ **MTTR** |
| **Madurez digital típica** | ⭐⭐☆☆☆ — Excel y papel dominan; poca integración |
| **Tiempo implementación** | **2–4 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** Maintenance → **Mañana** Inventory (repuestos) → Compras → Analytics → IAM |
| **Historia de demo** | *«Línea 3 lleva dos días parada. El gerente pregunta por qué. Nadie tiene el historial completo — solo un audio de WhatsApp del técnico. Con Roustix: abres el activo, ves OTs, tiempos y repuestos en un clic.»* |
| **MUX en demo** | Laura (dashboard) + Carlos (cerrar OT) · DMU: Gerente + Jefe de mantenimiento |
| **ICP Score** | Excel + activos + +20 empleados + procesos en papel |

**Origen auténtico:** experiencia industrial en Colombia (INR) — ver MCM-01-POS.

---

## 2 · Comercio y retail

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Comercio** — tiendas, ferreterías, tornillerías, mostradores, retail con bodega |
| **Problema principal** | Stock en Excel desactualizado · vender sin saber si hay producto · cartera en cuaderno · compras por intuición («creo que se acabó el tornillo ½») |
| **Módulo de entrada** | **Roustix Inventory** |
| **Transformación** | El negocio deja de vender a ciegas → inventario en tiempo real, ventas con stock visible, cartera vinculada al cliente |
| **KPIs relevantes** | **Rotación** · **Stock** / quiebres · **Cartera** · Margen · Precisión de inventario |
| **Prioridad KPIs** | 1️⃣ **Rotación** · 2️⃣ **Stock** · 3️⃣ **Cartera** |
| **Madurez digital típica** | ⭐⭐⭐☆☆ — Excel maduro; a veces POS o facturación aislada |
| **Tiempo implementación** | **1–2 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** Inventory → Compras → Analytics → Maintenance *(si hay equipos)* |
| **Historia de demo** | *«Un cliente pide 200 unidades del producto X. Valentina busca en tres Excels y dice «creo que hay». Con Roustix: cotiza en el mostrador con stock real — si no hay, sabe cuánto entraría mañana.»* |
| **MUX en demo** | Valentina (venta) + Roberto (bodega) · DMU: Dueño/gerente + jefe de bodega |
| **ICP Score** | Excel + inventario + multi-sede (bodega + mostrador) + digitalización |

**Origen auténtico:** tornillería en Venezuela — ver MCM-01-POS.

---

## 3 · Agropecuaria

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Agropecuaria** — fincas, hatos, agroinsumos, comercialización agrícola, bodegas de insumos |
| **Problema principal** | Temporadas y lotes difíciles de rastrear · inventario de insumos y producción en hojas separadas · ventas y cartera sin vínculo · decisiones de compra tarde |
| **Módulo de entrada** | **Roustix Inventory** *(maquinaria crítica → Maintenance como expansión)* |
| **Transformación** | De cuadernos de campo y Excel dispersos → un registro de stock, ventas y cartera; si hay flota o maquinaria, activar Maintenance después sin migrar |
| **KPIs relevantes** | **Stock por sede** · **Rotación** de insumos · **Cartera** · Mermas · Disponibilidad maquinaria |
| **Prioridad KPIs** | 1️⃣ **Stock por sede** · 2️⃣ **Rotación** insumos · 3️⃣ **Cartera** |
| **Madurez digital típica** | ⭐⭐☆☆☆ — cuadernos de campo y Excel por temporada |
| **Tiempo implementación** | **2–3 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** Inventory → Maintenance (maquinaria) → Compras → Analytics |
| **Historia de demo** | *«Antes de la siembra, el encargado no sabía con certeza cuánto fertilizante quedaba en bodega central vs sede 2. Tres llamadas y un Excel viejo. Con Roustix: un número, misma respuesta para compras y para el dueño.»* |
| **MUX en demo** | Roberto + Laura · DMU: Dueño (Gerente ⭐⭐⭐⭐⭐) + encargado de bodega |
| **ICP Score** | Inventario + multi-sede + procesos estacionales + Excel |

**Origen auténtico:** agropecuaria en Venezuela — ver MCM-01-POS.

---

## 4 · Servicios con activos

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Servicios** — flotas, HVAC, facilities, empresas de mantenimiento contratado, servicios con equipos críticos |
| **Problema principal** | Activos repartidos en varias sedes o clientes · mantenimiento reactivo · sin trazabilidad de intervenciones · reportes al cliente final tardan días |
| **Módulo de entrada** | **Roustix Maintenance** |
| **Transformación** | De «apagar incendios» a operación gobernable → calendario preventivo, historial por activo, reportes exportables para el cliente |
| **KPIs relevantes** | **Disponibilidad** flota · **Cumplimiento** visitas · **Tiempo de respuesta** · Costo por activo |
| **Prioridad KPIs** | 1️⃣ **Disponibilidad** · 2️⃣ **Cumplimiento** visitas · 3️⃣ **Tiempo de respuesta** |
| **Madurez digital típica** | ⭐⭐☆☆☆ — hojas de ruta y WhatsApp entre técnicos |
| **Tiempo implementación** | **2–3 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** Maintenance → Inventory (repuestos) → Analytics → IAM |
| **Historia de demo** | *«Un cliente llama: «¿Cuándo le hicieron mantenimiento al equipo 12?» El coordinador revisa chats y cuadernos. Con Roustix: historial completo con fecha, técnico y evidencia — respuesta en la llamada.»* |
| **MUX en demo** | Carlos + Laura · DMU: Coordinador de operaciones (champion) + Gerente |
| **ICP Score** | Activos + multi-sede + procesos definidos + busca digitalización |

---

## 5 · Distribución y logística

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Distribución** — mayoristas, distribuidores, logística de última milla con bodega propia |
| **Problema principal** | Alto volumen de SKUs · entradas y salidas sin trazabilidad · ventas prometen stock que bodega no tiene · rutas y cartera desconectadas del inventario |
| **Módulo de entrada** | **Roustix Inventory** *(flota de reparto → Maintenance)* |
| **Transformación** | Un solo registro de verdad para bodega y ventas → menos quiebres, menos devoluciones, cartera alineada a documentos reales |
| **KPIs relevantes** | **Quiebres** · **Rotación** por SKU · **Cartera** · Días de inventario · Precisión conteo |
| **Prioridad KPIs** | 1️⃣ **Quiebres de stock** · 2️⃣ **Rotación** · 3️⃣ **Cartera** |
| **Madurez digital típica** | ⭐⭐⭐☆☆ — ERP ligero o Excel avanzado en bodega |
| **Tiempo implementación** | **2–3 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** Inventory → Compras → Maintenance (flota) → Analytics |
| **Historia de demo** | *«El vendedor confirma un pedido grande. En bodega descubren que el SKU está en cero — el Excel no se actualizó desde ayer. Con Roustix: el vendedor ve el mismo stock que bodega, en el momento de la venta.»* |
| **MUX en demo** | Valentina + Roberto + Laura · DMU: Gerente comercial + jefe de bodega |
| **ICP Score** | Inventario + +20 empleados + multi-sede + Excel como sistema principal |

---

## 6 · Operación mixta

| Campo | Contenido |
|-------|-----------|
| **Sector** | **Operación mixta** — empresa con planta **y** bodega comercial, o mantenimiento **y** repuestos con inventario propio |
| **Problema principal** | Dos mundos en silos: mantenimiento en un Excel, inventario en otro · repuestos consumidos en OT no descuentan stock · gerencia sin vista unificada |
| **Módulo de entrada** | El **módulo del dolor más urgente** hoy · segundo módulo mañana |
| **Transformación** | **La transformación comienza con un módulo. El crecimiento ocurre dentro de una sola plataforma.** — OTs que consumen repuestos del inventario; un dashboard para Laura |
| **KPIs relevantes** | **Disponibilidad** + **rotación** · **Costo repuestos** por activo · Stock de críticos |
| **Prioridad KPIs** | 1️⃣ **Disponibilidad** · 2️⃣ **Stock críticos** · 3️⃣ **Costo repuestos** por activo |
| **Madurez digital típica** | ⭐⭐☆☆☆ — dos Excels que no se hablan |
| **Tiempo implementación** | **4–6 semanas** *(expectativa comercial)* |
| **Módulos futuros** | **Hoy** módulo del dolor → **Mañana** segundo módulo → Compras → Analytics → IAM |
| **Historia de demo** | *«Una OT de mantenimiento consume 4 rodamientos. Hoy nadie descuenta bodega. Con Roustix: cierras la OT y el inventario se actualiza — Laura ve costo por máquina y Roberto ve stock real.»* |
| **MUX en demo** | Laura + Carlos + Roberto · DMU: Gerente de operaciones (champion fuerte) |
| **ICP Score** | Inventario **y** activos (+20 ambos) · multi-sede · OMI 1–2 |

---

## 7 · Cómo usar este capítulo en ventas

| Momento | Acción |
|---------|--------|
| **Calificación (MCM-03-ICP)** | Sector sugiere puerta probable — confirmar con dolor real |
| **Pre-demo** | Leer **Historia de demo** del sector · invitar perfiles MUX y DMU correctos · ver [MCM-07-DEMO](07-demo-comercial.md) |
| **Demo** | Metodología 5 fases: apertura (historia sector) · operación · indicadores · cierre plan + trial |
| **Objeciones (MCM-08-OBJ)** | Fichas OBJ por sector · «muy específicos» → MCM-05 + OBJ-008 |
| **Marketing** | Landing por sector · **MTX-CASE** Antes/Después |

### Matriz rápida · Sector → puerta

| Sector | Puerta típica | Madurez típica | Tiempo impl. *(expectativa)* |
|--------|---------------|----------------|------------------------------|
| Manufactura | Maintenance | ⭐⭐☆☆☆ | 2–4 semanas |
| Comercio | Inventory | ⭐⭐⭐☆☆ | 1–2 semanas |
| Agropecuaria | Inventory | ⭐⭐☆☆☆ | 2–3 semanas |
| Servicios con activos | Maintenance | ⭐⭐☆☆☆ | 2–3 semanas |
| Distribución | Inventory | ⭐⭐⭐☆☆ | 2–3 semanas |
| Operación mixta | Dolor dominante | ⭐⭐☆☆☆ | 4–6 semanas |

*Tiempo de implementación: referencia comercial para alinear expectativas — no compromiso contractual. Ajustar según tamaño y champion.*

### Matriz · Sector → puerta → expansión

| Sector | Puerta típica | Expansión natural |
|--------|---------------|-------------------|
| Manufactura | Maintenance | Inventory (repuestos) |
| Comercio | Inventory | — |
| Agropecuaria | Inventory | Maintenance (maquinaria) |
| Servicios con activos | Maintenance | Inventory (repuestos) |
| Distribución | Inventory | Maintenance (flota) |
| Operación mixta | Dolor dominante | Segundo módulo |

---

## Conexión con capítulos anteriores

| Código | Aporta a sectores |
|--------|-------------------|
| MCM-01-POS | «No vendemos por industria» + orígenes reales por sector |
| MCM-02-VALUE | Transformación por bloque — reutilizar en cada ficha |
| MCM-03-ICP | Score por sector · urgencia · champion |
| MCM-04-DMU | Quién invitar a la demo según sector |
| **MCM-05-SECT** | **Guion sectorial consistente** |

---

## Pilar de marca · Crecimiento modular

Esta frase es un **pilar de marca** de Roustix (junto a *Toda la operación. Una sola plataforma.*). Debe aparecer de forma consistente en todos los canales comerciales:

> **La transformación comienza con un módulo. El crecimiento ocurre dentro de una sola plataforma.**

| Canal | Ubicación | Uso |
|-------|-----------|-----|
| **MCM** | MCM-02-VALUE · MCM-05-SECT · MCM-06-PLAN | Vendedor y socio |
| **Landing** | [templates/landing/index.html](/) — banda de crecimiento | Visitante web |
| **Folleto comercial** | [materials/folleto-comercial.md](materials/folleto-comercial.md) | Reuniones · PDF · impresión |
| **Presentaciones · pitch · videos** | Slide 2–3 y cierre | Prospecto |
| **Demo 20 min** | Cierre acto 3 · metodología completa | [MCM-07-DEMO](chapters/07-demo-comercial.md) |
| **Correo / bienvenida** | Post-registro · trial día 1 | Nuevo cliente |
| **Documentación** | [materials/pilar-crecimiento.md](materials/pilar-crecimiento.md) | Referencia completa |

---

> **Frase del capítulo:** El sector no cambia el producto. Cambia el **idioma** con el que cuentas la misma transformación.

**Próximo capítulo:** MCM-06-PLAN · Planes comerciales (Sprint 5.6)

---

*MCM-05-SECT · Roustix Commercial Manual · 2026*
