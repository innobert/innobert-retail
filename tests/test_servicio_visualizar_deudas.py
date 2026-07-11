from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def visualizar(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_visualizar_deudas import ServicioVisualizarDeudas
    return ServicioVisualizarDeudas


class TestServicioVisualizarDeudas:
    def test_obtener_detalles_inexistente(self, visualizar: Any):
        assert visualizar.obtener_detalles_deuda(9999) == {}

    def test_obtener_detalles(self, visualizar: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        detalle = visualizar.obtener_detalles_deuda(idd)
        assert detalle["id_deuda"] == idd
        assert detalle["total"] == 100000.0
        assert len(detalle["productos"]) == 1
        assert "Juan" in detalle["cliente"]
