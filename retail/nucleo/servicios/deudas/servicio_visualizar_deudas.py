"""
servicio_visualizar_deudas.py

Servicio para obtener información detallada de una deuda,
incluyendo todos sus productos, totales, cliente, etc.
"""

from typing import Dict, Any, List
from retail.nucleo.base_datos import get_connection


class ServicioVisualizarDeudas:
    """Servicio para obtener detalles completos de una deuda (solo lectura)."""

    @staticmethod
    def obtener_detalles_deuda(id_deuda: int) -> Dict[str, Any]:
        """
        Retorna un diccionario con toda la información de la deuda:
        - id_deuda, numero_factura, fecha, total, saldo, cliente
        - productos: lista de dicts con producto, cantidad, precio_unitario, subtotal
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT d.id_deuda, d.numero_factura, d.fecha, d.total, d.saldo,
                   COALESCE(c.nombres || ' ' || c.apellidos, 'Sin cliente') AS cliente
            FROM deudas d
            LEFT JOIN clientes c ON d.cliente_id = c.id_cliente
            WHERE d.id_deuda = ?
            """,
            (id_deuda,)
        )
        deuda = cursor.fetchone()
        if not deuda:
            conn.close()
            return {}

        id_deuda, numero_factura, fecha, total, saldo, cliente = deuda

        cursor.execute(
            """
            SELECT i.producto, dd.cantidad, dd.precio_unitario, dd.subtotal
            FROM detalle_deuda dd
            LEFT JOIN inventario i ON dd.id_producto = i.id_producto
            WHERE dd.id_deuda = ?
            ORDER BY dd.id_detalle
            """,
            (id_deuda,)
        )
        productos = cursor.fetchall()
        conn.close()

        lista_productos: List[Dict[str, Any]] = []
        for producto, cantidad, precio_unitario, subtotal in productos:
            lista_productos.append({
                "producto": producto or "Producto desconocido",
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal,
            })

        return {
            "id_deuda": id_deuda,
            "numero_factura": numero_factura,
            "fecha": fecha,
            "total": total,
            "saldo": saldo,
            "cliente": cliente,
            "productos": lista_productos,
        }