# Certificación de capacidad y cuotas · Piloto Roustix

**Fecha de corte:** 2026-07-29

**Alcance:** cuotas Start, Business y Enterprise; alerta preventiva; bloqueo de
cargas; add-on `ADD-STG-2G`; retiro de capacidad y nomenclatura comercial.

## Veredicto

| Control | Estado | Evidencia |
|---------|--------|-----------|
| Start · 1 GB | ✅ Aprobado | Catálogo y prueba de integración |
| Business · 5 GB | ✅ Aprobado | Clave técnica `grow`, etiqueta pública Business |
| Enterprise · 20 GB | ✅ Aprobado | Catálogo y prueba directa incorporada |
| Alerta al 80 % | ✅ Aprobado | Umbral exacto y banner cubiertos por pruebas |
| Bloqueo al 100 % | ✅ Aprobado | `save_bytes()` rechaza nuevas cargas |
| Add-on +2 GB | ✅ Aprobado | La cuota efectiva aumenta 2048 MB |
| Retiro del add-on | ✅ Aprobado | Conserva archivos y bloquea nuevas cargas si excede la base |
| Reemplazo de archivo | ✅ Aprobado | Acredita el tamaño anterior sin borrarlo antes del commit |
| Nomenclatura comercial | ✅ Aprobado | Start · Business · Enterprise; `grow` solo técnico |
| Operación comercial | ✅ Definida | Cobro anticipado mensual y retiro al cierre del periodo pagado |

**Estado global:** certificación aprobada para el piloto. Los controles de
código, política operativa y gate visual en producción quedaron verificados.

## Evidencia automatizada

Archivos principales:

- `tests/test_storage_quota.py`
- `tests/test_storage_upsell.py`
- `tests/test_commercial_pilot.py`

Resultado focalizado al 2026-07-29:

```text
28 passed
```

Regresión ampliada de almacenamiento, backup, migración y aislamiento:

```text
48 passed
```

La batería comprueba los tres cupos oficiales, el umbral preventivo, el hard
limit, el crédito de reemplazo, la cuota efectiva con add-on y la conservación
de archivos después de retirar capacidad.

## Política operativa del add-on

1. Durante el piloto se ofrece únicamente `ADD-STG-2G`: +2 GB por $100.000 COP
   mensuales.
2. El cobro es anticipado y la activación la realiza un SuperAdmin después de
   confirmar el pago.
3. El retiro solicitado se ejecuta al finalizar el periodo mensual pagado; no
   existe prorrateo automático.
4. El retiro nunca elimina archivos.
5. Si el uso queda igual o por encima de la cuota base, se bloquean nuevas
   cargas. El cliente conserva descarga y eliminación para liberar espacio.
6. La activación y el retiro quedan registrados en auditoría de plataforma.

## Gate visual posterior al despliegue

1. Abrir **Configuración → Almacenamiento** con un tenant por debajo del 80 %.
2. Confirmar la alerta preventiva con un tenant al 80 % o más.
3. Confirmar el mensaje de bloqueo con un tenant al 100 % o sobre la cuota.
4. Verificar que el mensaje indica que los archivos existentes se conservan.
5. Activar temporalmente `ADD-STG-2G` y comprobar que la cuota aumenta 2 GB.
6. Retirar el add-on y confirmar auditoría y cuota base restaurada.
7. Confirmar que la interfaz nunca muestra Grow como nombre comercial.

## Registro del gate visual

| Campo | Valor |
|-------|-------|
| Fecha Colombia | 2026-07-29 |
| Responsable | Gladis Rocio Gelves Pabon |
| Commit desplegado | `92649b4` · Roustix `1.0.30` |
| Start 1 GB | ✅ Producción: 31.1 KB / 1 GB en Inversiones Reinoso y Cía SAS |
| Business 5 GB | ✅ Catálogo oficial visible y prueba automatizada |
| Enterprise 20 GB | ✅ Catálogo oficial visible y prueba automatizada |
| Alerta 80 % | ✅ Texto preventivo visible; umbral exacto cubierto por pruebas |
| Bloqueo 100 % | ✅ Texto de bloqueo y conservación visible; hard limit cubierto por pruebas |
| Add-on +2 GB | ✅ Activación temporal: cuota 1 GB → 3 GB y confirmación de 2048 MB |
| Auditoría de retiro | ✅ Desactivación confirmada; cuota restaurada a 1 GB sin eliminar archivos |
| Nomenclatura | ✅ Start · Business · Enterprise; legacy oculto del filtro de plataforma |
| Veredicto final | ✅ Aprobado para piloto |

### Evidencia remota

- `/health/ready`: `status=ok`, versión `1.0.30`, PostgreSQL, migraciones,
  Redis y heartbeat del worker en verde.
- Tenant piloto: **Inversiones Reinoso y Cía SAS**, plan Start, uso inicial y
  final `31.1 KB / 1 GB`.
- Activación temporal: mensaje “Add-on +2 GB activado”, cuota efectiva
  `31.1 KB / 3 GB` y capacidad adicional `2048 MB`.
- Retiro temporal: mensaje “Add-on +2 GB desactivado”, capacidad adicional
  `0 MB` y cuota efectiva restaurada a `31.1 KB / 1 GB`.
- El gate detectó y corrigió la exposición del plan legacy Scale en el filtro
  interno; la oferta visible queda limitada a Start, Business y Enterprise.
