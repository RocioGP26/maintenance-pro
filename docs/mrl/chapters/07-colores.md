# MRL-07-COL · Colores

**Código:** MRL-07-COL · Sprint 7.7

> **No se inventan colores en MRL.** Se reutiliza el MDL y el Brand Book.

---

## Paleta base (MDL)

| Token MDL | Hex | Uso MRL |
|-----------|-----|---------|
| `--mdl-secondary` / primario | `#042C53` | Títulos, cabecera tabla |
| `--mdl-body` | `#444441` | Texto cuerpo |
| `--mdl-muted` | `#888780` | Metadata, footer |
| `--mdl-accent` | `#185FA5` | Enlaces, acentos |
| `--mdl-border` | `#E2E8F0` | Líneas, bordes tabla |

---

## Semántica operativa

| Color | Hex referencia | Significado |
|-------|----------------|-------------|
| **Verde** | `#38A169` | Operativo · OK · disponible |
| **Rojo** | `#E53E3E` | Crítico · vencido · falla |
| **Ámbar** | `#D69E2E` | Advertencia · próximo a límite |
| **Azul** | `#185FA5` | Información · neutro destacado |

---

## Reglas

1. Estado en tablas = texto + icono opcional, no solo color (accesibilidad impresión B/N)
2. No más de 4 colores semánticos por página
3. Fondos de KPI: blanco o `#F4F7FB` — nunca degradados
4. Gráficos usan la misma paleta (MRL-08)

---

## Impresión

- Contraste mínimo 4.5:1 cuerpo
- Cabecera tabla azul oscuro + blanco siempre legible
- Probar export PDF en escala de grises

---

→ [MRL-08-CHT · Gráficos](08-graficos.md)
