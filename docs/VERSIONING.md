# Política de versionado · Maintix Documentation Suite

> Esta política cubre la documentación. Para la aplicación Flask, consultar
> [APP_VERSIONING.md](APP_VERSIONING.md); su fuente canónica es
> `app/version.py` y sus tags usan `vX.Y.Z`.

## Documentación como producto independiente

La documentación tiene **releases propios**, distintos del software de aplicación.

→ Manifiesto: [DOCUMENTATION-PRODUCT.md](DOCUMENTATION-PRODUCT.md)  
→ Registro de versiones: [VERSIONS.md](VERSIONS.md)  
→ Changelog suite: [changelog.md](changelog.md)

---

## Principio

A partir del **release `docs-v1.0`**, los manuales publicados pueden **congelarse**.

Un cambio importante **no modifica la edición vigente en silencio**: abre una **nueva versión** (v1.1, v2.1, etc.) y se registra en el `changelog.md` del proyecto.

---

## Qué es un cambio importante

| Tipo | Ejemplo | Acción |
|------|---------|--------|
| **Mayor** | Nuevo capítulo, reestructura, cambio de posicionamiento | `v2.0` → `v3.0` |
| **Menor** | Capítulo nuevo, sección amplia, nuevos códigos PLAY/OBJ | `v1.0` → `v1.1` |
| **Parche** | Typo, enlace roto, aclaración sin cambiar significado | `v1.0.0` → `v1.0.1` |
| **Suite** | Nuevo manual (MPA, MAG…) o hito transversal | Suite `v1.0` → `v1.1` |

---

## Ediciones congeladas (`docs-v1.0`)

| # | Manual | Versión | Tag Git |
|---|--------|---------|---------|
| 01 | Brand Book (MBB) | **v2.0** | `docs-v1.0` |
| 02 | MDL | **v1.0** | `docs-v1.0` |
| 03 | MUX | **v1.2** | `docs-v1.0` |
| 04 | MCM | **v1.0** | `docs-v1.0` |

MPA y manuales posteriores siguen en desarrollo hasta su freeze oficial.

---

## Flujo para el próximo cambio

1. Editar contenido con bump de versión en [VERSIONS.md](VERSIONS.md)
2. Entrada en `{manual}/changelog.md`
3. Si afecta la suite → [changelog.md](changelog.md)
4. Actualizar [CROSS-REFERENCES.md](CROSS-REFERENCES.md) si hay enlaces nuevos
5. Sincronizar `/docs/` y catálogo HTML del manual
6. Release interno → tag Git `docs-vX.Y` + nota en [release-notes/](release-notes/)

---

## Referencias cruzadas

Todo release documental debe mantener enlaces consistentes entre manuales.

→ [CROSS-REFERENCES.md](CROSS-REFERENCES.md)

---

## Publicación pública (futuro)

Cuando la documentación sea externa (clientes, partners, inversionistas):

→ [publishing/README.md](publishing/README.md)

---

→ [RELEASE-v1.0.md](RELEASE-v1.0.md) · [Índice maestro](README.md)
