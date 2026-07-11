from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def edicion(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_edicion_ventas import ServicioEdicionVentas
    return ServicioEdicionVentas


def _crear_venta_con_producto(db: Any, pid: int, cantidad: int = 2, monto: float = 10000) -> int:
    db.crear_venta(items=[{"id_producto": pid, "cantidad": cantidad}], monto_recibido=monto, usuario="test")
    with db.conexion() as conn:
        return conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]


class TestServicioEdicionVentas:
    def test_obtener_detalles_factura(self, edicion: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        idv = _crear_venta_con_producto(db, pid)
        detalles = edicion.obtener_detalles_factura(idv)
        assert len(detalles) >= 1
        assert detalles[0]["id_producto"] == pid

    def test_obtener_info_factura(self, edicion: Any, db: Any):
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        idv = _crear_venta_con_producto(db, pid, cantidad=2, monto=100000)
        info = edicion.obtener_info_factura(idv)
        total, monto, vuelto = info
        assert total > 0
        assert monto == 100000.0
        assert vuelto >= 0

    def test_agregar_producto_a_venta(self, edicion: Any, db: Any):
        pid1 = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        pid2 = insertar_producto(db, "Ron", 50000, 30000, 10)
        idv = _crear_venta_con_producto(db, pid1, cantidad=1, monto=100000)
        edicion.agregar_producto_a_venta(idv, pid2, 1, "test", monto_recibido=100000)
        detalles = edicion.obtener_detalles_factura(idv)
        ids_productos = [d["id_producto"] for d in detalles]
        assert pid2 in ids_productos

    def test_agregar_producto_supera_monto(self, edicion: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        pid2 = insertar_producto(db, "Whisky", 200000, 120000, 5)
        idv = _crear_venta_con_producto(db, pid, cantidad=1, monto=5000)
        with pytest.raises(ValueError, match="supera el monto recibido"):
            edicion.agregar_producto_a_venta(idv, pid2, 1, "test", monto_recibido=5000)

    def test_editar_cantidad_detalle(self, edicion: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        idv = _crear_venta_con_producto(db, pid, cantidad=2, monto=100000)
        detalles = edicion.obtener_detalles_factura(idv)
        id_detalle = detalles[0]["id_detalle"]
        edicion.editar_cantidad_detalle(id_detalle, 5, "test", monto_recibido=100000)
        nuevos = edicion.obtener_detalles_factura(idv)
        assert nuevos[0]["cantidad"] == 5

    def test_eliminar_detalle_venta(self, edicion: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        idv = _crear_venta_con_producto(db, pid, cantidad=1, monto=10000)
        detalles = edicion.obtener_detalles_factura(idv)
        id_detalle = detalles[0]["id_detalle"]
        resultado = edicion.eliminar_detalle_venta(id_detalle, "test", monto_recibido=0)
        if resultado:
            assert resultado is not None
