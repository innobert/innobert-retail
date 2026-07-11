"""
servicio_diario.py

Servicio para gestionar la lógica de negocio del reporte diario de ganancias:
- Obtener total de registros (ventas + deudas pagadas) para una fecha.
- Obtener una página de registros con paginación.
- Calcular totales de ganancia y monto para una fecha.
"""

import datetime
from typing import List, Tuple, Dict, Any
from retail.nucleo.base_datos import obtener_conexion


class ServicioDiario:
    """Servicio para el reporte diario de ganancias."""

    @staticmethod
    def contar_registros(fecha: str) -> int:
        """Devuelve el número total de registros (ventas + deudas pagadas) para la fecha."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            # Ventas de contado
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM ventas v
                JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                WHERE date(v.fecha) = ?
                """,
                (fecha,)
            )
            ventas_count = cursor.fetchone()[0]

            # Deudas pagadas (productos asociados)
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM pagos_deuda p
                JOIN deudas d ON p.id_deuda = d.id_deuda
                JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                WHERE d.estado = 'PAGADA' AND date(p.fecha) = ?
                """,
                (fecha,)
            )
            deudas_count = cursor.fetchone()[0]

            return ventas_count + deudas_count
        finally:
            conn.close()

    @staticmethod
    def obtener_pagina(fecha: str, offset: int, limit: int) -> List[Tuple]:
        """
        Retorna una lista de registros (ventas + deudas pagadas) para la fecha,
        ordenados por fecha y hora, y limitados a la página solicitada.
        Cada registro es una tupla con los campos:
        (fecha, hora, cliente, producto, cantidad, costo, precio, ganancia, monto, tipo)
        """
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Ventas de contado
        cursor.execute(
            """
            SELECT v.fecha, v.hora,
                   COALESCE(c.nombres || ' ' || c.apellidos, v.cliente_rapido) AS cliente,
                   i.producto, dv.cantidad, i.costo, i.precio,
                   (i.precio - i.costo) * dv.cantidad AS ganancia,
                   (i.precio * dv.cantidad) AS monto,
                   1 AS tipo
            FROM ventas v
            JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
            JOIN inventario i ON dv.id_producto = i.id_producto
            LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
            WHERE date(v.fecha) = ?
            ORDER BY v.fecha, v.hora
            """,
            (fecha,)
        )
        ventas = cursor.fetchall()

        # Deudas pagadas
        cursor.execute(
            """
            SELECT p.fecha, p.hora,
                   c.nombres || ' ' || c.apellidos AS cliente,
                   i.producto, dd.cantidad, i.costo, dd.precio_unitario AS precio,
                   (dd.precio_unitario - i.costo) * dd.cantidad AS ganancia,
                   (dd.precio_unitario * dd.cantidad) AS monto,
                   2 AS tipo
            FROM pagos_deuda p
            JOIN deudas d ON p.id_deuda = d.id_deuda
            JOIN clientes c ON d.cliente_id = c.id_cliente
            JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
            JOIN inventario i ON dd.id_producto = i.id_producto
            WHERE d.estado = 'PAGADA' AND date(p.fecha) = ?
            ORDER BY p.fecha, p.hora
            """,
            (fecha,)
        )
        deudas = cursor.fetchall()
        conn.close()

        # Unir y ordenar globalmente
        todos = list(ventas) + list(deudas)
        todos.sort(key=lambda x: (x[0], x[1]))  # orden por fecha, hora

        # Aplicar paginación
        return todos[offset:offset + limit]

    @staticmethod
    def obtener_totales_fecha(fecha: str) -> Tuple[float, float]:
        """Suma total ganancia y total monto para la fecha completa (sin paginación)."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        total_ganancia = 0.0
        total_monto = 0.0

        try:
            # Ventas
            cursor.execute(
                """
                SELECT SUM((i.precio - i.costo) * dv.cantidad),
                       SUM(i.precio * dv.cantidad)
                FROM ventas v
                JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                JOIN inventario i ON dv.id_producto = i.id_producto
                WHERE date(v.fecha) = ?
                """,
                (fecha,)
            )
            venta_totales = cursor.fetchone()
            if venta_totales and venta_totales[0]:
                total_ganancia += venta_totales[0]
                total_monto += venta_totales[1]

            # Deudas pagadas
            cursor.execute(
                """
                SELECT SUM((dd.precio_unitario - i.costo) * dd.cantidad),
                       SUM(dd.precio_unitario * dd.cantidad)
                FROM pagos_deuda p
                JOIN deudas d ON p.id_deuda = d.id_deuda
                JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                JOIN inventario i ON dd.id_producto = i.id_producto
                WHERE d.estado = 'PAGADA' AND date(p.fecha) = ?
                """,
                (fecha,)
            )
            deuda_totales = cursor.fetchone()
            if deuda_totales and deuda_totales[0]:
                total_ganancia += deuda_totales[0]
                total_monto += deuda_totales[1]
        finally:
            conn.close()

        return total_ganancia, total_monto

    @staticmethod
    def formatear_registros_para_tabla(registros: List[Tuple]) -> List[Tuple]:
        """
        Convierte los registros obtenidos de `obtener_pagina` en tuplas listas para mostrar
        en el Treeview, incluyendo el número de fila y el día de la semana formateado.
        """
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        filas = []
        for idx, reg in enumerate(registros, start=1):
            fecha, hora, cliente, producto, cantidad, costo, precio, ganancia, monto, tipo = reg
            fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana = dias[fecha_dt.weekday()]
            filas.append((
                idx,
                dia_semana,
                cliente,
                fecha,
                hora,
                producto,
                cantidad,
                f"${costo:,.0f}".replace(",", "."),
                f"${precio:,.0f}".replace(",", "."),
                f"${ganancia:,.0f}".replace(",", "."),
            ))
        return filas