"""Imágenes de productos comerciales."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.file_storage import delete, key_from_reference, reference, save_bytes, tenant_key, url_for_reference
from werkzeug.utils import secure_filename

if TYPE_CHECKING:
    from app.models import InvProducto

PRODUCTO_IMAGEN_EXTENSIONS = frozenset({"png", "jpg", "jpeg", "webp"})


def normalizar_imagen_producto(ruta: str) -> Optional[str]:
    """Permite solo URLs https o rutas relativas bajo uploads/."""
    value = (ruta or "").strip()
    if not value:
        return None
    if value.startswith("https://"):
        return value
    if key_from_reference(value):
        return value
    if value.startswith("uploads/") and ".." not in value and not value.startswith("//"):
        return value
    return None


def producto_imagen_url_or_none(producto: Optional["InvProducto"]) -> Optional[str]:
    if not producto or not (getattr(producto, "imagen", None) or "").strip():
        return None
    ref = normalizar_imagen_producto(producto.imagen.strip())
    if not ref:
        return None
    return url_for_reference(ref)


def guardar_imagen_producto_archivo(producto: "InvProducto", archivo) -> None:
    if not archivo or not getattr(archivo, "filename", None):
        return
    if not producto.id:
        raise ValueError("El producto debe guardarse antes de subir la imagen.")
    nombre = secure_filename(archivo.filename)
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext not in PRODUCTO_IMAGEN_EXTENSIONS:
        raise ValueError("Formato de imagen no permitido. Use PNG, JPG o WEBP.")
    content = archivo.stream.read()
    if not content:
        raise ValueError("La imagen está vacía.")
    for old_ext in PRODUCTO_IMAGEN_EXTENSIONS:
        if old_ext != ext:
            delete(tenant_key(producto.empresa_id, "productos", f"{producto.id}.{old_ext}"))
    key = tenant_key(producto.empresa_id, "productos", f"{producto.id}.{ext}")
    save_bytes(key, content, content_type=f"image/{'jpeg' if ext in {'jpg', 'jpeg'} else ext}")
    producto.imagen = reference(key)


def aplicar_imagen_producto(producto: "InvProducto", form, archivo) -> None:
    imagen_url = (form.get("imagen_url") or "").strip()
    if imagen_url:
        norm = normalizar_imagen_producto(imagen_url)
        if norm is None:
            raise ValueError("URL de imagen no válida. Use https:// o una ruta bajo uploads/.")
        producto.imagen = norm
    if archivo and getattr(archivo, "filename", None):
        guardar_imagen_producto_archivo(producto, archivo)
