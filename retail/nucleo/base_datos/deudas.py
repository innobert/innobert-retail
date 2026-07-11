"""Operaciones CRUD para la tabla de deudas, detalle_deuda y pagos_deuda."""

from __future__ import annotations

import datetime
import logging
import random
from typing import Any, Optional

from retail.nucleo.base_datos.conexion import conexion
from retail.nucleo.base_datos.historiales import registrar_historial_deuda

registrador = logging.getLogger(__name__)


def insertar_deuda(
    numero_factura: str,
    cliente_id: int,
    total: float,
    saldo: float,
    usuario_creacion: str,
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO deudas (numero_factura, cliente_id, fecha, total, saldo, usuario_creacion) VALUES (?, ?, ?, ?, ?, ?)",
            (numero_factura, cliente_id, fecha, total, saldo, usuario_creacion),
        )


def insertar_detalle_deuda(
    id_deuda: int, id_producto: int, cantidad: int, precio_unitario: float, subtotal: float
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO detalle_deuda (id_deuda, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (id_deuda, id_producto, cantidad, precio_unitario, subtotal),
        )


def obtener_deudas() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deudas ORDER BY id_deuda DESC")
        return cursor.fetchall()


def obtener_deudas_abiertas() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deudas WHERE estado='ABIERTA' ORDER BY id_deuda DESC")
        return cursor.fetchall()


def obtener_deudas_por_cliente(cliente_id: int) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM deudas WHERE cliente_id=? ORDER BY id_deuda DESC",
            (cliente_id,),
        )
        return cursor.fetchall()


def obtener_deudas_rango_fechas(inicio: str, fin: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM deudas WHERE fecha BETWEEN ? AND ? ORDER BY id_deuda DESC",
            (inicio, fin),
        )
        return cursor.fetchall()


def obtener_deuda_por_id(id_deuda: int) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deudas WHERE id_deuda=?", (id_deuda,))
        return cursor.fetchone()


def obtener_deudas_por_numero_factura(numero_factura: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM deudas WHERE numero_factura LIKE ?",
            (f"%{numero_factura}%",),
        )
        return cursor.fetchall()


def obtener_detalle_deuda(id_deuda: int) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dd.*, i.producto FROM detalle_deuda dd JOIN inventario i ON dd.id_producto = i.id_producto WHERE dd.id_deuda=?",
            (id_deuda,),
        )
        return cursor.fetchall()


def registrar_pago(
    id_deuda: int, monto: float, usuario: str
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.execute(
            "INSERT INTO pagos_deuda (id_deuda, monto, fecha, hora, usuario) VALUES (?, ?, ?, ?, ?)",
            (id_deuda, monto, fecha, hora, usuario),
        )
        cursor.execute(
            "UPDATE deudas SET saldo = saldo - ? WHERE id_deuda = ?",
            (monto, id_deuda),
        )
        cursor.execute(
            "UPDATE deudas SET estado = 'PAGADA' WHERE id_deuda = ? AND saldo <= 0",
            (id_deuda,),
        )


def actualizar_saldo_deuda(id_deuda: int, nuevo_saldo: float) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE deudas SET saldo=? WHERE id_deuda=?", (nuevo_saldo, id_deuda)
        )


def sumatoria_deudas(cliente_id: int) -> tuple[float, float]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(total), 0), COALESCE(SUM(saldo), 0) FROM deudas WHERE cliente_id = ?",
            (cliente_id,),
        )
        return cursor.fetchone()


def generar_numero_factura_unico_deuda(cursor: Any) -> str:
    max_intentos = 1000
    for _ in range(max_intentos):
        numero = f"{random.randint(100000, 999999)}"
        cursor.execute(
            "SELECT COUNT(*) FROM deudas WHERE numero_factura = ?", (numero,)
        )
        if cursor.fetchone()[0] > 0:
            continue
        cursor.execute(
            "SELECT COUNT(*) FROM papelera_deudas WHERE numero_factura = ?", (numero,)
        )
        if cursor.fetchone()[0] > 0:
            continue
        return numero
    return f"{random.randint(100000, 999999)}"


def crear_deuda(
    cliente_id: int,
    items: Optional[list[dict[str, Any]]] = None,
    usuario: str = "sistema",
) -> dict[str, Any]:
    if not cliente_id:
        raise ValueError("Cliente es obligatorio para crear una deuda")
    if not items or len(items) == 0:
        raise ValueError("No hay items para crear la deuda")

    with conexion() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_cliente FROM clientes WHERE id_cliente = ?", (cliente_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Cliente ID {cliente_id} no existe")

        total = 0.0
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
            _, precio_db, _, _ = row
            precio_unit = float(it.get("precio", precio_db))
            subtotal = precio_unit * cant
            total += subtotal
            item_rows.append({
                "id_producto": pid,
                "cantidad": cant,
                "precio_unit": precio_unit,
                "subtotal": subtotal,
            })

        numero_factura = generar_numero_factura_unico_deuda(cursor)

        cursor.execute(
            "INSERT INTO deudas (numero_factura, cliente_id, fecha, total, saldo, usuario_creacion) VALUES (?, ?, ?, ?, ?, ?)",
            (numero_factura, cliente_id, datetime.datetime.now().strftime("%Y-%m-%d"), total, total, usuario),
        )
        id_deuda = cursor.lastrowid
        if id_deuda is None:
            raise RuntimeError("No se pudo obtener ID de deuda")

        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            cursor.execute(
                "INSERT INTO detalle_deuda (id_deuda, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_deuda, pid, cant, precio_unit, subtotal),
            )

        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            registrar_historial_deuda(
                id_deuda=id_deuda,
                id_producto=pid,
                cantidad=cant,
                subtotal=subtotal,
                accion="DEUDA",
                usuario=usuario,
                detalle=f"Deuda ID {id_deuda} - Producto agregado",
                cursor=cursor,
                abono=0,
            )

        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            cursor.execute(
                "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                (cant, pid),
            )

        return {
            "id_deuda": id_deuda,
            "total": total,
            "saldo": total,
            "numero_factura": numero_factura,
        }


def obtener_historial_deudas_por_deuda(id_deuda: int) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
            FROM historial_deudas h
            LEFT JOIN inventario i ON h.id_producto = i.id_producto
            WHERE h.id_deuda = ?
            ORDER BY h.fecha DESC, h.hora DESC
            """,
            (id_deuda,),
        )
        return cursor.fetchall()


def obtener_historial_deudas(nombre_cliente: str) -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
            FROM historial_deudas h
            JOIN inventario i ON h.id_producto = i.id_producto
            LEFT JOIN deudas d ON h.id_deuda = d.id_deuda
            LEFT JOIN clientes c ON d.cliente_id = c.id_cliente
            WHERE (c.nombres || ' ' || c.apellidos = ? OR d.cliente_rapido = ?)
            ORDER BY h.fecha DESC, h.hora DESC
            """,
            (nombre_cliente, nombre_cliente),
        )
        return cursor.fetchall()



