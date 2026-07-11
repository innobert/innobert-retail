from __future__ import annotations

from pathlib import Path
from typing import Any
import pytest


@pytest.fixture
def deudas(db: Any) -> Any:
    """Retorna la clase DeudasServicio con BD lista."""
    from retail.nucleo.servicios.deudas.servicio_deudas import DeudasServicio
    return DeudasServicio


@pytest.fixture
def carrito_deudas(db: Any) -> Any:
    """Retorna la clase ServicioCarritoDeudas con BD lista."""
    from retail.nucleo.servicios.deudas.servicio_carrito_deudas import (
        ServicioCarritoDeudas,
    )
    return ServicioCarritoDeudas


class TestObtenerStockActual:
    @staticmethod
    def test_producto_existente(deudas: Any, db: Any):
        pid = _insertar_producto(db, "Ron", 50000, 30000, 10)
        assert deudas.obtener_stock_actual(pid) == 10

    @staticmethod
    def test_producto_inexistente(deudas: Any):
        assert deudas.obtener_stock_actual(9999) is None


class TestValidarCantidad:
    @staticmethod
    def test_cantidad_valida(deudas: Any, db: Any):
        pid = _insertar_producto(db, "Whisky", 120000, 80000, 5)
        valido, stock, msg = deudas.validar_cantidad(pid, 3, [])
        assert valido is True
        assert stock == 5
        assert msg == ""

    @staticmethod
    def test_cantidad_cero(deudas: Any, db: Any):
        pid = _insertar_producto(db, "Vodka", 50000, 30000, 8)
        valido, stock, msg = deudas.validar_cantidad(pid, 0, [])
        assert valido is False
        assert "mayor a cero" in msg

    @staticmethod
    def test_cantidad_excede_stock(deudas: Any, db: Any):
        pid = _insertar_producto(db, "Tequila", 80000, 50000, 2)
        valido, stock, msg = deudas.validar_cantidad(pid, 5, [])
        assert valido is False
        assert stock == 2

    @staticmethod
    def test_stock_reservado_en_carrito(deudas: Any, db: Any):
        pid = _insertar_producto(db, "Ginebra", 70000, 45000, 5)
        carrito = [{"id_producto": pid, "cantidad": 3}]
        valido, stock, msg = deudas.validar_cantidad(pid, 3, carrito)
        assert valido is False
        assert stock == 2

    @staticmethod
    def test_producto_no_encontrado(deudas: Any):
        valido, stock, msg = deudas.validar_cantidad(9999, 1, [])
        assert valido is False
        assert stock == 0


class TestAgregarAlCarrito:
    @staticmethod
    def test_agregar_exitoso(carrito_deudas: Any, db: Any):
        pid = _insertar_producto(db, "Cerveza", 3000, 2000, 24)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Cerveza", "precio": 3000}
        carrito, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 2, 1, "Juan Pérez")
        assert error is None
        assert msg == ""
        assert len(carrito) == 1
        assert carrito[0]["cliente"] == "Juan Pérez"
        assert carrito[0]["cliente_id"] == 1
        assert carrito[0]["subtotal"] == 6000

    @staticmethod
    def test_agregar_stock_insuficiente(carrito_deudas: Any, db: Any):
        pid = _insertar_producto(db, "Brandy", 55000, 35000, 1)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Brandy", "precio": 55000}
        carrito, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 5, 1, "Juan Pérez")
        assert error is not None
        assert "error" in error

    @staticmethod
    def test_agregar_producto_duplicado(carrito_deudas: Any, db: Any):
        pid = _insertar_producto(db, "Ron Medellín", 45000, 25000, 15)
        carrito = []
        producto_data = {"id_producto": pid, "producto": "Ron Medellín", "precio": 45000}
        carrito, _, _ = carrito_deudas.agregar_al_carrito(carrito, producto_data, 2, 1, "Juan Pérez")
        carrito, msg, error = carrito_deudas.agregar_al_carrito(carrito, producto_data, 1, 1, "Juan Pérez")
        assert error is not None
        assert error["error"] == "duplicado"
        assert len(carrito) == 1


class TestObtenerClientesFormateados:
    @staticmethod
    def test_sin_clientes(deudas: Any):
        nombres, mapeo = deudas.obtener_clientes_formateados()
        assert nombres == []
        assert mapeo == {}

    @staticmethod
    def test_con_clientes(deudas: Any, db: Any):
        db.insertar_cliente("Juan", "Pérez", "12345", "3001234", "Norte")
        db.insertar_cliente("María", "García", "67890", "3005678", "Sur")
        nombres, mapeo = deudas.obtener_clientes_formateados()
        assert len(nombres) == 2
        assert "Juan Pérez" in nombres
        assert "María García" in nombres
        assert mapeo["Juan Pérez"] == 1
        assert mapeo["María García"] == 2


class TestObtenerNombreClientePorId:
    @staticmethod
    def test_cliente_existente(deudas: Any, db: Any):
        db.insertar_cliente("Carlos", "López", "11111", "3001111", "Este")
        assert deudas.obtener_nombre_cliente_por_id(1) == "Carlos López"

    @staticmethod
    def test_cliente_inexistente(deudas: Any):
        assert deudas.obtener_nombre_cliente_por_id(9999) is None


class TestObtenerProductosParaBusqueda:
    @staticmethod
    def test_sin_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "Coca-Cola", 3000, 2000, 20)
        _insertar_producto(db, "Pepsi", 3000, 2000, 20)
        resultado = deudas.obtener_productos_para_busqueda()
        assert len(resultado) == 2

    @staticmethod
    def test_con_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "Coca-Cola", 3000, 2000, 20)
        _insertar_producto(db, "Pepsi", 3000, 2000, 20)
        _insertar_producto(db, "Sprite", 3000, 2000, 20)
        resultado = deudas.obtener_productos_para_busqueda("Cola")
        assert len(resultado) == 1
        assert resultado[0]["producto"] == "Coca-Cola"

    @staticmethod
    def test_sin_resultados(deudas: Any, db: Any):
        _insertar_producto(db, "Agua", 2000, 1000, 50)
        resultado = deudas.obtener_productos_para_busqueda("XYZ")
        assert len(resultado) == 0


class TestCalcularTotalCarrito:
    @staticmethod
    def test_carrito_vacio(deudas: Any):
        assert deudas.calcular_total_carrito([]) == 0

    @staticmethod
    def test_carrito_con_items(deudas: Any):
        carrito = [
            {"subtotal": 10000},
            {"subtotal": 5000},
            {"subtotal": 3000},
        ]
        assert deudas.calcular_total_carrito(carrito) == 18000

    @staticmethod
    def test_subtotal_invalido_se_ignora(deudas: Any):
        carrito = [
            {"subtotal": 10000},
            {"subtotal": "invalido"},
        ]
        assert deudas.calcular_total_carrito(carrito) == 10000


class TestFiltrarClientesPorTexto:
    @staticmethod
    def test_filtrar_por_nombre(deudas: Any, db: Any):
        db.insertar_cliente("Juan", "Pérez", "12345", "3001234", "Norte")
        db.insertar_cliente("María", "García", "67890", "3005678", "Sur")
        resultado = deudas.filtrar_clientes_por_texto("Juan")
        assert len(resultado) == 1
        assert resultado[0]["nombres"] == "Juan"

    @staticmethod
    def test_filtrar_por_apellido(deudas: Any, db: Any):
        db.insertar_cliente("Juan", "Pérez", "12345", "3001234", "Norte")
        db.insertar_cliente("Pedro", "Pérez", "11111", "3001111", "Sur")
        resultado = deudas.filtrar_clientes_por_texto("Pérez")
        assert len(resultado) == 2

    @staticmethod
    def test_case_insensitive(deudas: Any, db: Any):
        db.insertar_cliente("Ana", "Torres", "22222", "3002222", "Oeste")
        resultado = deudas.filtrar_clientes_por_texto("ana")
        assert len(resultado) == 1

    @staticmethod
    def test_sin_coincidencias(deudas: Any, db: Any):
        db.insertar_cliente("Luis", "Rojas", "33333", "3003333", "Centro")
        resultado = deudas.filtrar_clientes_por_texto("ZZZ")
        assert len(resultado) == 0


class TestObtenerClientePorNombreCompleto:
    @staticmethod
    def test_cliente_existente(deudas: Any, db: Any):
        db.insertar_cliente("Laura", "Martínez", "44444", "3004444", "Norte")
        cliente = deudas.obtener_cliente_por_nombre_completo("Laura Martínez")
        assert cliente is not None
        assert cliente["nombres"] == "Laura"
        assert cliente["apellidos"] == "Martínez"
        assert cliente["id_cliente"] == 1

    @staticmethod
    def test_cliente_inexistente(deudas: Any):
        assert deudas.obtener_cliente_por_nombre_completo("No Existe") is None


class TestConfirmarDeuda:
    @staticmethod
    def test_carrito_vacio_lanza_error(carrito_deudas: Any):
        with pytest.raises(ValueError, match="vacío"):
            carrito_deudas.confirmar_deuda([], 1, "admin")

    @staticmethod
    def test_confirmar_deuda_exitosa(carrito_deudas: Any, db: Any):
        db.insertar_cliente("Roberto", "Díaz", "55555", "3005555", "Sur")
        pid = _insertar_producto(db, "Whisky Johnnie Walker", 180000, 120000, 3)
        carrito = [
            {
                "cliente": "Roberto Díaz",
                "cliente_id": 1,
                "producto": "Whisky Johnnie Walker",
                "id_producto": pid,
                "cantidad": 2,
                "precio": 180000,
                "subtotal": 360000,
            }
        ]
        resultado = carrito_deudas.confirmar_deuda(carrito, 1, "admin")
        assert "id_deuda" in resultado
        assert "total" in resultado
        assert resultado["total"] == 360000


class TestPaginacion:
    @staticmethod
    def test_obtener_productos_paginado(deudas: Any, db: Any):
        for i in range(10):
            _insertar_producto(db, f"Producto {i}", 1000 * (i + 1), 500 * (i + 1), 10)
        pagina = deudas.obtener_productos_paginado(0, 3)
        assert len(pagina) == 3

    @staticmethod
    def test_obtener_productos_paginado_con_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "Café", 5000, 3000, 20)
        _insertar_producto(db, "Café Especial", 8000, 5000, 15)
        _insertar_producto(db, "Té", 3000, 2000, 25)
        pagina = deudas.obtener_productos_paginado(0, 10, filtro="Café")
        assert len(pagina) == 2

    @staticmethod
    def test_contar_productos(deudas: Any, db: Any):
        for i in range(5):
            _insertar_producto(db, f"Prod {i}", 2000, 1000, 10)
        assert deudas.contar_productos() == 5

    @staticmethod
    def test_contar_productos_con_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "AAA", 1000, 500, 10)
        _insertar_producto(db, "AAB", 1000, 500, 10)
        _insertar_producto(db, "BBB", 1000, 500, 10)
        assert deudas.contar_productos(filtro="AA") == 2


class TestObtenerNombresProductosParaBusqueda:
    @staticmethod
    def test_sin_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "Ron", 50000, 30000, 10)
        _insertar_producto(db, "Vodka", 50000, 30000, 8)
        nombres = deudas.obtener_nombres_productos_para_busqueda()
        assert nombres == ["Ron", "Vodka"]

    @staticmethod
    def test_con_filtro(deudas: Any, db: Any):
        _insertar_producto(db, "Cerveza Águila", 3000, 2000, 24)
        _insertar_producto(db, "Cerveza Póker", 3000, 2000, 20)
        _insertar_producto(db, "Gaseosa", 2000, 1000, 30)
        nombres = deudas.obtener_nombres_productos_para_busqueda("Cerveza")
        assert len(nombres) == 2

    @staticmethod
    def test_sin_resultados(deudas: Any, db: Any):
        _insertar_producto(db, "Agua", 2000, 1000, 50)
        nombres = deudas.obtener_nombres_productos_para_busqueda("XYZ")
        assert len(nombres) == 0


def _insertar_producto(db: Any, nombre: str, precio: int, costo: int, stock: int) -> int:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, precio, costo, stock, 1, ""),
        )
        return cursor.lastrowid
