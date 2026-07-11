from __future__ import annotations

from typing import Any
import pytest


@pytest.fixture
def ventas_servicio(db: Any) -> Any:
    """Retorna la clase VentasServicio con BD lista."""
    from retail.nucleo.servicios.ventas.servicio_ventas import VentasServicio
    return VentasServicio


class TestObtenerStockActual:
    def test_producto_existente_retorna_stock(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Ron", 50000, 30000, 10, 1, "")
        stock = ventas_servicio.obtener_stock_actual(pid)
        assert stock == 10

    def test_producto_inexistente_retorna_none(self, ventas_servicio: Any):
        stock = ventas_servicio.obtener_stock_actual(9999)
        assert stock is None


class TestValidarCantidad:
    def test_cantidad_valida(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Whisky", 120000, 80000, 5, 1, "")
        valido, stock, msg = ventas_servicio.validar_cantidad(pid, 3, [])
        assert valido is True
        assert stock == 5
        assert msg == ""

    def test_cantidad_cero(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Cerveza", 3000, 2000, 24, 1, "")
        valido, stock, msg = ventas_servicio.validar_cantidad(pid, 0, [])
        assert valido is False
        assert "mayor a cero" in msg

    def test_cantidad_excede_stock(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Vodka", 50000, 30000, 8, 1, "")
        valido, stock, msg = ventas_servicio.validar_cantidad(pid, 20, [])
        assert valido is False
        assert "disponible" in msg

    def test_producto_no_existe(self, ventas_servicio: Any):
        valido, stock, msg = ventas_servicio.validar_cantidad(9999, 1, [])
        assert valido is False
        assert stock == 0
        assert "No se pudo obtener el stock" in msg

    def test_cantidad_reservada_en_carrito(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Ginebra", 70000, 45000, 6, 1, "")
        carrito = [
            {"id_producto": pid, "cantidad": 4, "producto": "Ginebra", "cliente": ""},
        ]
        valido, stock, msg = ventas_servicio.validar_cantidad(pid, 3, carrito)
        assert valido is False
        assert stock == 2


class TestAgregarAlCarrito:
    def test_agregar_exitoso(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Tequila", 80000, 50000, 4, 1, "")
        producto_data = {"id_producto": pid, "producto": "Tequila", "precio": 80000}
        carrito, msg, error = ventas_servicio.agregar_al_carrito(
            [], producto_data, 2, None, "rapida"
        )
        assert msg == ""
        assert error is None
        assert len(carrito) == 1
        assert carrito[0]["producto"] == "Tequila"
        assert carrito[0]["cantidad"] == 2
        assert carrito[0]["subtotal"] == 160000

    def test_agregar_producto_duplicado(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Brandy", 55000, 35000, 12, 1, "")
        producto_data = {"id_producto": pid, "producto": "Brandy", "precio": 55000}
        carrito = [
            {"producto": "Brandy", "id_producto": pid, "cantidad": 1, "precio": 55000, "subtotal": 55000, "cliente": "", "cliente_id": None},
        ]
        carrito, msg, error = ventas_servicio.agregar_al_carrito(
            carrito, producto_data, 1, None, "rapida"
        )
        assert "ya está en el carrito" in msg
        assert error is not None
        assert error["error"] == "duplicado"

    def test_agregar_sin_stock(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Ron Medellín", 45000, 25000, 2, 1, "")
        producto_data = {"id_producto": pid, "producto": "Ron Medellín", "precio": 45000}
        carrito, msg, error = ventas_servicio.agregar_al_carrito(
            [], producto_data, 99, None, "rapida"
        )
        assert error is not None
        assert "error" in error

    def test_agregar_mayorista_con_cliente(self, ventas_servicio: Any, db: Any):
        db.insertar_cliente("Juan", "Pérez", "12345678", "3001234567", "Norte")
        pid = _insertar_producto(db, "Coca-Cola", 3000, 2000, 20, 1, "")
        producto_data = {"id_producto": pid, "producto": "Coca-Cola", "precio": 3000}
        carrito, msg, error = ventas_servicio.agregar_al_carrito(
            [], producto_data, 5, 1, "mayorista"
        )
        assert msg == ""
        assert error is None
        assert carrito[0]["cliente"] == "Juan Pérez"


class TestObtenerClientesFormateados:
    def test_sin_clientes(self, ventas_servicio: Any):
        nombres, mapeo = ventas_servicio.obtener_clientes_formateados()
        assert nombres == []
        assert mapeo == {}

    def test_con_clientes(self, ventas_servicio: Any, db: Any):
        db.insertar_cliente("Carlos", "López", "11111111", "3001111111", "Sur")
        db.insertar_cliente("Ana", "Martínez", "22222222", "3002222222", "Centro")
        nombres, mapeo = ventas_servicio.obtener_clientes_formateados()
        assert len(nombres) == 2
        assert "Carlos López" in nombres
        assert "Ana Martínez" in nombres
        assert mapeo["Carlos López"] == 1
        assert mapeo["Ana Martínez"] == 2


class TestObtenerProductosParaBusqueda:
    def test_sin_filtro_retorna_todos(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "Pepsi", 3000, 2000, 20, 1, "")
        _insertar_producto(db, "Sprite", 3000, 2000, 20, 1, "")
        resultado = ventas_servicio.obtener_productos_para_busqueda()
        assert len(resultado) == 2

    def test_con_filtro_retorna_coincidencias(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "Coca-Cola", 3000, 2000, 20, 1, "")
        _insertar_producto(db, "Pepsi", 3000, 2000, 20, 1, "")
        _insertar_producto(db, "Sprite", 3000, 2000, 20, 1, "")
        resultado = ventas_servicio.obtener_productos_para_busqueda("Cola")
        assert len(resultado) == 1
        assert resultado[0]["producto"] == "Coca-Cola"


class TestCalcularTotalCarrito:
    def test_carrito_vacio_retorna_cero(self, ventas_servicio: Any):
        assert ventas_servicio.calcular_total_carrito([]) == 0

    def test_carrito_con_items(self, ventas_servicio: Any):
        carrito = [
            {"subtotal": 50000},
            {"subtotal": 30000},
            {"subtotal": 20000},
        ]
        assert ventas_servicio.calcular_total_carrito(carrito) == 100000


class TestConfirmarVenta:
    def test_venta_exitosa(self, ventas_servicio: Any, db: Any):
        pid = _insertar_producto(db, "Ron", 50000, 30000, 10, 1, "")
        carrito = [
            {
                "id_producto": pid,
                "producto": "Ron",
                "cantidad": 2,
                "precio": 50000,
                "subtotal": 100000,
                "cliente": "",
                "cliente_id": None,
            },
        ]
        resultado = ventas_servicio.confirmar_venta(carrito, None, 100000, "test_user")
        assert "id_ventas" in resultado
        assert resultado["total"] == 100000
        assert resultado["vuelto"] == 0

    def test_carrito_vacio_lanza_error(self, ventas_servicio: Any):
        with pytest.raises(ValueError, match="vacío"):
            ventas_servicio.confirmar_venta([], None, 0, "test_user")


class TestFiltrarClientesPorTexto:
    def test_filtro_coincide(self, ventas_servicio: Any, db: Any):
        db.insertar_cliente("Pedro", "Ramírez", "33333333", "3003333333", "Este")
        db.insertar_cliente("María", "Gómez", "44444444", "3004444444", "Oeste")
        resultado = ventas_servicio.filtrar_clientes_por_texto("Ramírez")
        assert len(resultado) == 1
        assert resultado[0]["nombres"] == "Pedro"

    def test_filtro_sin_resultados(self, ventas_servicio: Any):
        resultado = ventas_servicio.filtrar_clientes_por_texto("NoExiste")
        assert resultado == []


class TestObtenerClientePorNombreCompleto:
    def test_cliente_existente(self, ventas_servicio: Any, db: Any):
        db.insertar_cliente("Luis", "Fernández", "55555555", "3005555555", "Norte")
        cliente = ventas_servicio.obtener_cliente_por_nombre_completo("Luis Fernández")
        assert cliente is not None
        assert cliente["id_cliente"] == 1
        assert cliente["nombres"] == "Luis"

    def test_cliente_inexistente(self, ventas_servicio: Any):
        cliente = ventas_servicio.obtener_cliente_por_nombre_completo("No Existe")
        assert cliente is None


class TestObtenerProductosPaginado:
    def test_paginado_basico(self, ventas_servicio: Any, db: Any):
        for i in range(10):
            _insertar_producto(db, f"Producto {i}", 1000 * (i + 1), 500 * (i + 1), 10, 1, "")
        pagina = ventas_servicio.obtener_productos_paginado(0, 3)
        assert len(pagina) == 3
        assert pagina[0]["producto"] == "Producto 0"

    def test_paginado_con_filtro(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "Café", 5000, 3000, 20, 1, "")
        _insertar_producto(db, "Café Especial", 8000, 5000, 15, 1, "")
        _insertar_producto(db, "Té", 3000, 2000, 25, 1, "")
        pagina = ventas_servicio.obtener_productos_paginado(0, 10, filtro="Café")
        assert len(pagina) == 2


class TestContarProductos:
    def test_contar_todos(self, ventas_servicio: Any, db: Any):
        for i in range(5):
            _insertar_producto(db, f"Prod {i}", 2000, 1000, 10, 1, "")
        assert ventas_servicio.contar_productos() == 5

    def test_contar_con_filtro(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "AAA", 1000, 500, 10, 1, "")
        _insertar_producto(db, "AAB", 1000, 500, 10, 1, "")
        _insertar_producto(db, "BBB", 1000, 500, 10, 1, "")
        assert ventas_servicio.contar_productos(filtro="AA") == 2


class TestObtenerNombresProductosParaBusqueda:
    def test_sin_filtro(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "Zanahoria", 2000, 1000, 10, 1, "")
        _insertar_producto(db, "Manzana", 3000, 1500, 10, 1, "")
        nombres = ventas_servicio.obtener_nombres_productos_para_busqueda()
        assert "Manzana" in nombres
        assert "Zanahoria" in nombres

    def test_con_filtro(self, ventas_servicio: Any, db: Any):
        _insertar_producto(db, "Jabón Líquido", 5000, 3000, 15, 1, "")
        _insertar_producto(db, "Jabón Barra", 2000, 1000, 20, 1, "")
        _insertar_producto(db, "Shampoo", 8000, 5000, 10, 1, "")
        nombres = ventas_servicio.obtener_nombres_productos_para_busqueda(filtro="Jabón")
        assert len(nombres) == 2
        assert all("Jabón" in n for n in nombres)


class TestObtenerNombreClientePorId:
    def test_cliente_existente(self, ventas_servicio: Any, db: Any):
        db.insertar_cliente("Sofía", "Torres", "66666666", "3006666666", "Centro")
        nombre = ventas_servicio.obtener_nombre_cliente_por_id(1)
        assert nombre == "Sofía Torres"

    def test_cliente_inexistente(self, ventas_servicio: Any):
        nombre = ventas_servicio.obtener_nombre_cliente_por_id(9999)
        assert nombre is None


def _insertar_producto(
    db: Any, nombre: str, precio: int, costo: int, stock: int, estado: int, imagen: str
) -> int:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, precio, costo, stock, estado, imagen),
        )
        return cursor.lastrowid
