# Política de versionado · Maintix Documentation Suite

## Principio

A partir del **release `docs-v1.0`**, los manuales publicados están **congelados**.

Un cambio importante **no modifica la edición vigente**: abre una **nueva versión** (v1.1, v2.1, etc.) y se registra en el `changelog.md` del proyecto.

## Qué es un cambio importante

| Tipo | Ejemplo | Acción |
|------|---------|--------|
| **Mayor** | Nuevo capítulo, reestructura, cambio de posicionamiento | `v2.0` → `v3.0` |
| **Menor** | Capítulo nuevo, sección amplia, nuevos códigos PLAY/OBJ | `v1.0` → `v1.1` |
| **Parche** | Typo, enlace roto, aclaración sin cambiar significado | `v1.0.0` → `v1.0.1` |
| **Suite** | Nuevo manual (MAG, API…) o hito transversal | `Documentation Suite v1.0` → `v1.1` |

## Ediciones congeladas (Suite v1.0)

| # | Manual | Versión | Tag Git |
|---|--------|---------|---------|
| 01 | Brand Book (MBB) | **v2.0** | `docs-v1.0` |
| 02 | MDL | **v1.0** | `docs-v1.0` |
| 03 | MUX | **v1.2** | `docs-v1.0` |
| 04 | MCM | **v1.0** | `docs-v1.0` |

## Flujo para el próximo cambio

1. Crear rama o trabajo en `main` con bump de versión en README + catálogo HTML.
2. Entrada en `changelog.md` del proyecto.
3. Si afecta varios manuales → entrada en [changelog.md](changelog.md) de la suite.
4. Release interno opcional → tag `docs-v1.1` (o el que corresponda).

## Fuera de congelamiento (por ahora)

MRL v0.1 · Architecture · MAG · API · Roadmap — en desarrollo, sin política de freeze hasta su primera edición oficial.

→ [RELEASE-v1.0.md](RELEASE-v1.0.md) · [Índice maestro](README.md)
