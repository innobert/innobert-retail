"""
inventario_service.py

Servicio que encapsula la lógica de negocio para el módulo de Inventario.
Centraliza operaciones CRUD, validaciones de stock, registro de historial,
y actualización de vistas dependientes.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from tkinter import messagebox

from retail.nucleo.base_datos import (
    agregar_producto,
    obtener_productos,
    actualizar_producto,
    eliminar_producto,
    obtener_conexion,
    combobox_productos,
)


def peso_colombiano(value):
    """Formatea un valor a moneda colombiana."""
    return f"${value:,.0f}".replace(",", ".")


class InventarioServicio:
    """
    Servicio para operaciones de inventario.
    """

    @staticmethod
    def obtener_todos_productos() -> List[Dict[str, Any]]:
        """
        Retorna lista de todos los productos como diccionarios.
        """
        productos = obtener_productos()
        return [
            {
                "id_producto": p[0],
                "producto": p[1],
                "precio": p[2],
                "costo": p[3],
                "stock": p[4],
                "estado": p[5],
                "imagen": p[6],
            }
            for p in productos
        ]

    @staticmethod
    def obtener_productos_para_busqueda(termino: str = "") -> List[Dict[str, Any]]:
        """
        Filtra productos por coincidencia parcial en nombre.
        """
        if not termino:
            return InventarioServicio.obtener_todos_productos()
        productos = obtener_productos()
        termino_lower = termino.lower()
        return [
            {
                "id_producto": p[0],
                "producto": p[1],
                "precio": p[2],
                "costo": p[3],
                "stock": p[4],
                "estado": p[5],
                "imagen": p[6],
            }
            for p in productos if termino_lower in p[1].lower()
        ]

    @staticmethod
    def obtener_nombres_productos() -> List[str]:
        """
        Retorna lista de nombres de productos para combobox.
        """
        productos = obtener_productos()
        return [p[1] for p in productos]

    @staticmethod
    def obtener_producto_por_id(id_producto: int) -> Optional[Dict[str, Any]]:
        """
        Retorna un producto por su ID.
        """
        productos = obtener_productos()
        for p in productos:
            if p[0] == id_producto:
                return {
                    "id_producto": p[0],
                    "producto": p[1],
                    "precio": p[2],
                    "costo": p[3],
                    "stock": p[4],
                    "estado": p[5],
                    "imagen": p[6],
                }
        return None

    @staticmethod
    def agregar_producto(
        producto: str,
        precio: int,
        costo: int,
        stock: int,
        imagen: str,
        parent=None
    ) -> Tuple[bool, str]:
        """
        Valida y agrega un nuevo producto.
        Retorna (exito, mensaje).
        """
        if not producto or precio <= 0 or costo <= 0 or stock <= 0:
            return False, "Todos los campos son obligatorios y deben ser positivos."

        # Validación de rentabilidad
        if costo > precio:
            perdida = (costo - precio) * stock
            msg = (f"El costo ({peso_colombiano(costo)}) es mayor que el precio "
                   f"({peso_colombiano(precio)}). Generará una pérdida de {peso_colombiano(perdida)}.\n"
                   "¿Desea continuar?")
            if parent and not messagebox.askyesno("Advertencia", msg, parent=parent):
                return False, "Operación cancelada por el usuario."
        elif precio == costo:
            msg = "El precio y el costo son iguales. No se generará ganancia.\n¿Desea continuar?"
            if parent and not messagebox.askyesno("Advertencia", msg, parent=parent):
                return False, "Operación cancelada por el usuario."

        estado = 1 if stock > 0 else 0
        try:
            agregar_producto(producto, precio, costo, stock, estado, imagen)
            # Registrar historial
            InventarioServicio._registrar_historial_inventario(
                producto, precio, costo, stock, "Agregar", stock
            )
            return True, "Producto agregado correctamente"
        except Exception as e:
            return False, f"Error al agregar producto: {e}"

    @staticmethod
    def actualizar_producto(
        id_producto: int,
        producto: str,
        precio: int,
        costo: int,
        stock: int,
        imagen: str,
        parent=None
    ) -> Tuple[bool, str]:
        """
        Valida y actualiza un producto existente.
        """
        if not producto or precio <= 0 or costo <= 0 or stock <= 0:
            return False, "Todos los campos son obligatorios y deben ser positivos."

        # Obtener datos actuales
        producto_actual = InventarioServicio.obtener_producto_por_id(id_producto)
        if not producto_actual:
            return False, "Producto no encontrado."

        # Validación de rentabilidad
        if costo > precio:
            perdida = (costo - precio) * stock
            msg = (f"El costo ({peso_colombiano(costo)}) es mayor que el precio "
                   f"({peso_colombiano(precio)}). Generará una pérdida de {peso_colombiano(perdida)}.\n"
                   "¿Desea continuar?")
            if parent and not messagebox.askyesno("Advertencia", msg, parent=parent):
                return False, "Operación cancelada por el usuario."
        elif precio == costo:
            msg = "El precio y el costo son iguales. No se generará ganancia.\n¿Desea continuar?"
            if parent and not messagebox.askyesno("Advertencia", msg, parent=parent):
                return False, "Operación cancelada por el usuario."

        estado = 1 if stock > 0 else 0
        try:
            actualizar_producto(id_producto, producto, precio, costo, stock, estado, imagen)
            # Registrar historial solo si hubo cambios
            hay_cambios = (
                producto != producto_actual["producto"] or
                precio != producto_actual["precio"] or
                costo != producto_actual["costo"] or
                stock != producto_actual["stock"]
            )
            if hay_cambios:
                pedido = max(0, stock - producto_actual["stock"]) if stock > producto_actual["stock"] else 0
                InventarioServicio._registrar_historial_inventario(
                    producto, precio, costo, stock, "Editar", pedido
                )
            return True, "Producto actualizado correctamente"
        except Exception as e:
            return False, f"Error al actualizar producto: {e}"

    @staticmethod
    def eliminar_producto(id_producto: int) -> Tuple[bool, str]:
        """
        Elimina un producto.
        """
        try:
            eliminar_producto(id_producto)
            return True, "Producto eliminado correctamente"
        except Exception as e:
            return False, f"Error al eliminar producto: {e}"

    @staticmethod
    def _registrar_historial_inventario(
        producto_nombre: str,
        precio: int,
        costo: int,
        stock: int,
        accion: str,
        pedido: int
    ):
        """
        Registra un evento en el historial de inventario.
        """
        try:
            # Obtener id_producto
            productos = obtener_productos()
            id_producto = None
            for p in productos:
                if p[1] == producto_nombre:
                    id_producto = p[0]
                    break
            if id_producto is None:
                return

            now = datetime.now()
            dia = now.strftime("%A")
            fecha = now.strftime("%Y-%m-%d")
            hora = now.strftime("%H:%M:%S")
            ganancia = (precio - costo) * stock
            total = precio * stock

            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO historial_inventario
                (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error al registrar historial: {e}")

    @staticmethod
    def obtener_nombres_para_combobox() -> List[str]:
        """
        Retorna lista de nombres de productos para el combobox de búsqueda.
        """
        return combobox_productos()
    
    @staticmethod
    def verificar_rentabilidad(precio: float, costo: float, stock: int) -> Optional[Dict[str, Any]]:
        if precio > costo:
            return None
        if precio < costo:
            perdida = (costo - precio) * stock
            return {"tipo": "perdida", "mensaje": f"El producto genera pérdida de {peso_colombiano(perdida)}"}
        return {"tipo": "sin_ganancia", "mensaje": "El producto no genera ganancia (precio = costo)"}

    @staticmethod
    def obtener_producto_por_nombre(nombre: str) -> Optional[Dict[str, Any]]:
        """Retorna el producto con el nombre exacto (case-insensitive)."""
        productos = obtener_productos()
        for p in productos:
            if p[1].lower() == nombre.lower():
                return {
                    "id_producto": p[0],
                    "producto": p[1],
                    "precio": p[2],
                    "costo": p[3],
                    "stock": p[4],
                    "estado": p[5],
                    "imagen": p[6],
                }
        return None

    # ----------------------------------------------------------------------
    # Nuevos métodos para paginación con carga bajo demanda
    # ----------------------------------------------------------------------

    @staticmethod
    def obtener_productos_paginado(
        offset: int,
        limit: int,
        filtro: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Obtiene una página de productos desde la base de datos.
        offset: número de registros a saltar
        limit: cantidad de registros a obtener
        filtro: texto para filtrar por nombre (coincidencia parcial, case-insensitive)
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT * FROM inventario WHERE producto LIKE ? ORDER BY id_producto LIMIT ? OFFSET ?",
                (f"%{filtro}%", limit, offset)
            )
        else:
            cursor.execute(
                "SELECT * FROM inventario ORDER BY id_producto LIMIT ? OFFSET ?",
                (limit, offset)
            )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id_producto": r[0],
                "producto": r[1],
                "precio": r[2],
                "costo": r[3],
                "stock": r[4],
                "estado": r[5],
                "imagen": r[6],
            }
            for r in rows
        ]

    @staticmethod
    def contar_productos(filtro: str = "") -> int:
        """
        Retorna el número total de productos que coinciden con el filtro.
        """
        conn = obtener_conexion()
        cursor = conn.cursor()
        if filtro:
            cursor.execute(
                "SELECT COUNT(*) FROM inventario WHERE producto LIKE ?",
                (f"%{filtro}%",)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM inventario")
        count = cursor.fetchone()[0]
        conn.close()
        return count