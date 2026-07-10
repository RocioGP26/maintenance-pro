# MCM-07-DEMO · Guía oficial de demostración

**Código:** MCM-07-DEMO · Sprint 11.7 · **Entregado**

> Una demo no consiste en mostrar pantallas. Consiste en demostrar **cómo Maintix resuelve un problema real de operación**.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MCM-01-INTRO](01-intro-filosofia-comercial.md) · [MCM-02-VALUE](02-propuesta-de-valor.md) · [MCM-03-MARKETS](03-sectores-mercados.md) · [MCM-04-PLANS](04-planes-saas.md) · [MCM-05-MODULES](05-catalogo-modulos.md) · [ICP (apéndice)](appendix/icp-score.md) · [DMU (apéndice)](appendix/buyer-personas-dmu.md)

---

## Objetivo

Definir el **proceso oficial** para realizar demostraciones comerciales de Maintix — asegurando un mensaje **consistente**, **centrado en el cliente** y alineado con la propuesta de valor del producto.

---

## 1 · Filosofía

Una demo exitosa responde **tres preguntas**:

| # | Pregunta |
|---|----------|
| 1 | ¿Cuál es el **problema** del cliente? |
| 2 | ¿Cómo lo **resuelve Maintix**? |
| 3 | ¿Qué **cambia** después de implementarlo? |

**Nunca** comienza mostrando el menú.

Comienza **entendiendo el negocio**.

**Frase del capítulo:**

> *«Así es exactamente como trabajamos hoy… y esto nos ayudaría a hacerlo mejor.»*

Ese es el resultado que buscamos — no «qué bonito se ve el sistema».

---

## 2 · Estructura oficial

```
Introducción
      │
      ▼
Descubrir dolor
      │
      ▼
Historia del sector
      │
      ▼
Mostrar el módulo principal
      │
      ▼
Explicar expansión futura
      │
      ▼
Próximos pasos
```

| Fase | Código PLAY | Contenido |
|------|-------------|-----------|
| Antes de reunión | **PLAY-001** | Preparación · ICP · sector · módulo |
| Introducción + dolor | **PLAY-002** | Preguntas · historia del sector |
| Demo principal | **PLAY-003** | Flujo punta a punta · un módulo |
| Indicadores | **PLAY-004** | Dashboard · KPI del sector |
| Cierre | **PLAY-005** | Plan · trial · siguiente paso |

Códigos: [NOMENCLATURE.md](../NOMENCLATURE.md#playbook--códigos-play)

---

## 3 · Tiempo recomendado

| Bloque | Tiempo |
|--------|--------|
| Presentación | 5 min |
| Descubrimiento | 10 min |
| Demo principal | 20 min |
| Preguntas | 15 min |
| Próximos pasos | 10 min |

**Duración recomendada total:** **45–60 minutos**

| Variante | Cuándo |
|----------|--------|
| **45 min** | Prospecto con urgencia · banda ICP A |
| **60 min** | DMU completo · operación mixta · Finanzas en sala |
| **20 min** *(solo PLAY-003)* | Segunda reunión · ya hubo descubrimiento — no sustituye la demo oficial |

---

## 4 · Descubrir el dolor

**Antes de compartir pantalla**, preguntar:

- ¿Cómo gestionan hoy la operación?
- ¿Cuál es el **mayor problema**?
- ¿Qué sucede cuando falla un equipo?
- ¿Cómo controlan inventario?
- ¿Qué información tardan más en encontrar?

**El objetivo no es vender. Es entender.**

Anotar respuestas en CRM — alimentan PLAY-003 y el plan sugerido (MCM-04).

| Señal en respuestas | Puerta probable |
|---------------------|-----------------|
| Paradas · OT · activos | **Mantenimiento** |
| Stock · ventas · cartera | **Inventario** |
| Ambos con igual peso | Dolor más crítico hoy |

→ Calificación: [appendix/icp-score.md](appendix/icp-score.md)

---

## 5 · Elegir la puerta de entrada

| Dolor principal | Demo |
|-----------------|------|
| Equipos | **Mantenimiento** |
| Inventario | **Inventario** |
| Ambos | Comenzar por el **más crítico** |

**Regla:** nunca mostrar **ambos módulos completos** en los primeros minutos.

Si el prospecto tiene operación mixta, mencionar expansión al cierre (§9) — no mezclar flujos en PLAY-003.

→ [MCM-05-MODULES §7](05-catalogo-modulos.md#7--cómo-presentar-los-módulos)

---

## 6 · Historia (PLAY)

Toda demo debe apoyarse en una **historia** — conecta mejor que una lista de funciones.

Copiar o adaptar desde [MCM-03-MARKETS](03-sectores-mercados.md); no inventar un caso nuevo en la reunión.

### Ejemplo · Industria / Mantenimiento

1. Una máquina se detiene.
2. Se registra la **incidencia**.
3. Se genera una **OT**.
4. El técnico la ejecuta.
5. Se consumen **repuestos**.
6. La gerencia ve el **KPI**.

### Ejemplo · Comercio / Inventario

1. Llega **mercancía**.
2. Se actualiza **inventario**.
3. Se **vende**.
4. El stock disminuye.
5. Se genera una **alerta**.
6. **Compras** repone.

**En PLAY-002:** contar la historia en 60–90 segundos **antes** de abrir Maintix.

→ Historias extendidas: [appendix/sectores-detalle.md](appendix/sectores-detalle.md)

---

## 7 · Qué mostrar

Mostrar **únicamente** lo necesario para explicar el flujo de la historia.

### Mantenimiento

| Pantalla / flujo | Propósito en demo |
|------------------|-------------------|
| **Dashboard** | Vista gerencial · KPIs del sector |
| **Activos** | Estado · criticidad · historial |
| **Preventivos** | Anticipación vs reactivo |
| **Orden de trabajo** | Ciclo completo · técnico · cierre |
| **Historial** | Trazabilidad · evidencia |

→ [MRG-02 · Mantenimiento](/mrg/chapters/02-maintenance.md)

### Inventario

| Pantalla / flujo | Propósito en demo |
|------------------|-------------------|
| **Productos** | Catálogo · stock visible |
| **Compras** | Entrada · proveedor |
| **Ventas** | POS · descuento de stock |
| **Stock** | Alertas · mínimos |
| **Dashboard** | Rotación · quiebres · cartera |

→ [MRG-03 · Inventario](/mrg/chapters/03-inventario.md)

**Perfiles MUX:** invitar al operador y al decisor correctos — ver [MUX](/mux/) y DMU en [appendix/buyer-personas-dmu.md](appendix/buyer-personas-dmu.md).

---

## 8 · Qué NO mostrar

Evitar en demo comercial:

| ❌ No mostrar | Por qué |
|--------------|---------|
| Configuración avanzada | Distrae · no es el dolor del día 1 |
| Pantallas administrativas Mantis | Confunde tenant vs operador |
| Funciones **roadmap** | Honestidad comercial — MCM-05 §5 |
| Errores técnicos · bugs | Escalar post-demo |
| SQL · Flask · API · código | Audiencia incorrecta |

Eso pertenece a **MPA**, **MAG** y **MSD** — ofrecer sesión técnica aparte si TI lo pide (OBJ-010).

---

## 9 · Cierre

Toda demo debe terminar con **tres ideas**:

| # | Mensaje |
|---|---------|
| ✔ | **Hoy** solucionamos este problema. |
| ✔ | **Mañana** puedes activar más módulos. |
| ✔ | **Nunca** tendrás que migrar de plataforma. |

**PLAY-005 · incluir siempre:**

- Plan sugerido (**Start** / **Grow**) — [MCM-04-PLANS](04-planes-saas.md)
- Trial **15 días** · quién lo activa · cuándo
- **Siguiente reunión** con fecha — no «te escribo»

**Slogan MCM-01** *(opcional en cierre emocional):*

> *«No necesitas otro software. Necesitas recuperar el control de tu operación.»*

---

## 10 · Después de la demo

Registrar en **CRM** (debrief ≤ 24 h):

| Campo | Fuente |
|-------|--------|
| **Sector** | MCM-03 |
| **Módulo de entrada** | MCM-05 · PLAY-003 |
| **ICP** | Banda · score |
| **OMI** | Madurez operativa *(apéndice ICP)* |
| **Objeciones** | OBJ-001…010 · [MCM-09-OBJECTIONS](09-manejo-objeciones.md) |
| **Champion** | Nombre · strength 🟢🟡🔴 |
| **Siguiente reunión** | Fecha · objetivo · asistentes |

**La demo termina cuando existe un siguiente paso claro** — trial activado, segunda reunión agendada o descalificación documentada.

Handoff a onboarding si cierra: [MCM-06-ONBOARD](06-onboarding-implementacion.md)

---

## 11 · Relación documental

| Documento | Uso en demo |
|-----------|-------------|
| **MCM-01-INTRO** | Mensaje comercial · slogan |
| **MCM-02-VALUE** | Transformación antes/después |
| **MCM-03-MARKETS** | Adaptación por sector · historias |
| **MCM-04-PLANS** | Recomendación del plan |
| **MCM-05-MODULES** | Expansión modular · qué no prometer |
| **MCM-06-ONBOARD** | Próximo paso post-cierre |
| **MRG** | Respaldo funcional si preguntan «¿cómo funciona X?» |
| **MUX** | Personas y recorridos por rol |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Flujo oficial de demo definido
- [x] Adaptación por sector documentada
- [x] Guía de tiempos incluida
- [x] Historias PLAY incorporadas
- [x] Relación con CRM y onboarding establecida

---

## Filosofía del capítulo

La mejor demo **no** es la que muestra más funcionalidades.

Es la que consigue que el cliente diga:

> *«Así es exactamente como trabajamos hoy… y esto nos ayudaría a hacerlo mejor.»*

---

## Estado · Sprint 11

| Aspecto | Valor |
|---------|-------|
| **Playbook PLAY** | ✅ Definido |
| **Checklist detallado** | [appendix/demo-play-detalle.md](appendix/demo-play-detalle.md) *(Sprint 5)* |
| **Capítulos restantes Sprint 11** | MCM-08-FAQ · MCM-09-OBJECTIONS · MCM-10-PARTNERS |

---

**Próximo capítulo:** [MCM-09-OBJECTIONS · Objeciones](09-manejo-objeciones.md)

---

## Apéndice · Códigos PLAY (referencia rápida)

### PLAY-001 · Preparación

**Antes de la reunión** — completar:

- [ ] ICP · banda · urgencia · champion
- [ ] Sector · historia · módulo de entrada
- [ ] DMU esperado en sala
- [ ] Plan sugerido (Start/Grow)
- [ ] Entorno demo estable · datos coherentes con sector

### PLAY-002 · Apertura · 3 minutos

1. Agradecer · confirmar tiempo (45–60 min).
2. **Descubrir dolor** (§4) — mínimo 3 preguntas.
3. Contar **historia del sector** (§6) — sin abrir menú aún.
4. Confirmar módulo de entrada.

### PLAY-003 · Operación · 10–15 minutos

Un solo flujo **punta a punta** según §7 — siguiendo la historia, no el menú lateral.

### PLAY-004 · KPIs · 3 minutos

Abrir **dashboard** del perfil decisor (MUX · Laura/gerente). Señalar 1–2 KPIs prioritarios del sector (MCM-03).

### PLAY-005 · Cierre · 5 minutos

Tres ideas (§9) · plan · trial 15 días · **fecha** de siguiente paso.

→ Playbook extendido Sprint 5: [appendix/demo-play-detalle.md](appendix/demo-play-detalle.md)

---

*MCM-07-DEMO · Maintix Commercial Manual · Sprint 11 · 2026*
