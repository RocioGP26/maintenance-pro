# MTX-UX-RESEARCH · Investigación de experiencia

Maintix crecerá más allá de un solo diseñador. Este documento define **cómo evolucionar el producto con evidencia**, no solo intuición.

---

## Principios

1. **Pequeño y frecuente** > estudio anual enorme
2. **Observar operación real** (planta, bodega, mostrador)
3. **Priorizar por North Star** ([measure.md](measure.md))
4. **Registrar todo** — aunque sea una nota en MUX changelog

---

## ¿Cómo hacemos pruebas con usuarios?

| Método | Cuándo | Duración | Participantes |
|--------|--------|----------|---------------|
| **Prueba de 5 segundos** | Validar jerarquía visual | 5 min | 3–5 |
| **Tarea guiada** | Flujo crítico (OT, venta) | 15–30 min | 5 por perfil MUX |
| **Walkthrough remoto** | Clientes beta / trial | 45 min | 1–2 |
| **Shadowing en planta** | Descubrimiento profundo | 2–4 h | 1–2 técnicos |
| **Encuesta CSAT in-app** | Post-acción (cerrar OT) | 1 pregunta | Muestra aleatoria |

### Protocolo mínimo (tarea guiada)

1. Contexto: «Imagina que acabas de recibir esta OT…»
2. Tareas sin ayuda (medir TTCOT / TTFFI)
3. Think-aloud opcional
4. Debrief: frustraciones → Anti-Goals ([goals.md](goals.md))
5. Registrar en plantilla `research/sessions/YYYY-MM-DD-perfil.md` (futuro)

---

## ¿Cada cuánto revisamos la experiencia?

| Ritmo | Actividad |
|-------|-----------|
| **Cada PR UI** | Checklist UX Laws + DEC + COPY |
| **Cada sprint** | Revisar 1 journey ([journeys.md](journeys.md)) |
| **Cada release** | Snapshot métricas TTFAV / TTCOT / TTFFI |
| **Trimestral** | Auditoría MUX completa + 1 ronda pruebas usuarios |
| **Anual** | Revisión personas 006–008 · roadmap MUX |

---

## ¿Cómo priorizamos mejoras?

Matriz **Impacto × Evidencia**:

```
                    Alta evidencia
                          │
     Quick wins ──────────┼────────── Big bets
     (hacer ya)          │          (planificar)
                          │
                    Baja evidencia
          ─────────────────────────────
               Bajo impacto    Alto impacto
                    en NSM*
```

*NSM = North Star Metric ([measure.md](measure.md))

**Prioridad 1:** Incumplimiento UX Law en producción  
**Prioridad 2:** Métrica NSM degradada post-release  
**Prioridad 3:** Feedback recurrente de clientes (≥ 3 tenants)  
**Prioridad 4:** Deuda UX documentada en changelog  

---

## ¿Cómo registramos comentarios de clientes?

| Canal | Destino | Responsable |
|-------|---------|-------------|
| Soporte / ticket | Etiqueta `ux-feedback` | Producto |
| Demo comercial | Notas en CRM → revisión semanal | Ventas → Producto |
| NPS / CSAT | Dashboard interno | Producto |
| GitHub / issue interno | `label:ux` | Dev |

### Plantilla registro

```markdown
## Feedback · YYYY-MM-DD
- **Tenant / sector:**
- **Perfil MUX:** MTX-UX-PER-00X
- **Cita literal:**
- **Journey afectado:**
- **Métrica NSM:** TTFAV | TTCOT | TTFFI
- **Acción:** fix | research | backlog | wontfix
```

---

## Anti-patterns de research

- ❌ Preguntar «¿Te gusta el color?»
- ❌ Diseñar solo con el equipo sin usuario de planta
- ❌ Ignorar métricas porque «sientes» que mejoró
- ❌ Acumular feedback sin priorizar

---

## Evolución de personas

Cuando un módulo madure (Auditor 006, Proveedor 007, Cliente 008):

1. Entrevistas con 5 usuarios reales del rol
2. Ficha MUX completa + journey
3. Goals / Anti-Goals validados
4. Activar ID reservado en [personas.md](personas.md)

---

## Relación con Documentation Suite

| Doc | Rol en research |
|-----|-----------------|
| MUX RESEARCH | Proceso |
| MUX measure | Validación cuantitativa |
| MCM (Sprint 5) | Voz del cliente en ventas |
| MADR | Decisiones estructurales post-research |
