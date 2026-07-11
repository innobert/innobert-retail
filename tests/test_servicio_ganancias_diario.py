from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def diario_servicio(db: Any) -> Any:
    import importlib
    import retail.nucleo.servicios.ganancias.servicio_diario as sd
    importlib.reload(sd)
    return sd.ServicioDiario


class TestServicioDiario:
    @staticmethod
    def test_contar_registros_sin_datos(diario_servicio: Any) -> None:
        total = diario_servicio.contar_registros("2026-07-09")
        assert total == 0

    @staticmethod
    def test_contar_registros_con_venta(diario_servicio: Any, db: Any) -> None:
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Prod", 10000, 6000, 50, 1, ""),
            )
            pid = cursor.lastrowid
            conn.execute(
                "INSERT INTO ventas (numero_factura, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("FAC-T1", "2026-07-09", "10:00:00", 20000, 8000, 30000, 10000),
            )
            id_ventas = cursor.lastrowid
            conn.execute(
                "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_ventas, pid, 2, 10000, 20000),
            )
        total = diario_servicio.contar_registros("2026-07-09")
        assert total == 1

    @staticmethod
    def test_obtener_pagina_con_ventas(diario_servicio: Any, db: Any) -> None:
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Prod", 10000, 6000, 50, 1, ""),
            )
            pid = cursor.lastrowid
            conn.execute(
                "INSERT INTO ventas (numero_factura, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("FAC-T2", "2026-07-09", "11:00:00", 20000, 8000, 30000, 10000),
            )
            id_ventas = cursor.lastrowid
            conn.execute(
                "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_ventas, pid, 2, 10000, 20000),
            )
        pagina = diario_servicio.obtener_pagina("2026-07-09", 0, 10)
        assert len(pagina) >= 1
        assert pagina[0][3] == "Prod"

    @staticmethod
    def test_obtener_totales_fecha_con_venta(diario_servicio: Any, db: Any) -> None:
        with db.conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                ("Prod", 10000, 6000, 50, 1, ""),
            )
            pid = cursor.lastrowid
            conn.execute(
                "INSERT INTO ventas (numero_factura, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("FAC-T3", "2026-07-09", "12:00:00", 20000, 8000, 30000, 10000),
            )
            id_ventas = cursor.lastrowid
            conn.execute(
                "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_ventas, pid, 2, 10000, 20000),
            )
        ganancia, monto = diario_servicio.obtener_totales_fecha("2026-07-09")
        assert ganancia > 0
        assert monto > 0


class TestFormatearRegistrosParaTabla:
    @staticmethod
    def test_formatea_registro_correctamente() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        registros = [
            ("2026-07-09", "10:30:00", "Juan Perez", "Ron", 2, 5000.0, 8000.0, 6000.0, 16000.0, 1),
        ]
        resultado = ServicioDiario.formatear_registros_para_tabla(registros)
        assert len(resultado) == 1
        fila = resultado[0]
        assert fila[0] == 1
        assert fila[2] == "Juan Perez"
        assert fila[3] == "2026-07-09"
        assert fila[4] == "10:30:00"
        assert fila[5] == "Ron"
        assert fila[6] == 2
        assert fila[7].startswith("$")
        assert fila[8].startswith("$")
        assert fila[9].startswith("$")

    @staticmethod
    def test_dia_semana_correcto() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        registros = [("2026-07-09", "10:00:00", "Cliente", "Prod", 1, 100.0, 200.0, 100.0, 200.0, 1)]
        resultado = ServicioDiario.formatear_registros_para_tabla(registros)
        assert resultado[0][1] == "Jueves"

    @staticmethod
    def test_formatea_varios_registros() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        registros = [
            ("2026-07-09", "10:00:00", "Cliente A", "Prod 1", 1, 100.0, 200.0, 100.0, 200.0, 1),
            ("2026-07-09", "11:00:00", "Cliente B", "Prod 2", 3, 50.0, 150.0, 300.0, 450.0, 2),
        ]
        resultado = ServicioDiario.formatear_registros_para_tabla(registros)
        assert len(resultado) == 2
        assert resultado[0][0] == 1
        assert resultado[1][0] == 2

    @staticmethod
    def test_formato_moneda_colombiana() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        registros = [
            ("2026-07-09", "10:00:00", "Cliente", "Prod", 1, 1500000.0, 2000000.0, 500000.0, 2000000.0, 1),
        ]
        resultado = ServicioDiario.formatear_registros_para_tabla(registros)
        assert resultado[0][7] == "$1.500.000"
        assert resultado[0][8] == "$2.000.000"
        assert resultado[0][9] == "$500.000"

    @staticmethod
    def test_lista_vacia() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        resultado = ServicioDiario.formatear_registros_para_tabla([])
        assert resultado == []

    @staticmethod
    def test_registro_con_tipo_1_y_2() -> None:
        from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario
        registros = [
            ("2026-07-09", "10:00:00", "Cliente", "Prod", 1, 100.0, 200.0, 100.0, 200.0, 1),
            ("2026-07-09", "11:00:00", "Cliente", "Prod", 2, 50.0, 100.0, 100.0, 200.0, 2),
        ]
        resultado = ServicioDiario.formatear_registros_para_tabla(registros)
        assert len(resultado) == 2
