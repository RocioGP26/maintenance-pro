# Referencias cruzadas · Roustix Documentation Suite

**Sprint 16 · Purchasing:** [charter](purchasing/SPRINT16-REPORT.md) · [arquitectura](purchasing/architecture.md) · [contratos MAG/MRL](purchasing/contracts.md) · [migración](purchasing/migration.md) · [MRG-04](mrg/chapters/04-compras.md) · [MPA-05](mpa/chapters/05-roadmap-modulos.md)

**Sprint 19 · Maintenance Execution:** [charter](maintenance-execution/SPRINT19-REPORT.md) · [arquitectura](maintenance-execution/architecture.md) · [estados/permisos/eventos](maintenance-execution/contracts.md) · [migración](maintenance-execution/migration.md) · [MRG-02](mrg/chapters/02-maintenance.md) · [MPA-05](mpa/chapters/05-roadmap-modulos.md)

**Sprint 20 · Maintenance Automation:** [charter](maintenance-automation/SPRINT20-REPORT.md) · [arquitectura](maintenance-automation/architecture.md) · [contratos](maintenance-automation/contracts.md) · [MRG-02](mrg/chapters/02-maintenance.md) · [MPA-05](mpa/chapters/05-roadmap-modulos.md)

**Sprint 21 · Asset Health:** [charter](asset-health/SPRINT21-REPORT.md) · [arquitectura](asset-health/architecture.md) · [contrato de cálculo](asset-health/contracts.md) · [MRG-02](mrg/chapters/02-maintenance.md) · [MPA-05](mpa/chapters/05-roadmap-modulos.md)

**Sprint 22 · API pública y Webhooks (completo ✅):** [guía integradores](api/integrator-guide.md) · [ejemplos](api/examples.md) · [colecciones](api/collections/README.md) · [charter](api/charter.md) · [arquitectura](api/architecture.md) · [contrato REST](api/api-contract.md) · [webhooks](api/webhooks.md) · [permisos y planes](api/permissions-plans.md) · [reporte 22.5](api/SPRINT22.5-REPORT.md) · [MAG](mag/README.md) · [MPA-06](mpa/chapters/06-integraciones.md)

Convenciones para enlazar manuales de forma **consistente**. Objetivo: un lector siempre puede saltar de marca → producto → experiencia → ventas → arquitectura.

---

## 1 · Mapa de relaciones

```
                    ┌─────────────┐
                    │  MBB (01)   │  Marca · identidad
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  MCM (04)   │ │  MUX (03)   │ │  MDL (02)   │
    │  Comercial  │ │  Experiencia│ │  Diseño UI  │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │  MPA (05)   │  Plataforma · arquitectura
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  MRL (06)   │ │  MAG (07)   │ │  MSD (08)   │
    │  Reportes   │ │  API        │ │  SDK/Portal │
    └─────────────┘ └──────┬──────┘ └──────┬──────┘
                           │               │
                           └───────┬───────┘
                                   ▼
                            Developer (09)
```

---

## 2 · Matriz · Quién enlaza a quién

| Desde → Hacia | MBB | MDL | MUX | MCM | MPA | Cuándo enlazar |
|---------------|-----|-----|-----|-----|-----|----------------|
| **MBB** | — | UI tokens | UX Laws | Historia comercial | Ecosistema doc | Sección ecosistema |
| **MDL** | Marca | — | UX copy | — | — | Colores de marca |
| **MUX** | — | Componentes | — | Personas venta | — | Laws en desarrollo |
| **MCM** | Historia | — | Personas | — | **EMP · módulos** | Posicionamiento · sectores |
| **MPA** | Origen dual | Capa UI | Laws · MDL | Planes · GTM | — | Visión · modular · SaaS |
| **MRL** | Marca print | **mtx-pdf-*** | Legibilidad | — | Export MPA-06 | PDF · Excel |
| **MAG** | — | — | — | — | **MPA-06** · tenancy | Contrato API externo |
| **MSD** | — | — | — | — | **MAG** · MPA-06 | SDK · portal · OpenAPI |

---

## 3 · Enlaces canónicos (usar siempre estos)

| Manual | URL catálogo | README |
|--------|--------------|--------|
| Índice maestro | [/docs/](http://127.0.0.1:5000/docs/) | [README.md](README.md) |
| MBB | [/brandbook/](http://127.0.0.1:5000/brandbook/) | [brandbook/README.md](brandbook/README.md) |
| MDL | [/mdl/](http://127.0.0.1:5000/mdl/) | [mdl/README.md](mdl/README.md) |
| MUX | [/mux/](http://127.0.0.1:5000/mux/) | [mux/README.md](mux/README.md) |
| MCM | [/mcm/](http://127.0.0.1:5000/mcm/) | [mcm/README.md](mcm/README.md) |
| MPA | [/mpa/](http://127.0.0.1:5000/mpa/) | [mpa/README.md](mpa/README.md) |
| MRL | [/mrl/](http://127.0.0.1:5000/mrl/) | [mrl/README.md](mrl/README.md) |
| MAG | [/mag/](http://127.0.0.1:5000/mag/) | [mag/README.md](mag/README.md) |
| MSD | [/msd/](http://127.0.0.1:5000/msd/) | [msd/README.md](msd/README.md) |

---

## 4 · Referencias temáticas fijas

| Tema | Fuente de verdad | Enlazar desde |
|------|------------------|---------------|
| Frase de marca | MBB · MCM-01 | Todos |
| Historia dual CO/VE | MBB §02 · MCM-01 · **MPA-01** | MCM · MPA |
| Definición EMP | MCM-01 · **MPA-01** | MBB · MCM · MPA |
| UX Laws obligatorias | MUX laws.md | MDL · MPA-12 · Developer |
| Componentes UI | MDL | MUX · MPA-11 · MPA-12 |
| Planes Start/Grow/Scale | MCM-06 | MPA-05 · MPA-04 |
| Mapa de módulos | **MPA-02** | MCM-05 · MCM-10 |
| Arquitectura modular | **MPA-03** | MPA-04 · Developer |
| Constitución desarrollo | **MPA-12** | MUX · Developer |
| Contrato API externo | **MAG-01** · **MAG-03** · **MAG-04** | MPA-04 · MPA-06 · MSD |
| Ecosistema integradores | **MSD-01** · **MAG-09** | SDK · MPA-06 |
| Posicionamiento venta | MCM-01 | MBB · MPA-01 |

---

## 5 · Formato de enlaces

### En markdown (repositorio)

```markdown
→ [MCM-01 · Posicionamiento](mcm/chapters/01-posicionamiento.md)
→ [MPA-01 · Visión](mpa/chapters/01-vision-plataforma.md)
```

### En catálogos HTML (runtime)

```html
<a href="/mcm/#mcm-01">MCM-01</a>
<a href="/mpa/#mpa-03">MPA-03 · Modular</a>
<a href="/docs/">Roustix Docs</a>
```

### Entre capítulos del mismo manual

```markdown
**Anterior:** [MPA-01](01-vision-plataforma.md)
**Siguiente:** [MPA-03](03-arquitectura-modular.md)
```

---

## 6 · Bloque estándar «Suite» (pie de README)

Copiar al final de cada manual publicado:

```markdown
## Roustix Documentation Suite

| Doc | Enlace |
|-----|--------|
| Índice | [/docs/](http://127.0.0.1:5000/docs/) |
| Versiones | [VERSIONS.md](../VERSIONS.md) |
| Cross-refs | [CROSS-REFERENCES.md](../CROSS-REFERENCES.md) |
```

---

## 7 · Checklist al publicar un capítulo nuevo

- [ ] Enlaces «Anterior / Siguiente» en markdown
- [ ] Sección HTML en catálogo si aplica
- [ ] Referencia desde índice maestro si es manual nuevo
- [ ] Entrada en changelog del manual + suite si corresponde
- [ ] Al menos un enlace desde otro manual (matriz §2)
- [ ] Versión bump en [VERSIONS.md](VERSIONS.md)

---

→ [DOCUMENTATION-PRODUCT.md](DOCUMENTATION-PRODUCT.md) · [VERSIONING.md](VERSIONING.md)
