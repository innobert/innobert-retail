"""
servicio_facturas_ventas.py

Servicio que encapsula la lógica de negocio y acceso a datos para las facturas de ventas.
"""

from __future__ import annotations

from typing import List, Dict, Any
from retail.nucleo.base_datos import conexion, eliminar_venta


class ServicioFacturasVentas:
    """Servicio para operaciones relacionadas con facturas de ventas."""

    @staticmethod
    def contar_facturas(filtro: str = "") -> Any:
        """Retorna el número total de facturas que coinciden con el filtro."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro:
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM (
                        SELECT v.id_ventas
                        FROM ventas v
                        LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                        JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                        JOIN inventario i ON dv.id_producto = i.id_producto
                        WHERE v.numero_factura LIKE ?
                        GROUP BY v.id_ventas
                    )
                """,
                    (f"%{filtro}%",),
                )
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM (
                        SELECT v.id_ventas
                        FROM ventas v
                        LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                        JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                        JOIN inventario i ON dv.id_producto = i.id_producto
                        GROUP BY v.id_ventas
                    )
                """)
            count = cursor.fetchone()[0]
        return count

    @staticmethod
    def obtener_pagina_facturas(
        offset: int, limit: int, filtro: str = ""
    ) -> List[Dict[str, Any]]:
        """Devuelve una lista de facturas (como diccionarios) para la página solicitada."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro:
                cursor.execute(
                    """
                    SELECT v.id_ventas,
                           v.numero_factura,
                           CASE 
                               WHEN v.cliente_id IS NULL THEN 'VENTA RÁPIDA'
                               ELSE COALESCE(c.nombres || ' ' || c.apellidos, 'Sin nombre')
                           END AS nombre_cliente,
                           GROUP_CONCAT(i.producto || ' x' || dv.cantidad, ', ') AS productos,
                           v.monto_recibido, v.vuelto, v.total, v.hora, v.fecha,
                           COALESCE(c.zona, 'Local') AS zona
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                    JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                    JOIN inventario i ON dv.id_producto = i.id_producto
                    WHERE v.numero_factura LIKE ?
                    GROUP BY v.id_ventas
                    ORDER BY v.id_ventas ASC
                    LIMIT ? OFFSET ?
                """,
                    (f"%{filtro}%", limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT v.id_ventas,
                           v.numero_factura,
                           CASE 
                               WHEN v.cliente_id IS NULL THEN 'VENTA RÁPIDA'
                               ELSE COALESCE(c.nombres || ' ' || c.apellidos, 'Sin nombre')
                           END AS nombre_cliente,
                           GROUP_CONCAT(i.producto || ' x' || dv.cantidad, ', ') AS productos,
                           v.monto_recibido, v.vuelto, v.total, v.hora, v.fecha,
                           COALESCE(c.zona, 'Local') AS zona
                    FROM ventas v
                    LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                    JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                    JOIN inventario i ON dv.id_producto = i.id_producto
                    GROUP BY v.id_ventas
                    ORDER BY v.id_ventas ASC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )
            rows = cursor.fetchall()

        facturas = []
        for row in rows:
            facturas.append(
                {
                    "id_ventas": row[0],
                    "numero_factura": row[1],
                    "cliente_nombre": row[2],
                    "productos": row[3] if row[3] else "Sin productos",
                    "monto_recibido": row[4] if row[4] is not None else 0,
                    "vuelto": row[5] if row[5] is not None else 0,
                    "total": row[6],
                    "hora": row[7],
                    "fecha": row[8],
                    "zona": row[9] if row[9] else "Local",
                }
            )
        return facturas

    @staticmethod
    def calcular_total_ventas(filtro: str = "") -> float:
        """Suma el total de las ventas que coinciden con el filtro."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro:
                cursor.execute(
                    "SELECT SUM(total) FROM ventas WHERE numero_factura LIKE ?",
                    (f"%{filtro}%",),
                )
            else:
                cursor.execute("SELECT SUM(total) FROM ventas")
            resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] else 0.0

    @staticmethod
    def eliminar_factura(id_ventas: int, usuario_elimino: str) -> bool:
        """Mueve la factura a la papelera (usa la función base)."""
        return eliminar_venta(id_ventas, usuario_elimino)

    @staticmethod
    def obtener_detalles_para_pdf(id_ventas: int) -> Dict[str, Any]:
        """Retorna la información necesaria para generar el PDF de una factura."""
        with conexion() as conn:
            cursor = conn.cursor()
            # Detalle de productos
            cursor.execute(
                """
                SELECT i.producto, dv.cantidad, dv.subtotal, v.hora, v.fecha, v.numero_factura
                FROM detalle_venta dv
                JOIN inventario i ON dv.id_producto = i.id_producto
                JOIN ventas v ON dv.id_ventas = v.id_ventas
                WHERE dv.id_ventas = ?
            """,
                (id_ventas,),
            )
            productos = cursor.fetchall()
            # Nombre del cliente
            cursor.execute(
                """
                SELECT CASE 
                        WHEN v.cliente_id IS NULL THEN 'VENTA RÁPIDA'
                        ELSE COALESCE(c.nombres || ' ' || c.apellidos, 'Sin nombre')
                       END AS nombre_cliente
                FROM ventas v
                LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                WHERE v.id_ventas = ?
            """,
                (id_ventas,),
            )
            cliente_row = cursor.fetchone()
            cliente = cliente_row[0] if cliente_row else "Desconocido"
        return {
            "productos": productos,
            "cliente": cliente,
        }

    @staticmethod
    def obtener_lista_numeros_factura(filtro: str = "") -> List[str]:
        """Devuelve los números de factura únicos que coinciden con el filtro."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro:
                cursor.execute(
                    "SELECT DISTINCT numero_factura FROM ventas WHERE numero_factura LIKE ? ORDER BY numero_factura",
                    (f"%{filtro}%",),
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT numero_factura FROM ventas ORDER BY numero_factura"
                )
            numeros = [row[0] for row in cursor.fetchall() if row[0] is not None]
        return numeros
