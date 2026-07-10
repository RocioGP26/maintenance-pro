# MSD-09-PUB · Publicación

**Código:** MSD-09-PUB · Sprint 9.9 · **Entregado**

> Una plataforma para desarrolladores solo está completa cuando puede **distribuirse, instalarse y mantenerse** de forma oficial.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir el proceso oficial de **publicación, distribución y mantenimiento** de los artefactos para desarrolladores de Maintix: documentación, OpenAPI, SDK, CLI y colecciones.

**MSD-09 establece el ciclo de vida del ecosistema de desarrollo**, garantizando que todos los componentes evolucionen de forma sincronizada con MAG y con cada versión de la plataforma.

---

## 1 · Filosofía

Publicar no es subir archivos.

Es **distribuir un ecosistema coherente**.

Cada versión de Maintix debe publicar simultáneamente:

```
Código / MAG
      │
      ▼
   OpenAPI
      │
      ▼
     SDK
      │
      ▼
     CLI
      │
      ▼
Colecciones
      │
      ▼
Developer Portal
```

Toda la documentación debe representar **exactamente** el estado de la plataforma.

---

## 2 · Artefactos oficiales

Cada versión publica los siguientes componentes:

| Artefacto | Estado documental | Estado distribución |
|-----------|-------------------|---------------------|
| **OpenAPI 3.1** | ✅ Oficial | 🟢 `openapi.v1.yaml` · `/api/v1/openapi.json` |
| **SDK Python** | ✅ Estrategia MSD-04 | 📋 PyPI pendiente |
| **SDK JavaScript** | ✅ Estrategia MSD-04 | 📋 npm pendiente |
| **SDK PHP** | ✅ Estrategia MSD-04 | 📋 Packagist pendiente |
| **Maintix CLI** | ✅ Estrategia MSD-05 | 📋 PyPI pendiente |
| **Colección Postman** | ✅ Snapshot v1 | 🟢 `docs/api/collections/` |
| **Colección Insomnia** | ✅ Snapshot v1 | 🟢 `docs/api/collections/` |
| **Developer Portal** | ✅ MSD-02 | 🟡 `/msd/` · 📋 `developer.maintix.app` |

Todos siguen el **mismo número de versión del ecosistema** cuando se publiquen paquetes (`1.x` ↔ MAG v1).

---

## 3 · Plataformas de publicación

| Artefacto | Plataforma |
|-----------|------------|
| SDK Python | **PyPI** (`maintix`) |
| SDK JavaScript | **npm** (`@maintix/sdk`) |
| SDK PHP | **Packagist** (`maintix/sdk`) |
| CLI | **PyPI** (`maintix-cli`) |
| OpenAPI | Repositorio + `GET /api/v1/openapi.json` |
| Colecciones | `docs/api/collections/` + Portal |
| Documentación | **Developer Portal** · Maintix Docs |

---

## 4 · Versionado

Todos los componentes siguen el contrato definido en [MAG-07](/mag/chapters/07-versionado.md):

| Componente | Versionado |
|------------|------------|
| API | **MAG v1** |
| OpenAPI | **v1** (`info.version: 1.0.0`) |
| SDK | **1.x** |
| CLI | **1.x** |
| Colecciones | **v1** (`Maintix API v1`) |
| MSD (docs) | **v1.0.0** |

**No pueden existir** SDK o CLI oficiales incompatibles con la versión vigente de MAG.

---

## 5 · Flujo de publicación

```
Nueva versión Maintix
          │
          ▼
   Actualizar MAG
          │
          ▼
   Generar OpenAPI
          │
          ▼
    Generar SDK
          │
          ▼
    Generar CLI
          │
          ▼
 Generar colecciones
          │
          ▼
Publicar Developer Portal
          │
          ▼
   Release oficial
```

El flujo garantiza que **todos los artefactos permanezcan sincronizados**.

---

## 6 · Integración continua

La publicación forma parte del **pipeline CI/CD** (objetivo operativo MSD v1.0):

Cada release ejecuta automáticamente:

1. validación OpenAPI (Spectral · Prism)
2. pruebas del SDK
3. pruebas de la CLI
4. generación de colecciones
5. despliegue del Portal
6. publicación de documentación

**Solo si todas las verificaciones son exitosas** se realiza la publicación.

| Etapa | Herramienta |
|-------|-------------|
| Lint OpenAPI | Spectral |
| Contract tests | Prism · sandbox |
| SDK tests | pytest · jest · phpunit |
| Colecciones | openapi2postmanv2 |
| Portal | deploy estático / CDN |

> **Estado:** pipeline documentado · automatización en roadmap post MSD v1.0 doc.

---

## 7 · Changelog

Cada publicación incorpora un **historial de cambios**.

**Ejemplo:**

```
Maintix SDK 1.2.0

+ Nuevo módulo Inventory
+ Nuevos endpoints Work Orders
+ Correcciones CLI
+ Mejoras OpenAPI
```

Los cambios **incompatibles** solo aparecen en **nuevas versiones mayores** (MAG v2 · SDK 2.x).

Fuentes oficiales:

- [MSD changelog](../changelog.md)
- [MAG changelog](/mag/changelog.md)
- Changelog en Developer Portal

---

## 8 · Compatibilidad

Todos los artefactos mantienen compatibilidad con la **misma versión de la API**:

```
MAG v1
│
├── OpenAPI v1
├── SDK 1.x
├── CLI 1.x
└── Colecciones v1
```

**No se mezclan versiones mayores.**

---

## 9 · Distribución

Los desarrolladores disponen de un **único punto de acceso**:

```
https://developer.maintix.app
```

**Local (transitorio):** http://127.0.0.1:5000/msd/

Desde el Portal pueden:

- consultar la documentación
- descargar OpenAPI
- instalar SDK
- instalar la CLI
- descargar colecciones
- acceder al Sandbox
- revisar el changelog

El Portal es el **centro del ecosistema** para desarrolladores.

→ [MSD-02 · Developer Portal](02-developer-portal.md)

---

## 10 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Publicar todos los artefactos **conjuntamente** |
| 2 | Mantener el mismo versionado entre componentes |
| 3 | No distribuir SDK generados manualmente |
| 4 | Validar OpenAPI **antes** de publicar |
| 5 | Actualizar la documentación en cada versión |
| 6 | Mantener un changelog completo |
| 7 | Automatizar el proceso mediante CI/CD |

---

## 11 · Roadmap

Evolución prevista del ecosistema:

- publicación automática en **GitHub Releases**
- firma digital de paquetes
- **Docker** oficial para el Sandbox
- cliente **MCP** para IA y agentes
- SDK para Go, Java y C#
- **Marketplace** de integraciones
- registro de plugins oficiales

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MSD-02 · Developer Portal](02-developer-portal.md) | Centro de distribución |
| [MSD-03 · OpenAPI](03-openapi.md) | Especificación oficial |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Paquetes publicados |
| [MSD-05 · CLI](05-cli.md) | Cliente terminal oficial |
| [MSD-08 · Colecciones](08-colecciones.md) | Herramientas de prueba |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Política de versiones |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Proceso de publicación documentado (este capítulo)
- [x] OpenAPI publicado en repo y runtime (`/api/v1/openapi.json`)
- [ ] OpenAPI se publica automáticamente con cada versión (CI)
- [ ] SDK oficiales en PyPI, npm y Packagist
- [ ] CLI oficial publicada y versionada
- [x] Colecciones Postman e Insomnia en repo (snapshot v1)
- [ ] Colecciones generadas automáticamente en CI
- [ ] Developer Portal producción centraliza todos los artefactos
- [ ] Pipeline CI/CD automatiza la publicación completa
- [x] Changelog oficial MSD documentado

**MSD v1.0 documental:** ✅ · **Publicación operativa de paquetes:** 📋 roadmap

---

## Filosofía del capítulo

Una plataforma moderna no termina en su API. Su verdadero valor aparece cuando cualquier desarrollador puede **descubrirla, instalar sus herramientas, integrarlas y mantenerlas** con confianza.

**MSD-09 cierra el ecosistema para desarrolladores de Maintix**, unificando documentación, OpenAPI, SDK, CLI, Sandbox y Portal bajo un proceso de publicación coherente, automatizado y versionado.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Developer Portal** | 🟡 `/msd/` operativo · 📋 producción |
| **OpenAPI** | 🟢 v1.0 core publicado |
| **SDK** | 📋 Estrategia ✅ · paquetes pendientes |
| **CLI** | 📋 Especificación ✅ · PyPI pendiente |
| **Colecciones** | 🟢 Snapshot v1 en repo |
| **Publicación automatizada** | 📋 Roadmap CI/CD |
| **Resultado** | ✅ **MSD v1.0 documentación completa** |

---

## MSD v1.0 · Índice completo

| Código | Capítulo | Estado |
|--------|----------|--------|
| MSD-01 | Filosofía del ecosistema | ✅ |
| MSD-02 | Developer Portal | ✅ |
| MSD-03 | OpenAPI 3.1 | ✅ |
| MSD-04 | SDK oficiales | ✅ |
| MSD-05 | CLI | ✅ |
| MSD-06 | Sandbox y API Explorer | ✅ |
| MSD-07 | Quick Start | ✅ |
| MSD-08 | Colecciones Postman e Insomnia | ✅ |
| MSD-09 | Publicación | ✅ |

### Sprint 9 · Estado

**Sprint 9 (MSD v1.0) queda 100% completado en documentación.**

Con este sprint, Maintix dispone de un **ecosistema completo para desarrolladores** — comparable a plataformas SaaS consolidadas:

- contrato API (**MAG v1.0**)
- especificación **OpenAPI 3.1**
- **SDK** · **CLI** · **Sandbox**
- **Developer Portal** · **Quick Start**
- **colecciones** y **proceso de publicación**

MAG describe el contrato. **MSD entrega la experiencia.**

---

→ [Índice MSD](/msd/) · [MAG v1.0](/mag/) · [Maintix Docs](/docs/)
