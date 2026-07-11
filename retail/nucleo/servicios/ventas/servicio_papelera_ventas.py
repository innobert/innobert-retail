"""
servicio_papelera_ventas.py

Servicio para gestionar la papelera de ventas:
- Contar registros eliminados (con filtro por número de factura)
- Obtener página de registros
- Limpiar registros antiguos (más de 30 días)
- Obtener totales (opcional)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from retail.nucleo.base_datos import get_connection


class ServicioPapeleraVentas:
    """Servicio para operaciones de la papelera de ventas."""

    @staticmethod
    def contar_papelera(filtro_factura: str = "") -> int:
        """Devuelve el número total de registros en la papelera que coinciden con el filtro."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_factura:
            cursor.execute(
                "SELECT COUNT(*) FROM papelera_ventas WHERE numero_factura LIKE ?",
                (f"%{filtro_factura}%",)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM papelera_ventas")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def obtener_pagina(offset: int, limit: int, filtro_factura: str = "") -> List[Dict[str, Any]]:
        """Retorna una página de registros de la papelera como lista de diccionarios."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_factura:
            cursor.execute(
                """
                SELECT p.id_papelera, p.id_ventas, p.numero_factura,
                       p.cliente_rapido, p.cliente_id,
                       p.fecha, p.hora, p.total, p.usuario_elimino, p.fecha_eliminacion,
                       c.nombres, c.apellidos
                FROM papelera_ventas p
                LEFT JOIN clientes c ON p.cliente_id = c.id_cliente
                WHERE p.numero_factura LIKE ?
                ORDER BY p.fecha_eliminacion DESC
                LIMIT ? OFFSET ?
                """,
                (f"%{filtro_factura}%", limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT p.id_papelera, p.id_ventas, p.numero_factura,
                       p.cliente_rapido, p.cliente_id,
                       p.fecha, p.hora, p.total, p.usuario_elimino, p.fecha_eliminacion,
                       c.nombres, c.apellidos
                FROM papelera_ventas p
                LEFT JOIN clientes c ON p.cliente_id = c.id_cliente
                ORDER BY p.fecha_eliminacion DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
        rows = cursor.fetchall()
        conn.close()

        registros = []
        for row in rows:
            id_papelera, id_ventas, numero_factura, cliente_rapido, cliente_id, \
            fecha_venta, hora_venta, total, usuario_elimino, fecha_eliminacion, \
            nombres, apellidos = row

            if cliente_rapido:
                cliente = cliente_rapido
            else:
                cliente = f"{nombres} {apellidos}" if nombres else "Cliente desconocido"

            registros.append({
                "id_papelera": id_papelera,
                "id_ventas": id_ventas,
                "numero_factura": numero_factura,
                "cliente": cliente,
                "fecha_venta": fecha_venta,
                "hora_venta": hora_venta,
                "total": float(total) if total else 0.0,
                "usuario_elimino": usuario_elimino,
                "fecha_eliminacion": fecha_eliminacion,
            })
        return registros

    @staticmethod
    def limpiar_registros_antiguos(dias: int = 30) -> int:
        """
        Elimina permanentemente los registros de papelera con más de 'dias' días de antigüedad.
        Retorna el número de registros eliminados.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
            cursor.execute(
                "DELETE FROM papelera_ventas WHERE fecha_eliminacion <= ?",
                (fecha_limite,)
            )
            eliminados = cursor.rowcount
            conn.commit()
            return eliminados
        except Exception as e:
            conn.rollback()
            logging.error(f"Error limpiando papelera de ventas: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def obtener_total_eliminado(filtro_factura: str = "") -> float:
        """Suma el total de todas las ventas eliminadas que coinciden con el filtro."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_factura:
            cursor.execute(
                "SELECT SUM(total) FROM papelera_ventas WHERE numero_factura LIKE ?",
                (f"%{filtro_factura}%",)
            )
        else:
            cursor.execute("SELECT SUM(total) FROM papelera_ventas")
        resultado = cursor.fetchone()
        conn.close()
        return float(resultado[0]) if resultado and resultado[0] else 0.0