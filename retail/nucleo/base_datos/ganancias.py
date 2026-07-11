"""Operaciones para la tabla de ganancias."""

from __future__ import annotations

import datetime
import logging
from typing import Any

from retail.nucleo.base_datos.conexion import conexion

registrador = logging.getLogger(__name__)


def insertar_ganancia(
    fecha: str,
    total_dia: float = 0,
    total_semana: float = 0,
    total_mes: float = 0,
    total_anio: float = 0,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO ganancias (fecha, total_dia, total_semana, total_mes, total_anio) VALUES (?, ?, ?, ?, ?)",
            (fecha, total_dia, total_semana, total_mes, total_anio),
        )


def obtener_ganancias_rango_fechas(inicio: str, fin: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ganancias WHERE fecha BETWEEN ? AND ? ORDER BY fecha ASC",
            (inicio, fin),
        )
        return cursor.fetchall()


def obtener_ganancia_por_fecha(fecha: str) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ganancias WHERE fecha = ?", (fecha,)
        )
        return cursor.fetchone()


def actualizar_cuentas() -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, SUM(total)
            FROM ventas
            GROUP BY fecha
            ORDER BY fecha DESC
        """)
        ventas_por_dia = cursor.fetchall()
        for fecha, total_dia in ventas_por_dia:
            fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
            semana_inicio = (
                fecha_dt - datetime.timedelta(days=fecha_dt.weekday())
            ).strftime("%Y-%m-%d")
            semana_fin = (
                fecha_dt + datetime.timedelta(days=6 - fecha_dt.weekday())
            ).strftime("%Y-%m-%d")
            anio_inicio = fecha_dt.replace(month=1, day=1).strftime("%Y-%m-%d")
            anio_fin = fecha_dt.replace(month=12, day=31).strftime("%Y-%m-%d")
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN fecha BETWEEN ? AND ? THEN total ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN strftime('%Y-%m', fecha) = strftime('%Y-%m', ?) THEN total ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN fecha BETWEEN ? AND ? THEN total ELSE 0 END), 0)
                FROM ventas
            """,
                (semana_inicio, semana_fin, fecha, anio_inicio, anio_fin),
            )
            total_semana, total_mes, total_anio = cursor.fetchone()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ganancias (fecha, total_dia, total_semana, total_mes, total_anio)
                VALUES (?, ?, ?, ?, ?)
            """,
                (fecha, total_dia, total_semana, total_mes, total_anio),
            )


def calcular_ganancia_dia(fecha: str) -> float:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(ganancia), 0) FROM ventas WHERE fecha = ?",
            (fecha,),
        )
        venta = cursor.fetchone()[0]
        cursor.execute("""
            SELECT COALESCE(SUM((dd.precio_unitario - i.costo) * dd.cantidad), 0)
            FROM pagos_deuda p
            JOIN deudas d ON p.id_deuda = d.id_deuda
            JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
            JOIN inventario i ON dd.id_producto = i.id_producto
            WHERE d.estado = 'PAGADA' AND p.fecha = ?
        """, (fecha,))
        deuda = cursor.fetchone()[0]
        return venta + deuda
