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

## Migración de archivos existentes

Primero ejecutar el inventario sin modificar datos:

```powershell
flask --app run:app migrate-storage
```

Después de revisar el contador `missing`, aplicar:

```powershell
flask --app run:app migrate-storage --apply
```

La operación copia antes de cambiar la referencia en base de datos y puede
repetirse. No elimina automáticamente los archivos antiguos; deben conservarse
hasta validar imágenes y descargas en producción.

## Recuperación

1. Activar versionado, Object Lock o la alternativa de protección del proveedor.
2. Replicar el bucket a una cuenta o ubicación independiente.
3. Conservar las credenciales de recuperación fuera de Render.
4. Trimestralmente, restaurar una muestra en un bucket temporal y comprobar
   checksum, visualización y descarga desde Roustix.

La copia de PostgreSQL y la copia del bucket forman un único respaldo lógico:
restaurar solamente la base deja referencias a objetos inexistentes.
