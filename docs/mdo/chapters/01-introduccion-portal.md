# MDO-01 · Introducción al Portal de Documentación

**Código:** MDO-01 · Sprint 13.1 · **Entregado**

> La documentación de Roustix no existe para describir pantallas. Existe para permitir que clientes, partners, desarrolladores y equipos internos **comprendan, implementen, operen e integren** la plataforma con confianza.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [Roustix Docs · Índice maestro](/docs/) · [DOCUMENTATION-PRODUCT.md](/docs/DOCUMENTATION-PRODUCT.md) · [NOMENCLATURE.md](/docs/NOMENCLATURE.md)

---

## Objetivo del capítulo

Presentar la **filosofía, estructura y propósito** del ecosistema documental de Roustix.

Este capítulo es el **punto de entrada** para cualquier persona que llegue al portal `/docs`.

---

## 1 · ¿Qué es la documentación Roustix?

La documentación Roustix es un conjunto de **manuales especializados** que describen:

| Dominio | Qué documenta |
|---------|---------------|
| **Producto** | Funcionalidades, módulos, operación diaria |
| **Operación** | Procesos, roles, flujos de trabajo |
| **Arquitectura** | Plataforma, escalabilidad, decisiones técnicas |
| **Integraciones** | API, SDK, contratos de servicio |
| **Comercialización** | Ventas, planes, objeciones, demos |
| **Marketing** | Identidad, activos, casos, gobernanza de marca |
| **Gobernanza documental** | Portal, versionado, calidad, publicación |

Su objetivo es garantizar que **todos los actores trabajen sobre una única fuente de verdad**.

### Principio fundamental

> **La documentación es parte del producto.**

Un sistema bien diseñado pero mal documentado genera:

- Implementaciones lentas
- Soporte repetitivo
- Errores operativos
- Adopción limitada

Roustix documenta **desde el diseño** para evitar depender del conocimiento informal.

---

## 2 · Filosofía documental

La documentación Roustix sigue **cinco principios**.

| Principio | Significado |
|-----------|-------------|
| **Una fuente de verdad** | Evitar documentos paralelos |
| **Orientada por audiencia** | Cada manual responde a un perfil |
| **Versionada** | Cada cambio es trazable |
| **Conectada** | Los manuales se relacionan entre sí |
| **Práctica** | Prioriza uso real sobre teoría |

---

## 3 · La suite documental

La documentación oficial está organizada en **manuales especializados**.

| Código | Manual | Audiencia |
|--------|--------|-----------|
| **MPA** | Roustix Platform Architecture | Producto · Arquitectura |
| **MAG** | Roustix API Guide | Desarrolladores |
| **MSD** | Roustix Software Developer Portal | Integradores |
| **MRG** | Roustix Reference Guide | Usuarios · Implementadores |
| **MCM** | Roustix Commercial Manual | Ventas |
| **MKT** | Marketing Toolkit | Marketing |
| **MDO** | Roustix Documentation Operations | Gestión documental |

### Fundación (congelada)

| Código | Manual | Rol |
|--------|--------|-----|
| **MBB** | Brand Book | Identidad corporativa |
| **MDL** | Design Language | Sistema visual |
| **MUX** | User Experience Guide | Experiencia y microcopy |

### Relación entre manuales

```
MDO
 │
 ├── MPA
 ├── MAG
 ├── MSD
 ├── MRG
 ├── MCM
 └── MKT
```

**MDO** actúa como la capa de **gobierno y organización documental**.

---

## 4 · ¿Qué manual debo leer?

### Soy cliente

Comienza por:

→ [MRG](/mrg/)

### Soy implementador

Comienza por:

→ [MRG](/mrg/)  
→ [MCM](/mcm/)

### Soy desarrollador

Comienza por:

→ [MAG](/mag/)  
→ [MSD](/msd/)

### Soy partner

Comienza por:

→ [MCM](/mcm/)  
→ [MKT](/mkt/)

### Soy parte del equipo Roustix

Comienza por:

→ [MDO](/mdo/)

---

## 5 · Estructura del portal

El portal se organiza por **dominios**.

```
/docs          ← Índice maestro

/brandbook     ← MBB
/mdl           ← MDL
/mux           ← MUX
/mpa
/mag
/msd
/mrg
/mcm
/mkt
/mdo
```

Cada dominio posee:

- Índice visual (`index.html`)
- Capítulos en Markdown
- Referencias cruzadas
- Versionado propio (`changelog.md`)

---

## 6 · Convenciones

Todos los documentos siguen la **misma estructura**.

### Encabezado

```markdown
# Código · Título

Código:
Estado:
Prerequisitos:
```

### Objetivo

Todo documento explica:

> **Qué problema resuelve.**

### Desarrollo

Contenido principal.

### Relación

Documentos relacionados.

### Exit Criteria

Condiciones para considerar el documento terminado.

---

## 7 · Estados documentales

Cada documento posee un **estado** en su ciclo de vida.

| Estado | Significado |
|--------|-------------|
| 📋 **Planificado** | Aún no desarrollado |
| 🟡 **En desarrollo** | En construcción |
| 🔄 **Revisión técnica** | Validación de exactitud (producto) |
| 📝 **Revisión editorial** | Validación documental (MDO) |
| ✅ **Publicado** | Completo y oficial |
| 📦 **Archivado** | Histórico |
| ❌ **Obsoleto** | No utilizar |

→ Ciclo completo: [MDO-05 §5](chapters/05-versionado-releases.md#5--ciclo-de-vida-de-un-documento)

---

## 8 · Versionado

Toda documentación utiliza **versionado semántico**.

**Ejemplo:** `v1.0.0`

**Formato:** `MAJOR.MINOR.PATCH`

### Cuándo cambiar versión

| Cambio | Acción |
|--------|--------|
| Reescritura importante | **MAJOR** |
| Nuevo capítulo | **MINOR** |
| Corrección menor | **PATCH** |

→ Registro oficial: [VERSIONS.md](/docs/VERSIONS.md) · Política: [VERSIONING.md](/docs/VERSIONING.md)

---

## 9 · Referencias cruzadas

Los documentos **no duplican información**.

**Regla:**

> Explicar una vez. Referenciar muchas.

| Manual | Rol en la cadena |
|--------|------------------|
| **MRG** | Describe funcionalidades |
| **MCM** | Describe cómo venderlas |
| **MKT** | Describe cómo comunicarlas |

→ Matriz completa: [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md)

---

## 10 · Audiencias

| Audiencia | Manual principal |
|-----------|------------------|
| Usuario final | MRG |
| Administrador | MRG |
| Implementador | MRG |
| Comercial | MCM |
| Marketing | MKT |
| Partner | MCM |
| Desarrollador | MAG |
| Arquitecto | MPA |
| Equipo interno | MDO |

---

## 11 · Beneficios del modelo documental

### Para clientes

- Menos dependencia de soporte
- Adopción más rápida

### Para partners

- Implementaciones consistentes

### Para ventas

- Discurso alineado

### Para desarrollo

- Contratos claros

### Para Roustix

- Escalabilidad organizacional

---

## 12 · Roadmap documental

La documentación evoluciona **junto al producto**.

```
Producto nuevo
        │
        ▼
Documentación
        │
        ▼
Capacitación
        │
        ▼
Operación
```

> Ninguna funcionalidad debería considerarse completa sin documentación correspondiente.

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MPA](/mpa/) | Arquitectura |
| [MAG](/mag/) | API |
| [MSD](/msd/) | Portal desarrollador |
| [MRG](/mrg/) | Operación |
| [MCM](/mcm/) | Comercial |
| [MKT](/mkt/) | Marketing |
| [MDO-02](02-arquitectura-documentacion.md) | Arquitectura documental *(planificado)* |

---

## Exit Criteria

- [x] Filosofía documental definida
- [x] Suite documental presentada
- [x] Audiencias identificadas
- [x] Convenciones documentadas
- [x] Estados y versionado definidos
- [x] Estructura del portal explicada

---

## Filosofía del capítulo

La documentación **no es un anexo del producto**.

Es la **infraestructura** que permite que el producto pueda crecer, escalar y ser comprendido por personas que nunca hablarán directamente con quienes lo construyeron.

Si el conocimiento vive solo en las personas, la organización no escala.  
Si vive en la documentación, el conocimiento se convierte en **sistema**.

---

## Estado

| Aspecto | Estado |
|---------|--------|
| Portal documental | 🟡 En construcción |
| Gobernanza documental | 🟡 En construcción |
| MDO-01 | ✅ Entregado |
| Sprint 13 | 🚀 Iniciado |
