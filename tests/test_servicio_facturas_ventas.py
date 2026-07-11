from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_producto


@pytest.fixture
def facturas(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_facturas_ventas import ServicioFacturasVentas
    return ServicioFacturasVentas


class TestServicioFacturasVentas:
    def test_contar_facturas_sin_datos(self, facturas: Any):
        assert facturas.contar_facturas() == 0

    def test_contar_facturas_con_datos(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        assert facturas.contar_facturas() == 1

    def test_contar_facturas_con_filtro(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        with db.conexion() as conn:
            num = conn.execute("SELECT numero_factura FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        assert facturas.contar_facturas(filtro=num) == 1

    def test_obtener_pagina_vacia(self, facturas: Any):
        assert facturas.obtener_pagina_facturas(0, 10) == []

    def test_obtener_pagina_con_datos(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        pagina = facturas.obtener_pagina_facturas(0, 10)
        assert len(pagina) == 1
        assert "numero_factura" in pagina[0]
        assert "cliente_nombre" in pagina[0]
        assert "total" in pagina[0]

    def test_calcular_total_ventas(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 3}], monto_recibido=3000, usuario="test")
        total = facturas.calcular_total_ventas()
        assert total > 0

    def test_eliminar_factura(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 1}], monto_recibido=1000, usuario="test")
        with db.conexion() as conn:
            idv = conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        assert facturas.eliminar_factura(idv, "test") is True

    def test_obtener_lista_numeros_factura(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 1}], monto_recibido=1000, usuario="test")
        nums = facturas.obtener_lista_numeros_factura()
        assert len(nums) >= 1

    def test_obtener_detalles_para_pdf(self, facturas: Any, db: Any):
        pid = insertar_producto(db, "Test", 1000, 500, 10)
        db.crear_venta(items=[{"id_producto": pid, "cantidad": 2}], monto_recibido=2000, usuario="test")
        with db.conexion() as conn:
            idv = conn.execute("SELECT id_ventas FROM ventas ORDER BY id_ventas DESC LIMIT 1").fetchone()[0]
        detalle = facturas.obtener_detalles_para_pdf(idv)
        assert "productos" in detalle
        assert "cliente" in detalle
