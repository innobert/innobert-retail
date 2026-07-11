"""
servicio_edicion_deudas.py

Servicio para gestionar la edición de deudas:
- Obtener detalles de deuda
- Obtener información de deuda (total, saldo)
- Guardar cambios (actualizar cantidades, agregar/eliminar productos, actualizar stock e historial)
- Paginación de inventario para agregar productos (incluyendo la columna imagen)
- Soporte para transacciones compartidas para mantener consistencia durante edición
"""

from typing import List, Dict, Any, Tuple
import datetime
from retail.nucleo.base_datos import obtener_conexion, registrar_historial_deuda, mover_deuda_a_papelera


class ServicioEdicionDeudas:
    """Servicio para operaciones de edición de deudas."""

    @staticmethod
    def obtener_detalles_deuda(id_deuda: int, conn=None) -> List[Dict[str, Any]]:
        """Devuelve lista de detalles de la deuda (incluyendo id_producto, precios, cantidades)."""
        close_conn = False
        if conn is None:
            conn = obtener_conexion()
            close_conn = True
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dd.id_detalle, dd.id_producto, i.producto, dd.precio_unitario, dd.cantidad, dd.subtotal
            FROM detalle_deuda dd
            JOIN inventario i ON dd.id_producto = i.id_producto
            WHERE dd.id_deuda = ?
            ORDER BY dd.id_detalle
        """, (id_deuda,))
        rows = cursor.fetchall()
        if close_conn:
            conn.close()
        detalles = []
        for row in rows:
            detalles.append({
                "id_detalle": row[0],
                "id_producto": row[1],
                "producto": row[2],
                "precio_unit": row[3],
                "cantidad": row[4],
                "subtotal": row[5],
            })
        return detalles

    @staticmethod
    def obtener_info_deuda(id_deuda: int, conn=None) -> Tuple[float, float]:
        """Retorna (total, saldo) de la deuda."""
        close_conn = False
        try:
            if conn is None:
                conn = obtener_conexion()
                close_conn = True
            cursor = conn.cursor()
            cursor.execute("SELECT total, saldo FROM deudas WHERE id_deuda = ?", (id_deuda,))
            row = cursor.fetchone()
            total = float(row[0]) if row and row[0] else 0.0
            saldo = float(row[1]) if row and row[1] else 0.0
            return total, saldo
        except Exception:
            return 0.0, 0.0
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def eliminar_producto_deuda(id_detalle: int, usuario: str, conn=None, cursor=None) -> None:
        """
        Elimina un producto del detalle de la deuda.
        Restaura el stock en inventario y registra en historial.
        """
        close_conn = False
        if cursor is None:
            if conn is None:
                conn = obtener_conexion()
                close_conn = True
            cursor = conn.cursor()
        elif conn is None:
            conn = cursor.connection
        try:
            # Obtener información del detalle
            cursor.execute("""
                SELECT id_deuda, id_producto, cantidad, subtotal
                FROM detalle_deuda WHERE id_detalle = ?
            """, (id_detalle,))
            detalle = cursor.fetchone()
            if not detalle:
                raise ValueError("Detalle no encontrado")
            id_deuda, id_producto, cantidad, subtotal = detalle

            # Restaurar stock
            cursor.execute(
                "UPDATE inventario SET stock = stock + ? WHERE id_producto = ?",
                (cantidad, id_producto)
            )

            # Eliminar el detalle
            cursor.execute("DELETE FROM detalle_deuda WHERE id_detalle = ?", (id_detalle,))

            # Recalcular total y saldo de la deuda
            cursor.execute("SELECT SUM(subtotal) FROM detalle_deuda WHERE id_deuda = ?", (id_deuda,))
            nuevo_total = cursor.fetchone()[0] or 0.0
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM pagos_deuda WHERE id_deuda = ?", (id_deuda,))
            total_pagado = cursor.fetchone()[0] or 0.0
            nuevo_saldo = max(0.0, nuevo_total - total_pagado)
            nuevo_estado = "PAGADA" if nuevo_saldo == 0 else "ABIERTA"
            cursor.execute(
                "UPDATE deudas SET total = ?, saldo = ?, estado = ? WHERE id_deuda = ?",
                (nuevo_total, nuevo_saldo, nuevo_estado, id_deuda)
            )

            # Registrar en historial
            registrar_historial_deuda(
                id_deuda=id_deuda,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=subtotal,
                accion="ELIMINADO",
                usuario=usuario,
                detalle=f"Producto eliminado de la deuda (cantidad {cantidad})",
                cursor=cursor,
            )

            if close_conn:
                conn.commit()
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def editar_cantidad_detalle(id_detalle: int, nueva_cantidad: int, usuario: str, conn=None, cursor=None) -> None:
        """
        Edita la cantidad de un producto en el detalle de deuda.
        Actualiza stock, subtotal, total y saldo de la deuda.
        """
        close_conn = False
        if cursor is None:
            if conn is None:
                conn = obtener_conexion()
                close_conn = True
            cursor = conn.cursor()
        elif conn is None:
            conn = cursor.connection
        try:
            # Obtener datos actuales
            cursor.execute("""
                SELECT dd.id_deuda, dd.id_producto, dd.cantidad, dd.subtotal, i.stock, i.precio
                FROM detalle_deuda dd
                JOIN inventario i ON dd.id_producto = i.id_producto
                WHERE dd.id_detalle = ?
            """, (id_detalle,))
            detalle = cursor.fetchone()
            if not detalle:
                raise ValueError("Detalle no encontrado")
            id_deuda, id_producto, cantidad_antigua, subtotal_antiguo, stock_actual, precio_unit = detalle

            diferencia = nueva_cantidad - cantidad_antigua
            nuevo_subtotal = nueva_cantidad * precio_unit

            # Validar stock
            if diferencia > 0 and diferencia > stock_actual:
                raise ValueError("Stock insuficiente para aumentar la cantidad")

            # Actualizar stock (si aumenta, restamos; si disminuye, sumamos)
            if diferencia != 0:
                cursor.execute(
                    "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                    (diferencia, id_producto)
                )

            # Actualizar detalle
            cursor.execute(
                "UPDATE detalle_deuda SET cantidad = ?, subtotal = ? WHERE id_detalle = ?",
                (nueva_cantidad, nuevo_subtotal, id_detalle)
            )

            # Recalcular total de la deuda
            cursor.execute("SELECT SUM(subtotal) FROM detalle_deuda WHERE id_deuda = ?", (id_deuda,))
            nuevo_total = cursor.fetchone()[0] or 0.0
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM pagos_deuda WHERE id_deuda = ?", (id_deuda,))
            total_pagado = cursor.fetchone()[0] or 0.0
            nuevo_saldo = max(0.0, nuevo_total - total_pagado)
            nuevo_estado = "PAGADA" if nuevo_saldo == 0 else "ABIERTA"
            cursor.execute(
                "UPDATE deudas SET total = ?, saldo = ?, estado = ? WHERE id_deuda = ?",
                (nuevo_total, nuevo_saldo, nuevo_estado, id_deuda)
            )

            # Registrar en historial
            registrar_historial_deuda(
                id_deuda=id_deuda,
                id_producto=id_producto,
                cantidad=nueva_cantidad,
                subtotal=nuevo_subtotal,
                accion="EDITADO",
                usuario=usuario,
                detalle=f"Cantidad modificada de {cantidad_antigua} a {nueva_cantidad}",
                cursor=cursor,
            )

            if close_conn:
                conn.commit()
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def agregar_producto_a_deuda(id_deuda: int, id_producto: int, cantidad: int, usuario: str, conn=None, cursor=None) -> None:
        """
        Agrega un nuevo producto a la deuda.
        Actualiza stock, inserta detalle, y recalcula total/saldo.
        """
        close_conn = False
        if cursor is None:
            if conn is None:
                conn = obtener_conexion()
                close_conn = True
            cursor = conn.cursor()
        elif conn is None:
            conn = cursor.connection
        try:
            # Obtener precio y stock actual del producto
            cursor.execute(
                "SELECT precio, stock, producto FROM inventario WHERE id_producto = ?",
                (id_producto,)
            )
            prod = cursor.fetchone()
            if not prod:
                raise ValueError("Producto no encontrado")
            precio_unit, stock_actual, nombre_producto = prod

            if cantidad > stock_actual:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual}")

            # Restar stock
            cursor.execute(
                "UPDATE inventario SET stock = stock - ? WHERE id_producto = ?",
                (cantidad, id_producto)
            )

            # Insertar en detalle_deuda
            subtotal = precio_unit * cantidad
            cursor.execute("""
                INSERT INTO detalle_deuda (id_deuda, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_deuda, id_producto, cantidad, precio_unit, subtotal))

            # Recalcular total y saldo de la deuda
            cursor.execute("SELECT SUM(subtotal) FROM detalle_deuda WHERE id_deuda = ?", (id_deuda,))
            nuevo_total = cursor.fetchone()[0] or 0.0
            cursor.execute("SELECT COALESCE(SUM(monto), 0) FROM pagos_deuda WHERE id_deuda = ?", (id_deuda,))
            total_pagado = cursor.fetchone()[0] or 0.0
            nuevo_saldo = max(0.0, nuevo_total - total_pagado)
            nuevo_estado = "PAGADA" if nuevo_saldo == 0 else "ABIERTA"
            cursor.execute(
                "UPDATE deudas SET total = ?, saldo = ?, estado = ? WHERE id_deuda = ?",
                (nuevo_total, nuevo_saldo, nuevo_estado, id_deuda)
            )

            # Registrar en historial
            registrar_historial_deuda(
                id_deuda=id_deuda,
                id_producto=id_producto,
                cantidad=cantidad,
                subtotal=subtotal,
                accion="AGREGADO",
                usuario=usuario,
                detalle=f"Producto agregado: {nombre_producto} x{cantidad} = ${subtotal:,.0f}",
                cursor=cursor,
            )

            if close_conn:
                conn.commit()
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    # ----------------------------------------------------------------------
    # Métodos para paginación de inventario (para la ventana de agregar productos)
    # ----------------------------------------------------------------------
    @staticmethod
    def obtener_productos_paginado(filtro: str = "", offset: int = 0, limit: int = 12) -> List[Dict[str, Any]]:
        """Retorna lista de productos activos que coinciden con el filtro, incluyendo la imagen."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            SELECT id_producto, producto, precio, stock, imagen
            FROM inventario
            WHERE estado = 1
        """
        params = []
        if filtro:
            query += " AND producto LIKE ?"
            params.append(f"%{filtro}%")
        query += " ORDER BY producto ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        productos = []
        for row in rows:
            productos.append({
                "id_producto": row[0],
                "producto": row[1],
                "precio": row[2],
                "stock": row[3],
                "imagen": row[4] if row[4] else "default.png",
            })
        return productos

    @staticmethod
    def contar_productos_con_filtro(filtro: str = "") -> int:
        """Total de productos activos que coinciden con el filtro."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM inventario WHERE estado = 1"
        params = []
        if filtro:
            query += " AND producto LIKE ?"
            params.append(f"%{filtro}%")
        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        conn.close()
        return total