from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def edicion(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_edicion_deudas import ServicioEdicionDeudas
    return ServicioEdicionDeudas


def _crear_deuda_con_producto(db: Any, cid: int, pid: int, cantidad: int = 2) -> int:
    db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": cantidad}], usuario="test")
    with db.conexion() as conn:
        return conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]


class TestServicioEdicionDeudas:
    def test_obtener_detalles_deuda(self, edicion: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        idd = _crear_deuda_con_producto(db, cid, pid)
        detalles = edicion.obtener_detalles_deuda(idd)
        assert len(detalles) >= 1
        assert detalles[0]["id_producto"] == pid

    def test_obtener_info_deuda(self, edicion: Any, db: Any):
        cid = insertar_cliente(db, "Maria", "Gomez", "22222", "3002222222")
        pid = insertar_producto(db, "Whisky", 120000, 80000, 5)
        idd = _crear_deuda_con_producto(db, cid, pid)
        total, saldo = edicion.obtener_info_deuda(idd)
        assert total > 0
        assert saldo == total

    def test_agregar_producto_a_deuda(self, edicion: Any, db: Any):
        cid = insertar_cliente(db, "Carlos", "Ruiz", "33333", "3003333333")
        pid1 = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        pid2 = insertar_producto(db, "Ron", 50000, 30000, 10)
        idd = _crear_deuda_con_producto(db, cid, pid1)
        edicion.agregar_producto_a_deuda(idd, pid2, 1, "test")
        detalles = edicion.obtener_detalles_deuda(idd)
        ids = [d["id_producto"] for d in detalles]
        assert pid2 in ids

    def test_editar_cantidad_detalle(self, edicion: Any, db: Any):
        cid = insertar_cliente(db, "Ana", "Lopez", "44444", "3004444444")
        pid = insertar_producto(db, "Tequila", 80000, 50000, 10)
        idd = _crear_deuda_con_producto(db, cid, pid, cantidad=2)
        detalles = edicion.obtener_detalles_deuda(idd)
        id_detalle = detalles[0]["id_detalle"]
        edicion.editar_cantidad_detalle(id_detalle, 5, "test")
        nuevos = edicion.obtener_detalles_deuda(idd)
        assert nuevos[0]["cantidad"] == 5

    def test_eliminar_producto_deuda(self, edicion: Any, db: Any):
        cid = insertar_cliente(db, "Luis", "Martinez", "55555", "3005555555")
        pid = insertar_producto(db, "Vodka", 40000, 20000, 10)
        idd = _crear_deuda_con_producto(db, cid, pid, cantidad=1)
        detalles = edicion.obtener_detalles_deuda(idd)
        id_detalle = detalles[0]["id_detalle"]
        edicion.eliminar_producto_deuda(id_detalle, "test")
        nuevos = edicion.obtener_detalles_deuda(idd)
        assert len(nuevos) == 0
