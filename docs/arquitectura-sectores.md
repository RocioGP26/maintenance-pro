# Arquitectura multi-sector — Mantis CMMS

Un solo código base con **plantillas sectoriales**. No hay tablas `activo_manufactura`, `activo_logistica`, etc.

## Capas

### 1. Campos base (`machines`)

Aplican a **todos** los activos, independientemente del sector:

| Campo | Columna |
|-------|---------|
| Código | `codigo` |
| Nombre | `nombre` |
| Descripción | `descripcion` |
| Marca / Modelo | `marca`, `modelo` |
| Serie | `numero_serie` |
| Ubicación | `ubicacion` |
| Estado | `status` |
| Criticidad | `criticidad` (+ `es_critico` derivado) |
| Fecha compra | `fecha_compra` |
| Proveedor | `proveedor` |
| Manual | `manual_url` |
| Fotografía | `foto_url` |

### 2. Categorías de activo (`machine_types`)

Por empresa y sector. Se crean en el onboarding vía `crear_plantilla_sector()`.

- Clave interna: `e{empresa_id}_{categoria}` (ej. `e3_montacargas`)
- Nombre visible: «Montacargas», «Camiones», etc.
- Catálogo maestro: `app/sector_templates.py` → `SECTOR_CATEGORIES`

### 3. Campos personalizados

| Tabla | Rol |
|-------|-----|
| `campos_personalizados` | Definición (nombre, tipo, obligatorio, sector, categoría opcional) |
| `activo_campo_valores` | Valor por activo (`machine_id` + `campo_id`) |

Tipos soportados: `text`, `number`, `date`, `boolean`.

Definiciones por sector en `SECTOR_CUSTOM_FIELDS` (ej. Logística: placa, SOAT, kilometraje).

### 4. Plantilla de dashboard (`plantillas_dashboard`)

JSON por empresa con:

- `kpis`: etiquetas visibles por sector (misma métrica, distinto nombre)
- `categories`: agrupación del panel sectorial en el dashboard

Generado en onboarding; lectura con `get_plantilla_dashboard()`.

## Flujo onboarding

```
completar_onboarding()
  → crear_plantilla_sector(empresa_id, sector)
       → MachineType por categoría del sector
       → CampoPersonalizado del sector
       → PlantillaDashboard (JSON)
  → crear_activos_ejemplo()
```

## Sectores disponibles

`manufactura`, `logistica`, `salud`, `mineria`, `alimentos`, `construccion`, `educacion`

Ampliar en `app/sector_templates.py` (no duplicar lógica en rutas).

## Formulario de activo

- Una sola plantilla: `templates/activos/form.html`
- Bloque **datos base** + bloque **campos del sector**
- Al cambiar categoría, JS muestra/oculta campos (`machine_type_id` en `campos_personalizados`)
- API: `GET /activos/api/campos?type_id=`

## Empresas existentes

`ensure_empresa_sector_setup()` en el dashboard: si la empresa no tiene categorías propias, aplica la plantilla de su sector.

## Próximos pasos sugeridos

- Subida de archivo para `manual` / `foto` (hoy URL)
- Reportes filtrados por campos personalizados (SOAT, calibración)
- KPIs calculados específicos (km recorridos, % calibrados) usando los mismos valores dinámicos
- UI admin para editar campos sin tocar código

## Referencias en código

| Archivo | Contenido |
|---------|-----------|
| `app/sector_templates.py` | Catálogo estático |
| `app/sector_service.py` | `crear_plantilla_sector`, campos, plantilla |
| `app/onboarding_service.py` | Orquestación registro |
| `app/models.py` | `CampoPersonalizado`, `ActivoCampoValor`, `PlantillaDashboard` |
