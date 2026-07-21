# MDO-02 · Arquitectura de la Documentación

**Código:** MDO-02 · Sprint 13.2 · **Entregado**

> La arquitectura documental define cómo se organiza el conocimiento de Roustix. Su objetivo es que cualquier persona encuentre la información correcta, en el momento correcto y **sin duplicidad**.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-01 · Introducción](01-introduccion-portal.md) · [MPA](/mpa/) · [MRG](/mrg/) · [MAG](/mag/)

---

## Objetivo del capítulo

Definir la **arquitectura lógica y física** del ecosistema documental de Roustix: dominios, estructura, convenciones, navegación, referencias cruzadas y principios de organización.

Este capítulo sirve como guía para cualquier persona que **escriba, mantenga o publique** documentación oficial.

---

## 1 · Filosofía

La documentación de Roustix está organizada por **dominios de conocimiento**, no por equipos internos ni por carpetas técnicas.

Cada documento debe responder **una pregunta específica** y pertenecer a **un único dominio**.

### Principios

| Principio | Descripción |
|-----------|-------------|
| **Un tema, un lugar** | Cada concepto tiene un único documento fuente |
| **Dominios independientes** | Cada manual tiene un propósito definido |
| **Referencias antes que duplicación** | Se enlaza información existente en lugar de copiarla |
| **Escalable** | La estructura admite nuevos manuales y capítulos sin reorganizaciones mayores |
| **Consistente** | Todos los manuales siguen la misma arquitectura |

---

## 2 · Arquitectura general

La documentación se organiza en **siete dominios principales**.

```
/docs
│
├── /mpa    Arquitectura de plataforma
├── /mag    API y contratos
├── /msd    Portal para desarrolladores
├── /mrg    Guía funcional del producto
├── /mcm    Manual comercial
├── /mkt    Marketing y activos comerciales
└── /mdo    Gobernanza documental
```

### Fundación (congelada)

| Ruta | Dominio |
|------|---------|
| `/brandbook/` | MBB · Identidad corporativa |
| `/mdl/` | MDL · Sistema visual |
| `/mux/` | MUX · Experiencia y microcopy |

Cada dominio mantiene su **independencia**, pero comparte **convenciones comunes**.

---

## 3 · Jerarquía documental

```
Roustix Documentation
│
├── Dominio
│     ├── Índice
│     ├── Capítulos
│     ├── Apéndices
│     └── Materiales
│
└── Recursos compartidos
      ├── Glosario
      ├── Changelog
      ├── Roadmap
      └── Assets
```

---

## 4 · Estructura de un dominio

Todos los dominios siguen la **misma organización**.

```
mrg/
│
├── README.md
├── index.html          ← índice visual (portada)
├── chapters/
├── appendix/
├── materials/
├── assets/
└── changelog.md
```

### Descripción

| Carpeta / archivo | Contenido |
|-------------------|-----------|
| `README.md` | Presentación del manual |
| `index.html` | Índice navegable visual |
| `chapters/` | Documentación principal |
| `appendix/` | Material de apoyo |
| `materials/` | Recursos reutilizables |
| `assets/` | Imágenes, diagramas e íconos |
| `changelog.md` | Historial de cambios |

> **Nota:** Algunos manuales usan `index.html` en lugar de `index.md`. La convención canónica prioriza **README + index visual + chapters/**.

---

## 5 · Organización de capítulos

Cada capítulo utiliza un **código único**.

**Ejemplos:**

```
MRG-01 · MRG-02 · MRG-03
MCM-01 · MCM-02
MKT-01
MDO-01 · MDO-02
```

### Regla

> **El código nunca cambia** aunque cambie el título.

Esto evita enlaces rotos y facilita el versionado.

→ Registro de códigos: [NOMENCLATURE.md](../NOMENCLATURE.md) · [docs/NOMENCLATURE.md](/docs/NOMENCLATURE.md)

---

## 6 · Convención de archivos

Formato recomendado:

```
01-introduccion.md
02-arquitectura.md
03-reportes.md
```

**Evitar nombres ambiguos:**

| ❌ No usar |
|-----------|
| `nuevo.md` |
| `documento_final.md` |
| `version2.md` |

Patrón: `{NN}-{slug-descriptivo}.md` · el prefijo numérico refleja el orden del capítulo, no el código oficial.

---

## 7 · Navegación

Todos los capítulos deben incluir **navegación consistente**.

### Encabezado

- Código
- Estado
- Prerequisitos

### Final del documento

- Documento anterior
- Documento siguiente
- Índice del manual

**Ejemplo:**

```
← MRG-06          Índice          MRG-08 →
```

---

## 8 · Referencias cruzadas

La arquitectura documental **evita duplicar contenido**.

| Manual | Rol en la cadena |
|--------|------------------|
| **MRG** | Explica *cómo crear una OT* |
| **MCM** | Explica *cómo vender esa capacidad* |
| **MKT** | Explica *cómo comunicar ese beneficio* |
| **MAG** | Explica *cómo consumir la API correspondiente* |

Cada documento **enlaza al otro** cuando es necesario.

→ Matriz y reglas: [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md)

---

## 9 · Glosario común

Existe un **glosario compartido** para toda la plataforma.

| Término | Fuente oficial |
|---------|----------------|
| **Tenant** | MRG-01 |
| **OMI** | MCM |
| **ICP** | MCM · [appendix/icp-score](/mcm/chapters/appendix/icp-score.md) |
| **OT** | MRG |
| **EMP** | MCM-01 |
| **Roustix Platform** | MPA |

> **No redefinir** estos conceptos en múltiples manuales.

---

## 10 · Material reutilizable

Elementos comunes viven en `materials/`.

**Ejemplos:**

```
materials/
├── pilar-crecimiento.md
├── taglines.md
├── cta.md
├── logos.md
└── emails.md
```

Así se evita mantener **múltiples versiones** del mismo contenido.

---

## 11 · Assets compartidos

Todo recurso gráfico debe almacenarse **centralizadamente**.

```
assets/
├── logos/
├── screenshots/
├── icons/
├── diagrams/
└── illustrations/
```

> **Nunca duplicar imágenes** entre manuales.

Preferir referencia desde `docs/brandbook/assets/` para logos oficiales.

---

## 12 · Changelog

Cada dominio mantiene su **propio historial**.

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-09 | Publicación inicial |
| 1.1.0 | 2026-10 | Nuevo capítulo |
| 1.1.1 | 2026-10 | Correcciones |

→ Suite: [docs/changelog.md](/docs/changelog.md) · Por manual: `{dominio}/changelog.md`

---

## 13 · Versionado global

Toda la suite comparte una **versión documental agregada**.

**Ejemplo:** Roustix Docs **v1.13.0**

Cada manual puede evolucionar de forma **independiente**.

| Manual | Versión (referencia) |
|--------|----------------------|
| MPA | v1.0 |
| MAG | v1.0.12 |
| MRG | v1.0.0 |
| MCM | v1.0.0 |
| MKT | v1.0.0 |
| MDO | v0.2.0 |

→ Registro oficial: [VERSIONS.md](/docs/VERSIONS.md)

---

## 14 · Escalabilidad

La arquitectura permite agregar **nuevos dominios** sin reorganizar la estructura existente.

| Código | Dominio futuro |
|--------|----------------|
| **MBA** | Analytics |
| **MQA** | Quality Assurance |
| **MTR** | Training |
| **MOP** | Operations |

No requiere reorganizar los dominios actuales.

---

## 15 · Publicación

La arquitectura está diseñada para publicarse en:

| Motor | Uso |
|-------|-----|
| **Portal web** | Flask `/docs/` · producción futura |
| **GitHub Pages** | Sitio estático |
| **Docusaurus / MkDocs** | Portal con búsqueda |
| **Notion** | Lectura interna |
| **PDF** | Export por manual |

La **estructura permanece igual** independientemente del motor utilizado.

---

## 16 · Reglas para nuevos documentos

Antes de crear un documento, verificar:

- [ ] ¿Existe ya el tema?
- [ ] ¿Debe ser un capítulo o un apéndice?
- [ ] ¿Pertenece al dominio correcto?
- [ ] ¿Tiene referencias cruzadas?
- [ ] ¿Respeta la plantilla oficial?

> Si alguna respuesta es **no**, el documento **no debe publicarse**.

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-01](01-introduccion-portal.md) | Filosofía documental |
| [MDO-03](03-guia-usuarios.md) | Guía para usuarios del portal *(planificado)* |
| [MRG](/mrg/) | Manual funcional |
| [MCM](/mcm/) | Manual comercial |
| [MKT](/mkt/) | Marketing |
| [MAG](/mag/) | API |
| [MSD](/msd/) | Portal de desarrolladores |
| [MPA](/mpa/) | Arquitectura de plataforma |

---

## Exit Criteria

- [x] Arquitectura documental definida
- [x] Dominios organizados
- [x] Convenciones de archivos establecidas
- [x] Navegación estandarizada
- [x] Reglas de referencias cruzadas documentadas
- [x] Estrategia de versionado definida

---

## Filosofía del capítulo

Una buena arquitectura documental hace que la información sea **fácil de encontrar, mantener y ampliar**.

Cada nuevo capítulo debe integrarse de forma natural, sin romper la estructura existente ni generar duplicidad.

En Roustix, la documentación evoluciona igual que la plataforma: **modular, consistente y preparada para crecer**.

---

## Estado

| Aspecto | Estado |
|---------|--------|
| Arquitectura documental | ✅ Definida |
| Convenciones | ✅ Documentadas |
| Estructura de dominios | ✅ Definida |
| MDO-02 | ✅ Entregado |
| Sprint 13 | 🚧 En progreso |
