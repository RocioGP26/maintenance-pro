"""Cronograma preventivo: matriz PROG/EJEC y plantillas por sector."""

from __future__ import annotations

import unittest
from datetime import date, datetime

from app import create_app, db
from app.maintenance.cronograma_preventivo import (
    construir_cronograma,
    query_machines_sin_plan_preventivo,
    semana_del_mes,
    templates_for_sector,
)
from app.models import (
    Empresa,
    Machine,
    MachineType,
    PreventiveMaintenancePlan,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderType,
)
from app.preventive_maintenance import get_or_create_plan


class TestCronogramaPreventivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = create_app("testing")
        cls._ctx = cls.app.app_context()
        cls._ctx.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls) -> None:
        db.session.remove()
        db.drop_all()
        cls._ctx.pop()

    def setUp(self) -> None:
        self.emp = Empresa(razon_social="Demo Cronograma", sector="manufactura")
        db.session.add(self.emp)
        db.session.flush()
        self.mt = MachineType(
            empresa_id=self.emp.id,
            clave=f"e{self.emp.id}_motor",
            nombre="Motores",
            prefijo=f"MT{self.emp.id}"[:8],
            activo=True,
        )
        db.session.add(self.mt)
        db.session.flush()
        self.machine = Machine(
            empresa_id=self.emp.id,
            machine_type_id=self.mt.id,
            codigo="TP-068",
            nombre="TORNO CNC",
        )
        db.session.add(self.machine)
        db.session.commit()

    def tearDown(self) -> None:
        db.session.rollback()
        WorkOrder.query.delete()
        PreventiveMaintenancePlan.query.delete()
        Machine.query.delete()
        MachineType.query.delete()
        Empresa.query.delete()
        db.session.commit()

    def test_semana_del_mes(self) -> None:
        self.assertEqual(semana_del_mes(1), 1)
        self.assertEqual(semana_del_mes(8), 2)
        self.assertEqual(semana_del_mes(15), 3)
        self.assertEqual(semana_del_mes(28), 4)

    def test_templates_manufactura(self) -> None:
        t = templates_for_sector("manufactura")
        self.assertGreaterEqual(len(t), 2)
        self.assertEqual(t[0][1], "L")

    def test_matriz_prog_ejec(self) -> None:
        plan = get_or_create_plan(
            machine_id=self.machine.id,
            empresa_id=self.emp.id,
            actividad="Lubricación y refrigeración",
            frecuencia_valor=1,
            frecuencia_unidad="meses",
            tipo_codigo="L",
        )
        db.session.flush()
        wo_prog = WorkOrder(
            empresa_id=self.emp.id,
            machine_id=self.machine.id,
            titulo=plan.actividad,
            tipo=WorkOrderType.PREVENTIVO.value,
            status=WorkOrderStatus.PROGRAMADA.value,
            fecha_programada=date(2026, 6, 18),
            preventive_plan_id=plan.id,
        )
        wo_ok = WorkOrder(
            empresa_id=self.emp.id,
            machine_id=self.machine.id,
            titulo=plan.actividad,
            tipo=WorkOrderType.PREVENTIVO.value,
            status=WorkOrderStatus.COMPLETADO.value,
            fecha_programada=date(2026, 7, 10),
            fecha_cierre=datetime(2026, 7, 11, 12, 0),
            preventive_plan_id=plan.id,
            descripcion="Entregado en óptimas condiciones",
        )
        db.session.add_all([wo_prog, wo_ok])
        db.session.commit()

        crono = construir_cronograma(self.machine, 2026)
        self.assertEqual(len(crono.filas), 1)
        self.assertEqual(crono.filas[0].celdas[6][3].prog, "L")
        self.assertEqual(crono.filas[0].celdas[7][2].prog, "L")
        self.assertEqual(crono.filas[0].celdas[7][2].ejec, "ok")
        self.assertEqual(crono.cumplimiento["prog_total"], 2)
        self.assertEqual(crono.cumplimiento["ejec_total"], 1)
        self.assertTrue(crono.observaciones)

    def test_fechas_bimensual_omite_meses_pasados(self) -> None:
        from app.preventive_maintenance import fechas_preventivas_anio

        # Cadencia anclada al 1-ene: ene, mar, may, jul, sep, nov
        todas = fechas_preventivas_anio(date(2026, 1, 1), 2, "meses", 2026)
        self.assertEqual(
            [d.month for d in todas],
            [1, 3, 5, 7, 9, 11],
        )
        # A mitad de año (23-jul) solo quedan sep y nov
        pendientes = fechas_preventivas_anio(
            date(2026, 1, 1), 2, "meses", 2026, desde=date(2026, 7, 23)
        )
        self.assertEqual([d.month for d in pendientes], [9, 11])
        self.assertTrue(all(d >= date(2026, 7, 23) for d in pendientes))

    def test_query_machines_sin_plan_preventivo(self) -> None:
        sin_plan = Machine(
            empresa_id=self.emp.id,
            machine_type_id=self.mt.id,
            codigo="TP-069",
            nombre="SIN PLAN",
            requiere_mantenimiento=True,
        )
        sin_req = Machine(
            empresa_id=self.emp.id,
            machine_type_id=self.mt.id,
            codigo="TP-070",
            nombre="NO REQUIERE",
            requiere_mantenimiento=False,
        )
        db.session.add_all([sin_plan, sin_req])
        get_or_create_plan(
            machine_id=self.machine.id,
            empresa_id=self.emp.id,
            actividad="Lubricación",
            frecuencia_valor=1,
            frecuencia_unidad="meses",
            tipo_codigo="L",
        )
        db.session.commit()

        ids = {
            m.id
            for m in query_machines_sin_plan_preventivo(self.emp.id).all()
        }
        self.assertIn(sin_plan.id, ids)
        self.assertNotIn(self.machine.id, ids)
        self.assertNotIn(sin_req.id, ids)


if __name__ == "__main__":
    unittest.main()
