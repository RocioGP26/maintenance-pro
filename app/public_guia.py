"""Guía de producto pública — vista cliente (MRG → HTML maquetado).

Fuente interna: docs/mrg/chapters/*.md
Vista pública: /guia (sin códigos Sprint, ALIGN ni gaps de ingeniería).
"""

from __future__ import annotations

GUIA_INTRO = (
    "Esta guía explica cómo funciona Roustix en lenguaje de negocio: "
    "módulos, roles y capacidades disponibles hoy para operar tu empresa."
)

GUIA_PRINCIPIOS: tuple[dict[str, str], ...] = (
    {
        "titulo": "Una empresa, un espacio",
        "texto": "Tus datos quedan aislados por empresa. Cada equipo ve solo su operación.",
    },
    {
        "titulo": "Modular",
        "texto": "Activas Mantenimiento, Inventario o ambos. El menú se adapta a lo contratado.",
    },
    {
        "titulo": "En la nube",
        "texto": "SaaS mensual: sin instalación local. Prueba 15 días y opera desde el navegador.",
    },
    {
        "titulo": "Trazable",
        "texto": "Órdenes, movimientos y activos con historial. Menos Excel, más decisiones.",
    },
)

GUIA_ANTES_DESPUES: tuple[dict[str, str], ...] = (
    {
        "antes": "OT en papel o WhatsApp sin historial",
        "despues": "Órdenes de trabajo con técnico, estados y costos",
    },
    {
        "antes": "Inventario desactualizado entre Excels",
        "despues": "Stock en tiempo real con alertas de mínimo",
    },
    {
        "antes": "Datos mezclados entre sedes o áreas",
        "despues": "Una sola verdad operativa por empresa",
    },
    {
        "antes": "Reportes que tardan horas en armarse",
        "despues": "Dashboards e indicadores listos para decidir",
    },
)

GUIA_MANTENIMIENTO: dict[str, object] = {
    "titulo": "Roustix Maintenance",
    "subtitulo": "Activos, órdenes de trabajo y preventivos",
    "frase": "La planta deja de depender de la memoria del técnico.",
    "incluye": (
        "Registro de activos con estado, ubicación y criticidad",
        "Órdenes de trabajo correctivas, preventivas y de emergencia",
        "Planes de mantenimiento preventivo con seguimiento",
        "Incidencias convertibles en OT",
        "Repuestos técnicos consumidos en cada intervención",
        "Dashboard de OT abiertas, disponibilidad e indicadores",
    ),
    "roles": (
        ("Administrador", "Configura activos, planes y equipo"),
        ("Supervisor", "Planea OT y asigna técnicos o proveedores"),
        ("Técnico", "Ejecuta OT, registra tiempos y repuestos"),
        ("Solicitante", "Reporta fallas y solicita intervención"),
    ),
    "flujo": ("Programada", "Asignada", "En ejecución", "Cerrada"),
}

GUIA_INVENTARIO: dict[str, object] = {
    "titulo": "Roustix Inventory",
    "subtitulo": "Catálogo, stock, compras y ventas",
    "frase": "Deja de vender a ciegas.",
    "incluye": (
        "Catálogo de productos (SKU, precios, ubicaciones)",
        "Stock actualizado con entradas y salidas",
        "Alertas cuando el stock baja del mínimo",
        "Compras que aumentan existencias",
        "Ventas / POS que descuentan stock disponible",
        "Importación y exportación de catálogo en Excel",
    ),
    "roles": (
        ("Administrador", "Configura catálogo, bodega y permisos"),
        ("Bodega / compras", "Registra entradas y controla mínimos"),
        ("Ventas", "Vende con stock real y sigue cartera"),
        ("Gerencia", "Ve valorización e indicadores de rotación"),
    ),
}

GUIA_CRECIMIENTO: tuple[dict[str, str], ...] = (
    {
        "etapa": "Hoy",
        "texto": "Empiezas con Mantenimiento o Inventario — lo que duele en tu operación.",
    },
    {
        "etapa": "Mañana",
        "texto": "Activas el segundo módulo sin migrar de sistema ni perder historial.",
    },
    {
        "etapa": "Después",
        "texto": "La misma plataforma crece contigo: más usuarios, sedes y capacidades.",
    },
)
