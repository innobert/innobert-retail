from __future__ import annotations

from pathlib import Path
from typing import Any
import pytest


@pytest.fixture
def inventario(db: Any) -> Any:
    """Retorna la clase InventarioServicio con BD lista."""
    from retail.nucleo.servicios.inventario.servicio_inventario import InventarioServicio
    return InventarioServicio


class TestObtenerProductos:
    def test_sin_productos_retorna_vacio(self, inventario: Any):
        assert inventario.obtener_todos_productos() == []

    def test_con_productos_retorna_lista(self, inventario: Any, db: Any):
        _insertar_producto(db, "Ron", 50000, 30000, 10)
        _insertar_producto(db, "Whisky", 120000, 80000, 5)
        productos = inventario.obtener_todos_productos()
        assert len(productos) == 2
        assert productos[0]["producto"] == "Ron"

    def test_obtener_nombres_productos(self, inventario: Any, db: Any):
        _insertar_producto(db, "Cerveza", 3000, 2000, 24)
        _insertar_producto(db, "Vodka", 50000, 30000, 8)
        nombres = inventario.obtener_nombres_productos()
        assert nombres == ["Cerveza", "Vodka"]

    def test_obtener_productos_para_busqueda_sin_filtro(self, inventario: Any, db: Any):
        _insertar_producto(db, "Ginebra", 70000, 45000, 6)
        _insertar_producto(db, "Tequila", 80000, 50000, 4)
        resultado = inventario.obtener_productos_para_busqueda()
        assert len(resultado) == 2

    def test_obtener_productos_para_busqueda_con_filtro(self, inventario: Any, db: Any):
        _insertar_producto(db, "Coca-Cola", 3000, 2000, 20)
        _insertar_producto(db, "Pepsi", 3000, 2000, 20)
        _insertar_producto(db, "Sprite", 3000, 2000, 20)
        resultado = inventario.obtener_productos_para_busqueda("Cola")
        assert len(resultado) == 1
        assert resultado[0]["producto"] == "Coca-Cola"


class TestObtenerProductoPorId:
    def test_producto_existente(self, inventario: Any, db: Any):
        pid = _insertar_producto(db, "Brandy", 55000, 35000, 12)
        producto = inventario.obtener_producto_por_id(pid)
        assert producto is not None
        assert producto["producto"] == "Brandy"

    def test_producto_inexistente(self, inventario: Any):
        producto = inventario.obtener_producto_por_id(9999)
        assert producto is None


class TestObtenerProductoPorNombre:
    def test_nombre_exacto(self, inventario: Any, db: Any):
        _insertar_producto(db, "Ron Medellín", 45000, 25000, 15)
        producto = inventario.obtener_producto_por_nombre("Ron Medellín")
        assert producto is not None
        assert producto["precio"] == 45000

    def test_case_insensitive(self, inventario: Any, db: Any):
        _insertar_producto(db, "Whisky Johnnie Walker", 180000, 120000, 3)
        producto = inventario.obtener_producto_por_nombre("whisky johnnie walker")
        assert producto is not None

    def test_nombre_inexistente(self, inventario: Any):
        producto = inventario.obtener_producto_por_nombre("No existe")
        assert producto is None


class TestVerificarRentabilidad:
    def test_producto_rentable(self, inventario: Any):
        # precio > costo → rentable
        assert inventario.verificar_rentabilidad(100, 50, 10) is None

    def test_producto_en_perdida(self, inventario: Any):
        resultado = inventario.verificar_rentabilidad(50, 100, 10)
        assert resultado is not None
        assert resultado["tipo"] == "perdida"
        assert "pérdida" in resultado["mensaje"] or "perdida" in resultado["mensaje"]

    def test_producto_sin_ganancia(self, inventario: Any):
        resultado = inventario.verificar_rentabilidad(100, 100, 5)
        assert resultado is not None
        assert resultado["tipo"] == "sin_ganancia"
        assert "ganancia" in resultado["mensaje"]


class TestAgregarProducto:
    def test_agregar_exitoso(self, inventario: Any, db: Any):
        exito, mensaje = inventario.agregar_producto("Cerveza Águila", 4000, 2500, 100, "")
        assert exito is True
        assert "correctamente" in mensaje
        # Verificar que se insertó
        productos = inventario.obtener_todos_productos()
        assert len(productos) == 1

    def test_agregar_sin_nombre(self, inventario: Any):
        exito, mensaje = inventario.agregar_producto("", 4000, 2500, 100, "")
        assert exito is False

    def test_agregar_precio_cero(self, inventario: Any):
        exito, mensaje = inventario.agregar_producto("Test", 0, 2500, 100, "")
        assert exito is False

    def test_agregar_costo_negativo(self, inventario: Any):
        exito, mensaje = inventario.agregar_producto("Test", 5000, -1, 100, "")
        assert exito is False

    def test_agregar_stock_cero(self, inventario: Any):
        exito, mensaje = inventario.agregar_producto("Test", 5000, 2500, 0, "")
        assert exito is False

    def test_agregar_producto_duplicado(self, inventario: Any, db: Any):
        inventario.agregar_producto("Único", 10000, 5000, 10, "")
        exito, mensaje = inventario.agregar_producto("Único", 10000, 5000, 10, "")
        assert exito is False
        assert "Error" in mensaje


class TestActualizarProducto:
    def test_actualizar_exitoso(self, inventario: Any, db: Any):
        pid = _insertar_producto(db, "Vodka Smirnoff", 60000, 40000, 8)
        exito, mensaje = inventario.actualizar_producto(
            pid, "Vodka Smirnoff Premium", 65000, 40000, 10, ""
        )
        assert exito is True
        producto = inventario.obtener_producto_por_id(pid)
        assert producto["producto"] == "Vodka Smirnoff Premium"
        assert producto["precio"] == 65000
        assert producto["stock"] == 10

    def test_actualizar_producto_inexistente(self, inventario: Any):
        exito, mensaje = inventario.actualizar_producto(9999, "No existe", 1000, 500, 5, "")
        assert exito is False
        assert "no encontrado" in mensaje

    def test_actualizar_sin_cambios(self, inventario: Any, db: Any):
        pid = _insertar_producto(db, "Ron Viejo", 55000, 35000, 12)
        # Actualizar con los mismos valores
        exito, mensaje = inventario.actualizar_producto(
            pid, "Ron Viejo", 55000, 35000, 12, ""
        )
        assert exito is True


class TestEliminarProducto:
    def test_eliminar_exitoso(self, inventario: Any, db: Any):
        pid = _insertar_producto(db, "Tequila José Cuervo", 90000, 60000, 5)
        exito, mensaje = inventario.eliminar_producto(pid)
        assert exito is True
        assert inventario.obtener_producto_por_id(pid) is None

    def test_eliminar_inexistente(self, inventario: Any):
        # dlt_producto no lanza error si no existe (DELETE sin match es exitoso)
        exito, mensaje = inventario.eliminar_producto(9999)
        assert exito is True


class TestPaginacion:
    def test_obtener_productos_paginado(self, inventario: Any, db: Any):
        for i in range(10):
            _insertar_producto(db, f"Producto {i}", 1000 * (i + 1), 500 * (i + 1), 10)
        pagina = inventario.obtener_productos_paginado(0, 3)
        assert len(pagina) == 3
        assert pagina[0]["producto"] == "Producto 0"

    def test_obtener_productos_paginado_con_filtro(self, inventario: Any, db: Any):
        _insertar_producto(db, "Café", 5000, 3000, 20)
        _insertar_producto(db, "Café Especial", 8000, 5000, 15)
        _insertar_producto(db, "Té", 3000, 2000, 25)
        pagina = inventario.obtener_productos_paginado(0, 10, filtro="Café")
        assert len(pagina) == 2

    def test_contar_productos(self, inventario: Any, db: Any):
        for i in range(5):
            _insertar_producto(db, f"Prod {i}", 2000, 1000, 10)
        assert inventario.contar_productos() == 5

    def test_contar_productos_con_filtro(self, inventario: Any, db: Any):
        _insertar_producto(db, "AAA", 1000, 500, 10)
        _insertar_producto(db, "AAB", 1000, 500, 10)
        _insertar_producto(db, "BBB", 1000, 500, 10)
        assert inventario.contar_productos(filtro="AA") == 2


def _insertar_producto(db: Any, nombre: str, precio: int, costo: int, stock: int) -> int:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, precio, costo, stock, 1, ""),
        )
        return cursor.lastrowid
