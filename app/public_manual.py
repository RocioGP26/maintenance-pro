"""Manual de usuario público — Roustix Maintenance (paso a paso).

Fuente Markdown: docs/manual-usuario/
Vista pública: /manual (sin códigos Sprint, ALIGN ni gaps de ingeniería).
"""

from __future__ import annotations

MANUAL_INTRO = (
    "Este manual explica cómo usar Roustix Maintenance día a día: "
    "iniciar sesión, gestionar activos, crear y cerrar órdenes de trabajo, "
    "reportar incidencias, controlar repuestos y consultar indicadores."
)

MANUAL_TOC: tuple[dict[str, str], ...] = (
    {"id": "acceso", "titulo": "1. Acceso y primeros pasos"},
    {"id": "roles", "titulo": "2. Roles y menú"},
    {"id": "activos", "titulo": "3. Activos"},
    {"id": "ordenes", "titulo": "4. Órdenes de trabajo"},
    {"id": "preventivo", "titulo": "5. Preventivo y calendario"},
    {"id": "incidencias", "titulo": "6. Incidencias"},
    {"id": "repuestos", "titulo": "7. Repuestos técnicos"},
    {"id": "analisis", "titulo": "8. Inicio y reportes"},
    {"id": "admin", "titulo": "9. Administración"},
    {"id": "faq", "titulo": "10. Preguntas frecuentes"},
)

MANUAL_ACCESO: dict[str, object] = {
    "pasos_login": (
        "Abre la URL de tu empresa e ingresa a Iniciar sesión.",
        "Escribe usuario y contraseña. Si hay homónimos entre empresas, completa también el identificador de empresa.",
        "Pulsa Entrar. Llegarás a Inicio, el centro de operaciones del día.",
    ),
    "recuperar": (
        "En el login elige «¿Olvidaste tu contraseña?».",
        "Indica el correo registrado (y el slug de empresa si aplica).",
        "Abre el enlace del mensaje y define una nueva contraseña.",
    ),
    "checklist_admin": (
        "Configurar datos de la empresa",
        "Crear usuarios y roles",
        "Registrar tipos de activo y activos",
        "Cargar repuestos técnicos con stock mínimo",
        "Definir planes preventivos en activos críticos",
        "Probar el flujo incidencia → OT → cierre",
    ),
}

MANUAL_ROLES: tuple[tuple[str, str], ...] = (
    ("Superadministrador", "Acceso total a la empresa y configuración avanzada"),
    ("Administrador", "Catálogos, equipo, OT, activos y reportes"),
    ("Supervisor", "Planea, asigna, cambia estados y crea OT"),
    ("Técnico", "Ejecuta OT e incidencias asignadas; consulta activos y repuestos"),
    ("Solicitante", "Reporta incidencias y sigue solo las suyas"),
    ("Usuario (consulta)", "Lectura de información autorizada"),
    ("Vendedor", "Inventario comercial; en mantenimiento solo sus incidencias"),
)

MANUAL_ESTADOS_ACTIVO: tuple[tuple[str, str], ...] = (
    ("Operativo", "En servicio normal"),
    ("En mantenimiento", "Intervención programada o en curso"),
    ("En falla", "Detenido por avería"),
)

MANUAL_ESTADOS_OT: tuple[tuple[str, str], ...] = (
    ("Programada", "Fecha futura; aún no inicia"),
    ("Abierta", "Lista para ejecutar"),
    ("En proceso", "Trabajo en curso"),
    ("Vencida", "Pasó la fecha sin cierre"),
    ("Completado", "Técnico terminó; falta cierre administrativo"),
    ("Cerrada", "Finalizada; ya no se edita"),
)

MANUAL_CREAR_OT: tuple[str, ...] = (
    "Ve a Órdenes de trabajo → Listado → Nueva.",
    "Selecciona el activo, el tipo (preventivo, correctivo o emergencia) y la prioridad.",
    "Indica si la ejecución es interna (técnico) o externa (proveedor).",
    "Describe el trabajo, asigna responsable y fecha si aplica.",
    "Guarda. El estado típico inicial es programada o abierta.",
)

MANUAL_EJECUTAR_OT: tuple[str, ...] = (
    "Abre la OT asignada y pásala a En proceso.",
    "Registra jornadas (tiempos). La mano de obra usa la tarifa hora del momento.",
    "Registra repuestos consumidos; descuentan stock técnico.",
    "Completa checklist u observaciones si aplica.",
    "Solicita finalización → estado Completado.",
    "Un supervisor o administrador confirma el cierre → Cerrada.",
)

MANUAL_INCIDENCIA: tuple[str, ...] = (
    "Reporta en Reportar incidencia: área, prioridad, descripción y activo si lo conoces.",
    "El equipo del área recibe la alerta (no toda la empresa).",
    "El supervisor puede resolver sin OT o crear una OT vinculada.",
    "El solicitante recibe notificaciones cuando cambia el estado de su ticket.",
)

MANUAL_INICIO_BLOQUES: tuple[tuple[str, str], ...] = (
    ("OT abiertas / vencidas", "Carga pendiente y trabajo fuera de fecha"),
    ("Preventivos de hoy", "Intervenciones de la jornada"),
    ("Incidencias", "Reportes nuevos o abiertos"),
    ("Repuestos bajo mínimo", "Riesgo de paro por falta de piezas"),
    ("Activos fuera de servicio", "Equipos en mantenimiento o falla"),
    ("Garantías por vencer", "Coberturas en los próximos 30 días"),
)

MANUAL_FAQ: tuple[tuple[str, str], ...] = (
    (
        "¿Por qué no veo algunas opciones del menú?",
        "El menú depende de tu rol, tu área y los módulos contratados. Lo no autorizado no se muestra.",
    ),
    (
        "¿El técnico puede cerrar una OT?",
        "El técnico deja la OT en Completado. El cierre definitivo (Cerrada) lo hace un supervisor o administrador.",
    ),
    (
        "¿Toda incidencia genera una OT?",
        "No. El supervisor decide si se resuelve sin OT o se escala a una orden de trabajo.",
    ),
    (
        "¿Repuestos técnicos es lo mismo que Inventario comercial?",
        "No. Repuestos son piezas de mantenimiento. Inventario comercial es compra y venta de mercancía.",
    ),
    (
        "¿Dónde veo MTBF y cumplimiento preventivo?",
        "En Inteligencia → Análisis → Mantenimiento, con filtros por período.",
    ),
)

MANUAL_RUTAS: tuple[tuple[str, str], ...] = (
    ("Login", "/login"),
    ("Inicio", "/dashboard"),
    ("Activos", "/activos"),
    ("Nueva OT", "/ordenes/nueva"),
    ("Calendario", "/calendario"),
    ("Reportar incidencia", "/incidencia"),
    ("Repuestos técnicos", "/inventario"),
    ("Análisis mantenimiento", "/analisis/mantenimiento"),
    ("Usuarios y roles", "/equipo"),
    ("Guía de producto", "/guia"),
)
