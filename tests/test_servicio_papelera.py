from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def papelera_ventas(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_papelera_ventas import ServicioPapeleraVentas
    return ServicioPapeleraVentas


@pytest.fixture
def papelera_deudas(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_papelera_deudas import ServicioPapeleraDeudas
    return ServicioPapeleraDeudas


class TestServicioPapeleraVentas:
    def test_obtener_pagina_vacia(self, papelera_ventas: Any):
        pagina = papelera_ventas.obtener_pagina(0, 10)
        assert pagina == []

    def test_contar_papelera(self, papelera_ventas: Any, db: Any):
        pid = insertar_producto(db, "Producto Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        ultima = db.obtener_ultima_venta()
        db.mover_venta_a_papelera(ultima[0], "test", "motivo test")
        assert papelera_ventas.contar_papelera() == 1

    def test_obtener_pagina_con_datos(self, papelera_ventas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        ultima = db.obtener_ultima_venta()
        db.mover_venta_a_papelera(ultima[0], "test", "motivo test")
        pagina = papelera_ventas.obtener_pagina(0, 10)
        assert len(pagina) == 1
        assert "total" in pagina[0]
        assert "numero_factura" in pagina[0]

    def test_limpiar_registros_antiguos(self, papelera_ventas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        ultima = db.obtener_ultima_venta()
        db.mover_venta_a_papelera(ultima[0], "test", "motivo")
        with db.conexion() as conn:
            conn.execute(
                "UPDATE papelera_ventas SET fecha_eliminacion = '2020-01-01' WHERE numero_factura = ?",
                (ultima[1],),
            )
        eliminados = papelera_ventas.limpiar_registros_antiguos(dias=0)
        assert eliminados >= 1


class TestServicioPapeleraDeudas:
    def test_obtener_pagina_vacia(self, papelera_deudas: Any):
        pagina = papelera_deudas.obtener_pagina(0, 10)
        assert pagina == []

    def test_contar_papelera(self, papelera_deudas: Any, db: Any):
        cid = insertar_cliente(db, "Juan", "Perez", "11111", "3001111111")
        pid = insertar_producto(db, "Ron", 50000, 30000, 10)
        db.crear_deuda(cliente_id=cid, items=[{"id_producto": pid, "cantidad": 2}], usuario="test")
        with db.conexion() as conn:
            id_deuda = conn.execute(
                "SELECT id_deuda FROM deudas ORDER BY id_deuda DESC LIMIT 1"
            ).fetchone()[0]
        db.mover_deuda_a_papelera(id_deuda, "test", "motivo test")
        assert papelera_deudas.contar_papelera() == 1
