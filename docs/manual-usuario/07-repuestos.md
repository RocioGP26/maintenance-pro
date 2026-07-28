# 07 · Repuestos técnicos

Los **repuestos técnicos** son piezas y consumibles que se usan al ejecutar mantenimiento. Son distintos del catálogo de **Inventario comercial**.

**Menú:** `Mantenimiento → Repuestos técnicos` · `/inventario`

---

## 1. Alta de un repuesto

1. Ve a **Repuestos técnicos**.
2. Crea el ítem con código, descripción, unidad y **costo unitario**.
3. Define **stock mínimo** (alerta cuando baje de ese nivel).
4. Registra la entrada de stock inicial o posterior.

---

## 2. Consumo en una OT

1. Abre la OT en ejecución.
2. Registra las líneas de repuesto utilizadas.
3. Al guardar, el sistema **descuenta stock** y suma el costo a la OT (cantidad × costo unitario al momento del consumo).

> El consumo operativo principal ocurre en OT **correctivas**. Verifica en tu proceso interno si también registras piezas en preventivos.

---

## 3. Alertas de mínimo

En **Inicio** y en reportes de mantenimiento verás **repuestos bajo mínimo**.

Cuando aparezca la alerta:

1. Confirma el stock físico.
2. Gestiona la reposición (compra o traslado interno).
3. Registra la entrada en el módulo de repuestos.

---

## 4. Buenas prácticas

- Un código = una pieza; evita duplicados.
- Actualiza el costo unitario cuando cambie el precio de compra (las OT ya consumidas conservan el costo histórico).
- No uses el módulo comercial para piezas de taller salvo que tu empresa lo haya definido así a propósito.
- Revisa mínimos de piezas críticas (sellos, filtros, rodamientos de alta rotación).

→ Siguiente: [Inicio, análisis y reportes](08-analisis-y-reportes.md)
