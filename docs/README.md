# Maintix Documentation Suite · v1.5.0

**Producto documental independiente** del software de aplicación.

**Índice maestro** del ecosistema documental de Maintix.

**Frase:** Toda la operación. Una sola plataforma.

```powershell
python run.py
```

→ **http://127.0.0.1:5000/docs/** (índice visual)  
→ Este archivo: `docs/README.md`

| Meta | Enlace |
|------|--------|
| Versiones oficiales | [VERSIONS.md](VERSIONS.md) |
| Changelog suite | [changelog.md](changelog.md) |
| Cross-refs | [CROSS-REFERENCES.md](CROSS-REFERENCES.md) |
| Producto documental | [DOCUMENTATION-PRODUCT.md](DOCUMENTATION-PRODUCT.md) |
| Versionado | [VERSIONING.md](VERSIONING.md) |
| Nomenclatura | [NOMENCLATURE.md](NOMENCLATURE.md) |
| Sitio público (futuro) | [publishing/README.md](publishing/README.md) |
| Sprint 16 · Purchasing | [purchasing/README.md](purchasing/README.md) |

---

## MAINTIX DOCS · Árbol maestro (01 – 10)

```
MAINTIX DOCS
│
├── 01 Brand Book       (MBB)   → /brandbook/
├── 02 MDL                        → /mdl/
├── 03 MUX                        → /mux/
├── 04 MCM                        → /mcm/
├── 05 MPA                        → /mpa/          ← Sprint 6
├── 06 MRL                        → docs/mrl/
├── 07 MAG                        → docs/mag/
├── 08 MSD                        → /msd/          ← Sprint 9
├── 08 SDK (paquetes)             → docs/sdk/
├── 09 Developer Docs             → docs/developer/
├── 10 Release Notes              → docs/release-notes/
└── README                        → docs/README.md
```

---

## Suite · Estado y enlaces

| # | Código | Nombre | Versión | URL |
|---|--------|--------|---------|-----|
| **01** | **MBB** | Brand Book | v2.0 ✔ | [/brandbook/](http://127.0.0.1:5000/brandbook/) |
| **02** | **MDL** | Design Language | v1.0 ✔ | [/mdl/](http://127.0.0.1:5000/mdl/) |
| **03** | **MUX** | User Experience | v1.2 ✔ | [/mux/](http://127.0.0.1:5000/mux/) |
| **04** | **MCM** | Commercial Manual | v1.0 ✔ | [/mcm/](http://127.0.0.1:5000/mcm/) |
| **05** | **MPA** | Platform Architecture | v1.0 ✔ | [/mpa/](http://127.0.0.1:5000/mpa/) |
| **06** | **MRL** | Report Language | v1.0 | [/mrl/](http://127.0.0.1:5000/mrl/) |
| **07** | **MAG** | API Guide | v1.0.12 ✔ | [/mag/](http://127.0.0.1:5000/mag/) |
| **08** | **MSD** | SDK & Developer Portal | v0.1.0 | [/msd/](http://127.0.0.1:5000/msd/) |
| **09** | **—** | Developer Docs | En curso | [developer/README.md](developer/README.md) |
| **10** | **—** | Release Notes | Activo | [release-notes/README.md](release-notes/README.md) |

✔ = congelado (Suite v1.0 · tag `docs-v1.0`)

---

## Cuatro pilares (Sprint 6+)

| Pilar | Documentación | Rol |
|-------|---------------|-----|
| **Comunicación** | MBB · MCM | Marca y ventas |
| **Experiencia** | MUX · MRL | Usuario y reportes |
| **Plataforma** | **MPA** | Arquitectura de producto |
| **Ingeniería** | MDL · MAG · SDK · Developer | UI, API, código |

---

## 05 · MPA · Capítulos (Sprint 6)

| # | Código | Título |
|---|--------|--------|
| 01 | MPA-01-VIS | Visión de plataforma (EMP) |
| 02 | MPA-02-ECO | Ecosistema Maintix |
| 03 | MPA-03-MOD | Arquitectura modular |
| 04 | MPA-04-SAAS | Arquitectura SaaS |
| 05 | MPA-05-ROAD | Roadmap de módulos |
| 06 | MPA-06-INT | Integraciones |
| 07 | MPA-07-SEC | Seguridad |
| 08 | MPA-08-SCALE | Escalabilidad |
| 09 | MPA-09-PHIL | Filosofía técnica |
| 10 | MPA-10-2030 | Roadmap 2030 |
| 11 | MPA-11-LOG | Arquitectura lógica (complemento) |
| 12 | MPA-12-EVO | Principios de evolución · Constitución |

→ [mpa/README.md](mpa/README.md) · [mpa/NOMENCLATURE.md](mpa/NOMENCLATURE.md)

---

## Filosofía MUX (obligatoria pre-merge)

→ [mux/laws.md](mux/laws.md)

---

## ¿Qué leo primero?

| Rol | Empieza por |
|-----|-------------|
| **Nuevo en el equipo** | **MPA-01** → **MPA-11** → MUX Laws → MDL |
| **Desarrollo** | MPA → MUX Laws → MDL |
| **Arquitectura / producto** | MPA → MCM-02 |
| **Ventas** | MCM → MBB |
| **Diseño** | MDL → MUX |
| **Integraciones** | MPA-06 → MAG → SDK |

---

## Referencias cruzadas · Núcleo

| | MBB | MDL | MUX | MCM | MPA |
|---|:---:|:---:|:---:|:---:|:---:|
| **MBB** | — | [UI](/mdl/) | [UX](/mux/) | [Venta](/mcm/) | [Plataforma](/mpa/) |
| **MDL** | [Marca](/brandbook/) | — | [Laws](/mux/) | — | [Capas](/mpa/#mpa-11) |
| **MUX** | — | [MDL](/mdl/) | — | [DMU](/mcm/#mcm-04) | [Constitución](/mpa/#mpa-12) |
| **MCM** | [Historia](/brandbook/#historia-origen) | — | [Personas](/mux/) | — | [EMP](/mpa/#mpa-01) |
| **MPA** | [Origen](/brandbook/) | [MDL](/mdl/) | [Laws](/mux/) | [GTM](/mcm/#mcm-10) | — |

Matriz completa: [CROSS-REFERENCES.md](CROSS-REFERENCES.md)

---

*Maintix Documentation Suite · v1.2 · 2026*
