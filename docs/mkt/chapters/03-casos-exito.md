# MKT-03 · Casos de éxito

**Código:** MKT-03 · Sprint 12.3 · **Entregado**

> Las empresas no compran únicamente funcionalidades. Compran la confianza de que alguien con un problema similar ya obtuvo resultados.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MKT-01 · Identidad y mensajes](01-identidad-mensajes-marca.md) · [MKT-02 · Elevator Pitch](02-elevator-pitch-guiones.md) · [MCM-03 · Sectores](/mcm/chapters/03-sectores-mercados.md)

**Biblioteca:** [`mtx-case/`](../mtx-case/README.md) — un archivo por caso · este capítulo = gobierno y metodología

---

## Objetivo del capítulo

Definir la estrategia oficial para documentar, clasificar y comunicar los **casos de éxito Roustix (MTX-CASE)**.

Los casos de éxito son la principal evidencia comercial para demostrar que Roustix resuelve problemas reales de operación.

No son testimonios aislados.

Son evidencia estructurada.

---

## 1 · Filosofía

Las funcionalidades generan interés.

Los casos generan confianza.

El objetivo de un caso de éxito **no** es demostrar que Roustix tiene muchas funciones.

Es demostrar que una empresa logró mejores resultados.

La estructura siempre debe responder cinco preguntas:

```
¿Quién era?
    ↓
¿Qué problema tenía?
    ↓
¿Cómo se implementó?
    ↓
¿Qué cambió?
    ↓
¿Qué aprendimos?
```

→ Arquitectura narrativa alineada a [MKT-01 · §11](01-identidad-mensajes-marca.md#11--arquitectura-del-mensaje)

---

## 2 · Biblioteca MTX-CASE

Todos los casos oficiales utilizan el prefijo:

```
MTX-CASE-001
MTX-CASE-002
MTX-CASE-003
...
```

**Ubicación:** `docs/mkt/mtx-case/` · servido en `/mkt/mtx-case/`

| Archivo | Caso |
|---------|------|
| [MTX-CASE-001-industria-colombia.md](../mtx-case/MTX-CASE-001-industria-colombia.md) | Manufactura · Colombia |
| [MTX-CASE-002-tornilleria-venezuela.md](../mtx-case/MTX-CASE-002-tornilleria-venezuela.md) | Comercio · tornillería |
| [MTX-CASE-003-agroindustria.md](../mtx-case/MTX-CASE-003-agroindustria.md) | Agroindustria |
| [MTX-CASE-004-taller-mantenimiento.md](../mtx-case/MTX-CASE-004-taller-mantenimiento.md) | Taller · servicios |
| [MTX-CASE-005-distribucion.md](../mtx-case/MTX-CASE-005-distribucion.md) | Distribución |
| [MTX-CASE-006-comercio-multisede.md](../mtx-case/MTX-CASE-006-comercio-multisede.md) | Operación mixta |

Cada caso puede publicarse en:

| Canal | Estado |
|-------|--------|
| Web | ✅ |
| PDF comercial | ✅ |
| Presentación ventas | ✅ |
| Partners | ✅ |
| Demo oficial | ✅ |
| Blog | Opcional |

**Legacy comercial:** [MCM appendix casos-exito](/mcm/chapters/appendix/casos-exito.md) — referencia Sprint 5 · **MKT mtx-case/** es la fuente para activos de marketing.

---

## 3 · Niveles de evidencia

No todos los casos tienen el mismo nivel de validación.

| Nivel | Evidencia | Uso comercial |
|-------|-----------|---------------|
| **A** | Cliente autoriza nombre, logo y resultados | Público |
| **B** | Cliente autoriza historia pero no cifras completas | Público |
| **C** | Caso anonimizado | Comercial interno |
| **D** | Caso construido a partir de experiencia real (sin cliente identificable) | Storytelling inicial |

### Nivel A

Puede incluir: nombre empresa · logo · fotografías · indicadores · declaraciones · video.

Es el objetivo ideal.

### Nivel B

Permite decir *«Empresa manufacturera de Colombia»* pero no publicar datos sensibles.

### Nivel C

Ejemplo: *«Empresa con tres sedes dedicada a distribución»* — sin revelar identidad.

### Nivel D

Historias basadas en experiencias reales. Útiles mientras la biblioteca crece.

**Siempre indicar internamente:**

```
Nivel D
No utilizar como prueba cuantitativa.
```

**Hoy:** MTX-CASE-001–006 están en nivel **D**.

**Progresión:** D → C (post-trial) → B (cliente autoriza nombre) → A (métricas + cita).

---

## 4 · Plantilla oficial

Cada caso en `mtx-case/` utiliza la misma estructura.

### Resumen

| Campo | Contenido |
|-------|-----------|
| Código | MTX-CASE-001 |
| Nivel | A / B / C / D |
| Sector | Manufactura |
| País | Colombia |
| Módulo inicial | Mantenimiento |
| Plan | Grow |

### Secciones

| Sección | Pregunta |
|---------|----------|
| **Antes** | ¿Cómo trabajaba el cliente? |
| **Problema** | ¿Qué estaba ocurriendo? |
| **Implementación** | ¿Qué módulo? · ¿Cómo fue el onboarding? |
| **Resultado** | ¿Qué cambió? |
| **Aprendizajes** | ¿Qué recomendaría el equipo? |

### Relación documental

MRG · MCM · Demo · Pitch · Landing

Ver plantilla completa en cualquier archivo de [mtx-case/](../mtx-case/README.md).

---

## 5 · Indicadores

Cuando existan datos autorizados pueden incluirse.

| Indicador | Ejemplo |
|-----------|---------|
| Tiempo búsqueda OT | −70 % |
| Preventivos cumplidos | +35 % |
| Diferencias inventario | −80 % |
| Tiempo preparación reportes | −60 % |
| Horas administrativas | −25 % |

**Si no existen cifras verificadas:** no inventarlas. Usar únicamente mejoras cualitativas.

---

## 6 · Casos iniciales

La biblioteca parte de los orígenes de Roustix.

| Código | Título | Archivo | Nivel |
|--------|--------|---------|-------|
| MTX-CASE-001 | Industria Colombia | [001](../mtx-case/MTX-CASE-001-industria-colombia.md) | D |
| MTX-CASE-002 | Tornillería Venezuela | [002](../mtx-case/MTX-CASE-002-tornilleria-venezuela.md) | D |
| MTX-CASE-003 | Agroindustria | [003](../mtx-case/MTX-CASE-003-agroindustria.md) | D |
| MTX-CASE-004 | Taller mantenimiento | [004](../mtx-case/MTX-CASE-004-taller-mantenimiento.md) | D |
| MTX-CASE-005 | Distribución | [005](../mtx-case/MTX-CASE-005-distribucion.md) | D |
| MTX-CASE-006 | Comercio multisede | [006](../mtx-case/MTX-CASE-006-comercio-multisede.md) | D |

Estos casos alimentan: MCM · Landing · Demo · Presentaciones · Pitch.

---

## 7 · Uso por sector

| Sector | Caso principal |
|--------|----------------|
| Manufactura | [MTX-CASE-001](../mtx-case/MTX-CASE-001-industria-colombia.md) |
| Comercio | [MTX-CASE-002](../mtx-case/MTX-CASE-002-tornilleria-venezuela.md) |
| Agro | [MTX-CASE-003](../mtx-case/MTX-CASE-003-agroindustria.md) |
| Talleres | [MTX-CASE-004](../mtx-case/MTX-CASE-004-taller-mantenimiento.md) |
| Distribución | [MTX-CASE-005](../mtx-case/MTX-CASE-005-distribucion.md) |
| Operación mixta | [MTX-CASE-006](../mtx-case/MTX-CASE-006-comercio-multisede.md) |

**Regla:** nunca presentar un caso de un sector completamente distinto si existe uno más cercano.

→ Matching prospecto: [mtx-case/README.md](../mtx-case/README.md#elegir-caso-por-prospecto)

---

## 8 · Uso en ventas

Durante una reunión:

```
Dolor
    ↓
Caso similar
    ↓
Resultado
    ↓
Demo
    ↓
Propuesta
```

**No** comenzar mostrando el caso.

**Primero** identificar el dolor.

→ Pitch: [MKT-02 · §14](02-elevator-pitch-guiones.md#14--matriz-contexto--pitch) · Demo: [MCM-07](/mcm/chapters/07-demo-comercial.md)

**Lenguaje honesto (nivel D):** *«Empresas con operaciones como la suya suelen pasar de… a…»* — no *«nuestro cliente X logró…»* hasta tener permiso escrito.

---

## 9 · Storytelling

Todo caso debe responder cuatro preguntas:

| Fase | Pregunta |
|------|----------|
| **Antes** | ¿Cómo era la operación? |
| **Cambio** | ¿Qué decidió hacer? |
| **Después** | ¿Qué cambió? |
| **Futuro** | ¿Qué sigue ahora? |

La historia debe hablar de **personas**, no de pantallas.

---

## 10 · Formatos

Cada MTX-CASE puede existir como:

| Formato | Uso |
|---------|-----|
| PDF | Comercial |
| Landing | Marketing |
| Video | Redes |
| Slide | Presentaciones |
| Blog | SEO |
| Demo | PLAY |

Todos parten del **mismo contenido** en `mtx-case/`.

---

## 11 · Gobierno de casos

Solo **Marketing** puede aprobar un caso público.

Antes de publicarlo validar:

- Autorización cliente
- Cifras verificadas
- Logos autorizados
- Fotografías
- Versión final

**No modificar** un caso publicado sin actualizar su versión.

### Checklist · Migrar D → A

1. Validar permiso de uso (nombre · logo · cifras).
2. Subir nivel de evidencia (D → C → B → A).
3. Registrar fecha de publicación.
4. Completar empleados · industria · país para matching.
5. Reemplazar historia con cita verificada (nivel A).
6. Añadir métricas reales.
7. Actualizar cross-refs en OBJ · PLAY · landing · folleto.

---

## 12 · Relación documental

| Documento | Uso |
|-----------|-----|
| [MCM-03](/mcm/chapters/03-sectores-mercados.md) | Sectores |
| [MCM-07](/mcm/chapters/07-demo-comercial.md) | Demo |
| [MCM-09](/mcm/chapters/09-manejo-objeciones.md) | Objeciones |
| [MKT-02](02-elevator-pitch-guiones.md) | Pitch |
| [MKT-04](04-presentacion-comercial.md) | Presentación |
| MKT-05 | Landing |
| [MCM-10](/mcm/chapters/10-partners-canales.md) | Partners |

---

## Filosofía del capítulo

Los casos de éxito no sirven para demostrar que Roustix funciona.

Sirven para demostrar que empresas reales recuperaron el control de su operación.

Cada nuevo cliente debe convertirse, con el tiempo, en el siguiente **MTX-CASE**.

---

## Exit Criteria · MKT-03

- [x] Biblioteca MTX-CASE definida
- [x] Clasificación A–D documentada
- [x] Plantilla oficial creada
- [x] Casos iniciales definidos (6 archivos en `mtx-case/`)
- [x] Reglas de publicación establecidas

---

**Próximo capítulo:** [MKT-04 · Presentación comercial oficial](04-presentacion-comercial.md) *(Sprint 12.4)*

---

*MKT-03 · Sales Enablement & Marketing Assets · Sprint 12 · 2026*
