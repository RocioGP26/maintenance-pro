"""FAQ público — fuente única MCM-08-FAQ (Sprint 14 · Fase 2)."""

from __future__ import annotations

FAQ_SECTIONS: tuple[dict, ...] = (
    {
        "id": "producto",
        "title": "Producto y plataforma",
        "entries": (
            {
                "q": "¿Qué es Maintix?",
                "a": (
                    "Una Enterprise Management Platform (EMP) SaaS modular para controlar "
                    "la operación de PYMEs en crecimiento — mantenimiento, inventario y "
                    "módulos futuros en una sola plataforma."
                ),
            },
            {
                "q": "¿Es un ERP?",
                "a": (
                    "No en el sentido tradicional. Maintix no requiere meses de implementación "
                    "ni consultoría pesada. Es operación digitalizada en días, modular y escalable."
                ),
            },
            {
                "q": "¿Es solo mantenimiento o solo inventario?",
                "a": (
                    "Puede empezar por Mantenimiento o Inventario según el dolor dominante. "
                    "Ambos son puertas a la misma plataforma."
                ),
            },
            {
                "q": "¿Qué módulos están disponibles hoy?",
                "a": (
                    "En producción: Mantenimiento e Inventario (incluye compras, ventas POS, "
                    "clientes y cuentas por pagar operativas). En roadmap: CRM, Purchasing "
                    "formal, Finance y Analytics."
                ),
            },
        ),
    },
    {
        "id": "precios",
        "title": "Precios y planes",
        "entries": (
            {
                "q": "¿Cuánto cuesta?",
                "a": (
                    "SaaS mensual por plan: Start · Grow · Scale · Enterprise. "
                    "Los precios definitivos estarán disponibles próximamente. "
                    "Contacta al equipo Maintix para recibir información comercial."
                ),
            },
            {
                "q": "¿Hay prueba gratuita?",
                "a": "Sí — 15 días sin compromiso y sin tarjeta de crédito.",
            },
            {
                "q": "¿Puedo empezar con un solo módulo?",
                "a": (
                    "Sí. El plan Start incluye un módulo a elegir. "
                    "Es el diseño intencional del producto."
                ),
            },
            {
                "q": "¿Qué pasa cuando crecemos?",
                "a": (
                    "Subes de plan cuando la operación evoluciona — más usuarios, sedes "
                    "o segundo módulo — sin cambiar de plataforma."
                ),
            },
        ),
    },
    {
        "id": "implementacion",
        "title": "Implementación y soporte",
        "entries": (
            {
                "q": "¿Cuánto tarda implementar?",
                "a": (
                    "Orientación por plan: Start 3–7 días · Grow 1–2 semanas · "
                    "Scale 2–4 semanas."
                ),
            },
            {
                "q": "¿Necesito consultoría externa?",
                "a": (
                    "No es obligatorio. Start es self-service con guías oficiales. "
                    "Grow y superiores incluyen onboarding guiado."
                ),
            },
            {
                "q": "¿Quién administra la plataforma?",
                "a": (
                    "Dos niveles: el administrador de tu empresa (usuarios, configuración) "
                    "y el operador SaaS de plataforma (tenants y planes comerciales)."
                ),
            },
        ),
    },
    {
        "id": "tecnico",
        "title": "Técnico e integraciones",
        "entries": (
            {
                "q": "¿Tiene API?",
                "a": "Sí. Contrato público en MAG · herramientas para integradores en MSD.",
            },
            {
                "q": "¿Se integra con mi ERP?",
                "a": (
                    "Enfoque API-first. Integraciones según plan y alcance — "
                    "escala con preventa o TI cuando aplique."
                ),
            },
            {
                "q": "¿Mis datos están aislados?",
                "a": "Sí — modelo tenant-first: cada empresa ve solo sus datos.",
            },
            {
                "q": "¿Dónde se aloja?",
                "a": "SaaS en la nube — sin instalación local.",
            },
        ),
    },
    {
        "id": "comercial",
        "title": "Comercial y mercado",
        "entries": (
            {
                "q": "¿Para qué tamaño de empresa?",
                "a": (
                    "Orientativo: 10–500 empleados en crecimiento. "
                    "No microempresa sin procesos ni enterprise global desde el día 1."
                ),
            },
            {
                "q": "¿En qué países operan?",
                "a": "Latinoamérica — foco inicial Colombia y Venezuela.",
            },
            {
                "q": "¿Venden por industria?",
                "a": (
                    "No. Venden por operación. Los sectores adaptan el idioma del discurso, "
                    "no el producto."
                ),
            },
            {
                "q": "¿Tienen casos de éxito?",
                "a": (
                    "Narrativas por sector documentadas en Maintix Docs (MTX-CASE). "
                    "Cada caso indica su nivel de evidencia."
                ),
            },
        ),
    },
    {
        "id": "diferenciacion",
        "title": "Competencia y diferenciación",
        "entries": (
            {
                "q": "¿En qué se diferencian de un ERP tradicional?",
                "a": (
                    "Implementación rápida · modular · UX moderna · precio accesible "
                    "para PYME · enfoque operativo real."
                ),
            },
            {
                "q": "¿Y frente a un CMMS o inventario aislado?",
                "a": (
                    "Una plataforma — mantenimiento e inventario comparten tenant, usuarios "
                    "y dashboards. Segundo módulo sin migración."
                ),
            },
            {
                "q": "¿Pueden desarrollar a medida?",
                "a": (
                    "Maintix es producto SaaS, no consultora. Personalización acotada "
                    "en plan Enterprise."
                ),
            },
        ),
    },
)
