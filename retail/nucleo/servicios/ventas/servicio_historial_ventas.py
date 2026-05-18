
"""
servicio_historial_ventas.py

Servicio para obtener el historial de ventas (por venta específica o por cliente).
Ahora incluye las acciones 'AGREGADO' para reflejar productos añadidos posteriormente.
"""

from typing import List, Dict, Any
import datetime
from retail.nucleo.base_datos import get_connection


class ServicioHistorialVentas:
    """Servicio para operaciones de historial de ventas."""

    @staticmethod
    def obtener_por_venta(id_ventas: int) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una venta específica.
        Retorna lista de diccionarios con las claves:
        id_historial, producto, fecha, hora, cantidad, subtotal, accion,
        monto_recibido, vuelto, dia_semana.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion,
                   h.monto_recibido, h.vuelto, v.id_ventas
            FROM historial_ventas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            LEFT JOIN ventas v ON h.id_ventas = v.id_ventas
            WHERE v.id_ventas = ?
              AND h.accion IN ('VENTA', 'X MAYOR', 'EDITADO', 'ELIMINADO', 'MONTO_ACTUALIZADO', 'AGREGADO')
            ORDER BY h.fecha DESC, h.hora DESC
            """,
            (id_ventas,)
        )
        rows = cursor.fetchall()
        conn.close()
        return ServicioHistorialVentas._procesar_filas(rows)

    @staticmethod
    def obtener_por_cliente(id_cliente: int, cliente_rapido: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de ventas para un cliente (por id o por cliente_rapido).
        Retorna lista de diccionarios con las mismas claves.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion,
                   h.monto_recibido, h.vuelto, v.id_ventas
            FROM historial_ventas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            LEFT JOIN ventas v ON h.id_ventas = v.id_ventas
            WHERE (v.cliente_id = ? OR v.cliente_rapido = ?)
              AND h.accion IN ('VENTA', 'X MAYOR', 'EDITADO', 'ELIMINADO', 'MONTO_ACTUALIZADO', 'AGREGADO')
            ORDER BY h.fecha DESC, h.hora DESC
            """,
            (id_cliente, cliente_rapido)
        )
        rows = cursor.fetchall()
        conn.close()
        return ServicioHistorialVentas._procesar_filas(rows)

    @staticmethod
    def _procesar_filas(rows) -> List[Dict[str, Any]]:
        """Convierte las filas de la base de datos en diccionarios enriquecidos."""
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        historial = []
        for idx, row in enumerate(rows, start=1):
            id_historial, producto, fecha, hora, cantidad, subtotal, accion, monto_recibido, vuelto, id_ventas = row
            # Calcular día de la semana
            try:
                fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                dia_semana = dias[fecha_dt.weekday()]
            except Exception:
                dia_semana = ""
            # Manejo de valores nulos
            cantidad_str = str(cantidad) if cantidad is not None else ""
            subtotal_str = f"${subtotal:,.0f}".replace(",", ".") if subtotal is not None else ""
            monto_str = f"${monto_recibido:,.0f}".replace(",", ".") if monto_recibido is not None else "0"
            vuelto_str = f"${vuelto:,.0f}".replace(",", ".") if vuelto is not None else "0"
            historial.append({
                "idx": idx,
                "id_historial": id_historial,
                "producto": producto if producto is not None else "",
                "fecha": fecha,
                "hora": hora,
                "dia_semana": dia_semana,
                "cantidad": cantidad_str,
                "subtotal": subtotal_str,
                "accion": accion if accion is not None else "",
                "monto_recibido": monto_str,
                "vuelto": vuelto_str,
                "id_ventas": id_ventas
            })
        return historial