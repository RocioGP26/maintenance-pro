# Maintix Documentation Suite v1.0

Ecosistema documental de Maintix. Cada proyecto es **independiente** y puede crecer sin límite.

**Frase:** Toda la operación. Una sola plataforma.

Nomenclatura oficial: [NOMENCLATURE.md](NOMENCLATURE.md)

---

## Filosofía de desarrollo

Cada nueva funcionalidad desarrollada para Maintix deberá cumplir las **cinco UX Laws** (MUX) antes de ser considerada lista para producción.

**Si una funcionalidad incumple una sola ley, deberá rediseñarse antes del merge.**

Las leyes no son decorativas — son **cultura de desarrollo obligatoria**:

1. Nunca pantalla vacía  
2. Toda acción con retroalimentación  
3. Nunca perder información del usuario  
4. Siempre explicar el siguiente paso  
5. Acción principal evidente  

Detalle: [mux/laws.md](mux/laws.md) · Matriz: [mux/decision-matrix.md](mux/decision-matrix.md) · Copy: [mux/copy.md](mux/copy.md)

---

## Suite completa

```
Maintix Docs
│
├── MBB   Maintix Brand Book       → docs/brandbook/   /brandbook/
├── MDL   Maintix Design Language  → docs/mdl/         /mdl/
├── MUX   Maintix User Experience  → docs/mux/         /mux/
├── MRL   Maintix Report Language  → docs/mrl/
├── MCM   Maintix Commercial Manual→ docs/mcm/         Sprint 5
├── MAG   Maintix API Guide        → docs/mag/
├── MADR  Architecture Decisions   → docs/madr/
├── Handbook · Deployment · Security · Roadmap
```

## Estado

| Código | Nombre completo | Versión | URL |
|--------|-----------------|---------|-----|
| **MBB** | Maintix Brand Book | v2.0 | [/brandbook/](http://127.0.0.1:5000/brandbook/) |
| **MDL** | Maintix Design Language | v1.0 | [/mdl/](http://127.0.0.1:5000/mdl/) |
| **MUX** | Maintix User Experience Guide | v1.2 | [/mux/](http://127.0.0.1:5000/mux/) |
| **MRL** | Maintix Report Language | v0.1 | `docs/mrl/` |
| **MCM** | Maintix Commercial Manual | Sprint 5 | `docs/mcm/` |
| **MAG** | Maintix API Guide | Planificado | `docs/mag/` |
| **MADR** | Maintix Architecture Decision Records | Planificado | `docs/madr/` |

## MUX · Capítulos clave

| ID | Documento |
|----|-----------|
| MTX-UX-LAW | [laws.md](mux/laws.md) — cultura de desarrollo |
| MTX-UX-DEC | [decision-matrix.md](mux/decision-matrix.md) |
| MTX-UX-COPY | [copy.md](mux/copy.md) |
| MTX-UX-MEASURE | [measure.md](mux/measure.md) — TTFAV &lt; 3m · TTCOT &lt; 2m · TTFFI &lt; 15s |
| MTX-UX-RESEARCH | [research.md](mux/research.md) |

## Tres pilares del producto

| Pilar | Documentación |
|-------|---------------|
| **Tecnología** | MDL, MAG, Handbook, MADR |
| **Experiencia** | MUX, MRL |
| **Comunicación comercial** | MBB, MCM |

## Código producto

| Archivo | Rol |
|---------|-----|
| `static/css/mdl-tokens.css` | Tokens `--mdl-*` |
| `static/css/mdl.css` | Componentes `mtx-*` |

```powershell
python run.py
```

- MBB: http://127.0.0.1:5000/brandbook/
- MDL: http://127.0.0.1:5000/mdl/
- MUX: http://127.0.0.1:5000/mux/
