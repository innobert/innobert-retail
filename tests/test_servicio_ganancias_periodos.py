from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def semanal(db: Any) -> Any:
    from retail.nucleo.servicios.ganancias.servicio_semanal import ServicioSemanal
    return ServicioSemanal


@pytest.fixture
def mensual(db: Any) -> Any:
    from retail.nucleo.servicios.ganancias.servicio_mensual import ServicioMensual
    return ServicioMensual


@pytest.fixture
def anual(db: Any) -> Any:
    from retail.nucleo.servicios.ganancias.servicio_anual import ServicioAnual
    return ServicioAnual


class TestServicioSemanal:
    def test_obtener_semanas_sin_datos(self, semanal: Any):
        assert semanal.obtener_semanas() == []

    def test_obtener_semanas_con_venta(self, semanal: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        semanas = semanal.obtener_semanas()
        assert len(semanas) >= 1
        assert len(semanas[0]) == 7  # week_num, start, end, total_ventas, ganancia, prod, clientes

    def test_obtener_totales_globales(self, semanal: Any):
        total_ventas, total_ganancia = semanal.obtener_totales_globales()
        assert total_ventas >= 0
        assert total_ganancia >= 0


class TestServicioMensual:
    def test_obtener_periodos_sin_datos(self, mensual: Any):
        assert mensual.obtener_periodos() == []

    def test_obtener_periodos_con_venta(self, mensual: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        periodos = mensual.obtener_periodos()
        assert len(periodos) >= 1
        assert len(periodos[0]) == 8

    def test_obtener_totales_globales(self, mensual: Any):
        total_ventas, total_ganancia = mensual.obtener_totales_globales()
        assert total_ventas >= 0
        assert total_ganancia >= 0


class TestServicioAnual:
    def test_obtener_periodos_sin_datos(self, anual: Any):
        assert anual.obtener_periodos() == []

    def test_obtener_periodos_con_venta(self, anual: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        periodos = anual.obtener_periodos()
        assert len(periodos) >= 1
        assert len(periodos[0]) == 7

    def test_obtener_totales_globales(self, anual: Any):
        total_ventas, total_ganancia = anual.obtener_totales_globales()
        assert total_ventas >= 0
        assert total_ganancia >= 0
