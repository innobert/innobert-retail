from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def hist_deudas(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_historial_deudas import ServicioHistorialDeudas
    return ServicioHistorialDeudas


class TestServicioHistorialDeudas:
    def test_obtener_por_deuda_vacia(self, hist_deudas: Any):
        assert hist_deudas.obtener_por_deuda(9999) == []

    def test_obtener_por_deuda(self, hist_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        historial = hist_deudas.obtener_por_deuda(idd)
        assert len(historial) >= 1
        assert historial[0]["accion"] in ("DEUDA",)

    def test_obtener_nombre_cliente(self, hist_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Maria", "Gomez", "22222", "3002222222")
        pid = insertar_producto(db, "Whisky", 120000, 80000, 5)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 1}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        nombre = hist_deudas.obtener_nombre_cliente_por_deuda(idd)
        assert "Maria" in nombre

    def test_obtener_numero_factura(self, hist_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Carlos", "Ruiz", "33333", "3003333333")
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 10}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        factura = hist_deudas.obtener_numero_factura_por_deuda(idd)
        assert factura != "N/A"

    def test_obtener_por_cliente_por_id(self, hist_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Ana", "Lopez", "44444", "3004444444")
        pid = insertar_producto(db, "Tequila", 80000, 50000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 1}], usuario="test")
        historial = hist_deudas.obtener_por_cliente("Ana Lopez", id_cliente=cid)
        assert len(historial) >= 1

    def test_obtener_por_cliente_por_nombre(self, hist_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Cliente", "Rapido", "66666", "3006666666")
        pid = insertar_producto(db, "Vodka", 40000, 20000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        historial = hist_deudas.obtener_por_cliente("Cliente Rapido", id_cliente=cid)
        assert len(historial) >= 1
