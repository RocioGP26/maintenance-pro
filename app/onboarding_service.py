"""Configuración inicial de empresa, sede, plan y datos de ejemplo."""



from datetime import date, timedelta

   

from app import db

from app.models import (

    Empresa,

    Machine,

    PlanSuscripcion,

    PlanTipo,

    Sede,

    Technician,

    User,

    UserRole,

    WorkOrder,

    WorkOrderStatus,

    WorkOrderType,

    PLAN_CATALOG,

)

from app.wo_numbering import asignar_numero_ot

from app.sector_service import crear_activos_ejemplo, crear_plantilla_sector

from app.sector_templates import normalizar_sector





from app.subscription_service import crear_suscripcion_trial





def completar_onboarding(
    empresa_data: dict,
    admin_data: dict,
    sede_nombre: str,
    plan_key: str,
    modulos: list[str] | None = None,
) -> tuple[User, Empresa]:
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO, normalizar_modulos, set_modulos_activos

    sector = normalizar_sector(empresa_data.get("sector"))
    modulos_norm = normalizar_modulos(modulos)
    from app.tenancy.slug import slug_unico_empresa

    slug = slug_unico_empresa(empresa_data["razon_social"])

    empresa = Empresa(
        razon_social=empresa_data["razon_social"],
        slug=slug,
        nit=empresa_data.get("nit", ""),
        direccion=empresa_data.get("direccion", ""),
        ciudad=empresa_data.get("ciudad", ""),
        pais=empresa_data.get("pais", "Colombia"),
        sector=sector,
        telefono=empresa_data.get("telefono", ""),
        email=empresa_data.get("email", ""),
        moneda=empresa_data.get("moneda", "COP"),
        zona_horaria=empresa_data.get("zona_horaria", "America/Bogota"),
    )
    set_modulos_activos(empresa, modulos_norm)
    from app.currency import set_monedas_empresa

    set_monedas_empresa(
        empresa,
        empresa_data.get("monedas_activas"),
        empresa_data.get("moneda"),
    )

    db.session.add(empresa)

    db.session.flush()

    sede = Sede(empresa_id=empresa.id, nombre=sede_nombre or "Sede principal", es_principal=True)

    db.session.add(sede)

    db.session.flush()



    crear_suscripcion_trial(empresa, plan_key)

    from app.user_service import normalizar_username

    user = User(
        empresa_id=empresa.id,
        username=normalizar_username(admin_data.get("username")),
        email=admin_data.get("email", ""),
        nombre_visible=admin_data.get("nombre", ""),
        telefono=admin_data.get("telefono", ""),
        rol=UserRole.SUPERADMIN.value,
        activo=True,
        onboarding_completado=True,
    )

    user.set_password(admin_data["password"])

    db.session.add(user)

    db.session.flush()

    if MODULO_MANTENIMIENTO in modulos_norm:
        resultado = crear_plantilla_sector(empresa.id, sector)
        crear_activos_ejemplo(empresa.id, sede, resultado["tipos"], sector)

        tech = Technician(
            empresa_id=empresa.id,
            nombre=admin_data.get("nombre") or "Técnico de planta",
            especialidad="Mantenimiento general",
            email=admin_data.get("email", ""),
            telefono=admin_data.get("telefono", ""),
            activo=True,
        )
        db.session.add(tech)
        db.session.flush()

        primera = Machine.query.filter_by(empresa_id=empresa.id).first()
        if primera:
            wo_ejemplo = WorkOrder(
                empresa_id=empresa.id,
                titulo="Inspección inicial de bienvenida",
                descripcion="Orden de ejemplo generada al configurar la cuenta.",
                tipo=WorkOrderType.PREVENTIVO.value,
                status=WorkOrderStatus.ABIERTA.value,
                prioridad="media",
                machine_id=primera.id,
                technician_id=tech.id,
                fecha_programada=date.today() + timedelta(days=7),
            )
            db.session.add(wo_ejemplo)
            db.session.flush()
            asignar_numero_ot(wo_ejemplo)

    if MODULO_INVENTARIO in modulos_norm:
        from app.inventario_comercial.service import crear_datos_ejemplo_inventario

        crear_datos_ejemplo_inventario(empresa.id)

    db.session.commit()

    return user, empresa

