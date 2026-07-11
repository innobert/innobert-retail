from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def facturas(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_facturas_deudas import ServicioFacturasDeudas
    return ServicioFacturasDeudas


class TestServicioFacturasDeudas:
    def test_contar_deudas_sin_datos(self, facturas: Any):
        assert facturas.contar_deudas() == 0

    def test_contar_deudas_con_datos(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        assert facturas.contar_deudas() == 1
        assert facturas.contar_deudas(filtro_cliente="Juan") == 1
        assert facturas.contar_deudas(filtro_cliente="NoExiste") == 0

    def test_obtener_pagina(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Maria", "Gomez", "22222", "3002222222")
        pid = insertar_producto(db, "Whisky", 120000, 80000, 5)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 1}], usuario="test")
        pagina = facturas.obtener_pagina(0, 10)
        assert len(pagina) >= 1
        assert "cliente" in pagina[0]
        assert "total" in pagina[0]

    def test_calcular_total_deudas(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Carlos", "Ruiz", "33333", "3003333333")
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 10}], usuario="test")
        total = facturas.calcular_total_deudas()
        assert total == 30000.0

    def test_obtener_lista_clientes(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Ana", "Lopez", "44444", "3004444444")
        pid = insertar_producto(db, "Tequila", 80000, 50000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 1}], usuario="test")
        clientes = facturas.obtener_lista_clientes()
        assert len(clientes) >= 1

    def test_registrar_pago_parcial(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Pago", "Test", "55555", "3005555555")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        exito, msg, vuelto = facturas.registrar_pago(idd, 30000, 100000, "test")
        assert exito is True
        with db.conexion() as conn:
            saldo = conn.execute("SELECT saldo FROM deudas WHERE id_deuda = ?", (idd,)).fetchone()[0]
        assert saldo == 70000.0

    def test_registrar_pago_exacto(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "PagoExacto", "Test", "66666", "3006666666")
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 10}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        exito, msg, vuelto = facturas.registrar_pago(idd, 30000, 30000, "test")
        assert exito is True
        with db.conexion() as conn:
            estado = conn.execute("SELECT estado FROM deudas WHERE id_deuda = ?", (idd,)).fetchone()[0]
        assert estado == "PAGADA"

    def test_registrar_pago_con_vuelto(self, facturas: Any, db: Any):
        cid = insertar_cliente(db, "Vuelto", "Test", "77777", "3007777777")
        pid = insertar_producto(db, "Whisky", 120000, 80000, 5)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 1}], usuario="test")
        with db.conexion() as conn:
            idd = conn.execute("SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1").fetchone()[0]
        exito, msg, vuelto = facturas.registrar_pago(idd, 150000, 120000, "test")
        assert exito is True
        assert vuelto == 30000.0
