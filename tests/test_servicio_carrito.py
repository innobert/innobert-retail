from __future__ import annotations

from typing import Any
import pytest

from tests.conftest import insertar_cliente, insertar_producto


@pytest.fixture
def carrito_base(db: Any) -> Any:
    from retail.nucleo.servicios.base.carrito_base import BaseCarritoServicio
    return BaseCarritoServicio


@pytest.fixture
def carrito_ventas(db: Any) -> Any:
    from retail.nucleo.servicios.ventas.servicio_carrito_ventas import ServicioCarritoVentas
    return ServicioCarritoVentas


@pytest.fixture
def carrito_deudas(db: Any) -> Any:
    from retail.nucleo.servicios.deudas.servicio_carrito_deudas import ServicioCarritoDeudas
    return ServicioCarritoDeudas


class TestBaseCarritoServicio:
    def test_validar_cantidad_para_edicion_valida(self, carrito_base: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 10)
        carrito = [{"id_producto": pid, "cantidad": 2, "precio": 3000, "subtotal": 6000}]
        item = carrito[0]
        valido, stock, msg = carrito_base.validar_cantidad_para_edicion(carrito, pid, 3, item)
        assert valido is True
        assert stock >= 8

    def test_validar_cantidad_para_edicion_excede(self, carrito_base: Any, db: Any):
        pid = insertar_producto(db, "Ron", 50000, 30000, 5)
        carrito = [{"id_producto": pid, "cantidad": 2, "precio": 50000, "subtotal": 100000}]
        item = carrito[0]
        valido, stock, msg = carrito_base.validar_cantidad_para_edicion(carrito, pid, 10, item)
        assert valido is False
        assert "Stock" in msg

    def test_validar_cantidad_para_edicion_cero(self, carrito_base: Any, db: Any):
        pid = insertar_producto(db, "Vodka", 40000, 20000, 10)
        carrito = [{"id_producto": pid, "cantidad": 2, "precio": 40000, "subtotal": 80000}]
        item = carrito[0]
        valido, stock, msg = carrito_base.validar_cantidad_para_edicion(carrito, pid, 0, item)
        assert valido is False
        assert "mayor a cero" in msg

    def test_validar_cantidad_sin_stock(self, carrito_base: Any, db: Any):
        pid = insertar_producto(db, "Brandy", 55000, 35000, 0)
        carrito = [{"id_producto": pid, "cantidad": 0, "precio": 55000, "subtotal": 0}]
        item = carrito[0]
        valido, stock, msg = carrito_base.validar_cantidad_para_edicion(carrito, pid, 1, item)
        assert valido is False
        assert stock == 0

    def test_actualizar_cantidad_en_carrito(self, carrito_base: Any):
        carrito = [{"id_producto": 1, "cantidad": 2, "precio": 5000, "subtotal": 10000}]
        nuevo_carrito, item = carrito_base.actualizar_cantidad_en_carrito(carrito, 0, 5)
        assert nuevo_carrito[0]["cantidad"] == 5
        assert nuevo_carrito[0]["subtotal"] == 25000
        assert item["cantidad"] == 5

    def test_eliminar_producto_del_carrito(self, carrito_base: Any):
        carrito = [
            {"id_producto": 1, "cantidad": 2, "subtotal": 10000},
            {"id_producto": 2, "cantidad": 3, "subtotal": 15000},
        ]
        result = carrito_base.eliminar_producto_del_carrito(carrito, 0)
        assert len(result) == 1
        assert result[0]["id_producto"] == 2

    def test_calcular_total_general(self, carrito_base: Any):
        carrito = [
            {"subtotal": 10000},
            {"subtotal": 20000},
            {"subtotal": 30000},
        ]
        total = carrito_base.calcular_total_general(carrito)
        assert total == 60000

    def test_calcular_total_general_vacio(self, carrito_base: Any):
        assert carrito_base.calcular_total_general([]) == 0


class TestServicioCarritoVentas:
    def test_calcular_totales_por_cliente(self, carrito_ventas: Any):
        carrito = [
            {"cliente": "Juan", "subtotal": 10000},
            {"cliente": "Maria", "subtotal": 20000},
            {"cliente": "Juan", "subtotal": 15000},
        ]
        totales = carrito_ventas.calcular_totales_por_cliente(carrito)
        assert totales == {"Juan": 25000, "Maria": 20000}

    def test_calcular_totales_por_cliente_vacio(self, carrito_ventas: Any):
        assert carrito_ventas.calcular_totales_por_cliente([]) == {}


class TestServicioCarritoDeudas:
    def test_agregar_al_carrito_exitoso(self, carrito_deudas: Any, db: Any):
        pid = insertar_producto(db, "Whisky", 120000, 80000, 10)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Whisky", "precio": 120000}
        nuevo, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 2, 1, "Juan Perez")
        assert error is None
        assert msg == ""
        assert len(nuevo) == 1
        assert nuevo[0]["cliente"] == "Juan Perez"
        assert nuevo[0]["subtotal"] == 240000

    def test_agregar_al_carrito_stock_insuficiente(self, carrito_deudas: Any, db: Any):
        pid = insertar_producto(db, "Tequila", 80000, 50000, 1)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Tequila", "precio": 80000}
        nuevo, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 5, 1, "Juan Perez")
        assert error is not None
        assert "error" in error

    def test_agregar_al_carrito_duplicado(self, carrito_deudas: Any, db: Any):
        pid = insertar_producto(db, "Cerveza", 3000, 2000, 50)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Cerveza", "precio": 3000}
        carrito, _, _ = carrito_deudas.agregar_al_carrito(carrito, producto_data, 2, 1, "Juan Perez")
        carrito, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 1, 1, "Juan Perez")
        assert error is not None
        assert error["error"] == "duplicado"
        assert len(carrito) == 1
