# MPA-09-PHIL · Filosofía técnica

**Código:** MPA-09-PHIL · Sprint 6.9

> Las decisiones que mantienen Maintix como **plataforma** y evitan que se convierta en un monolito de parches.

---

## 1 · Frase rectora

> **Cada línea de código debe servir a la plataforma completa, no únicamente a un módulo.**

Si una feature solo tiene sentido en Inventory y rompe tenancy, no entra. Si beneficia a todos los módulos futuros, tiene prioridad.

---

## 2 · Principios de ingeniería

| # | Principio | En la práctica |
|---|-----------|----------------|
| 1 | **Tenant primero** | Toda entidad de negocio tiene `empresa_id` |
| 2 | **Módulo explícito** | Registrar en `modules.py` antes de exponer rutas |
| 3 | **Una UI** | Componentes MDL (`mtx-*`), no CSS ad hoc |
| 4 | **UX no negociable** | MUX Laws antes de merge |
| 5 | **Sector = configuración** | Plantillas, no tablas duplicadas |
| 6 | **API como contrato** | Cambios breaking → versión MAG |
| 7 | **Documentar decisiones** | MADR para trade-offs importantes |

---

## 3 · Lo que evitamos

| Anti-patrón | Consecuencia |
|-------------|--------------|
| `if empresa_id == 7` | Deuda imposible de escalar |
| Pantalla sin empty state | Violación MUX Law #1 |
| Tabla `inventario_v2` | Fragmentación de datos |
| Permiso solo en template | Agujero de seguridad |
| Feature flag permanente | Complejidad sin dueño |

---

## 4 · Relación con MUX y MDL

```
MPA (qué construimos)
  ↓
MUX (cómo debe sentirse)
  ↓
MDL (cómo se ve)
  ↓
Código
```

Un desarrollador nuevo lee **MPA** para contexto, **MUX** para criterios de aceptación, **MDL** para implementar UI.

---

## 5 · Definición de «hecho»

Un cambio está hecho cuando:

- [ ] Respeta tenancy y módulos activos
- [ ] Pasa MUX Laws (checklist en PR)
- [ ] Usa tokens y componentes MDL
- [ ] Tiene empty/loading/error states
- [ ] No introduce N+1 queries evidentes en listados
- [ ] Si es decisión arquitectónica → MADR

---

## 6 · De Mantis a Maintix

El nombre cambió. La lección no:

> Resolver problemas reales de operación con software que la empresa **sí adopta**.

La filosofía técnica sirve a eso: simple de operar, modular de extender, serio de escalar.

---

## Siguiente

→ [MPA-10-2030 · Roadmap 2030](10-roadmap-2030.md)
