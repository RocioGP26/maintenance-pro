# MSD-05-CLI · Maintix CLI

**Código:** MSD-05-CLI · Sprint 9.5 · **Entregado**

> Automatizar la integración también forma parte de la experiencia del desarrollador.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir la **interfaz oficial de línea de comandos (CLI)** de Maintix, permitiendo a desarrolladores, administradores y pipelines de automatización interactuar con la plataforma sin construir solicitudes HTTP manualmente.

La CLI utiliza el mismo contrato definido en **MAG v1.0** y el **SDK oficial** ([MSD-04](04-sdk-oficiales.md)), ofreciendo una experiencia consistente para desarrollo, pruebas y automatización.

---

## 1 · Filosofía

La CLI es el **puente entre la API y la automatización**.

No reemplaza el SDK ni el Portal para Desarrolladores.

Cada comando ejecuta operaciones utilizando **exactamente el mismo contrato REST**.

```
Usuario
      │
      ▼
 maintix-cli
      │
      ▼
 SDK Oficial
      │
      ▼
   OpenAPI
      │
      ▼
 API Maintix
```

La CLI es un **cliente oficial** de Maintix.

| Rol | Herramienta |
|-----|-------------|
| Exploración humana | Developer Portal · Quick Start |
| Integración en código | SDK |
| Scripts · CI/CD | **CLI** |

---

## 2 · Instalación

### Python (PyPI)

```bash
pip install maintix-cli
```

### Verificación

```bash
maintix --version
```

**Salida esperada:**

```
Maintix CLI 1.0.0
API MAG v1
```

> **Estado:** paquete `maintix-cli` planificado · especificación MSD-05 entregada.

---

## 3 · Configuración

Primer inicio:

```bash
maintix login
```

El asistente solicita:

- URL del servidor
- Usuario
- Contraseña
- Empresa (`empresa_slug`)

Configuración almacenada localmente:

```
~/.maintix/config.yaml
```

**Ejemplo:**

```yaml
server: https://api.maintix.app
empresa: empresa-demo
token: "************"
```

El token **nunca** se almacena en texto plano cuando el sistema operativo dispone de un almacén seguro de credenciales (Keychain · Credential Manager · Secret Service).

Variables de entorno alternativas para CI:

```bash
export MAINTIX_API=https://api.maintix.app/api/v1
export MAINTIX_TOKEN=<jwt>
```

---

## 4 · Autenticación

La CLI utiliza el endpoint oficial:

```http
POST /api/v1/auth/login
```

→ [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md)

Una vez autenticado:

```bash
maintix whoami
```

**Resultado:**

```
Usuario : Ana García
Empresa : Empresa Demo
Rol     : Admin
Plan    : Grow
```

Equivalente a `GET /api/v1/me` con contexto enriquecido cuando el plan esté disponible en el token.

---

## 5 · Organización de comandos

```
maintix
│
├── login
├── logout
├── whoami
│
├── assets
│     ├── list
│     ├── get
│     ├── create
│     └── delete
│
├── work-orders
├── inventory
├── purchases
├── sales
├── admin
│
├── openapi
├── config
└── version
```

La estructura refleja **exactamente** los recursos definidos en [MAG-04](/mag/chapters/04-recursos.md).

| Comando | Recurso MAG |
|---------|-------------|
| `maintix assets` | `maintenance/assets` |
| `maintix work-orders` | `maintenance/work-orders` |
| `maintix inventory` | `inventory/*` |
| `maintix admin` | `admin/*` |

---

## 6 · Ejemplos

**Listar activos:**

```bash
maintix assets list
```

**Obtener un activo:**

```bash
maintix assets get 25
```

**Crear una orden:**

```bash
maintix work-orders create
```

**Consultar inventario:**

```bash
maintix inventory products list
```

Todos los comandos invocan el SDK internamente — no construyen HTTP manualmente.

---

## 7 · Formatos de salida

**Formato por defecto** — tabla legible en terminal:

```
┌────┬──────────┬─────────────┐
│ ID │ Código   │ Nombre      │
├────┼──────────┼─────────────┤
│ 25 │ CMP-025  │ Compresor B │
└────┴──────────┴─────────────┘
```

**Salida JSON** (automatización):

```bash
maintix assets list --json
```

**Salida YAML:**

```bash
maintix assets list --yaml
```

**Salida CSV:**

```bash
maintix assets list --csv
```

| Flag | Uso |
|------|-----|
| `--json` | Pipelines · jq · scripts |
| `--yaml` | Config · legibilidad |
| `--csv` | Excel · reportes |
| *(default)* | Operación interactiva humana |

---

## 8 · Automatización

La CLI está diseñada para integrarse con:

- GitHub Actions
- GitLab CI
- Azure DevOps
- Jenkins
- Scripts Bash
- PowerShell

**Ejemplo:**

```bash
maintix inventory stock-low --json
```

Puede utilizarse **directamente** dentro de pipelines CI/CD.

```yaml
# GitHub Actions (conceptual)
- name: Check low stock
  env:
    MAINTIX_TOKEN: ${{ secrets.MAINTIX_TOKEN }}
  run: maintix inventory stock-low --json
```

---

## 9 · OpenAPI

Descargar la especificación oficial:

```bash
maintix openapi download
```

**Resultado:** `openapi.v1.yaml`

**Opciones:**

```bash
maintix openapi validate
maintix openapi version
```

Basado en [MSD-03 · OpenAPI 3.1](03-openapi.md).

| Comando | Acción |
|---------|--------|
| `openapi download` | Guarda spec desde `/api/v1/openapi.yaml` |
| `openapi validate` | Lint local (Spectral) |
| `openapi version` | Muestra `info.version` del contrato |

---

## 10 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Nunca almacenar tokens en scripts versionados |
| 2 | Utilizar variables de entorno para automatización |
| 3 | Mantener la CLI sincronizada con MAG |
| 4 | Toda operación utiliza el SDK oficial |
| 5 | Respetar los códigos de error definidos en MAG-06 |
| 6 | Mostrar mensajes legibles y códigos de salida estándar |
| 7 | Preferir `--json` en CI · tabla en terminal interactiva |

---

## 11 · Códigos de salida

| Código | Significado |
|--------|-------------|
| **0** | Operación exitosa |
| **1** | Error de ejecución genérico |
| **2** | Error de autenticación |
| **3** | Error de validación |
| **4** | Error de conexión |
| **5** | Error interno |

Estos códigos facilitan la integración con scripts y pipelines.

Los errores API mapean desde [MAG-06](/mag/chapters/06-manejo-errores.md):

| HTTP / `error.code` | Exit code CLI |
|---------------------|---------------|
| 401 · `UNAUTHORIZED` | 2 |
| 422 · `VALIDATION_ERROR` | 3 |
| Timeout · red | 4 |
| 500 · `INTERNAL_ERROR` | 5 |

---

## 12 · Roadmap

Próximas funcionalidades:

- autocompletado para Bash, Zsh y PowerShell
- actualización automática (`maintix update`)
- plugins oficiales
- modo interactivo (`maintix shell`)
- gestión de múltiples perfiles (`maintix config use staging`)
- diagnóstico (`maintix doctor`)
- importación y exportación masiva

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MSD-03 · OpenAPI](03-openapi.md) | Descarga y validación del contrato |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Base de implementación de la CLI |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | Recursos disponibles |
| [MAG-06 · Errores](/mag/chapters/06-manejo-errores.md) | Errores y códigos de salida |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Compatibilidad entre versiones |
| [MSD-02 · Portal](02-developer-portal.md) | Documentación y descarga CLI |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Existe el paquete oficial `maintix-cli`
- [ ] La autenticación utiliza JWT mediante MAG-02
- [ ] Los recursos principales (assets, work-orders, inventory) están disponibles
- [ ] La CLI permite descargar y validar OpenAPI
- [ ] Se soportan salidas en texto, JSON, YAML y CSV
- [ ] Los códigos de salida están documentados e implementados

**Especificación CLI:** ✅ · **Paquete PyPI:** 📋 pendiente

---

## Filosofía del capítulo

La CLI convierte el contrato MAG en **acciones ejecutables desde la terminal** — sin fricción para DevOps, soporte y desarrolladores que automatizan Maintix.

Junto al SDK y al Portal para Desarrolladores, completa el triángulo de integración: **explorar · codificar · automatizar**.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación** | 📋 Pendiente |
| **Dependencias** | MSD-03 · MSD-04 · MAG v1.0 |
| **Publicación** | 📋 PyPI (`maintix-cli`) |
| **Siguiente capítulo** | [MSD-06 · Sandbox & API Explorer](06-sandbox-explorer.md) |

---

→ [MSD-06-SBOX · Sandbox y API Explorer](06-sandbox-explorer.md)
