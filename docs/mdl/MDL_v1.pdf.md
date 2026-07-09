# MDL v1.0 — PDF

Fuente para exportar **MDL_v1.pdf**:

| Archivo | Uso |
|---------|-----|
| [MDL_v1.md](MDL_v1.md) | Fuente Markdown consolidada |
| [index.html](index.html) | Catálogo visual (Imprimir → PDF en navegador) |

## Generar PDF

### Opción A — Navegador

1. `python run.py`
2. Abrir http://127.0.0.1:5000/mdl/
3. Imprimir → Guardar como PDF

### Opción B — Pandoc

```powershell
cd docs/mdl
pandoc MDL_v1.md components.md tokens.md -o MDL_v1.pdf
```

En dos años este documento puede tener 200 páginas. Eso es el objetivo.
