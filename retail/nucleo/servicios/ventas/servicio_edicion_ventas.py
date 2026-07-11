"""
servicio_edicion_ventas.py

Servicio para gestionar la edición de facturas de ventas:
- Obtener detalles de factura
- Obtener información de factura (total, monto recibido, vuelto)
- Guardar cambios (actualizar cantidades, agregar/eliminar productos, actualizar stock e historial)
- Paginación de inventario para agregar productos (incluyendo imagen)
- **NUEVO**: Si una venta se queda sin productos durante la edición, se mueve automáticamente a la papelera
  con timestamp exacto, lanzando una excepción personalizada para notificar a la capa de vista.

VALIDACIONES ADICIONALES:
- Al editar cantidad, se verifica que el nuevo total no supere el monto recibido.
- Al agregar producto, se verifica que el nuevo total no supere el monto recibido.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional, Tuple
from contextlib import nullcontext
import datetime
from retail.nucleo.base_datos import conexion, registrar_historial_venta

logger = logging.getLogger(__name__)


class VentaVaciaError(Exception):
    """
    Excepción lanzada cuando, después de eliminar un producto, la venta queda sin ningún detalle
    y es movida automáticamente a la papelera.
    """

    pass


class ServicioEdicionVentas:
    """Servicio para operaciones de edición de facturas."""

    @staticmethod
    def obtener_detalles_factura(id_ventas: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Devuelve lista de detalles de la factura (incluyendo id_producto).
        Si se proporciona una conexión, la reutiliza; de lo contrario, crea una nueva.
        """
        ctx = conexion() if conn is None else nullcontext(conn)
        with ctx as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT dv.id_detalle, dv.id_producto, i.producto, dv.precio_unitario, dv.cantidad, dv.subtotal
                FROM detalle_venta dv
                JOIN inventario i ON dv.id_producto = i.id_producto
                WHERE dv.id_ventas = ?
                ORDER BY dv.id_detalle
            """,
                (id_ventas,),
            )
            rows = cursor.fetchall()
        return [
            {
                "id_detalle": row[0],
                "id_producto": row[1],
                "producto": row[2],
                "precio_unit": row[3],
                "cantidad": row[4],
                "subtotal": row[5],
            }
            for row in rows
        ]

    @staticmethod
    def obtener_info_factura(id_ventas: int, conn: Optional[Any] = None) -> Tuple[float, float, float]:
        """
        Retorna (total, monto_recibido, vuelto) de la factura.
        """
        try:
            ctx = conexion() if conn is None else nullcontext(conn)
            with ctx as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT total, monto_recibido, vuelto FROM ventas WHERE id_ventas = ?",
                    (id_ventas,),
                )
                row = cursor.fetchone()
                if not row:
                    return 0.0, 0.0, 0.0
                return float(row[0]), float(row[1]), float(row[2])
        except Exception:
            return 0.0, 0.0, 0.0

    @staticmethod
    def eliminar_detalle_venta(
        id_detalle: int, usuario: str, monto_recibido: float, conn: Optional[Any] = None, cursor: Optional[Any] = None
    ) -> Optional[str]:
        """
        Elimina un detalle de venta, restaura stock, actualiza total y vuelto.
        Si después de la eliminación la venta queda sin productos, la mueve a la papelera
        y lanza una excepción VentaVaciaError.
        """
        ctx = conexion() if conn is None and cursor is None else nullcontext(conn)
        with ctx as conn:
            assert conn is not None
            if cursor is None:
                cursor = conn.cursor()
            elif conn is None:
                conn = cursor.connection

            # 1. Obtener datos del detalle
            cursor.execute(
                """
                SELECT id_ventas, id_producto, cantidad, subtotal
                FROM detalle_venta WHERE id_detalle = ?
            """,
                (id_detalle,),
            )
            detalle = cursor.fetchone()
            if not detalle:
                raise ValueError("Detalle no encontrado")
            id_ventas, id_producto, cantidad, subtotal = detalle

            # 2. Restaurar stock
            cursor.execute(
                "UPDATE inventario SET stock = stock + ? WHERE id_producto = ?",
                (cantidad, id_producto),
            )

            # 3. Eliminar el detalle
            cursor.execute(
                "DELETE FROM detalle_venta WHERE id_detalle = ?", (id_detalle,)
            )

            # 4. Recalcular total y vuelto
            cursor.execute(
                "SELECT SUM(subtotal) FROM detalle_venta WHERE id_ventas = ?",
                (id_ventas,),
            )
            nuevo_total = cursor.fetchone()[0] or 0.0
            nuevo_vuelto = monto_recibido - nuevo_total
            cursor.execute(
                "UPDATE ventas SET total = ?, vuelto = ? WHERE id_ventas = ?",
                (nuevo_total, nuevo_vuelto, id_ventas),
            )

            # 5. Registrar en historial
            registrar_historial_venta(
                id_ventas=id_ventas,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=subtotal,
                accion="ELIMINADO",
                usuario=usuario,
                detalle=f"Producto eliminado de la venta (cantidad {cantidad})",
                cursor=cursor,
                monto_recibido=monto_recibido,
                vuelto=nuevo_vuelto,
            )

            # 6. Verificar si la venta quedó sin productos
            #    Si se movió a la papelera, devolvemos el timestamp para que la UI cierre.
            trashed_timestamp = ServicioEdicionVentas._mover_a_papelera_si_vacia(
                id_ventas, usuario, conn=conn, cursor=cursor
            )
            return trashed_timestamp

    @staticmethod
    def _mover_a_papelera_si_vacia(
        id_ventas: int, usuario: str, conn: Optional[Any] = None, cursor: Optional[Any] = None
    ) -> Optional[str]:
        """
        Verifica si la venta tiene detalles. Si no tiene ninguno, la mueve a la papelera
        con timestamp exacto (fecha y hora) del momento de verificación.
        Retorna el timestamp si se movió a papelera, o None en caso contrario.
        """
        ctx = conexion() if conn is None and cursor is None else nullcontext(conn)
        with ctx as conn:
            assert conn is not None
            if cursor is None:
                cursor = conn.cursor()
            elif conn is None:
                conn = cursor.connection

            cursor.execute(
                "SELECT COUNT(*) FROM detalle_venta WHERE id_ventas = ?", (id_ventas,)
            )
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    "SELECT numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto "
                    "FROM ventas WHERE id_ventas = ?",
                    (id_ventas,),
                )
                venta = cursor.fetchone()
                if not venta:
                    logger.warning("Venta con id %s no encontrada", id_ventas)
                    return None
                (
                    numero_factura,
                    cliente_id,
                    cliente_rapido,
                    fecha,
                    hora,
                    total,
                    ganancia,
                    monto_recibido,
                    vuelto,
                ) = venta

                ahora = datetime.datetime.now()
                timestamp_str = ahora.strftime("%Y-%m-%d %H:%M:%S")
                motivo = f"Venta vaciada durante edición - Último producto eliminado a las {ahora.strftime('%H:%M:%S')}"

                cursor.execute(
                    "INSERT INTO papelera_ventas "
                    "(id_ventas, numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, "
                    "monto_recibido, vuelto, usuario_elimino, fecha_eliminacion, detalle) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        id_ventas,
                        numero_factura,
                        cliente_id,
                        cliente_rapido,
                        fecha,
                        hora,
                        total,
                        ganancia,
                        monto_recibido,
                        vuelto,
                        usuario,
                        timestamp_str,
                        motivo,
                    ),
                )
                cursor.execute(
                    "DELETE FROM detalle_venta WHERE id_ventas = ?", (id_ventas,)
                )
                cursor.execute("DELETE FROM ventas WHERE id_ventas = ?", (id_ventas,))
                return timestamp_str
            logger.warning("Venta con id %s no encontrada", id_ventas)
            return None

    @staticmethod
    def editar_cantidad_detalle(
        id_detalle: int,
        nueva_cantidad: int,
        usuario: str,
        monto_recibido: float,
        conn: Optional[Any] = None,
        cursor: Optional[Any] = None,
    ) -> None:
        """
        Edita la cantidad de un producto en la venta, actualiza stock, total y vuelto.
        Valida que el nuevo total no supere el monto recibido.
        """
        ctx = conexion() if conn is None and cursor is None else nullcontext(conn)
        with ctx as conn:
            assert conn is not None
            if cursor is None:
                cursor = conn.cursor()
            elif conn is None:
                conn = cursor.connection

            # Obtener datos actuales
            cursor.execute(
                """
                SELECT dv.id_ventas, dv.id_producto, dv.cantidad, dv.subtotal, i.stock, i.precio
                FROM detalle_venta dv
                JOIN inventario i ON dv.id_producto = i.id_producto
                WHERE dv.id_detalle = ?
            """,
                (id_detalle,),
            )
            detalle = cursor.fetchone()
            if not detalle:
                raise ValueError("Detalle no encontrado")
            (
                id_ventas,
                id_producto,
                cant_antigua,
                sub_antiguo,
                stock_actual,
                precio_unit,
            ) = detalle

            diferencia = nueva_cantidad - cant_antigua
            nuevo_subtotal = nueva_cantidad * precio_unit

            # Validar stock si se aumenta
            if diferencia > 0 and diferencia > stock_actual:
                raise ValueError("Stock insuficiente para aumentar la cantidad")

            # Validar que el nuevo total no supere el monto recibido
            cursor.execute(
                "SELECT SUM(subtotal) FROM detalle_venta WHERE id_ventas = ?",
                (id_ventas,),
            )
            total_actual = cursor.fetchone()[0] or 0.0
            nuevo_total = total_actual - sub_antiguo + nuevo_subtotal
            if nuevo_total > monto_recibido:
                raise ValueError(
                    f"El nuevo total (${nuevo_total:,.0f}) supera el monto recibido (${monto_recibido:,.0f})."
                )

            # Actualizar stock
            if diferencia != 0:
                cursor.execute(
                    "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                    (diferencia, id_producto),
                )

            # Actualizar detalle
            cursor.execute(
                "UPDATE detalle_venta SET cantidad = ?, subtotal = ? WHERE id_detalle = ?",
                (nueva_cantidad, nuevo_subtotal, id_detalle),
            )

            # Recalcular total y vuelto
            cursor.execute(
                "SELECT SUM(subtotal) FROM detalle_venta WHERE id_ventas = ?",
                (id_ventas,),
            )
            nuevo_total_db = cursor.fetchone()[0] or 0.0
            nuevo_vuelto = monto_recibido - nuevo_total_db
            cursor.execute(
                "UPDATE ventas SET total = ?, vuelto = ? WHERE id_ventas = ?",
                (nuevo_total_db, nuevo_vuelto, id_ventas),
            )

            # Registrar historial
            registrar_historial_venta(
                id_ventas=id_ventas,
                id_producto=id_producto,
                cantidad=nueva_cantidad,
                subtotal=nuevo_subtotal,
                accion="EDITADO",
                usuario=usuario,
                detalle=f"Cantidad modificada de {cant_antigua} a {nueva_cantidad}",
                cursor=cursor,
                monto_recibido=monto_recibido,
                vuelto=nuevo_vuelto,
            )

    @staticmethod
    def agregar_producto_a_venta(
        id_ventas: int,
        id_producto: int,
        cantidad: int,
        usuario: str,
        monto_recibido: float,
        conn: Optional[Any] = None,
        cursor: Optional[Any] = None,
    ) -> None:
        """
        Agrega un producto a la venta, actualiza stock, total y vuelto.
        Valida que el nuevo total no supere el monto recibido.
        """
        ctx = conexion() if conn is None and cursor is None else nullcontext(conn)
        with ctx as conn:
            assert conn is not None
            if cursor is None:
                cursor = conn.cursor()
            elif conn is None:
                conn = cursor.connection

            cursor.execute(
                "SELECT precio, stock, producto FROM inventario WHERE id_producto = ?",
                (id_producto,),
            )
            prod = cursor.fetchone()
            if not prod:
                raise ValueError("Producto no encontrado")
            precio_unit, stock_actual, nombre = prod
            if cantidad > stock_actual:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual}")

            subtotal = precio_unit * cantidad

            # Validar que el nuevo total no supere el monto recibido
            cursor.execute(
                "SELECT SUM(subtotal) FROM detalle_venta WHERE id_ventas = ?",
                (id_ventas,),
            )
            total_actual = cursor.fetchone()[0] or 0.0
            nuevo_total = total_actual + subtotal
            if nuevo_total > monto_recibido:
                raise ValueError(
                    f"El nuevo total (${nuevo_total:,.0f}) supera el monto recibido (${monto_recibido:,.0f})."
                )

            # Actualizar stock
            cursor.execute(
                "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                (cantidad, id_producto),
            )

            # Insertar detalle
            cursor.execute(
                """
                INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """,
                (id_ventas, id_producto, cantidad, precio_unit, subtotal),
            )

            # Recalcular total y vuelto
            nuevo_total_db = total_actual + subtotal
            nuevo_vuelto = monto_recibido - nuevo_total_db
            cursor.execute(
                "UPDATE ventas SET total = ?, vuelto = ? WHERE id_ventas = ?",
                (nuevo_total_db, nuevo_vuelto, id_ventas),
            )

            # Registrar historial
            registrar_historial_venta(
                id_ventas=id_ventas,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=subtotal,
                accion="AGREGADO",
                usuario=usuario,
                detalle=f"Producto agregado: {nombre} x{cantidad} = ${subtotal:,.0f}",
                cursor=cursor,
                monto_recibido=monto_recibido,
                vuelto=nuevo_vuelto,
            )

    # ----------------------------------------------------------------------
    # Métodos auxiliares para paginación de inventario (sin cambios)
    # ----------------------------------------------------------------------
    @staticmethod
    def obtener_productos_paginado(
        filtro: str = "", offset: int = 0, limit: int = 12, conn: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Retorna lista de productos activos que coinciden con el filtro, incluyendo la imagen."""
        ctx = conexion() if conn is None else nullcontext(conn)
        with ctx as conn:
            cursor = conn.cursor()
            query = """
                SELECT id_producto, producto, precio, stock, imagen
                FROM inventario
                WHERE estado = 1
            """
            params: list[Any] = []
            if filtro:
                query += " AND producto LIKE ?"
                params.append(f"%{filtro}%")
            query += " ORDER BY producto ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [
            {
                "id_producto": row[0],
                "producto": row[1],
                "precio": row[2],
                "stock": row[3],
                "imagen": row[4] if row[4] else "default.png",
            }
            for row in rows
        ]

    @staticmethod
    def contar_productos_con_filtro(filtro: str = "", conn: Optional[Any] = None) -> Any:
        """Total de productos activos que coinciden con el filtro."""
        ctx = conexion() if conn is None else nullcontext(conn)
        with ctx as conn:
            cursor = conn.cursor()
            query = "SELECT COUNT(*) FROM inventario WHERE estado = 1"
            params = []
            if filtro:
                query += " AND producto LIKE ?"
                params.append(f"%{filtro}%")
            cursor.execute(query, params)
            total = cursor.fetchone()[0]
        return total
