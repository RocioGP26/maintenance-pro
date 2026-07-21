# Colecciones API · Roustix v1

Colecciones oficiales alineadas a [`openapi.v1.yaml`](../openapi.v1.yaml) · [MSD-08](../../msd/chapters/08-colecciones.md).

## Archivos

| Archivo | Uso |
|---------|-----|
| `roustix-api-v1.postman_collection.json` | Postman · Collection v2.1 |
| `roustix-sandbox.postman_environment.json` | Postman · entorno Sandbox |
| `roustix-api-v1.insomnia.json` | Insomnia · Export v4 |

## Importación

### Postman

1. Import → `roustix-api-v1.postman_collection.json`
2. Import → `roustix-sandbox.postman_environment.json`
3. Seleccionar entorno **Roustix Sandbox**
4. Ejecutar **Authentication → Login** (ajustar credenciales)
5. El script guarda `token` automáticamente

### Insomnia

1. Application → Import → `roustix-api-v1.insomnia.json`
2. Configurar variables de entorno en el workspace

## Variables

| Variable | Valor por defecto |
|----------|-------------------|
| `base_url` | `http://127.0.0.1:5000` |
| `api_v1` | `{{base_url}}/api/v1` |
| `api_legacy` | `{{base_url}}/api` |
| `empresa_slug` | `empresa-demo` |
| `token` | *(vacío — se llena tras login)* |

## Nota local (legacy)

Hasta alias `/api/v1/*` completos, use la carpeta **Legacy (local)** en Postman o sustituya:

- `POST {{api_legacy}}/auth/login`
- `GET {{api_legacy}}/me`
- `GET {{api_legacy}}/activos`

## Regeneración (planificado)

```bash
openapi2postmanv2 -s ../openapi.v1.yaml -o roustix-api-v1.postman_collection.json
```

→ [MSD-03 OpenAPI](../../msd/chapters/03-openapi.md)
