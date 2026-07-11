from __future__ import annotations

from pathlib import Path
from typing import Any, Generator

import pytest


@pytest.fixture
def db(tmp_path: Path, monkeypatch: Any) -> Any:
    """Crea una BD temporal totalmente aislada."""
    import importlib
    import retail.nucleo.base_datos as bd

    importlib.reload(bd)

    # Sobrescribir DB_NAME y forzar conexion() a usar la BD temporal
    db_path = str(tmp_path / "test_pos.db")
    bd.DB_NAME = db_path

    bd.crear_tablas()
    return bd


class TestConexion:
    def test_obtener_conexion(self, db: Any):
        conn = db.obtener_conexion()
        assert conn is not None
        conn.close()

    def test_conexion_context_manager(self, db: Any):
        with db.conexion() as conn:
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1

    def test_conexion_rollback_on_error(self, db: Any):
        # Insertar un producto primero
        with db.conexion() as conn:
            conn.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Test", 1000, 500, 10, 1, ""),
            )
        # Luego forzar un rollback en otra transacción
        with pytest.raises(ValueError):
            with db.conexion() as conn:
                conn.execute("UPDATE inventario SET stock = 999 WHERE producto = 'Test'")
                raise ValueError("forzar rollback")
        # Verificar que el UPDATE no se persistió
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock FROM inventario WHERE producto = 'Test'")
            assert cursor.fetchone()[0] == 10

    def test_ejecutar_consulta(self, db: Any):
        resultado = db.ejecutar_consulta("SELECT 42")
        assert resultado[0] == 42


class TestProductos:
    def test_crear_tablas_crea_inventario(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE name='inventario'"
            )
            assert cursor.fetchone() is not None

    def test_producto_a_dict(self, db: Any):
        producto = (1, "Ron", 50000, 30000, 10, 1, "ron.jpg")
        d = db.producto_a_dict(producto)
        assert d["id_producto"] == 1
        assert d["producto"] == "Ron"
        assert d["precio"] == 50000
        assert d["costo"] == 30000
        assert d["stock"] == 10
        assert d["estado"] == 1
        assert d["imagen"] == "ron.jpg"

    def test_paginar_productos_sin_filtro(self, db: Any):
        # Insertar productos de prueba
        with db.conexion() as conn:
            cursor = conn.cursor()
            for i in range(5):
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"Producto {i}", 1000 * (i + 1), 500 * (i + 1), 10, 1, ""),
                )
        productos = db.paginar_productos(0, 3)
        assert len(productos) == 3
        assert productos[0]["producto"] == "Producto 0"

    def test_paginar_productos_con_filtro(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["Coca-Cola", "Pepsi", "Sprite"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 3000, 2000, 20, 1, ""),
                )
        productos = db.paginar_productos(0, 10, filtro="Cola")
        assert len(productos) == 1
        assert productos[0]["producto"] == "Coca-Cola"

    def test_contar_productos(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for i in range(7):
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"Prod {i}", 1000, 500, 5, 1, ""),
                )
        assert db.contar_productos() == 7

    def test_contar_productos_con_filtro(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["AAA", "AAB", "BBB"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 1000, 500, 5, 1, ""),
                )
        assert db.contar_productos(filtro="AA") == 2

    def test_obtener_nombres_productos(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["Zumo", "Agua", "Jugo"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 2000, 1000, 15, 1, ""),
                )
        nombres = db.obtener_nombres_productos()
        assert nombres == ["Agua", "Jugo", "Zumo"]


class TestPesoColombiano:
    def test_formato_inicia_con_peso(self, db: Any):
        assert db.peso_colombiano(50000).startswith("$")

    def test_formato_incluye_numero(self, db: Any):
        resultado = db.peso_colombiano(50000)
        assert "50000" in resultado.replace(".", "").replace(",", "")

    def test_formato_cero(self, db: Any):
        resultado = db.peso_colombiano(0)
        assert resultado.startswith("$")

    def test_formato_millon(self, db: Any):
        resultado = db.peso_colombiano(1000000)
        assert "1000000" in resultado.replace(".", "").replace(",", "")


class TestObtenerNombresProductosConFiltro:
    def test_con_filtro_retorna_coincidencias(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["Coca-Cola", "Pepsi Cola", "Sprite", "Fanta"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 2000, 1000, 15, 1, ""),
                )
        nombres = db.obtener_nombres_productos(filtro="Cola")
        assert nombres == ["Coca-Cola", "Pepsi Cola"]

    def test_con_filtro_sin_resultados(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Test", 1000, 500, 5, 1, ""),
            )
        nombres = db.obtener_nombres_productos(filtro="NoExiste")
        assert nombres == []


class TestTotalesGlobales:
    def test_sin_datos_devuelve_cero(self, db: Any):
        total_ventas, total_ganancia = db.obtener_totales_globales_ganancias()
        assert total_ventas == 0.0
        assert total_ganancia == 0.0

    def test_con_ventas_devuelve_totales(self, db: Any):
        pid = _insertar_producto(db, "ProdV", 10000, 6000, 50)
        items = [{"id_producto": pid, "cantidad": 2, "precio": 10000}]
        db.crear_venta(items=items, monto_recibido=50000, usuario="test")
        total_ganancia, total_ventas = db.obtener_totales_globales_ganancias()
        assert total_ventas == 20000
        assert total_ganancia == 8000

    def test_con_deudas_pagadas_devuelve_totales(self, db: Any):
        pid = _insertar_producto(db, "ProdD", 20000, 12000, 30)
        db.insertar_cliente("Deudor", "Test", "33333", "3003333333", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("33333",))
            cliente_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO deudas (numero_factura, cliente_id, fecha, total, saldo, estado, usuario_creacion) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("FAC-D-1", cliente_id, "2026-07-09", 40000, 0, "PAGADA", "test"),
            )
            id_deuda = cursor.lastrowid
            cursor.execute(
                "INSERT INTO detalle_deuda (id_deuda, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_deuda, pid, 2, 20000, 40000),
            )
            cursor.execute(
                "INSERT INTO pagos_deuda (id_deuda, fecha, hora, monto, usuario) VALUES (?, ?, ?, ?, ?)",
                (id_deuda, "2026-07-09", "12:00:00", 40000, "test"),
            )
        total_ganancia, total_ventas = db.obtener_totales_globales_ganancias()
        assert total_ventas == 40000
        assert total_ganancia == 16000


class TestClientesDirectos:
    def test_eliminar_cliente(self, db: Any):
        db.insertar_cliente("Eliminar", "Test", "44444", "3004444444", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("44444",))
            cliente_id = cursor.fetchone()[0]
        db.eliminar_cliente(cliente_id)
        clientes = db.obtener_clientes()
        assert len(clientes) == 0

    def test_actualizar_cliente(self, db: Any):
        db.insertar_cliente("Original", "Test", "55555", "3005555555", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("55555",))
            cliente_id = cursor.fetchone()[0]
        db.actualizar_cliente(cliente_id, "nombres", "Actualizado")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombres FROM clientes WHERE id_cliente = ?", (cliente_id,))
            assert cursor.fetchone()[0] == "Actualizado"

    def test_buscar_cliente_por_cedula_funcion(self, db: Any):
        db.insertar_cliente("Buscar", "Test", "66666", "3006666666", "Zona")
        resultado = db.buscar_cliente_por_cedula("66666")
        assert resultado is not None
        assert resultado[0] > 0


class TestClientes:
    def test_insertar_y_obtener_clientes(self, db: Any):
        db.insertar_cliente("Juan", "Pérez", "12345", "3001234567", "Bogotá")
        clientes = db.obtener_clientes()
        assert len(clientes) == 1
        assert clientes[0][1] == "Juan"

    def test_insertar_cliente_con_existente(self, db: Any):
        db.insertar_cliente("Ana", "García", "99999", "3000000000", "Medellín")
        db.insertar_cliente("Luis", "Martínez", "88888", "3001111111", "Cali")
        clientes = db.obtener_clientes()
        assert len(clientes) == 2

    def test_buscar_cliente_por_cedula(self, db: Any):
        db.insertar_cliente("Test", "User", "55555", "3005555555", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE cedula = ?", ("55555",))
            row = cursor.fetchone()
        assert row is not None
        assert str(row[3]) == "55555"


def _insertar_producto(db: Any, nombre: str, precio: int, costo: int, stock: int) -> int:
    with db.conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, precio, costo, stock, 1, ""),
        )
        return cursor.lastrowid


class TestCrearVenta:
    def test_crear_venta_exitosa(self, db: Any):
        # Preparar producto
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Cerveza", 4000, 2500, 100, 1, ""),
            )
            producto_id = cursor.lastrowid

        # Crear venta
        items = [{"id_producto": producto_id, "cantidad": 2, "precio": 4000}]
        resultado = db.crear_venta(
            cliente_id=None,
            items=items,
            monto_recibido=10000,
            usuario="test",
        )

        assert "id_ventas" in resultado
        assert resultado["total"] == 8000
        assert resultado["vuelto"] == 2000

    def test_crear_venta_con_cliente(self, db: Any):
        pid = _insertar_producto(db, "Whisky", 120000, 80000, 5)
        db.insertar_cliente("Carlos", "Ruiz", "11111", "3000000001", "Bogotá")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE cedula = ?", ("11111",)
            )
            cliente_id = cursor.fetchone()[0]

        items = [{"id_producto": pid, "cantidad": 1, "precio": 120000}]
        resultado = db.crear_venta(
            cliente_id=cliente_id,
            items=items,
            monto_recibido=120000,
            usuario="test",
        )
        assert resultado["total"] == 120000
        assert resultado["vuelto"] == 0

    def test_crear_venta_sin_items_lanza_error(self, db: Any):
        with pytest.raises(ValueError, match="No hay items"):
            db.crear_venta(items=[])

    def test_crear_venta_stock_insuficiente_lanza_error(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Vodka", 50000, 30000, 1, 1, ""),
            )
            pid = cursor.lastrowid

        items = [{"id_producto": pid, "cantidad": 5}]
        with pytest.raises(ValueError, match="Stock insuficiente"):
            db.crear_venta(items=items, monto_recibido=500000)

    def test_crear_venta_monto_insuficiente_lanza_error(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Tequila", 80000, 50000, 3, 1, ""),
            )
            pid = cursor.lastrowid

        items = [{"id_producto": pid, "cantidad": 1}]
        with pytest.raises(ValueError, match="Monto recibido insuficiente"):
            db.crear_venta(items=items, monto_recibido=10000)


class TestCrearDeuda:
    def test_crear_deuda_exitosa(self, db: Any):
        pid = _insertar_producto(db, "Ron", 60000, 40000, 20)
        db.insertar_cliente("Pedro", "López", "22222", "3002222222", "Cali")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE cedula = ?", ("22222",)
            )
            cliente_id = cursor.fetchone()[0]

        items = [{"id_producto": pid, "cantidad": 3}]
        resultado = db.crear_deuda(
            cliente_id=cliente_id, items=items, usuario="test"
        )
        assert "id_deuda" in resultado
        assert resultado["total"] == 180000
        assert resultado["saldo"] == 180000

    def test_crear_deuda_sin_cliente_lanza_error(self, db: Any):
        with pytest.raises(ValueError, match="Cliente es obligatorio"):
            db.crear_deuda(cliente_id=None, items=[])

    def test_crear_deuda_sin_items_lanza_error(self, db: Any):
        with pytest.raises(ValueError, match="No hay items"):
            db.crear_deuda(cliente_id=1, items=[])

    def test_crear_deuda_cliente_inexistente_lanza_error(self, db: Any):
        items = [{"id_producto": 999, "cantidad": 1}]
        with pytest.raises(ValueError, match="no existe"):
            db.crear_deuda(cliente_id=9999, items=items)


class TestRegistrarHistorialVenta:
    def test_registrar_historial_venta(self, db: Any):
        pid = _insertar_producto(db, "Ginebra", 70000, 45000, 8)

        db.registrar_historial_venta(
            id_ventas=1,
            id_producto=pid,
            cantidad=2,
            subtotal=140000,
            accion="VENTA",
            usuario="test",
            detalle="Venta de prueba",
        )

        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accion FROM historial_ventas")
            rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "VENTA"


class TestRegistrarHistorialDeuda:
    def test_registrar_historial_deuda(self, db: Any):
        pid = _insertar_producto(db, "Brandy", 55000, 35000, 12)

        db.registrar_historial_deuda(
            id_deuda=1,
            id_producto=pid,
            cantidad=1,
            subtotal=55000,
            accion="DEUDA",
            usuario="test",
            detalle="Deuda de prueba",
        )

        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accion FROM historial_deudas")
            rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "DEUDA"


class TestFuncionesInventario:
    def test_combobox_productos(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["Zumo", "Agua", "Jugo"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 2000, 1000, 15, 1, ""),
                )
        nombres = db.combobox_productos()
        assert sorted(nombres) == ["Agua", "Jugo", "Zumo"]

    def test_editar_producto_existente(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Editar", 5000, 3000, 10, 1, "img.jpg"),
            )
            pid = cursor.lastrowid
        producto = db.editar_producto(pid)
        assert producto is not None
        assert producto[1] == "Editar"

    def test_editar_producto_inexistente(self, db: Any):
        producto = db.editar_producto(9999)
        assert producto is None

    def test_buscar_productos_por_nombre(self, db: Any):
        with db.conexion() as conn:
            cursor = conn.cursor()
            for nombre in ["Coca-Cola", "Pepsi", "Sprite"]:
                cursor.execute(
                    "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre, 3000, 2000, 20, 1, ""),
                )
        resultados = db.buscar_productos_por_nombre("Cola")
        assert len(resultados) == 1
        assert resultados[0][1] == "Coca-Cola"

    def test_registrar_historial_inventario(self, db: Any):
        pid = _insertar_producto(db, "Historial", 1000, 500, 10)
        db.registrar_historial_inventario(
            id_producto=pid, accion="COMPRA", pedido=5, stock=15,
            precio=1000, costo=500, ganancia=2500, total=5000,
        )
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT accion FROM historial_inventario")
            rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "COMPRA"

    def test_dlt_producto_directo(self, db: Any):
        pid = _insertar_producto(db, "Delete", 1000, 500, 5)
        db.eliminar_producto(pid)
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_producto = ?", (pid,))
            assert cursor.fetchone()[0] == 0


class TestFuncionesUsuarios:
    def test_insertar_y_buscar_usuario(self, db: Any):
        db.insertar_usuario("testuser", "testpass")
        resultado = db.buscar_usuario("testuser", "testpass")
        assert resultado is not None
        assert resultado[1] == "testuser"

    def test_buscar_usuario_contrasena_incorrecta(self, db: Any):
        db.insertar_usuario("user1", "pass1")
        resultado = db.buscar_usuario("user1", "wrongpass")
        assert resultado is None

    def test_obtener_usuarios(self, db: Any):
        db.insertar_usuario("user_a", "pass_a")
        db.insertar_usuario("user_b", "pass_b")
        usuarios = db.obtener_usuarios()
        assert len(usuarios) >= 2

    def test_actualizar_usuario(self, db: Any):
        db.insertar_usuario("oldname", "oldpass")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ("oldname",))
            uid = cursor.fetchone()[0]
        db.actualizar_usuario(uid, "newname", "newpass")
        resultado = db.buscar_usuario("newname", "newpass")
        assert resultado is not None

    def test_eliminar_usuario(self, db: Any):
        db.insertar_usuario("delete_me", "pass")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ("delete_me",))
            uid = cursor.fetchone()[0]
        db.eliminar_usuario(uid)
        resultado = db.buscar_usuario("delete_me", "pass")
        assert resultado is None


class TestFuncionesCombobox:
    def test_combobox_clientes(self, db: Any):
        db.insertar_cliente("Ana", "Pérez", "111", "3001111111", "Bogotá")
        db.insertar_cliente("Luis", "Martínez", "222", "3002222222", "Cali")
        nombres = db.combobox_clientes()
        assert "Ana" in nombres
        assert "Luis" in nombres

    def test_combobox_clientes_sin_datos(self, db: Any):
        nombres = db.combobox_clientes()
        assert nombres == []


class TestObtenerHistorialPorVenta:
    def test_historial_por_venta(self, db: Any):
        pid = _insertar_producto(db, "ProdH", 1000, 500, 10)
        items = [{"id_producto": pid, "cantidad": 1, "precio": 1000}]
        resultado = db.crear_venta(items=items, monto_recibido=2000, usuario="test")
        id_ventas = resultado["id_ventas"]
        historial = db.obtener_historial_por_venta(id_ventas)
        assert len(historial) >= 1

    def test_historial_por_venta_inexistente(self, db: Any):
        historial = db.obtener_historial_por_venta(9999)
        assert historial == []


class TestCrearVentaEdgeCases:
    def test_cantidad_cero_lanza_error(self, db: Any):
        pid = _insertar_producto(db, "Prod", 1000, 500, 10)
        items = [{"id_producto": pid, "cantidad": 0, "precio": 1000}]
        with pytest.raises(ValueError, match="Cantidad inválida"):
            db.crear_venta(items=items, monto_recibido=1000)

    def test_producto_inexistente_lanza_error(self, db: Any):
        items = [{"id_producto": 9999, "cantidad": 1}]
        with pytest.raises(ValueError, match="Producto ID 9999 no existe"):
            db.crear_venta(items=items, monto_recibido=1000)


class TestCrearDeudaEdgeCases:
    def test_cantidad_cero_lanza_error(self, db: Any):
        db.insertar_cliente("Test", "User", "77777", "3007777777", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("77777",))
            cliente_id = cursor.fetchone()[0]
        items = [{"id_producto": 1, "cantidad": 0}]
        with pytest.raises(ValueError, match="Cantidad inválida"):
            db.crear_deuda(cliente_id=cliente_id, items=items)

    def test_producto_inexistente_lanza_error(self, db: Any):
        db.insertar_cliente("Test2", "User", "88888", "3008888888", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("88888",))
            cliente_id = cursor.fetchone()[0]
        items = [{"id_producto": 9999, "cantidad": 1}]
        with pytest.raises(ValueError, match="Producto ID 9999 no existe"):
            db.crear_deuda(cliente_id=cliente_id, items=items)


class TestMoverAPapelera:
    def test_mover_venta_a_papelera(self, db: Any):
        pid = _insertar_producto(db, "PapeleraV", 1000, 500, 10)
        items = [{"id_producto": pid, "cantidad": 1, "precio": 1000}]
        resultado = db.crear_venta(items=items, monto_recibido=2000, usuario="test")
        id_ventas = resultado["id_ventas"]
        exito = db.mover_venta_a_papelera(id_ventas, "test_user", "motivo prueba")
        assert exito is True
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_ventas = ?", (id_ventas,))
            assert cursor.fetchone()[0] == 0

    def test_mover_venta_inexistente(self, db: Any):
        exito = db.mover_venta_a_papelera(9999, "test")
        assert exito is False

    def test_mover_deuda_a_papelera(self, db: Any):
        pid = _insertar_producto(db, "PapeleraD", 1000, 500, 10)
        db.insertar_cliente("DP", "Test", "99999", "3009999999", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("99999",))
            cliente_id = cursor.fetchone()[0]
        items = [{"id_producto": pid, "cantidad": 1}]
        resultado = db.crear_deuda(cliente_id=cliente_id, items=items, usuario="test")
        id_deuda = resultado["id_deuda"]
        exito = db.mover_deuda_a_papelera(id_deuda, "test_user", "motivo prueba")
        assert exito is True

    def test_eliminar_venta_wrapper(self, db: Any):
        pid = _insertar_producto(db, "ElimV", 1000, 500, 10)
        items = [{"id_producto": pid, "cantidad": 1, "precio": 1000}]
        resultado = db.crear_venta(items=items, monto_recibido=2000, usuario="test")
        id_ventas = resultado["id_ventas"]
        assert db.eliminar_venta(id_ventas, "test") is True

    def test_eliminar_deuda_wrapper(self, db: Any):
        pid = _insertar_producto(db, "ElimD", 1000, 500, 10)
        db.insertar_cliente("EW", "Test", "00000", "3000000000", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("00000",))
            cliente_id = cursor.fetchone()[0]
        items = [{"id_producto": pid, "cantidad": 1}]
        resultado = db.crear_deuda(cliente_id=cliente_id, items=items, usuario="test")
        id_deuda = resultado["id_deuda"]
        assert db.eliminar_deuda(id_deuda, "test") is True


class TestPapeleras:
    def test_obtener_papelera_ventas(self, db: Any):
        pid = _insertar_producto(db, "PapV", 1000, 500, 10)
        items = [{"id_producto": pid, "cantidad": 1, "precio": 1000}]
        resultado = db.crear_venta(items=items, monto_recibido=2000, usuario="test")
        db.mover_venta_a_papelera(resultado["id_ventas"], "test")
        rows = db.obtener_papelera_ventas()
        assert len(rows) >= 1

    def test_obtener_papelera_deudas(self, db: Any):
        pid = _insertar_producto(db, "PapD", 1000, 500, 10)
        db.insertar_cliente("PapD", "Test", "11111_2", "3001111112", "Zona")
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", ("11111_2",))
            cliente_id = cursor.fetchone()[0]
        items = [{"id_producto": pid, "cantidad": 1}]
        resultado = db.crear_deuda(cliente_id=cliente_id, items=items, usuario="test")
        db.mover_deuda_a_papelera(resultado["id_deuda"], "test")
        rows = db.obtener_papelera_deudas()
        assert len(rows) >= 1


class TestActualizarCuentas:
    def test_actualizar_cuentas_vacia(self, db: Any):
        db.actualizar_cuentas()
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ganancias")
            assert cursor.fetchone()[0] == 0

    def test_actualizar_cuentas_con_venta(self, db: Any):
        pid = _insertar_producto(db, "Cuentas", 10000, 6000, 50)
        items = [{"id_producto": pid, "cantidad": 2, "precio": 10000}]
        db.crear_venta(items=items, monto_recibido=50000, usuario="test")
        db.actualizar_cuentas()
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT total_dia, total_semana, total_mes, total_anio FROM ganancias")
            row = cursor.fetchone()
        assert row is not None
        assert row[0] == 20000
