"""
servicio_visualizar_ventas.py

Servicio para obtener información detallada de una factura de venta,
incluyendo todos sus productos, subtotales, totales, cliente, etc.
"""

from __future__ import annotations

from typing import Dict, Any
from retail.nucleo.base_datos import conexion


class ServicioVisualizarVentas:
    """Servicio para obtener detalles completos de una factura de venta (solo lectura)."""

    @staticmethod
    def obtener_detalles_factura(id_ventas: int) -> Dict[str, Any]:
        """
        Retorna un diccionario con toda la información de la factura:
        - id_ventas, numero_factura, fecha, hora, total, monto_recibido, vuelto
        - cliente (nombre)
        - productos: lista de dicts con producto, cantidad, precio_unit, subtotal
        """
        with conexion() as conn:
            cursor = conn.cursor()

            # Datos principales de la venta y cliente
            cursor.execute(
                """
                SELECT v.id_ventas, v.numero_factura, v.fecha, v.hora, v.total, v.monto_recibido, v.vuelto,
                       CASE 
                           WHEN v.cliente_id IS NULL THEN 'VENTA RÁPIDA'
                           ELSE COALESCE(c.nombres || ' ' || c.apellidos, 'Sin nombre')
                       END AS cliente
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                WHERE v.id_ventas = ?
            """,
                (id_ventas,),
            )
            venta = cursor.fetchone()
            if not venta:
                return {}

            (
                id_ventas,
                numero_factura,
                fecha,
                hora,
                total,
                monto_recibido,
                vuelto,
                cliente,
            ) = venta

            # Productos de la venta
            cursor.execute(
                """
                SELECT i.producto, dv.cantidad, dv.precio_unitario, dv.subtotal
                FROM detalle_venta dv
                JOIN inventario i ON dv.id_producto = i.id_producto
                WHERE dv.id_ventas = ?
                ORDER BY dv.id_detalle
            """,
                (id_ventas,),
            )
            productos = cursor.fetchall()

            lista_productos = []
            for prod in productos:
                lista_productos.append(
                    {
                        "producto": prod[0],
                        "cantidad": prod[1],
                        "precio_unit": prod[2],
                        "subtotal": prod[3],
                    }
                )

            return {
                "id_ventas": id_ventas,
                "numero_factura": numero_factura,
                "fecha": fecha,
                "hora": hora,
                "total": total,
                "monto_recibido": monto_recibido,
                "vuelto": vuelto,
                "cliente": cliente,
                "productos": lista_productos,
            }
