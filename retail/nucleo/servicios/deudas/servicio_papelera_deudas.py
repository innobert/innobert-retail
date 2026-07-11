"""
servicio_papelera_deudas.py

Servicio para gestionar la papelera de deudas:
- Contar registros eliminados (con filtro por número de factura)
- Obtener página de registros
- Limpiar automáticamente registros antiguos (más de 30 días)
- Obtener totales (suma de totales de deudas eliminadas)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from retail.nucleo.base_datos import get_connection


class ServicioPapeleraDeudas:
    """Servicio para operaciones de la papelera de deudas."""

    @staticmethod
    def contar_papelera(filtro_factura: str = "") -> int:
        """Devuelve el número total de registros en la papelera que coinciden con el filtro."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_factura:
            cursor.execute(
                "SELECT COUNT(*) FROM papelera_deudas WHERE numero_factura LIKE ?",
                (f"%{filtro_factura}%",)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM papelera_deudas")
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
                SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha,
                       total, saldo, usuario_elimino, fecha_eliminacion, detalle
                FROM papelera_deudas
                WHERE numero_factura LIKE ?
                ORDER BY fecha_eliminacion DESC
                LIMIT ? OFFSET ?
                """,
                (f"%{filtro_factura}%", limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha,
                       total, saldo, usuario_elimino, fecha_eliminacion, detalle
                FROM papelera_deudas
                ORDER BY fecha_eliminacion DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
        rows = cursor.fetchall()
        conn.close()

        registros = []
        for row in rows:
            # Obtener nombre del cliente si es posible (aunque cliente_id puede ser válido)
            cliente_nombre = "Cliente eliminado"
            if row[3]:  # cliente_id
                try:
                    conn2 = get_connection()
                    cursor2 = conn2.cursor()
                    cursor2.execute(
                        "SELECT nombres || ' ' || apellidos FROM clientes WHERE id_cliente = ?",
                        (row[3],)
                    )
                    res = cursor2.fetchone()
                    if res:
                        cliente_nombre = res[0]
                    conn2.close()
                except Exception:
                    pass
            registros.append({
                "id_papelera": row[0],
                "id_deuda": row[1],
                "numero_factura": row[2],
                "cliente_id": row[3],
                "cliente": cliente_nombre,
                "fecha": row[4],
                "total": float(row[5]) if row[5] else 0.0,
                "saldo": float(row[6]) if row[6] else 0.0,
                "usuario_elimino": row[7],
                "fecha_eliminacion": row[8],
                "detalle": row[9] if row[9] else "",
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
                "DELETE FROM papelera_deudas WHERE fecha_eliminacion <= ?",
                (fecha_limite,)
            )
            eliminados = cursor.rowcount
            conn.commit()
            return eliminados
        except Exception as e:
            conn.rollback()
            logging.error(f"Error limpiando papelera de deudas: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def obtener_total_eliminado(filtro_factura: str = "") -> float:
        """Suma el total de todas las deudas eliminadas que coinciden con el filtro."""
        conn = get_connection()
        cursor = conn.cursor()
        if filtro_factura:
            cursor.execute(
                "SELECT SUM(total) FROM papelera_deudas WHERE numero_factura LIKE ?",
                (f"%{filtro_factura}%",)
            )
        else:
            cursor.execute("SELECT SUM(total) FROM papelera_deudas")
        resultado = cursor.fetchone()
        conn.close()
        return float(resultado[0]) if resultado and resultado[0] else 0.0