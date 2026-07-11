from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def hist_ventas(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_historial_ventas import ServicioHistorialVentas
    return ServicioHistorialVentas


class TestServicioHistorialVentas:
    def test_obtener_por_venta_vacia(self, hist_ventas: Any):
        assert hist_ventas.obtener_por_venta(9999) == []

    def test_obtener_por_venta(self, hist_ventas: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=6000, usuario="test")
        with db.conexion() as conn:
            idv = conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        historial = hist_ventas.obtener_por_venta(idv)
        assert len(historial) >= 1
        assert historial[0]["accion"] in ("VENTA", "X MAYOR")

    def test_obtener_por_cliente(self, hist_ventas: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 1}], monto_recibido=50000, usuario="test", cliente_id=cid)
        historial = hist_ventas.obtener_por_cliente(cid, "")
        assert len(historial) >= 1

    def test_procesar_filas_vacio(self, hist_ventas: Any):
        assert hist_ventas._procesar_filas([]) == []
