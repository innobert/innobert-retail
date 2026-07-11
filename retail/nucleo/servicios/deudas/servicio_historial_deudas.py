"""
servicio_historial_deudas.py

Servicio para obtener el historial de deudas (por deuda específica o por cliente).
"""
from typing import List, Dict, Any
import datetime
from retail.nucleo.base_datos import get_connection


class ServicioHistorialDeudas:
    """Servicio para operaciones de historial de deudas."""

    @staticmethod
    def obtener_por_deuda(id_deuda: int) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de una deuda específica.
        Retorna lista de diccionarios con las claves:
        id_historial, producto, fecha, hora, cantidad, subtotal, accion,
        abono, recibido, vuelto, dia_semana, saldo_acumulado (calculado).
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, h.id_producto, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal,
                   h.accion, h.abono, h.recibido, h.vuelto
            FROM historial_deudas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            WHERE h.id_deuda = ?
            ORDER BY h.fecha ASC, h.hora ASC
            """,
            (id_deuda,)
        )
        rows = cursor.fetchall()
        conn.close()
        return ServicioHistorialDeudas._procesar_filas(rows, id_deuda)

    @staticmethod
    def obtener_nombre_cliente_por_deuda(id_deuda: int) -> str:
        """
        Devuelve el nombre completo del cliente asociado a una deuda.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.nombres || ' ' || c.apellidos FROM deudas d JOIN clientes c ON d.cliente_id = c.id_cliente WHERE d.id_deuda = ?",
            (id_deuda,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else "Cliente desconocido"

    @staticmethod
    def obtener_numero_factura_por_deuda(id_deuda: int) -> str:
        """
        Devuelve el número de factura asociado a una deuda.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT numero_factura FROM deudas WHERE id_deuda = ?",
            (id_deuda,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else "N/A"

    @staticmethod
    def obtener_por_cliente(nombre_cliente: str, id_cliente: int = None) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de deudas para un cliente (por nombre o id).
        """
        conn = get_connection()
        cursor = conn.cursor()
        if id_cliente is not None:
            cursor.execute(
                """
                SELECT h.id_historial, h.id_producto, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal,
                       h.accion, h.abono, h.recibido, h.vuelto, d.id_deuda
                FROM historial_deudas h
                LEFT JOIN inventario i ON h.id_producto = i.id_producto
                JOIN deudas d ON h.id_deuda = d.id_deuda
                WHERE d.cliente_id = ?
                ORDER BY h.fecha ASC, h.hora ASC
                """,
                (id_cliente,)
            )
        else:
            cursor.execute(
                """
                SELECT h.id_historial, h.id_producto, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal,
                       h.accion, h.abono, h.recibido, h.vuelto, d.id_deuda
                FROM historial_deudas h
                LEFT JOIN inventario i ON h.id_producto = i.id_producto
                JOIN deudas d ON h.id_deuda = d.id_deuda
                WHERE d.cliente_rapido = ?
                ORDER BY h.fecha ASC, h.hora ASC
                """,
                (nombre_cliente,)
            )
        rows = cursor.fetchall()
        conn.close()
        return ServicioHistorialDeudas._procesar_filas(rows, None)

    @staticmethod
    def _procesar_filas(rows, id_deuda_fijo=None) -> List[Dict[str, Any]]:
        """Convierte las filas en diccionarios y calcula saldo acumulado."""
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        saldo_acumulado = 0
        historial = []
        producto_subtotales = {}
        total_abonos = 0
        for idx, row in enumerate(rows, start=1):
            if id_deuda_fijo is not None:
                id_historial, id_producto, producto, fecha, hora, cantidad, subtotal, accion, abono, recibido, vuelto = row
                id_deuda = id_deuda_fijo
            else:
                id_historial, id_producto, producto, fecha, hora, cantidad, subtotal, accion, abono, recibido, vuelto, id_deuda = row

            # Calcular día de la semana
            try:
                fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
                dia_semana = dias[fecha_dt.weekday()]
            except Exception:
                dia_semana = ""

            accion_normalizado = accion.upper().strip() if accion else ""
            if accion_normalizado == 'DEUDA DIRECTA':
                accion_normalizado = 'DEUDA'

            if accion_normalizado == 'ABONO':
                total_abonos += abono if abono else 0
            elif accion_normalizado == 'ELIMINADO':
                if id_producto is not None:
                    producto_subtotales.pop(id_producto, None)
            elif id_producto is not None:
                if accion_normalizado in ('DEUDA', 'AGREGADO'):
                    producto_subtotales[id_producto] = producto_subtotales.get(id_producto, 0) + (subtotal or 0)
                else:
                    producto_subtotales[id_producto] = subtotal or 0

            total_productos = sum(producto_subtotales.values())
            saldo_acumulado = max(0.0, total_productos - total_abonos)

            cantidad_total = cantidad if accion_normalizado not in ('ABONO', 'ELIMINADO') and cantidad else 0

            producto_mostrar = producto if producto is not None else ("ABONO" if accion_normalizado == 'ABONO' else "")
            subtotal_text = ""
            if accion_normalizado not in ('ABONO', 'ELIMINADO') and subtotal is not None:
                subtotal_text = f"${subtotal:,.0f}".replace(",", ".")

            historial.append({
                "idx": idx,
                "id_historial": id_historial,
                "id_deuda": id_deuda,
                "producto": producto_mostrar,
                "fecha": fecha,
                "hora": hora,
                "dia_semana": dia_semana,
                "accion": accion_normalizado,
                "cantidad": str(cantidad) if cantidad is not None else "",
                "subtotal": subtotal_text,
                "abono": f"${abono:,.0f}".replace(",", ".") if abono else "",
                "recibido": f"${recibido:,.0f}".replace(",", ".") if recibido else "",
                "vuelto": f"${vuelto:,.0f}".replace(",", ".") if vuelto else "",
                "saldo": f"${saldo_acumulado:,.0f}".replace(",", "."),
                "cantidad_total": cantidad_total,
                "saldo_numerico": saldo_acumulado
            })
        return historial