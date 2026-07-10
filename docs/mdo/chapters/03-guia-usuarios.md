# MDO-03 · Guía de Uso del Portal de Documentación

**Código:** MDO-03 · Sprint 13.3 · **Entregado**

> La documentación de Maintix está diseñada para responder preguntas rápidamente. Este capítulo explica cómo **navegar el portal**, encontrar información y utilizar correctamente la suite documental.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-01 · Introducción](01-introduccion-portal.md) · [MDO-02 · Arquitectura](02-arquitectura-documentacion.md)

---

## Objetivo del capítulo

Guiar a **usuarios, clientes, partners y equipos internos** en el uso del portal de documentación oficial de Maintix, explicando cómo está organizado, cómo encontrar información y cómo interpretar la estructura documental.

---

## 1 · Filosofía del portal

El portal de documentación está pensado para que cualquier persona pueda encontrar una respuesta **sin depender del equipo de soporte**.

Los principios de navegación son:

| Principio | Significado |
|-----------|-------------|
| **Simple** | La información debe encontrarse en pocos clics |
| **Consistente** | Todos los manuales comparten la misma estructura |
| **Orientado por audiencia** | Cada perfil encuentra primero la información que necesita |
| **Conectado** | Los documentos se relacionan entre sí mediante referencias |
| **Actualizado** | El contenido refleja el estado actual del producto |

---

## 2 · ¿Quién debería usar el portal?

| Perfil | Manual recomendado |
|--------|-------------------|
| Cliente final | [MRG](/mrg/) |
| Administrador de empresa | [MRG](/mrg/) |
| Implementador | [MRG](/mrg/) + [MCM](/mcm/) |
| Comercial | [MCM](/mcm/) |
| Marketing | [MKT](/mkt/) |
| Partner | [MCM](/mcm/) + [MKT](/mkt/) |
| Desarrollador | [MAG](/mag/) + [MSD](/msd/) |
| Arquitecto de software | [MPA](/mpa/) |
| Equipo interno Maintix | Toda la suite |

---

## 3 · Página principal

La página inicial del portal presenta los **principales manuales**.

**Portal de Documentación** → [/docs/](/docs/)

| Dominio | Manual |
|---------|--------|
| Arquitectura | [MPA](/mpa/) |
| API | [MAG](/mag/) |
| Developer | [MSD](/msd/) |
| Producto | [MRG](/mrg/) |
| Comercial | [MCM](/mcm/) |
| Marketing | [MKT](/mkt/) |
| Documentación | [MDO](/mdo/) |

Desde esta página el usuario puede acceder **directamente** al dominio que necesita.

---

## 4 · Navegación por manuales

Cada manual mantiene la **misma estructura**.

```
Manual
│
├── Introducción
├── Índice
├── Capítulos
├── Apéndices
├── Materiales
└── Changelog
```

Esto permite cambiar de un manual a otro **sin aprender una navegación diferente**.

---

## 5 · Navegación por capítulos

Cada capítulo contiene:

- Código único
- Estado
- Objetivo
- Desarrollo
- Relación con otros documentos
- Exit Criteria
- Enlaces al capítulo anterior y siguiente

**Ejemplo:**

```
← MRG-04          Índice          MRG-06 →
```

---

## 6 · Uso del buscador

El buscador es el **punto de entrada recomendado** cuando el usuario conoce el tema, pero no el manual.

Se puede buscar por:

- Código del documento
- Nombre del capítulo
- Palabras clave
- Funcionalidad
- Concepto

**Ejemplos de búsqueda:**

| Término | Puede llevar a |
|---------|----------------|
| OT | MRG · mantenimiento |
| Inventario | MRG-03 |
| Tenant | MRG · MAG |
| CRM | MRG · MCM |
| JWT | MAG · MSD |
| Preventivo | MRG |
| Dashboard | MRG · MRL |
| Partners | MCM · MKT |
| API | MAG · MSD |

> **Nota:** El buscador unificado del portal está planificado en [MDO-08](08-busqueda.md). Hoy se puede buscar por código en [NOMENCLATURE.md](/docs/NOMENCLATURE.md) o usar la búsqueda del navegador dentro de cada manual.

---

## 7 · Búsqueda por código

Todos los documentos poseen un **identificador único**.

| Código | Documento |
|--------|-----------|
| **MRG-03** | Inventario |
| **MAG-02** | Autenticación |
| **MCM-04** | Planes SaaS |
| **MKT-05** | Landing Page |
| **MDO-02** | Arquitectura documental |

Buscar por código suele ser el **método más rápido** para usuarios frecuentes.

→ Índice de códigos: [docs/NOMENCLATURE.md](/docs/NOMENCLATURE.md)

---

## 8 · Referencias cruzadas

Los documentos incluyen **enlaces relacionados**.

**Ejemplo:**

```
MRG-02
  ↓
MAG-04
  ↓
MSD Tutorial
```

Esto evita duplicar información y permite **profundizar** según el perfil del lector.

→ Reglas: [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md) · [MDO-02 §8](02-arquitectura-documentacion.md#8--referencias-cruzadas)

---

## 9 · Cómo interpretar el estado de un documento

Cada capítulo indica su **estado** en el ciclo de vida documental.

| Estado | Significado |
|--------|-------------|
| 📋 **Planificado** | Definido, pendiente de desarrollo |
| 🟡 **En desarrollo** | En construcción |
| 🔄 **Revisión técnica** | Producto valida exactitud |
| 📝 **Revisión editorial** | Documentación valida formato |
| ✅ **Publicado** | Completo · referencia oficial |
| 📦 **Archivado** | Conservado por razones históricas |
| ❌ **Obsoleto** | No utilizar |

> Antes de utilizar un documento como referencia oficial, **verificar su estado** (debe ser ✅ Publicado).

→ Matriz de madurez: [MDO-05 §14](05-versionado-releases.md#14--matriz-de-madurez-documental)

---

## 10 · Versiones

Cada documento muestra su **versión** y **fecha de actualización**.

| Campo | Ejemplo |
|-------|---------|
| Versión | `1.0.0` |
| Última actualización | Septiembre 2026 |

Si existen varias versiones, siempre se recomienda consultar la **más reciente**, salvo que se trabaje con una versión específica del producto.

→ Registro: [VERSIONS.md](/docs/VERSIONS.md)

---

## 11 · Recursos adicionales

Además de los capítulos principales, algunos manuales incluyen **recursos complementarios**.

| Recurso | Contenido |
|---------|-----------|
| **Apéndices** | Información especializada |
| **Materiales** | Plantillas y recursos reutilizables |
| **Assets** | Diagramas e imágenes |
| **Changelog** | Historial de cambios |

Estos recursos ayudan a profundizar **sin sobrecargar** los capítulos principales.

---

## 12 · Buenas prácticas de consulta

Para obtener mejores resultados:

1. Comenzar por el **índice** del manual correspondiente.
2. Utilizar el **buscador** antes de navegar manualmente.
3. Revisar los **documentos relacionados** cuando un tema abarque varias áreas.
4. Confirmar el **estado** y la **versión** del documento.
5. Consultar el **glosario** cuando aparezcan términos desconocidos.

---

## 13 · Preguntas frecuentes

### No sé en qué manual buscar

Comienza por [MDO-01](01-introduccion-portal.md) o utiliza el buscador del portal.

### Soy cliente y quiero aprender a usar Maintix

Consulta [MRG](/mrg/).

### Necesito integrar un sistema externo

Consulta [MAG](/mag/) y [MSD](/msd/).

### Quiero entender los planes comerciales

Consulta [MCM](/mcm/).

### Necesito materiales para marketing

Consulta [MKT](/mkt/).

### Quiero contribuir a la documentación

Consulta [MDO-04 · Guía para Colaboradores](04-guia-colaboradores.md).

---

## 14 · Flujo recomendado de navegación

### Cliente

```
Portal (/docs/)
    ↓
MRG
    ↓
Capítulo específico
    ↓
Documentos relacionados
```

### Comercial

```
Portal (/docs/)
    ↓
MCM
    ↓
MKT
    ↓
Material comercial
```

### Desarrollador

```
Portal (/docs/)
    ↓
MAG
    ↓
MSD
    ↓
Sandbox
    ↓
API
```

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MDO-01](01-introduccion-portal.md) | Introducción al portal |
| [MDO-02](02-arquitectura-documentacion.md) | Arquitectura documental |
| [MDO-04](04-guia-colaboradores.md) | Guía para colaboradores *(planificado)* |
| [MRG](/mrg/) | Guía funcional |
| [MCM](/mcm/) | Manual comercial |
| [MKT](/mkt/) | Marketing |
| [MAG](/mag/) | API |
| [MSD](/msd/) | Portal para desarrolladores |

---

## Exit Criteria

- [x] Uso del portal explicado
- [x] Navegación documentada
- [x] Buscador y referencias descritos
- [x] Estados y versiones explicados
- [x] Flujos de navegación por perfil definidos

---

## Filosofía del capítulo

Un buen portal de documentación **no solo almacena información**: guía al usuario hacia la respuesta correcta.

La documentación de Maintix está organizada para que cada perfil encuentre rápidamente lo que necesita, reduciendo la dependencia del soporte y favoreciendo una **adopción más rápida** de la plataforma.

> La mejor documentación es aquella que responde una pregunta **antes** de que el usuario tenga que hacerla.

---

## Estado

| Aspecto | Estado |
|---------|--------|
| Guía de uso del portal | ✅ Completa |
| Navegación por perfiles | ✅ Definida |
| Buenas prácticas de consulta | ✅ Documentadas |
| MDO-03 | ✅ Entregado |
| Sprint 13 | 🚧 En progreso |

---

← [MDO-02](02-arquitectura-documentacion.md) · [Índice MDO](/mdo/) · [MDO-04](04-guia-colaboradores.md) →
