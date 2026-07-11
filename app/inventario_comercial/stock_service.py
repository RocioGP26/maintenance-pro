"""Único límite para movimientos de stock originados fuera de Inventory."""


def aplicar_entrada_confirmada(producto, cantidad: float) -> None:
    """Incrementa stock por una recepción ya validada."""
    if cantidad <= 0:
        return
    if not float(cantidad).is_integer():
        raise ValueError("El stock de productos solo admite unidades enteras.")
    producto.stock = int(producto.stock or 0) + int(cantidad)
