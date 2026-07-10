# MPA-12-EVO · Principios de evolución

**Código:** MPA-12-EVO · Complemento Sprint 6  
**Audiencia:** Todo el equipo de ingeniería y producto técnico

> La **Constitución del desarrollo** de Maintix.  
> Reglas cortas, prioridad clara, aplicables en cada PR y cada decisión de diseño.

---

## 1 · Por qué existe este documento

MPA-01 define **qué es** el producto. MPA-09 define **cómo pensar** el código.  
**MPA-12 define qué no se negocia** al evolucionar la plataforma.

Si hay conflicto entre velocidad y un principio de este documento, **el principio gana** — o se abre un MADR que explique por qué se hace una excepción temporal.

---

## 2 · La Constitución · Seis artículos

### Artículo I · Compatibilidad

> **No romper compatibilidad sin migración.**

| Significa | En la práctica |
|-----------|----------------|
| Esquema de BD versionado | Alembic obligatorio · nunca `ALTER` manual en prod |
| Datos existentes protegidos | Migraciones reversibles o con plan de rollback |
| APIs internas | Cambios breaking documentados antes de merge |
| Módulos activos en producción | Feature flags o despliegue gradual cuando el riesgo es alto |

**Violación típica:** renombrar columna sin migración · asumir tenant vacío · borrar endpoint sin avisar a integradores.

---

### Artículo II · Diseño unificado

> **Un módulo nuevo debe reutilizar el MDL.**

| Significa | En la práctica |
|-----------|----------------|
| Componentes `mtx-*` | Botones, tablas, cards, modales oficiales |
| Tokens `--mdl-*` | Color, radius, shadow, motion |
| Sin CSS paralelo | No inventar `btn-custom-maintix` |
| Patrones documentados | Listados, formularios, empty states en MDL |

**Violación típica:** pantalla nueva con estilos inline únicos · tabla que no sigue `mtx-table`.

→ [MDL](/mdl/) · [MUX Laws](/mux/#laws)

---

### Artículo III · Aislamiento tenant

> **Todo módulo debe respetar el aislamiento por tenant.**

| Significa | En la práctica |
|-----------|----------------|
| `empresa_id` en datos | Toda entidad de negocio |
| Queries acotadas | `query_tenant` o filtro explícito |
| Sin fugas cross-tenant | Tests que fallen si cambia el tenant |
| Archivos y exports | Contexto de empresa en rutas de medios |

**Violación típica:** `Model.query.get(id)` sin verificar empresa · reporte que mezcla datos de dos clientes.

→ [MPA-04 · SaaS](04-arquitectura-saas.md) · [MPA-11 · Capas](11-arquitectura-logica.md)

---

### Artículo IV · Impacto medible

> **Toda funcionalidad nueva debe tener impacto medible.**

| Significa | En la práctica |
|-----------|----------------|
| Objetivo claro | ¿Qué KPI o MUX metric mejora? |
| Antes / después | TTFAV · TTCOT · TTFFI cuando aplique |
| No feature por feature | Cada entrega responde un dolor operativo (MCM) |
| Telemetría mínima | Logs útiles · eventos de uso cuando sea crítico |

**Violación típica:** pantalla que nadie pidió · reporte que no usa nadie · configuración sin usuario.

→ [MUX MEASURE](/mux/) · [MCM-02 VALUE](/mcm/chapters/02-propuesta-de-valor.md)

---

### Artículo V · No duplicar

> **Ningún módulo puede duplicar lógica existente.**

| Significa | En la práctica |
|-----------|----------------|
| DRY en plataforma | Permisos en `permissions.py` · módulos en `modules.py` |
| Servicios compartidos | Moneda, tenancy, sectores, numeración OT |
| Un solo lugar por regla | Si existe `sector_service`, no copiar en inventario |
| Extraer antes de repetir | Tercera copia = refactor obligatorio |

**Violación típica:** validar plan en tres rutas · segunda función de backup · otro helper de slug.

---

### Artículo VI · UX sobre complejidad técnica

> **La experiencia de usuario siempre prevalece sobre la complejidad técnica.**

| Significa | En la práctica |
|-----------|----------------|
| MUX Laws primero | Las cinco leyes son gate de merge |
| Simplicidad visible | El usuario no paga la deuda técnica interna |
| Complejidad interna OK | Services y repositories pueden ser sofisticados si la UI es simple |
| Rediseñar antes de merge | Una violación UX = no entra a producción |

**Violación típica:** exponer detalle de error SQL al usuario · pantalla vacía «porque aún no hay datos en dev» · flujo de 7 pasos cuando bastan 3.

---

## 3 · Jerarquía de conflictos

Cuando dos reglas parecen chocar:

```
1. Seguridad y tenant (Art. III)
2. Experiencia de usuario (Art. VI)
3. Compatibilidad (Art. I)
4. No duplicar (Art. V)
5. MDL (Art. II)
6. Impacto medible (Art. IV) — define si la feature debía existir
```

Ejemplo: una feature rápida que rompe tenancy → **no se hace**, aunque el UX sea excelente.

---

## 4 · Aplicación en el día a día

### En un PR

- [ ] ¿Migración si toqué modelos?
- [ ] ¿UI con MDL?
- [ ] ¿Queries con tenant?
- [ ] ¿MUX Laws cumplidas?
- [ ] ¿Reutilicé servicio existente?
- [ ] ¿Puedo explicar el impacto en una frase?

### En una decisión de arquitectura

Si la respuesta afecta varios módulos o es difícil de revertir → **MADR** en Developer Docs (09).

### En un módulo nuevo

Checklist MPA-03 + esta Constitución + registro en `modules.py`.

---

## 5 · Relación con MPA-09

| Documento | Rol |
|-----------|-----|
| **MPA-09** | Filosofía y frase rectora («cada línea al servicio de la plataforma») |
| **MPA-12** | Artículos concretos y aplicables en review |

MPA-09 inspira. MPA-12 **obliga**.

---

## 6 · Enmiendas

Esta Constitución cambia **raramente**. Una enmienda requiere:

1. Entrada en changelog MPA
2. Comunicación al equipo
3. Si afecta arquitectura → MADR

La versión vigente es la de este capítulo en `/mpa/`.

---

**Anterior:** [MPA-11-LOG · Arquitectura lógica](11-arquitectura-logica.md)  
**Índice:** [MPA · Inicio](/mpa/)

---

*MPA-12-EVO · Constitución del desarrollo Maintix · 2026*
