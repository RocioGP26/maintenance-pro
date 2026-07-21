# MSD-02-PORT · Developer Portal

**Código:** MSD-02-PORT · Sprint 9.2 · **Entregado**

> La API es el producto.  
> El Developer Portal es la puerta de entrada.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir el **Developer Portal oficial de Roustix** (Portal para Desarrolladores), el punto único desde el cual cualquier desarrollador puede:

- descubrir la plataforma
- autenticarse
- consultar la documentación
- probar la API
- descargar SDKs
- seguir la evolución del ecosistema

Si **MAG** define el contrato técnico, **MSD** define la **experiencia del desarrollador**.

---

## 1 · Filosofía

El Portal para Desarrolladores no es únicamente un sitio web.

Es la **interfaz oficial** entre Roustix y los integradores.

Debe permitir que un desarrollador pueda:

- entender la plataforma
- obtener un token
- realizar su primera llamada
- descargar el SDK
- consultar OpenAPI
- probar endpoints
- seguir cambios del contrato

**Todo desde un único lugar.**

→ [MSD-01 · Filosofía del ecosistema](01-filosofia-ecosistema.md)

---

## 2 · URL oficial

### Producción

```
https://developer.roustix.app
```

### Desarrollo

```
http://127.0.0.1:5000/msd/
```

```powershell
python run.py
```

El Developer Portal forma parte del ecosistema Roustix, pero mantiene una **identidad propia** orientada exclusivamente a desarrolladores.

| Recurso relacionado | URL local |
|---------------------|-----------|
| API | `http://127.0.0.1:5000/api/v1` |
| MAG (contrato) | `http://127.0.0.1:5000/mag/` |
| Docs suite | `http://127.0.0.1:5000/docs/` |

---

## Estado del Portal

| Aspecto | Valor |
|---------|-------|
| **Portal** | MSD v1.0.0 |
| **API** | MAG v1.0 |
| **OpenAPI** | v1.0 (core publicado) |
| **SDK** | Roadmap · estrategia MSD-04 ✅ |

---

## 3 · Estructura general

```
Developer Portal
│
├── Inicio
├── Quick Start
├── API Reference
├── OpenAPI
├── SDK
├── CLI
├── Sandbox
├── Changelog
├── Estado API
└── Comunidad
```

Cada sección responde a una necesidad distinta durante el **ciclo de integración**.

| Sección | Capítulo MSD | Fase |
|---------|--------------|------|
| Quick Start | MSD-07 | 📋 |
| OpenAPI · API Reference | MSD-03 | ▶️ Siguiente |
| SDK | MSD-04 | 📋 |
| CLI | MSD-05 | 📋 |
| Sandbox · Explorer | MSD-06 | 📋 |
| Colecciones | MSD-08 | 📋 |
| Publicación | MSD-09 | 📋 |

---

## 4 · Página principal

La portada resume todo el ecosistema.

```
ROUSTIX
Developer Portal

Toda la operación.
Una sola plataforma.

[ Comenzar ]

Quick Start    API Reference    OpenAPI    SDK    Sandbox
```

Debe permitir comenzar una integración en **menos de diez minutos**.

**Above the fold:**

1. Hero + CTA «Comenzar» → Quick Start
2. Accesos directos — Quick Start · API Reference · OpenAPI · SDK · Sandbox
3. Badge de versión API (`v1.0`) y estado operativo
4. Callout multi-tenant — JWT + `empresa_slug`

---

## 5 · Navegación

El menú principal mantiene la misma organización documental del ecosistema.

| Sección | Contenido |
|---------|-----------|
| **Quick Start** | Primera integración |
| **API** | Documentación MAG |
| **OpenAPI** | Especificación REST |
| **SDK** | Librerías oficiales |
| **CLI** | Herramienta de línea de comandos |
| **Sandbox** | Ambiente de pruebas |
| **Changelog** | Cambios del contrato |
| **Estado** | Disponibilidad de la API |

### Barra global

| Elemento | Destino |
|----------|---------|
| Logo · Roustix Developers | Inicio portal |
| Quick Start | MSD-07 |
| API Reference | MAG + OpenAPI UI |
| SDK | MSD-04 |
| Sandbox | MSD-06 |
| Changelog | Historial API · MSD |

---

## 6 · Integración con MAG

El Portal para Desarrolladores **no duplica** documentación.

**MAG** continúa siendo la referencia técnica.

**Ejemplo — API Reference · Maintenance Assets:**

```
Maintenance · Assets
Ver especificación → MAG-04
```

Cada recurso del portal enlaza directamente con el capítulo correspondiente.

| Recurso portal | Capítulo MAG |
|----------------|--------------|
| Autenticación | [MAG-02](/mag/chapters/02-autenticacion-jwt.md) |
| Multi-tenant | [MAG-03](/mag/chapters/03-multi-tenant.md) |
| Recursos REST | [MAG-04](/mag/chapters/04-recursos.md) |
| Errores | [MAG-06](/mag/chapters/06-manejo-errores.md) |
| Versionado | [MAG-07](/mag/chapters/07-versionado.md) |
| Webhooks | [MAG-08](/mag/chapters/08-webhooks.md) |
| Buenas prácticas | [MAG-10](/mag/chapters/10-limites-buenas-practicas.md) |

**Regla:** enlazar, nunca copiar contenido MAG al portal.

---

## 7 · Integración con OpenAPI

El Developer Portal utiliza **OpenAPI como fuente de información**.

```
openapi.v1.yaml
        │
        ▼
     Portal
        │
        ▼
Referencia interactiva
```

No existen definiciones manuales duplicadas.

La documentación visible debe **generarse desde el contrato OpenAPI**.

→ [MSD-03 · OpenAPI 3.1](03-openapi.md) · [`docs/api/openapi.v1.yaml`](../../api/openapi.v1.yaml)

---

## 8 · SDK oficiales

Desde el Portal para Desarrolladores podrán descargarse los **SDK oficiales**.

**Python:**

```bash
pip install roustix
```

**JavaScript:**

```bash
npm install @roustix/sdk
```

**PHP:**

```bash
composer require roustix/sdk
```

Cada SDK comparte exactamente el mismo contrato definido por **MAG**.

→ [MSD-04 · SDK oficiales](04-sdk-oficiales.md)

---

## 9 · Sandbox

El portal ofrece un ambiente de pruebas **aislado**.

| Elemento | Valor |
|----------|-------|
| Tenant | `empresa-demo` |
| Token | JWT temporal |
| Datos | Ficticios |
| Producción | Sin afectar |

Cada desarrollador puede experimentar libremente.

→ [MSD-06 · Sandbox](06-sandbox-explorer.md) · [MAG-03](/mag/chapters/03-multi-tenant.md)

---

## 10 · API Explorer

Cada endpoint podrá ejecutarse desde el navegador.

```http
GET /api/v1/me
```

```
[ Ejecutar ]
```

**Respuesta:**

```json
{
  "user": "...",
  "empresa": "..."
}
```

El Explorer utiliza el **mismo OpenAPI** publicado.

→ [MSD-06 · Sandbox & API Explorer](06-sandbox-explorer.md)

---

## 11 · Changelog

Todas las modificaciones públicas de la API aparecen registradas.

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 2026-07-10 | **v1.0.0** | Publicación inicial MAG · contrato `/api/v1` |
| — | v1.0.1 | Nuevo endpoint Inventory (planificado) |
| — | v1.1.0 | Webhooks implementados (planificado) |

El historial permite conocer la **evolución del contrato**.

→ [MAG-07 · Versionado](/mag/chapters/07-versionado.md) · [MSD changelog](../changelog.md)

---

## 12 · Estado de la API

El portal incorpora un **panel de disponibilidad**.

```
API REST
● Operativa
99.95%
```

**Información visible:**

- disponibilidad
- incidentes
- mantenimientos
- historial

> **Estado actual:** panel planificado · blueprint `/msd/` operativo en desarrollo.

---

## 13 · Documentación relacionada

El Portal para Desarrolladores concentra toda la documentación pública conectada.

```
MAG
├── API · JWT · Recursos · Versionado · Webhooks
MRL
MPA
MSD
```

| Manual | Rol en portal |
|--------|---------------|
| [MAG](/mag/) | Contrato API · guías profundas |
| [MRL](/mrl/) | Exportaciones · reportes |
| [MPA](/mpa/) | Arquitectura · [MPA-06](/mpa/chapters/06-integraciones.md) |
| [MSD](/msd/) | Este manual · herramientas |

Toda la documentación permanece **conectada** — sin silos.

---

## 14 · Diseño

El Developer Portal reutiliza el **Design System** de Roustix.

**Componentes:**

- Cards
- Sidebar
- Breadcrumb
- Hero
- Search
- Tabs
- Code Blocks
- Dark Mode

No existen estilos independientes. La identidad visual permanece **consistente**.

| Referencia | Manual |
|------------|--------|
| Marca | [MBB](/brandbook/) |
| UI | [MDL](/mdl/) · componentes `mtx-*` |
| Docs shell | Brand Book CSS · `msd-docs.css` |

---

## 15 · Arquitectura

Pipeline documental del Portal para Desarrolladores:

```
Markdown
      │
      ▼
  OpenAPI
      │
      ▼
Generador Docs
      │
      ▼
Flask Blueprint
      │
      ▼
Developer Portal
```

**Archivos actuales:**

| Archivo | Rol |
|---------|-----|
| `app/msd_routes.py` | Blueprint Flask · sirve `/msd/` |
| `docs/msd/` | Manual MSD · capítulos · catálogo HTML |
| `docs/api/openapi.v1.yaml` | Contrato machine-readable (MSD-03) |

Toda la documentación continúa viviendo como **archivos Markdown versionados** en el repositorio.

---

## 16 · Arquitectura del ecosistema

Relación entre los componentes del Developer Portal:

```
                 Developer Portal
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
     OpenAPI          MAG Docs        Quick Start
        │               │
        ▼               ▼
       SDK         API Reference
        │
        ▼
      Sandbox
```

Este diagrama resume cómo **MSD organiza** MAG, OpenAPI, SDK y sandbox antes de profundizar en cada capítulo.

---

## 17 · Roadmap

Versiones futuras del Developer Portal incorporarán:

```
Portal
├── Search
├── API Explorer
├── SDK
├── Sandbox
├── autenticación del desarrollador
├── API Keys
├── Playground
├── snippets automáticos
├── documentación por módulo
├── ejemplos interactivos
└── IA contextual
```

**Search** será uno de los componentes principales — acceso unificado a MAG, MSD, OpenAPI y guías.

| Fase | Entrega |
|------|---------|
| **Fase 0** ✅ | Blueprint `/msd/` · catálogo MSD |
| **Fase 1** | Nav completa · home con CTA · Search (básico) |
| **Fase 2** | OpenAPI UI · referencia interactiva (MSD-03) |
| **Fase 3** | Sandbox · API Explorer (MSD-06) |
| **Fase 4** | `developer.roustix.app` producción |

---

## 18 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | OpenAPI es la única fuente técnica |
| 2 | No duplicar documentación de MAG |
| 3 | Todo ejemplo debe ser ejecutable |
| 4 | El Quick Start debe mantenerse actualizado |
| 5 | Todo SDK debe generarse desde OpenAPI |
| 6 | El Portal es público |
| 7 | Todo cambio de API debe reflejarse en el Changelog |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-04 · Recursos REST](/mag/chapters/04-recursos.md) | Catálogo oficial de endpoints |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Evolución del contrato |
| [MSD-03 · OpenAPI](03-openapi.md) | Fuente del Portal |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Descarga de librerías oficiales |
| [MSD-07 · Quick Start](07-quick-start.md) | Primera integración |
| [Developer Docs (09)](/docs/developer/README.md) | Repo interno — no es el portal externo |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Existe el Portal del Desarrollador en `/msd/`
- [x] Toda la documentación pública (MAG, MSD, MPA y MRL) es accesible desde el Portal
- [ ] OpenAPI alimenta la referencia interactiva
- [ ] El Portal ofrece acceso a SDK, Sandbox y Quick Start
- [ ] Existe un Changelog oficial de la API en el portal
- [x] La navegación reutiliza el Design System de Roustix

**Documentación:** ✅ · **Funcionalidad completa:** 🟡 en progreso (MSD-03–07)

---

## Filosofía del capítulo

Una buena API necesita una buena documentación.

Un gran producto necesita una **excelente experiencia para desarrolladores**.

El Developer Portal convierte la documentación de Roustix en una **plataforma viva**, donde descubrir, aprender, integrar y evolucionar ocurren desde un único lugar. Es el **punto de entrada oficial** para todo desarrollador que construya sobre Roustix.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación actual** | 🟢 Blueprint `/msd/` operativo |
| **Fuente de datos** | Markdown + OpenAPI |
| **Compatibilidad** | MAG v1.0 |
| **Siguiente capítulo** | [MSD-04 · SDK oficiales](04-sdk-oficiales.md) |

---

→ [MSD-03-OAPI · OpenAPI 3.1](03-openapi.md)
