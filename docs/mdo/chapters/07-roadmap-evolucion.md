# MDO-07 · Roadmap y Evolución de la Documentación

**Código:** MDO-07 · Sprint 13.7 · **Entregado**

> La documentación de Maintix evoluciona junto con la plataforma. Cada nueva funcionalidad, módulo o servicio debe reflejarse en un **ecosistema documental coherente, versionado y mantenible**.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-01](01-introduccion-portal.md) · [MDO-02](02-arquitectura-documentacion.md) · [MDO-03](03-guia-usuarios.md) · [MDO-04](04-guia-colaboradores.md) · [MDO-05](05-versionado-releases.md) · [MDO-06](06-catalogo-documental.md)

---

## Objetivo del capítulo

Definir la **estrategia de evolución** de la documentación de Maintix: cómo crecerán los manuales, cómo se incorporarán nuevas suites documentales y cómo se mantendrá la consistencia del ecosistema a largo plazo.

Este capítulo establece la **hoja de ruta documental** para futuras versiones de Maintix Docs.

→ Catálogo actual: [MDO-06](06-catalogo-documental.md) · [VERSIONS.md](/docs/VERSIONS.md)

---

## 1 · Filosofía

La documentación **nunca está «terminada»**.

Cada versión del producto genera:

- Nuevos procesos
- Nuevas pantallas
- Nuevos módulos
- Nuevas APIs
- Nuevos casos de uso

La documentación debe evolucionar al mismo ritmo del producto para evitar la **deriva documental** (*documentation drift*), mediante responsables claros, revisiones periódicas y sincronización con los lanzamientos del producto.

---

## 2 · Principios de evolución

| Principio | Aplicación |
|-----------|------------|
| **Producto primero** | La documentación refleja el producto publicado |
| **Una única fuente de verdad** | Evitar contenido duplicado |
| **Versionado permanente** | Toda modificación queda registrada |
| **Documentación modular** | Cada manual evoluciona de forma independiente |
| **Compatibilidad** | Mantener referencias entre suites |
| **Escalabilidad** | Preparada para nuevos productos Maintix |

→ Compatibilidad entre manuales: [MDO-05 §13](05-versionado-releases.md#13--política-de-compatibilidad-entre-manuales)

---

## 3 · Roadmap documental

### Versión 1.0 · Fundación documental

Incluye:

- Arquitectura documental (MPA)
- Producto (MRG)
- Comercial (MCM)
- Marketing (MKT)
- API (MAG · MSD)
- UX (MUX)
- Diseño (MDL · MRL)
- Marca (MBB)
- Gobierno documental (MDO)

**Estado:** ✅ **Base completa** · Suite v1.13 · MDO en curso (Sprint 13)

### Versión 2.x · Consolidación

| Objetivo |
|----------|
| Portal documental público |
| Mejor buscador |
| Mejor navegación (sidebar · breadcrumb) |
| Casos prácticos |
| Videos · tutoriales |
| Centro de aprendizaje |

### Versión 3.x · Automatización

| Objetivo |
|----------|
| Documentación generada desde código |
| Integración CI/CD |
| Release Notes automáticas |
| Catálogo sincronizado con [VERSIONS.md](/docs/VERSIONS.md) |
| Validación automática de enlaces |
| Traducciones |

> La automatización de verificaciones, enlaces y metadatos reduce el esfuerzo manual y mantiene la documentación consistente conforme el producto crece.

### Versión 4.x · Ecosistema

Posibles expansiones:

- Academia Maintix
- Certificaciones
- Portal Partners
- Knowledge Base
- Casos interactivos · playbooks

---

## 4 · Evolución por manual

| Manual | Evolución prevista |
|--------|-------------------|
| **MPA** | Nuevos servicios y arquitectura |
| **MAG** | API v2 · Webhooks · SDK |
| **MSD** | Sandbox completo |
| **MRG** | Nuevos módulos |
| **MCM** | Nuevas estrategias comerciales |
| **MKT** | Campañas y activos |
| **MUX** | Nuevos recorridos UX |
| **MDL** | Componentes UI |
| **MBB** | Evolución de marca |
| **MRL** | Nuevos tipos de reportes |
| **MDO** | Gobierno · portal · métricas |

---

## 5 · Incorporación de nuevos módulos

Cuando se publique un **nuevo módulo** del producto deberá actualizarse, como mínimo:

| Documento | Acción |
|-----------|--------|
| **MPA** | Arquitectura |
| **MRG** | Operación |
| **MAG** | API |
| **MSD** | Ejemplos |
| **MCM** | Comercialización |
| **MKT** | Material marketing |
| **MUX** | Experiencia usuario |
| **MDL** | Componentes |
| **MRL** | Reportes |

> **Ningún módulo debe considerarse terminado** sin su documentación correspondiente.

---

## 6 · Ciclo de crecimiento

```
Idea
    ↓
Diseño
    ↓
Desarrollo
    ↓
Documentación
    ↓
QA
    ↓
Publicación
    ↓
Retroalimentación
    ↓
Nueva versión
```

La documentación forma parte del **ciclo de desarrollo**, no es una actividad posterior.

→ Publicación: [MDO-05 §7](05-versionado-releases.md#7--flujo-de-publicación)

---

## 7 · Métricas de madurez documental

| Indicador | Objetivo |
|-----------|----------|
| Cobertura documental | > 95 % |
| Referencias rotas | 0 |
| Documentos sin responsable | 0 |
| Documentos obsoletos | < 5 % |
| Tiempo medio de actualización | < 1 sprint |
| Capítulos con changelog | 100 % |

→ Matriz de madurez: [MDO-05 §14](05-versionado-releases.md#14--matriz-de-madurez-documental) · Dashboard: [MDO-06 §13](06-catalogo-documental.md#13--dashboard-documental-roadmap)

---

## 8 · Integración con el ciclo de producto

Cada Sprint debe responder:

| Pregunta |
|----------|
| ¿Qué cambió? |
| ¿Qué documentación requiere actualización? |
| ¿Qué manuales deben publicarse? |
| ¿Qué referencias deben modificarse? |

> Una versión del producto **no debe considerarse cerrada** sin revisar su impacto documental.

---

## 9 · Roadmap de nuevos manuales

La arquitectura documental permite incorporar **nuevas suites** sin modificar las existentes.

| Código | Manual |
|--------|--------|
| **MTR** | Training Manual |
| **MSP** | Support Playbooks |
| **MQA** | Quality Assurance Manual |
| **MOP** | Operations Manual |
| **MSEC** | Security Manual |

La estructura modular facilita ampliar el ecosistema sin reorganizar el contenido existente, siempre que exista arquitectura de información consistente y **propietarios definidos**.

→ Escalabilidad: [MDO-02 §14](02-arquitectura-documentacion.md#14--escalabilidad)

---

## 10 · Objetivo a largo plazo

La visión documental de Maintix es un ecosistema donde **cualquier persona** encuentre la información correcta según su perfil:

```
Cliente → Comercial → Implementador → Administrador
    → Desarrollador → Partner → Equipo interno
```

Cada perfil encuentra exactamente el manual que necesita.

→ Guía por perfil: [MDO-03 §2](03-guia-usuarios.md#2--quién-debería-usar-el-portal)

---

## 11 · Criterios de evolución

Toda incorporación documental deberá cumplir:

- [ ] Mantener la nomenclatura oficial
- [ ] Definir propietario y audiencia
- [ ] Registrar versión inicial
- [ ] Incluir referencias cruzadas
- [ ] Publicarse mediante el proceso [MDO-05](05-versionado-releases.md)
- [ ] Incorporarse al [Catálogo Documental (MDO-06)](06-catalogo-documental.md)

---

## 12 · Visión del ecosistema

La documentación futura de Maintix aspira a un **portal único** que integre:

| Capa |
|------|
| Manuales · APIs · Casos de uso |
| Tutoriales · Videos · Academia |
| Base de conocimiento · Material comercial |
| Centro para partners · Historial de versiones |
| **Buscador unificado** |

Todo accesible desde un único portal documental.

→ Portal shell: [MDO-08](08-portal-docs.md) · Búsqueda: [MDO-09](09-busqueda.md)

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-01](01-introduccion-portal.md) | Filosofía documental |
| [MDO-02](02-arquitectura-documentacion.md) | Arquitectura del portal |
| [MDO-03](03-guia-usuarios.md) | Uso del portal |
| [MDO-04](04-guia-colaboradores.md) | Estándares editoriales |
| [MDO-05](05-versionado-releases.md) | Publicación y ciclo de vida |
| [MDO-06](06-catalogo-documental.md) | Catálogo documental |
| Todos los manuales Maintix | Evolución coordinada |

---

## Exit Criteria

- [x] Roadmap documental definido
- [x] Estrategia de crecimiento establecida
- [x] Integración con el ciclo del producto documentada
- [x] Evolución por manual especificada
- [x] Métricas de madurez definidas
- [x] Visión de largo plazo documentada

---

## Filosofía del capítulo

La documentación **no acompaña al producto: es parte del producto**.

Cada nueva capacidad de Maintix debe ir acompañada por documentación clara, versionada y mantenible. El objetivo final no es solo publicar manuales, sino construir un **ecosistema de conocimiento** que permita a clientes, partners y equipos internos aprender, implementar y evolucionar la plataforma con la misma velocidad con la que evoluciona el software.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| Roadmap documental | ✅ Definido |
| Gobierno de evolución | ✅ Implementado |
| Integración con producto | ✅ Establecida |
| Visión de largo plazo | ✅ Documentada |
| MDO-07 | ✅ Entregado |
| Manual MDO | v0.7.0 · objetivo v1.0.0 al cierre Sprint 13 |
| Sprint 13 | 🚧 En progreso |

---

← [MDO-06](06-catalogo-documental.md) · [Índice MDO](/mdo/) · [MDO-08](08-portal-docs.md) →
