"""Operaciones para el módulo de papelera (ventas y deudas eliminadas)."""

from __future__ import annotations

import datetime
import logging
from typing import Any, Optional

from retail.nucleo.base_datos.conexion import conexion

registrador = logging.getLogger(__name__)


def mover_venta_a_papelera(id_ventas: int, usuario_elimino: str, detalle_motivo: Optional[str] = None) -> bool:
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto FROM ventas WHERE id_ventas = ?",
                (id_ventas,),
            )
            venta = cursor.fetchone()
            if not venta:
                return False

            numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto = venta

            cursor.execute(
                "SELECT id_producto, cantidad FROM detalle_venta WHERE id_ventas = ?",
                (id_ventas,),
            )
            detalles = cursor.fetchall()
            detalles_text = (
                ", ".join([f"Producto ID {p} x{c}" for p, c in detalles])
                if detalles
                else ""
            )

            for id_producto, cantidad in detalles:
                cursor.execute(
                    "UPDATE inventario SET stock = stock + ? WHERE id_producto = ?",
                    (cantidad, id_producto),
                )

            fecha_elim = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                INSERT INTO papelera_ventas
                (id_ventas, numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia,
                 monto_recibido, vuelto, usuario_elimino, fecha_eliminacion, detalle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (id_ventas, numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto, usuario_elimino, fecha_elim, detalle_motivo or detalles_text),
            )

            cursor.execute("DELETE FROM detalle_venta WHERE id_ventas = ?", (id_ventas,))
            cursor.execute("DELETE FROM ventas WHERE id_ventas = ?", (id_ventas,))

            return True
    except Exception:
        registrador.exception("Error al mover venta a papelera")
        return False


def mover_deuda_a_papelera(id_deuda: int, usuario_elimino: str, detalle_motivo: Optional[str] = None) -> bool:
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT numero_factura, cliente_id, fecha, total, saldo, estado FROM deudas WHERE id_deuda = ?",
                (id_deuda,),
            )
            deuda = cursor.fetchone()
            if not deuda:
                return False

            numero_factura, cliente_id, fecha, total, saldo, estado = deuda

            cursor.execute(
                "SELECT i.producto, hd.cantidad FROM historial_deudas hd JOIN inventario i ON hd.id_producto = i.id_producto WHERE hd.id_deuda = ? AND UPPER(hd.accion) != 'ABONO'",
                (id_deuda,),
            )
            detalles = cursor.fetchall()
            detalles_text = (
                ", ".join([f"{row[0]} x{row[1]}" for row in detalles]) if detalles else ""
            )

            fecha_elim = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                "INSERT INTO papelera_deudas (id_deuda, numero_factura, cliente_id, fecha, total, saldo, estado, usuario_elimino, fecha_eliminacion, detalle) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id_deuda, numero_factura, cliente_id, fecha, total, saldo, estado, usuario_elimino, fecha_elim, detalle_motivo or detalles_text),
            )

            cursor.execute("DELETE FROM historial_deudas WHERE id_deuda = ?", (id_deuda,))
            cursor.execute("DELETE FROM detalle_deuda WHERE id_deuda = ?", (id_deuda,))
            cursor.execute("DELETE FROM deudas WHERE id_deuda = ?", (id_deuda,))

            return True
    except Exception:
        registrador.exception("Error al mover deuda a papelera")
        return False


def obtener_papelera_ventas() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_papelera, id_ventas, numero_factura, cliente_rapido, fecha, hora, total, usuario_elimino, fecha_eliminacion, detalle FROM papelera_ventas ORDER BY id_papelera DESC"
        )
        return cursor.fetchall()


def obtener_papelera_deudas() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha, total, saldo, usuario_elimino, fecha_eliminacion, detalle FROM papelera_deudas ORDER BY id_papelera DESC"
        )
        return cursor.fetchall()


def eliminar_venta(id_ventas: int, usuario_elimino: str, motivo: Optional[str] = None) -> bool:
    return mover_venta_a_papelera(id_ventas, usuario_elimino, detalle_motivo=motivo)


def eliminar_deuda(id_deuda: int, usuario_elimino: str, motivo: Optional[str] = None) -> bool:
    return mover_deuda_a_papelera(id_deuda, usuario_elimino, detalle_motivo=motivo)


# Alias para compatibilidad con código que usaba nombres anteriores
obtener_ventas_papelera = obtener_papelera_ventas
obtener_deudas_papelera = obtener_papelera_deudas
