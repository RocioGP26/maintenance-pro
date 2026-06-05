"""Constructor y utilidades de campos personalizados por activo."""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Optional

from app.models import CampoPersonalizado

CAMPO_TIPOS = (
    ("text", "Texto"),
    ("date", "Fecha"),
    ("number", "Número"),
    ("boolean", "Sí/No"),
    ("list", "Lista (una opción)"),
    ("list_multi", "Lista múltiple"),
)

TIPOS_CON_OPCIONES = frozenset({"list", "list_multi"})

CAMPO_TIPOS_VALIDOS = {t for t, _ in CAMPO_TIPOS}

CAMPO_TIPOS_LABEL = dict(CAMPO_TIPOS)

# Anchura de columna Bootstrap según tipo (formulario de activo / equipo)
# 4 campos por fila (col-md-3) en pantallas medianas en adelante
CAMPO_GRID_4_POR_FILA = "col-6 col-md-3"

CAMPO_TIPO_GRID_COL: dict[str, str] = {
    "number": CAMPO_GRID_4_POR_FILA,
    "date": CAMPO_GRID_4_POR_FILA,
    "boolean": "col-6 col-md-3",
    "list": "col-12 col-sm-6 col-md-4",
    "list_multi": "col-12",
}

TEXTO_TAMANO_CORTO = "corto"
TEXTO_TAMANO_MEDIANO = "mediano"
TEXTO_TAMANO_LARGO = "largo"
TEXTO_TAMANO_DEFAULT = TEXTO_TAMANO_MEDIANO

TEXTO_TAMANOS = (
    (TEXTO_TAMANO_CORTO, "Texto corto"),
    (TEXTO_TAMANO_MEDIANO, "Texto mediano"),
    (TEXTO_TAMANO_LARGO, "Texto largo"),
)
TEXTO_TAMANOS_VALIDOS = {t for t, _ in TEXTO_TAMANOS}
TEXTO_TAMANO_LABEL = dict(TEXTO_TAMANOS)

CAMPO_TEXTO_GRID_COL: dict[str, str] = {
    TEXTO_TAMANO_CORTO: CAMPO_GRID_4_POR_FILA,
    TEXTO_TAMANO_MEDIANO: "col-12 col-md-6",
    TEXTO_TAMANO_LARGO: "col-12",
}


def normalizar_texto_tamano(valor: str | None) -> str:
    key = (valor or TEXTO_TAMANO_DEFAULT).strip().lower()
    return key if key in TEXTO_TAMANOS_VALIDOS else TEXTO_TAMANO_DEFAULT


def parse_texto_tamano_form(form, tipo: str) -> str:
    if (tipo or "").strip().lower() != "text":
        return ""
    return normalizar_texto_tamano(form.get("texto_tamano"))


def columna_grid_para_campo(tipo: str, texto_tamano: str | None = None) -> str:
    key = (tipo or "text").strip().lower()
    if key == "text":
        return CAMPO_TEXTO_GRID_COL[normalizar_texto_tamano(texto_tamano)]
    return CAMPO_TIPO_GRID_COL.get(key, CAMPO_TEXTO_GRID_COL[TEXTO_TAMANO_MEDIANO])


def columna_grid_campo_tipo(tipo: str) -> str:
    return columna_grid_para_campo(tipo)


def campo_es_columna_compacta(campo) -> bool:
    t = (getattr(campo, "tipo", None) or "text").strip().lower()
    if t in ("number", "date"):
        return True
    if t == "text":
        return normalizar_texto_tamano(getattr(campo, "texto_tamano", None)) == TEXTO_TAMANO_CORTO
    return False


def seccion_campos_cuatro_por_fila(campos) -> bool:
    """True si todos los campos caben en 4 columnas por fila."""
    if not campos:
        return False
    return all(campo_es_columna_compacta(c) for c in campos)


CAMPO_ENTIDAD_ACTIVO = "activo"
CAMPO_ENTIDAD_EQUIPO = "equipo"

CAMPO_ENTIDADES = (
    (CAMPO_ENTIDAD_ACTIVO, "Activos (equipos)"),
    (CAMPO_ENTIDAD_EQUIPO, "Equipo técnico"),
)

CAMPO_ENTIDAD_LABEL = dict(CAMPO_ENTIDADES)


def slugify_campo_clave(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return (s or "campo")[:48]


def clave_campo_unica(
    empresa_id: int,
    sector: str,
    base: str,
    exclude_id: Optional[int] = None,
    entidad: str = CAMPO_ENTIDAD_ACTIVO,
) -> str:
    c = base[:48]
    n = 2
    while True:
        q = CampoPersonalizado.query.filter_by(
            empresa_id=empresa_id, sector=sector, clave=c, entidad=entidad
        )
        if exclude_id:
            q = q.filter(CampoPersonalizado.id != exclude_id)
        if not q.first():
            return c
        suffix = f"_{n}"
        c = (base[: 48 - len(suffix)] + suffix)[:48]
        n += 1


def parse_opciones_texto(texto: str) -> tuple[Optional[str], Optional[str]]:
    """Convierte líneas o JSON a texto JSON almacenado. Devuelve (json, error)."""
    raw = (texto or "").strip()
    if not raw:
        return "[]", None
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            items = [str(x).strip() for x in data if str(x).strip()]
            if not items:
                return None, "Indica al menos una opción para la lista."
            return json.dumps(items, ensure_ascii=False), None
    except json.JSONDecodeError:
        pass
    items = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not items:
        items = [p.strip() for p in raw.split(",") if p.strip()]
    if not items:
        return None, "Indica al menos una opción (una por línea)."
    return json.dumps(items, ensure_ascii=False), None


def opciones_desde_campo(campo: CampoPersonalizado) -> list[str]:
    raw = (campo.opciones or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except json.JSONDecodeError:
        pass
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]


def opciones_a_texto_form(campo: Optional[CampoPersonalizado]) -> str:
    if not campo or not campo.opciones:
        return ""
    items = opciones_desde_campo(campo)
    return "\n".join(items)


def valores_lista_multi_desde_almacenado(valor: Optional[str]) -> list[str]:
    """Valores guardados de un campo lista múltiple (JSON o texto legado)."""
    raw = (valor or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
    except json.JSONDecodeError:
        pass
    if raw.startswith("[") and raw.endswith("]"):
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def lista_multi_valor_guardar(
    seleccion: list, opciones_validas: list[str]
) -> tuple[str, Optional[str]]:
    valid_set = set(opciones_validas)
    items: list[str] = []
    for raw in seleccion:
        s = (raw or "").strip()
        if not s:
            continue
        if s not in valid_set:
            return "", f"Opción no válida: «{s}»."
        if s not in items:
            items.append(s)
    if not items:
        return "", None
    return json.dumps(items, ensure_ascii=False), None


def multi_seleccion_desde_valor(campo: CampoPersonalizado, valor: Optional[str]) -> set[str]:
    opts = set(campo.opciones_lista())
    return set(valores_lista_multi_desde_almacenado(valor)) & opts


def valor_campo_desde_form(campo: CampoPersonalizado, form) -> tuple[str, Optional[str]]:
    """Lee y valida el valor enviado en el formulario para un campo personalizado."""
    tipo = (campo.tipo or "").strip().lower()
    key = f"campo_{campo.id}"

    if tipo == "boolean":
        raw = form.get(key, "")
        val = "1" if raw in ("1", "on", "true") else ""
        if campo.obligatorio and not val:
            return "", f"El campo «{campo.nombre}» es obligatorio."
        return val, None

    if tipo == "list_multi":
        val, err = lista_multi_valor_guardar(form.getlist(key), campo.opciones_lista())
        if err:
            return "", err
        if campo.obligatorio and not val:
            return "", f"El campo «{campo.nombre}» es obligatorio."
        return val, None

    val = (form.get(key, "") or "").strip()
    if tipo == "list" and val and val not in campo.opciones_lista():
        return "", f"Valor no válido para «{campo.nombre}»."
    if campo.obligatorio and not val:
        return "", f"El campo «{campo.nombre}» es obligatorio."
    return val, None


def categorias_ids_desde_campo(campo: CampoPersonalizado) -> list[int]:
    """IDs de categorías donde aplica; lista vacía = todas."""
    raw = (campo.categorias_ids or "").strip()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return sorted({int(x) for x in data if str(x).isdigit() or isinstance(x, int)})
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    if campo.machine_type_id:
        return [int(campo.machine_type_id)]
    return []


def categorias_ids_a_json(ids: list[int]) -> str:
    return json.dumps(sorted(set(int(i) for i in ids)), ensure_ascii=False)


def parse_categorias_form(form, tipos_validos: set[int]) -> list[int]:
    """IDs marcados en el formulario; ninguno = aplica a todas."""
    ids: list[int] = []
    for raw in form.getlist("categorias_ids"):
        if str(raw).isdigit():
            tid = int(raw)
            if tid in tipos_validos:
                ids.append(tid)
    return sorted(set(ids))


def campo_aplica_a_tipo(campo: CampoPersonalizado, machine_type_id: int | None) -> bool:
    if not machine_type_id:
        return len(categorias_ids_desde_campo(campo)) == 0
    ids = categorias_ids_desde_campo(campo)
    if not ids:
        return True
    return int(machine_type_id) in ids


def etiqueta_categorias_campo(
    campo: CampoPersonalizado, tipos_map: dict[int, str]
) -> str:
    ids = categorias_ids_desde_campo(campo)
    if not ids:
        return "Todas las categorías"
    nombres = [tipos_map.get(i, f"#{i}") for i in ids]
    return ", ".join(nombres)
