from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_producto


@pytest.fixture
def visualizar(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_visualizar_ventas import ServicioVisualizarVentas
    return ServicioVisualizarVentas


class TestServicioVisualizarVentas:
    def test_obtener_detalles_inexistente(self, visualizar: Any):
        assert visualizar.obtener_detalles_factura(9999) == {}

    def test_obtener_detalles(self, visualizar: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=6000, usuario="test")
        with db.conexion() as conn:
            idv = conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        detalle = visualizar.obtener_detalles_factura(idv)
        assert detalle["id_ventas"] == idv
        assert detalle["total"] == 6000.0
        assert len(detalle["productos"]) == 1
        assert detalle["productos"][0]["producto"] == "Cerveza"
        assert detalle["cliente"] == "VENTA RÁPIDA"

    def test_obtener_detalles_con_cliente(self, visualizar: Any, db: Any):
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        from tests.conftest import insertar_cliente
        insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        with db.conexion() as conn:
            cid = conn.execute("SELECT id_cliente FROM clientes ORDER BY id_cliente DESC LIMIT 1").fetchone()[0]
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 1}], monto_recibido=50000, usuario="test", cliente_id=cid)
        with db.conexion() as conn:
            idv = conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        detalle = visualizar.obtener_detalles_factura(idv)
        assert "Juan" in detalle["cliente"]
