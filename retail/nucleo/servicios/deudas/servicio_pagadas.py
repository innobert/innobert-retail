"""
servicio_pagadas.py

Servicio para gestionar las deudas pagadas:
- Contar deudas pagadas (con filtro opcional)
- Obtener página de deudas pagadas
- Calcular total pagado (con filtro)
- Obtener clientes únicos (con filtro)
- Obtener detalles para PDF
"""

from typing import List, Dict, Any, Tuple
from retail.nucleo.base_datos import get_connection


class ServicioPagadas:
    """Servicio para operaciones de deudas pagadas."""

    @staticmethod
    def contar_pagadas(filtro_cliente: str = "") -> int:
        """Cuenta las deudas con estado 'PAGADA' que coinciden con el filtro de cliente."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_cliente:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                WHERE d.estado = 'PAGADA'
                  AND (c.nombres || ' ' || c.apellidos) LIKE ?
                """,
                (f"%{filtro_cliente}%",)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM deudas WHERE estado = 'PAGADA'")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def obtener_pagina(offset: int, limit: int, filtro_cliente: str = "") -> List[Dict[str, Any]]:
        """Retorna una página de deudas pagadas como lista de diccionarios."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_cliente:
            cursor.execute(
                """
                SELECT d.id_deuda,
                    d.numero_factura,
                    c.nombres || ' ' || c.apellidos AS cliente,
                    GROUP_CONCAT(i.producto || ' x' || dd.cantidad, ', ') AS productos,
                    d.fecha,
                    d.total,
                    d.saldo
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                LEFT JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                LEFT JOIN inventario i ON dd.id_producto = i.id_producto
                WHERE d.estado = 'PAGADA'
                AND (c.nombres || ' ' || c.apellidos) LIKE ?
                GROUP BY d.id_deuda
                ORDER BY d.id_deuda DESC
                LIMIT ? OFFSET ?
                """,
                (f"%{filtro_cliente}%", limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT d.id_deuda,
                       d.numero_factura,
                       c.nombres || ' ' || c.apellidos AS cliente,
                       GROUP_CONCAT(i.producto || ' x' || dd.cantidad, ', ') AS productos,
                       d.fecha,
                       d.total,
                       d.saldo
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                LEFT JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                LEFT JOIN inventario i ON dd.id_producto = i.id_producto
                WHERE d.estado = 'PAGADA'
                GROUP BY d.id_deuda
                ORDER BY d.id_deuda DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
        rows = cursor.fetchall()
        conn.close()

        pagadas = []
        for row in rows:
            id_deuda, num_factura, cliente, productos, fecha, total, saldo = row
            saldo_pagado = float(total) - float(saldo) if saldo is not None else float(total)
            pagadas.append({
                "id_deuda": id_deuda,
                "numero_factura": num_factura,
                "cliente": cliente,
                "productos": productos if productos else "Sin productos",
                "fecha": fecha,
                "total": float(total),
                "saldo_pagado": saldo_pagado
            })
        return pagadas

    @staticmethod
    def calcular_total_pagado(filtro_cliente: str = "") -> float:
        """Suma el monto pagado de todas las deudas pagadas que coinciden con el filtro."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_cliente:
            cursor.execute(
                """
                SELECT SUM(d.total - d.saldo)
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                WHERE d.estado = 'PAGADA'
                  AND (c.nombres || ' ' || c.apellidos) LIKE ?
                """,
                (f"%{filtro_cliente}%",)
            )
        else:
            cursor.execute("SELECT SUM(total - saldo) FROM deudas WHERE estado = 'PAGADA'")
        resultado = cursor.fetchone()
        conn.close()
        return float(resultado[0]) if resultado and resultado[0] else 0.0

    @staticmethod
    def obtener_lista_clientes(filtro_cliente: str = "") -> List[str]:
        """Retorna lista de nombres de clientes con deudas pagadas, opcionalmente filtrados."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_cliente:
            cursor.execute(
                """
                SELECT DISTINCT c.nombres || ' ' || c.apellidos
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                WHERE d.estado = 'PAGADA'
                  AND (c.nombres || ' ' || c.apellidos) LIKE ?
                ORDER BY c.nombres
                """,
                (f"%{filtro_cliente}%",)
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT c.nombres || ' ' || c.apellidos
                FROM deudas d
                INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                WHERE d.estado = 'PAGADA'
                ORDER BY c.nombres
                """
            )
        clientes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return clientes

    @staticmethod
    def obtener_detalles_para_pdf(id_deuda: int) -> Tuple[List[tuple], str]:
        """Obtiene los detalles de productos y el nombre del cliente para generar el PDF."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_producto, COALESCE(i.producto, 'ABONO') as producto,
                   h.cantidad, h.subtotal
            FROM historial_deudas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            WHERE h.id_deuda = ? AND UPPER(h.accion) IN ('DEUDA',  'EDITADO', 'ABONO')
            ORDER BY h.id_historial
            """,
            (id_deuda,)
        )
        productos_detalle = cursor.fetchall()
        cursor.execute(
            """
            SELECT c.nombres || ' ' || c.apellidos
            FROM deudas d
            JOIN clientes c ON d.cliente_id = c.id_cliente
            WHERE d.id_deuda = ?
            """,
            (id_deuda,)
        )
        cliente_row = cursor.fetchone()
        cliente = cliente_row[0] if cliente_row else "Desconocido"
        conn.close()
        return productos_detalle, cliente
