# MDO-06 · Catálogo Documental

**Código:** MDO-06 · Sprint 13.6 · **Entregado**

> La documentación de Roustix es un producto vivo. El catálogo documental permite conocer **qué manual existe**, cuál es su estado, su versión, sus dependencias y quién es responsable de mantenerlo.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-01](01-introduccion-portal.md) · [MDO-02](02-arquitectura-documentacion.md) · [MDO-03](03-guia-usuarios.md) · [MDO-04](04-guia-colaboradores.md) · [MDO-05](05-versionado-releases.md)

---

## Objetivo del capítulo

Definir el **Catálogo Documental Oficial** de Roustix: organización, clasificación y reglas de mantenimiento.

Este catálogo constituye el **índice maestro** de toda la documentación técnica, funcional, comercial y de diseño de la plataforma.

→ Registro vivo: [VERSIONS.md](/docs/VERSIONS.md) · Portal: [/docs/](/docs/)

---

## 1 · Filosofía

La documentación debe poder responder rápidamente:

| Pregunta |
|----------|
| ¿Existe este documento? |
| ¿Cuál es su versión? |
| ¿Está vigente? |
| ¿Qué manual debo leer? |
| ¿Quién es el responsable? |
| ¿Qué otros documentos dependen de él? |

El catálogo evita **duplicidad**, documentos huérfanos y referencias rotas.

---

## 2 · Estructura general

La documentación se organiza por **Suites Documentales**.

| Código | Manual | Propósito | URL |
|--------|--------|-----------|-----|
| **MPA** | Platform Architecture | Arquitectura general | [/mpa/](/mpa/) |
| **MAG** | API Guide | APIs y contratos | [/mag/](/mag/) |
| **MSD** | Developer Portal | SDK, ejemplos y sandbox | [/msd/](/msd/) |
| **MRG** | Product Guide | Operación del producto | [/mrg/](/mrg/) |
| **MCM** | Commercial Manual | Ventas | [/mcm/](/mcm/) |
| **MKT** | Marketing Assets | Marketing | [/mkt/](/mkt/) |
| **MUX** | UX Manual | Experiencia de usuario | [/mux/](/mux/) |
| **MDL** | Design Language | Diseño visual | [/mdl/](/mdl/) |
| **MBB** | Brand Book | Marca | [/brandbook/](/brandbook/) |
| **MRL** | Report Language | Reportes PDF | [/mrl/](/mrl/) |
| **MDO** | Documentation Operations | Gobierno documental | [/mdo/](/mdo/) |

Cada suite posee:

- Índice propio (`index.html` / README)
- Capítulos (`chapters/`)
- Anexos (`appendix/`)
- Materiales (`materials/`)
- Recursos compartidos (`assets/`)

---

## 3 · Clasificación documental

| Nivel | Tipo | Ejemplo |
|-------|------|---------|
| **Nivel 1** | Manual | MRG |
| **Nivel 2** | Capítulo | MRG-04 |
| **Nivel 3** | Apéndice | `appendix/` |
| **Nivel 4** | Material | `materials/` |
| **Nivel 5** | Recursos | `assets/` |

---

## 4 · Catálogo maestro

**Suite documental:** **v1.13.0** · Actualizado: 2026-07-10

| Manual | Estado | Versión | Cobertura | Madurez |
|--------|--------|---------|-----------|---------|
| **MPA** | ✔ Congelado | v1.0 | 🟢 Completa | Nivel 5 |
| **MAG** | ✅ Activo | v1.0.12 | 🟢 Completa | Nivel 4 |
| **MSD** | ✅ Sprint 9 | v1.0.0 | 🟢 Completa | Nivel 4 |
| **MRG** | ✅ v1 entregado | v1.0.0 | 🟢 Completa | Nivel 4 |
| **MCM** | ✅ v1 entregado | v1.0.0 | 🟢 Completa | Nivel 4 |
| **MKT** | ✅ Sprint 12 | v1.0.0 | 🟢 Completa | Nivel 4 |
| **MUX** | ✔ Congelado | v1.2 | 🟢 Completa | Nivel 5 |
| **MDL** | ✔ Congelado | v1.0 | 🟢 Completa | Nivel 5 |
| **MBB** | ✔ Congelado | v2.0 | 🟢 Completa | Nivel 5 |
| **MRL** | ✔ Sprint 7 | v1.0.1 | 🟡 Parcial | Nivel 3 |
| **MDO** | 🟡 Sprint 13 | v1.0.0 | 🟢 Completa | Nivel 4 |
| **Developer** | 🟡 En curso | — | 🔴 Pendiente | Nivel 1 |
| **Release Notes** | Activo | — | 🟡 Parcial | Nivel 2 |

> **Fuente única de verdad:** [VERSIONS.md](/docs/VERSIONS.md) — este capítulo describe la política; el registro numérico vive allí.

→ Matriz de madurez: [MDO-05 §14](05-versionado-releases.md#14--matriz-de-madurez-documental)

---

## 5 · Información mínima por manual

Todo manual debe declarar:

| Campo | Obligatorio |
|-------|-------------|
| Código | Sí |
| Nombre | Sí |
| Objetivo | Sí |
| Audiencia | Sí |
| Estado | Sí |
| Versión | Sí |
| Responsable | Sí |
| Fecha | Sí |
| Dependencias | Sí |
| Índice | Sí |
| Changelog | Sí |

### Ejemplo · MRG

| Campo | Valor |
|-------|-------|
| **Código** | MRG |
| **Nombre** | Roustix Reference Guide |
| **Versión** | 1.0.0 |
| **Estado** | ✅ Publicado |
| **Responsable** | Equipo Producto |
| **Dependencias** | MPA · MAG · MUX |
| **URL** | [/mrg/](/mrg/) |
| **Changelog** | [mrg/changelog.md](/mrg/changelog.md) |

---

## 6 · Metadatos por capítulo

Cada capítulo comienza con:

- Código
- Estado / Sprint
- Versión *(del manual)*
- Objetivo
- Prerequisitos
- Cross references

**Ejemplo:**

```markdown
# MCM-03 · Sectores y mercados

**Código:** MCM-03 · Sprint 11.3 · **Entregado**
**Prerequisitos:** MCM-01 · MCM-02
```

> En portal, el estado operativo sigue el ciclo [MDO-05 §5](05-versionado-releases.md#5--ciclo-de-vida-de-un-documento): hasta **✅ Publicado** no es referencia oficial externa.

---

## 7 · Relaciones entre documentos

Todo documento debe indicar sus **referencias**.

**Ejemplo · MRG:**

```
MRG
│
├── depende de MPA
├── usa MAG
├── usa MRL
└── referencia MUX
```

| Manual | Relaciones típicas |
|--------|-------------------|
| **MRG** | ← MPA · → MAG · MRL · MUX |
| **MCM** | ← MRG · → MKT · MBB |
| **MKT** | ← MCM · MBB · → MTX-CASE |
| **MAG** | ← MPA · → MSD |
| **MDO** | Gobierna todos |

→ Matriz: [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md) · Compatibilidad: [MDO-05 §13](05-versionado-releases.md#13--política-de-compatibilidad-entre-manuales)

---

## 8 · Estado documental

Cada documento utiliza el ciclo oficial:

| Estado | Significado |
|--------|-------------|
| 📋 **Planificado** | Existe en roadmap |
| 🟡 **En desarrollo** | En construcción |
| 🔄 **Revisión técnica** | Validación funcional |
| 📝 **Revisión editorial** | Validación documental |
| ✅ **Publicado** | Oficial |
| 📦 **Archivado** | Histórico |
| ❌ **Obsoleto** | Ya no aplica |

---

## 9 · Índice automático

El portal documental debe generar automáticamente *(MDO-08 · roadmap)*:

- Manuales disponibles
- Capítulos por manual
- Última versión
- Fecha de actualización
- Estado
- Responsable

**Hoy:** el índice maestro visual está en [/docs/](/docs/) · registro en [VERSIONS.md](/docs/VERSIONS.md).

```
/docs
├── /brandbook  MBB
├── /mdl        MDL
├── /mux        MUX
├── /mpa        MPA
├── /mag        MAG
├── /msd        MSD
├── /mrg        MRG
├── /mcm        MCM
├── /mkt        MKT
├── /mrl        MRL
└── /mdo        MDO
```

---

## 10 · Navegación

Cada capítulo debe incluir **navegación estándar**:

```
← Capítulo anterior    Índice del manual    Capítulo siguiente →
```

Y bloque **Relacionado** con manuales enlazados (MRG · MCM · MPA · MAG · MUX…).

→ Convención: [MDO-02 §7](02-arquitectura-documentacion.md#7--navegación)

---

## 11 · Convenciones de nombres

Nomenclatura uniforme:

```
chapters/
├── 01-intro.md
├── 02-arquitectura.md
└── 03-producto.md

materials/
appendix/
assets/
```

**Evitar:**

| ❌ No usar |
|-----------|
| `nuevo2.md` |
| `manual-final.docx` |
| `capitulo_ok.md` |

→ Patrón: `{NN}-{slug-descriptivo}.md` · [MDO-02 §6](02-arquitectura-documentacion.md#6--convención-de-archivos)

---

## 12 · Cobertura documental

El catálogo muestra el **nivel de cobertura** por manual.

| Cobertura | Significado |
|-----------|-------------|
| 🟢 **Completa** | Manual finalizado · v1.0+ |
| 🟡 **Parcial** | En desarrollo · capítulos pendientes |
| 🔴 **Pendiente** | Sin documentación estructurada |

### Cobertura actual (Sprint 13.6)

| Manual | Capítulos | Cobertura |
|--------|-----------|-----------|
| MRG | 10+ | 🟢 |
| MCM | 10 | 🟢 |
| MKT | 10 | 🟢 |
| MDO | 10 / 10 | 🟢 |
| MSD | 8+ | 🟢 |
| MAG | 9+ | 🟢 |
| Developer | — | 🔴 |

---

## 13 · Dashboard documental (Roadmap)

En futuras versiones el portal mostrará *(MDO-08 · MDO-09)*:

| Indicador |
|-----------|
| Manuales publicados |
| Capítulos por sprint |
| Cobertura documental |
| Referencias rotas |
| Documentos pendientes de revisión |
| Manuales sin actualizar |
| Tiempo promedio entre versiones |
| Estado por suite documental |

Estos indicadores facilitarán la **gobernanza** y la planificación editorial.

---

## 14 · Gobernanza del catálogo

El Catálogo Documental es administrado por el **Equipo de Documentación Roustix** y constituye la única fuente oficial para conocer el estado de cada manual.

Toda incorporación, modificación o retiro de documentos debe reflejarse **primero** en [VERSIONS.md](/docs/VERSIONS.md) antes de publicarse en el portal.

### Reglas de gobernanza

1. No crear manuales fuera de las suites oficiales.
2. No reutilizar códigos de capítulos eliminados.
3. Mantener actualizadas las referencias cruzadas.
4. Registrar toda publicación en el `changelog.md` correspondiente.
5. Verificar consistencia con [MDO-05](05-versionado-releases.md) antes de liberar una nueva versión.

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-01](01-introduccion-portal.md) | Filosofía documental |
| [MDO-02](02-arquitectura-documentacion.md) | Arquitectura del portal |
| [MDO-03](03-guia-usuarios.md) | Uso del portal |
| [MDO-04](04-guia-colaboradores.md) | Estándares editoriales |
| [MDO-05](05-versionado-releases.md) | Versionado y ciclo de vida |
| [VERSIONS.md](/docs/VERSIONS.md) | Registro oficial · inventario |
| Todos los manuales | Estado documental y cobertura |

---

## Exit Criteria

- [x] Suites documentales catalogadas
- [x] Estructura documental definida
- [x] Estados y cobertura documentados
- [x] Reglas de nomenclatura establecidas
- [x] Relaciones entre manuales documentadas
- [x] Gobernanza del catálogo definida

---

## Filosofía del capítulo

La documentación de Roustix **no es una colección de archivos**. Es un **ecosistema organizado**, donde cada manual tiene un propósito, un responsable, un estado y una relación clara con el resto de la plataforma.

El Catálogo Documental es el **mapa** que permite navegar ese ecosistema de forma consistente, garantizando trazabilidad, mantenimiento y crecimiento ordenado.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| Contrato documental | ✅ Definido |
| Catálogo maestro | ✅ Implementado |
| Portal documental | 🟡 Integración continua |
| Gobernanza | ✅ Definida |
| MDO-06 | ✅ Entregado |
| Manual MDO | v1.0.0 · Sprint 13 ✅ |
| Sprint 13 | 🚧 En progreso |

---

← [MDO-05](05-versionado-releases.md) · [Índice MDO](/mdo/) · [MDO-07](07-roadmap-evolucion.md) →
