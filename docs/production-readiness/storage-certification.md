# Certificación de almacenamiento · Piloto Roustix

**Fecha de corte:** 2026-07-29

**Alcance:** Cloudflare R2, referencias PostgreSQL, aislamiento por tenant,
medición, cuotas, reemplazo, eliminación y migración legacy.

## Veredicto

| Capa | Estado | Evidencia |
|------|--------|-----------|
| Contrato de código S3/R2 | ✅ Aprobado | Roundtrip, `head`, listado, lectura y borrado con cliente S3 controlado |
| Aislamiento tenant | ✅ Aprobado | Tenant autenticado abre su medio; otro tenant recibe HTTP 403 |
| Cuotas por plan y add-on | ✅ Aprobado | Hard-limit, crédito de reemplazo y +2 GB cubiertos por pruebas |
| Ciclo de reemplazo/eliminación | ✅ Aprobado | El objeto anterior vive hasta el commit; limpieza posterior tolerante a fallos |
| Migración legacy local | ✅ Lista | 11 referencias recuperables; `missing = 0`; 2 referencias ya migradas |
| Cutover sobre R2 de producción | ⏳ Pendiente de ejecución remota | El workspace local no contiene bucket ni credenciales R2 |

**Estado global:** aprobado a nivel de código; certificación de producción
condicionada a ejecutar y firmar el cutover remoto descrito abajo.

> **Bucket de recuperación de backups:** operativo en producción. Los respaldos
> diarios se conservan en el bucket de recuperación mediante GitHub Actions y
> la validación remota está documentada en `SPRINT23.1-REPORT.md`. Este control
> de recuperación es independiente del cutover de las 11 referencias legacy
> del almacenamiento operativo de archivos de clientes.

## Evidencia local

### Inventario

```text
public_media_legacy = 11
reports_legacy = 0
evidence_legacy = 0
log_attachments_legacy = 0
already_object = 2
legacy_total = 11
```

La simulación produjo:

```text
public_media = 11
missing = 0
legacy_refs_pending = 11
```

Las 11 referencias corresponden a logos e imágenes de producto y tienen archivo
local disponible. No se aplicó la migración en este workspace porque su backend
es `local`; hacerlo aquí no certificaría Cloudflare R2.

### Pruebas

- Batería focalizada de storage, migración, backup, infraestructura, adjuntos y
  hardening: **71 aprobadas**.
- Contrato específico de `file_storage`: **9 aprobadas**.
- CLI `migrate-storage --list`: corregida y ejecutada correctamente en PowerShell.
- Suite completa: **292 aprobadas**; 3 fallos preexistentes ajenos a storage
  (expectativa HTML de guía y métricas Prometheus no instaladas en el venv local).

## Controles certificados

- Todas las escrituras activas usan `save_bytes()` y claves
  `empresas/{empresa_id}/...`.
- PostgreSQL conserva `storage://...` para medios públicos protegidos y claves
  de objeto para evidencias/adjuntos privados; no conserva binarios.
- `static/uploads` solo permanece como compatibilidad de lectura y origen de
  migración; no se detectaron escrituras activas nuevas.
- El endpoint `/media` limita tipos públicos y valida empresa propietaria.
- Informes, evidencias y adjuntos usan rutas privadas del recurso.
- Una clave de otro tenant no puede usarse para acreditar cuota durante un
  reemplazo.
- Las fallas S3/R2 emiten alerta operativa y se propagan en escritura/lectura.
- Las limpiezas posteriores al commit son best-effort y alertables.

## Gate remoto obligatorio

Ejecutar desde una consola conectada a la configuración real de Render/R2:

```powershell
flask --app run:app migrate-storage --inventory-only
flask --app run:app migrate-storage --list
flask --app run:app migrate-storage
flask --app run:app migrate-storage --apply
flask --app run:app migrate-storage --inventory-only
```

Criterios de aprobación:

1. `STORAGE_BACKEND=s3` y todas las variables `STORAGE_*` requeridas presentes.
2. Simulación con `missing = 0`.
3. Aplicación finaliza sin error.
4. Inventario final con `legacy_total = 0`.
5. Abrir logo, foto de activo, imagen de producto, informe OT, evidencia y
   adjunto de bitácora de un tenant piloto.
6. Confirmar HTTP 403 desde un usuario de otra empresa.
7. Comparar uso por tenant antes/después y verificar que no hay doble conteo.
8. Registrar fecha, responsable, commit, conteos y capturas en esta sección.

## Registro del cutover

| Campo | Valor |
|-------|-------|
| Fecha UTC | Pendiente |
| Responsable | Pendiente |
| Commit desplegado | Pendiente |
| Inventario inicial | Pendiente |
| Resultado `--apply` | Pendiente |
| Inventario final | Pendiente |
| Smoke de seis tipos de archivo | Pendiente |
| Aislamiento cruzado | Pendiente |
| Veredicto final | Pendiente |

No eliminar `static/uploads` hasta completar este registro y conservar un
backup verificable de PostgreSQL + R2 de la misma ventana.
