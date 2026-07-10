# Maintix Documentation Suite v1.0

**Índice maestro** del ecosistema documental de Maintix.

**Frase:** Toda la operación. Una sola plataforma.

```powershell
python run.py
```

→ **http://127.0.0.1:5000/docs/** (índice visual)  
→ Este archivo: `docs/README.md`

Nomenclatura: [NOMENCLATURE.md](NOMENCLATURE.md) · Resumen: [ecosystem/README.md](ecosystem/README.md)  
Release: [RELEASE-v1.0.md](RELEASE-v1.0.md) · Versionado: [VERSIONING.md](VERSIONING.md) · Tag: `docs-v1.0`

---

## Release interno · Suite v1.0

**Primera edición oficial congelada** — julio 2026.

| Manual | Versión | Estado |
|--------|---------|--------|
| Brand Book (MBB) | v2.0 | ✔ Congelado |
| MDL | v1.0 | ✔ Congelado |
| MUX | v1.2 | ✔ Congelado |
| MCM | v1.0 | ✔ Congelado |

A partir de aquí, cambios importantes → **nueva versión** (v1.1, v2.1…), no edición silenciosa.

---

## MAINTIX DOCS · Árbol maestro

```
MAINTIX DOCS
│
├── 01 Brand Book       (MBB)   → docs/brandbook/     /brandbook/
├── 02 MDL                        → docs/mdl/           /mdl/
├── 03 MUX                        → docs/mux/           /mux/
├── 04 MCM                        → docs/mcm/           /mcm/
├── 05 MRL                        → docs/mrl/
├── 06 MAG                        → docs/mag/
├── 07 API                        → docs/api/
├── 08 Architecture               → docs/architecture/
├── 09 Roadmap                    → docs/roadmap/
└── README                        → docs/README.md (este archivo)
```

Cada proyecto es **independiente** y crece sin romper los demás.

---

## Suite · Estado y enlaces

| # | Código | Nombre | Versión | URL / ruta |
|---|--------|--------|---------|------------|
| **01** | **MBB** | Maintix Brand Book | v2.0 ✔ | [/brandbook/](http://127.0.0.1:5000/brandbook/) |
| **02** | **MDL** | Maintix Design Language | v1.0 ✔ | [/mdl/](http://127.0.0.1:5000/mdl/) |
| **03** | **MUX** | Maintix User Experience Guide | v1.2 ✔ | [/mux/](http://127.0.0.1:5000/mux/) |
| **04** | **MCM** | Maintix Commercial Manual | v1.0 ✔ | [/mcm/](http://127.0.0.1:5000/mcm/) |
| **05** | **MRL** | Maintix Report Language | v0.1 | [mrl/README.md](mrl/README.md) |
| **06** | **MAG** | Maintix API Guide | Planificado | [mag/README.md](mag/README.md) |
| **07** | **API** | Referencia técnica API | Planificado | [api/README.md](api/README.md) |
| **08** | **Architecture** | Arquitectura y decisiones | En curso | [architecture/README.md](architecture/README.md) |
| **09** | **Roadmap** | Roadmap de producto | Planificado | [roadmap/README.md](roadmap/README.md) |

---

## Tres pilares

| Pilar | Documentación | Rol |
|-------|---------------|-----|
| **Comunicación** | MBB · MCM | Marca, identidad, ventas, GTM |
| **Experiencia** | MUX · MRL | Usuario, leyes UX, PDFs |
| **Tecnología** | MDL · MAG · API · Architecture | UI, integraciones, ingeniería |

---

## Filosofía de desarrollo (MUX)

Las **5 UX Laws** son obligatorias antes de merge a producción:

1. Nunca pantalla vacía  
2. Toda acción con retroalimentación  
3. Nunca perder información del usuario  
4. Siempre explicar el siguiente paso  
5. Acción principal evidente  

→ [mux/laws.md](mux/laws.md) · [mux/decision-matrix.md](mux/decision-matrix.md)

---

## 04 · MCM · Capítulos (Sprint 5 completo)

| Capítulo | Código |
|----------|--------|
| Posicionamiento | MCM-01-POS |
| Propuesta de valor | MCM-02-VALUE |
| ICP Score | MCM-03-ICP |
| Buyer Personas y DMU | MCM-04-DMU |
| Sectores | MCM-05-SECT |
| Planes comerciales | MCM-06-PLAN |
| Demo comercial | MCM-07-DEMO · PLAY-001–005 |
| Objeciones | MCM-08-OBJ · OBJ-001–010 |
| Casos de éxito | MCM-09-CASE · MTX-CASE-001–006 |
| Go To Market | MCM-10-GTM |

→ [mcm/README.md](mcm/README.md) · [mcm/NOMENCLATURE.md](mcm/NOMENCLATURE.md)

---

## 08 · Architecture · Documentos relacionados

| Documento | Ruta |
|-----------|------|
| Architecture Decision Records | [madr/README.md](madr/README.md) |
| Developer Handbook | [handbook/README.md](handbook/README.md) |
| Arquitectura por sectores | [arquitectura-sectores.md](arquitectura-sectores.md) |
| Deployment | [deployment/README.md](deployment/README.md) |
| Security | [security/README.md](security/README.md) |

---

## Código producto (MDL)

| Archivo | Rol |
|---------|-----|
| `static/css/mdl-tokens.css` | Tokens `--mdl-*` |
| `static/css/mdl.css` | Componentes `mtx-*` |

---

## Mapa rápido · ¿Qué leo primero?

| Rol | Empieza por |
|-----|-------------|
| **Diseño / UI** | MDL → MUX Laws |
| **Producto** | MUX → MCM-02 |
| **Ventas** | MCM → MBB historia |
| **Desarrollo** | MUX Laws → MDL → Architecture |
| **Integraciones** | MAG → API (cuando exista) |
| **Nuevo en el equipo** | **Este README** → [/docs/](http://127.0.0.1:5000/docs/) |

---

*Maintix Documentation Suite · 2026 · Pre-Sprint 6*
