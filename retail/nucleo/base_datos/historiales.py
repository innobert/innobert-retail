"""Inserción y consulta en historiales (ventas y deudas)."""

from __future__ import annotations

import datetime
import logging
from typing import Any, Optional

import sqlite3

from retail.nucleo.base_datos.conexion import conexion

registrador = logging.getLogger(__name__)


def registrar_historial_venta(
    id_ventas: int,
    id_producto: int,
    cantidad: int,
    subtotal: float,
    accion: str,
    usuario: str,
    detalle: str,
    cursor: Optional[sqlite3.Cursor] = None,
    monto_recibido: float = 0,
    vuelto: float = 0,
) -> None:
    if cursor is None:
        with conexion() as conn:
            c = conn.cursor()
            _ejecutar_historial_venta(c, id_ventas, id_producto, cantidad, subtotal, accion, usuario, detalle, monto_recibido, vuelto)
    else:
        _ejecutar_historial_venta(cursor, id_ventas, id_producto, cantidad, subtotal, accion, usuario, detalle, monto_recibido, vuelto)


def _ejecutar_historial_venta(
    cursor: sqlite3.Cursor,
    id_ventas: int,
    id_producto: int,
    cantidad: int,
    subtotal: float,
    accion: str,
    usuario: str,
    detalle: str,
    monto_recibido: float,
    vuelto: float,
) -> None:
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    cursor.execute(
        """
        INSERT INTO historial_ventas (id_ventas, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, monto_recibido, vuelto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_ventas, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, monto_recibido, vuelto),
    )


def registrar_historial_deuda(
    id_deuda: int,
    id_producto: int | None,
    cantidad: int,
    subtotal: float,
    accion: str,
    usuario: str,
    detalle: str,
    cursor: Optional[sqlite3.Cursor] = None,
    abono: float = 0,
    recibido: float = 0,
    vuelto: float = 0,
) -> None:
    if cursor is None:
        with conexion() as conn:
            c = conn.cursor()
            _ejecutar_historial_deuda(c, id_deuda, id_producto, cantidad, subtotal, accion, usuario, detalle, abono, recibido, vuelto)
    else:
        _ejecutar_historial_deuda(cursor, id_deuda, id_producto, cantidad, subtotal, accion, usuario, detalle, abono, recibido, vuelto)


def _ejecutar_historial_deuda(
    cursor: sqlite3.Cursor,
    id_deuda: int,
    id_producto: int | None,
    cantidad: int,
    subtotal: float,
    accion: str,
    usuario: str,
    detalle: str,
    abono: float,
    recibido: float,
    vuelto: float,
) -> None:
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    cursor.execute(
        """
        INSERT INTO historial_deudas (id_deuda, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, abono, recibido, vuelto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_deuda, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, abono, recibido, vuelto),
    )


def obtener_historial_ventas(fecha_inicio: str, fecha_fin: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM historial_ventas WHERE fecha BETWEEN ? AND ?",
            (fecha_inicio, fecha_fin),
        )
        return cursor.fetchall()


def obtener_historial_por_venta(id_ventas: int) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
            FROM historial_ventas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            WHERE h.id_ventas = ?
            ORDER BY h.fecha DESC, h.hora DESC
            """,
            (id_ventas,),
        )
        return cursor.fetchall()
