"""Operaciones CRUD para la tabla de inventario y helpers de paginación."""

from __future__ import annotations

import datetime
import logging
from typing import Any

from retail.nucleo.base_datos.conexion import conexion
from retail.nucleo.base_datos.indices import producto_a_dict

registrador = logging.getLogger(__name__)


def agregar_producto(
    producto: str,
    precio: float,
    costo: float,
    stock: int,
    estado: int,
    imagen: str,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventario (producto, precio, costo, stock, estado, imagen) VALUES (?, ?, ?, ?, ?, ?)",
            (producto, precio, costo, stock, estado, imagen),
        )


def obtener_productos() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario")
        return cursor.fetchall()


def actualizar_producto(
    id_producto: int,
    producto: str,
    precio: float,
    costo: float,
    stock: int,
    estado: int,
    imagen: str,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inventario SET producto = ?, precio = ?, costo = ?, stock = ?, estado = ?, imagen = ? WHERE id_producto = ?",
            (producto, precio, costo, stock, estado, imagen, id_producto),
        )


def eliminar_producto(id_producto: int) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventario WHERE id_producto = ?", (id_producto,))


def registrar_historial_inventario(
    id_producto: int,
    accion: str,
    pedido: int,
    stock: int,
    precio: float,
    costo: float,
    ganancia: float,
    total: float,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        dia = datetime.datetime.now().strftime("%A")
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.execute(
            "INSERT INTO historial_inventario (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total),
        )


def combobox_productos() -> list[str]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT producto FROM inventario")
        return [row[0] for row in cursor.fetchall()]


def editar_producto(id_producto: int) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventario WHERE id_producto = ?", (id_producto,))
        return cursor.fetchone()


def buscar_productos_por_nombre(nombre: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM inventario WHERE producto LIKE ?",
            (f"%{nombre}%",),
        )
        return cursor.fetchall()


# ── Paginación ──────────────────────────────────────────────────────────


def paginar_productos(
    offset: int, limit: int, filtro: str = ""
) -> list[dict[str, Any]]:
    with conexion() as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT * FROM inventario WHERE producto LIKE ? ORDER BY id_producto LIMIT ? OFFSET ?",
                (f"%{filtro}%", limit, offset),
            )
        else:
            cursor.execute(
                "SELECT * FROM inventario ORDER BY id_producto LIMIT ? OFFSET ?",
                (limit, offset),
            )
        return [producto_a_dict(r) for r in cursor.fetchall()]


def contar_productos(filtro: str = "") -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT COUNT(*) FROM inventario WHERE producto LIKE ?",
                (f"%{filtro}%",),
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM inventario")
        return cursor.fetchone()[0]


def obtener_nombres_productos(filtro: str = "") -> list[str]:
    with conexion() as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT producto FROM inventario WHERE producto LIKE ? ORDER BY producto",
                (f"%{filtro}%",),
            )
        else:
            cursor.execute("SELECT producto FROM inventario ORDER BY producto")
        return [row[0] for row in cursor.fetchall()]


def obtener_totales_globales_ganancias() -> tuple[float, float]:
    total_ventas = 0.0
    total_ganancia = 0.0
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(i.precio * dv.cantidad),
                   SUM((i.precio - i.costo) * dv.cantidad)
            FROM ventas v
            JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
            JOIN inventario i ON dv.id_producto = i.id_producto
        """)
        venta = cursor.fetchone()
        if venta and venta[0]:
            total_ventas += venta[0]
            total_ganancia += venta[1]
        cursor.execute("""
            SELECT SUM(dd.precio_unitario * dd.cantidad),
                   SUM((dd.precio_unitario - i.costo) * dd.cantidad)
            FROM pagos_deuda p
            JOIN deudas d ON p.id_deuda = d.id_deuda
            JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
            JOIN inventario i ON dd.id_producto = i.id_producto
            WHERE d.estado = 'PAGADA'
        """)
        deuda = cursor.fetchone()
        if deuda and deuda[0]:
            total_ventas += deuda[0]
            total_ganancia += deuda[1]
    return total_ganancia, total_ventas
