"""Operaciones CRUD para la tabla de ventas y detalle_venta."""

from __future__ import annotations

import datetime
import logging
import random
from typing import Any, Optional

from retail.nucleo.base_datos.conexion import conexion
from retail.nucleo.base_datos.historiales import registrar_historial_venta

registrador = logging.getLogger(__name__)


def insertar_venta(
    numero_factura: str,
    cliente_id: int,
    cliente_rapido: str,
    total: float,
    ganancia: float,
    monto_recibido: float,
    vuelto: float,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.execute(
            "INSERT INTO ventas (numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto),
        )


def insertar_detalle_venta(
    id_venta: int, id_producto: int, cantidad: int, precio_unitario: float, subtotal: float
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (id_venta, id_producto, cantidad, precio_unitario, subtotal),
        )


def obtener_detalle_venta(id_venta: int) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dv.*, i.producto FROM detalle_venta dv JOIN inventario i ON dv.id_producto = i.id_producto WHERE dv.id_ventas = ?",
            (id_venta,),
        )
        return cursor.fetchall()


def obtener_todas_ventas() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas ORDER BY id_ventas DESC")
        return cursor.fetchall()


def obtener_ventas_por_cliente(
    cliente_id: int, fecha_inicio: str, fecha_fin: str
) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ventas WHERE cliente_id = ? AND fecha BETWEEN ? AND ?",
            (cliente_id, fecha_inicio, fecha_fin),
        )
        return cursor.fetchall()


def obtener_ventas_rango_fechas(
    inicio: str, fin: str
) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ventas WHERE fecha BETWEEN ? AND ? ORDER BY id_ventas DESC",
            (inicio, fin),
        )
        return cursor.fetchall()


def obtener_ultima_venta() -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas ORDER BY id_ventas DESC LIMIT 1")
        return cursor.fetchone()


def obtener_ventas_por_numero_factura(numero_factura: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM ventas WHERE numero_factura LIKE ?",
            (f"%{numero_factura}%",),
        )
        return cursor.fetchall()


def obtener_ventas_por_id(id_ventas: int) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ventas WHERE id_ventas = ?", (id_ventas,))
        return cursor.fetchone()


def generar_numero_factura() -> str:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ventas")
        cantidad = cursor.fetchone()[0] + 1
    return f"FAC-{datetime.datetime.now().strftime('%Y%m%d')}-{cantidad:05d}"


def generar_numero_factura_unico(cursor: Any) -> str:
    max_intentos = 1000
    for _ in range(max_intentos):
        numero = f"{random.randint(100000, 999999)}"
        cursor.execute(
            "SELECT COUNT(*) FROM ventas WHERE numero_factura = ?", (numero,)
        )
        if cursor.fetchone()[0] > 0:
            continue
        cursor.execute(
            "SELECT COUNT(*) FROM papelera_ventas WHERE numero_factura = ?", (numero,)
        )
        if cursor.fetchone()[0] > 0:
            continue
        return numero
    return f"{random.randint(100000, 999999)}"


def generar_id_venta_rapida(cursor: Any) -> str:
    fecha_db = datetime.datetime.now().strftime("%Y-%m-%d")
    fecha_id = datetime.datetime.now().strftime("%Y%m%d")
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM ventas
        WHERE fecha = ?
          AND cliente_id IS NULL
          AND cliente_rapido LIKE ?
    """,
        (fecha_db, f"VR-{fecha_id}-%"),
    )
    count = cursor.fetchone()[0] + 1
    return f"VR-{fecha_id}-{count:03d}"


def crear_venta(
    cliente_id: Optional[int] = None,
    items: Optional[list[dict[str, Any]]] = None,
    monto_recibido: float = 0,
    usuario: str = "sistema",
) -> dict[str, Any]:
    if not items or len(items) == 0:
        raise ValueError("No hay items para crear la venta")

    with conexion() as conn:
        cursor = conn.cursor()

        numero_factura = generar_numero_factura_unico(cursor)

        total = 0.0
        total_ganancia = 0.0
        item_rows: list[dict[str, Any]] = []
        for it in items:
            pid = int(it["id_producto"])
            cant = int(it.get("cantidad", 0))
            if cant <= 0:
                raise ValueError(f"Cantidad inválida para producto {pid}")
            cursor.execute(
                "SELECT producto, precio, costo, stock FROM inventario WHERE id_producto = ?",
                (pid,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Producto ID {pid} no existe")
            nombre, precio_db, costo_db, stock_db = row
            if cant > stock_db:
                raise ValueError(
                    f"Stock insuficiente para {nombre}: {stock_db} disponibles, se solicita {cant}"
                )
            precio_unit = float(it.get("precio", precio_db))
            subtotal = precio_unit * cant
            ganancia = (precio_unit - costo_db) * cant
            total += subtotal
            total_ganancia += ganancia
            item_rows.append({
                "id_producto": pid,
                "cantidad": cant,
                "precio_unit": precio_unit,
                "subtotal": subtotal,
            })

        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")

        cliente_rapido = None
        if cliente_id is None:
            cliente_rapido = generar_id_venta_rapida(cursor)

        if float(monto_recibido) < total:
            raise ValueError("Monto recibido insuficiente para esta venta")

        vuelto_calculado = float(monto_recibido) - total
        cursor.execute(
            "INSERT INTO ventas (numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                numero_factura,
                cliente_id,
                cliente_rapido,
                fecha,
                hora,
                total,
                total_ganancia,
                float(monto_recibido),
                vuelto_calculado,
            ),
        )
        id_ventas = cursor.lastrowid
        if id_ventas is None:
            raise RuntimeError("No se pudo obtener ID de venta")

        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            cursor.execute(
                "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_ventas, pid, cant, precio_unit, subtotal),
            )
            cursor.execute(
                "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                (cant, pid),
            )
            accion = "X MAYOR" if cliente_id else "VENTA"
            registrar_historial_venta(
                id_ventas=id_ventas,
                id_producto=pid,
                cantidad=cant,
                subtotal=subtotal,
                accion=accion,
                usuario=usuario,
                detalle=f"Venta ID {id_ventas}",
                cursor=cursor,
                monto_recibido=monto_recibido,
                vuelto=vuelto_calculado,
            )

        return {"id_ventas": id_ventas, "total": total, "vuelto": vuelto_calculado}
