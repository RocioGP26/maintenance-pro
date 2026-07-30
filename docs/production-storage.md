# Almacenamiento persistente de Roustix

Roustix usa un backend S3-compatible para que fotografías, logos, informes y
evidencias no dependan del disco efímero del contenedor de Render.

## Proveedores compatibles

- Amazon S3
- Cloudflare R2
- Backblaze B2 (API S3-compatible)

## Configuración

Configurar en Render:

```text
STORAGE_BACKEND=s3
STORAGE_BUCKET=roustix-production
STORAGE_ENDPOINT_URL=https://<endpoint-del-proveedor>
STORAGE_REGION=auto
STORAGE_ACCESS_KEY_ID=<secreto>
STORAGE_SECRET_ACCESS_KEY=<secreto>
```

El bucket debe ser privado. Las descargas pasan por Roustix y validan que el
usuario pertenezca a la empresa propietaria de la clave `empresas/<id>/...`.

Con `STORAGE_BACKEND=s3`, el metering **no** suma `static/uploads` (evita doble
conteo tras migrar). Forzar legacy solo si hace falta:

```text
STORAGE_INCLUDE_LEGACY_UPLOADS=true
```

## Cuota por plan (hard-limit)

Cada upload bajo `empresas/{id}/...` pasa por `save_bytes`, que consulta el cupo
efectivo del tenant (plan + add-ons) y **rechaza** el archivo si no cabe.

Los reemplazos entre extensiones acreditan el tamaño del objeto anterior, pero
no lo eliminan hasta que la transacción PostgreSQL termina correctamente. Una
falla de limpieza posterior se alerta y no convierte un cambio ya confirmado
en un error para el usuario.

- Alerta preventiva: ≥ 80% del cupo (banner portal + página `/configuracion/almacenamiento`).
- Mensaje de rechazo al 100 %: ofrece add-on +2 GB (`ADD-STG-2G`) vía `contacto@roustix.com`.
- CTA **Ampliar almacenamiento** → correo a `contacto@roustix.com`.
- Activación comercial (P0): SuperAdmin en `/platform/empresas/<id>` → **Activar +2 GB**
  (columna `empresas.storage_addon_mb`; suma 2048 MB a la cuota).
- Migración legacy: `migrate-storage --apply` usa `enforce_quota=False`.

### Capacidades oficiales del piloto

| Plan comercial | Clave técnica | Cuota base |
|----------------|---------------|-----------:|
| Start | `basico` | 1 GB |
| Business | `grow` | 5 GB |
| Enterprise | `enterprise` | 20 GB |

`grow` se conserva exclusivamente como clave compatible. La interfaz y la
oferta comercial deben mostrar siempre **Business**.

### Retiro del add-on durante el piloto

- El add-on `ADD-STG-2G` se factura por mes anticipado a **$100.000 COP**.
- La activación es manual después de confirmar el pago y queda auditada.
- La solicitud de retiro se ejecuta al terminar el periodo mensual ya pagado;
  durante el piloto no hay prorrateo automático.
- Retirar el add-on nunca elimina archivos existentes.
- Si el uso queda igual o por encima de la cuota base, las nuevas cargas se
  bloquean hasta liberar espacio, reactivar capacidad o cambiar de plan.
- Las descargas y eliminaciones permanecen disponibles para que el cliente
  pueda volver a estar por debajo del límite.

## Cutover S0 · Migración de archivos existentes

### 1. Inventario (solo BD)

```powershell
flask --app run:app migrate-storage --inventory-only
```

Si `legacy_total = 0`, no hay refs `uploads/` ni evidencias fuera de `empresas/`.

### 2. Listar pendientes (local vs R2)

```powershell
flask --app run:app migrate-storage --list
```

Cada línea indica `local` / `no-local` y `remote` / `no-remote`.

### 3. Simulación (disco + R2)

```powershell
flask --app run:app migrate-storage
```

Revisar `missing`. Ideal: `missing = 0`. Archivos ausentes en disco quedarán
contados como missing (refs rotas previas).

### 3. Aplicar

```powershell
flask --app run:app migrate-storage --apply
```

Copia al backend configurado y reescribe referencias a `storage://...` (o keys
`empresas/...` en evidencias/bitácora). Es idempotente: se puede repetir.

Si el archivo **ya no está** en el disco del contenedor (Render efímero) pero
**sí existe en R2**, `--apply` reescribe la BD igual (`from_remote`).

Refs sin local ni remoto: listar con `--list` y, si son irrecuperables:

```powershell
flask --app run:app migrate-storage --clear-broken
flask --app run:app migrate-storage --clear-broken --apply
```

### 4. Validar en producción

Comprobar por un tenant piloto:

- Logo empresa
- Foto de activo
- Informe OT (descarga)
- Evidencia de checklist
- Adjunto de bitácora

Además:

- Reemplazar una foto PNG por JPG con el tenant al límite de cuota.
- Confirmar que otro tenant recibe HTTP 403 al intentar abrir la clave.
- Simular indisponibilidad R2 y comprobar alerta operativa sin referencia nueva en BD.
- Eliminar un activo y comprobar que foto, manual y ficha dejan de contabilizarse.

### 5. Limpieza

Conservar `static/uploads` y `data/checklist_evidence|maintenance_log` hasta
validar. Después, borrar residuales del disco/efímero. El metering con
`STORAGE_BACKEND=s3` ya no los incluye.

## Recuperación

Documento canónico: [`docs/production-readiness/backup-restore-runbook.md`](production-readiness/backup-restore-runbook.md)
(RTO/RPO, procedimiento, integridad). Plantilla de simulacro:
[`backup-recovery-drill.md`](production-readiness/backup-recovery-drill.md).

1. Activar versionado, Object Lock o la alternativa de protección del proveedor.
2. Replicar el bucket a una cuenta o ubicación independiente (`STORAGE_BACKUP_*`).
3. Conservar las credenciales de recuperación fuera de Render (GitHub Secrets).
4. Trimestralmente, completar un simulacro en `backup-recovery-drill.md`
   (BD + muestra de archivos + smoke).

La copia de PostgreSQL y la copia del bucket forman un único respaldo lógico:
restaurar solamente la base deja referencias a objetos inexistentes.

Estado y evidencia de certificación: [`storage-certification.md`](production-readiness/storage-certification.md).
