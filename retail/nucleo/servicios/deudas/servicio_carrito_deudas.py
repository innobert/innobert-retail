"""
servicio_carrito_deudas.py

Servicio para gestionar la lógica del carrito de deudas:
- Validación de stock al editar cantidades
- Actualización de cantidades en el carrito
- Eliminación de productos del carrito
- Cálculo de totales por cliente
"""
from typing import List, Dict, Any, Optional, Tuple
from retail.nucleo.servicios.deudas.servicio_deudas import DeudasServicio


class ServicioCarritoDeudas:
    """Servicio para operaciones del carrito de deudas."""

    @staticmethod
    def validar_cantidad_para_edicion(
        carrito: List[Dict[str, Any]],
        id_producto: int,
        nueva_cantidad: int,
        item_actual: Dict[str, Any]
    ) -> Tuple[bool, int, str]:
        """
        Valida si la nueva cantidad es válida considerando stock y otros items del carrito.
        Retorna (válido, stock_disponible, mensaje).
        """
        stock_total = DeudasServicio.obtener_stock_actual(id_producto)
        if stock_total is None:
            return False, 0, "No se pudo obtener el stock del producto."

        # Sumar cantidades del mismo producto en el carrito, excluyendo el item actual
        cantidad_otros = sum(
            item["cantidad"] for item in carrito
            if item["id_producto"] == id_producto and item is not item_actual
        )
        stock_disponible = stock_total - cantidad_otros

        if nueva_cantidad <= 0:
            return False, stock_disponible, "La cantidad debe ser mayor a cero."

        if nueva_cantidad > stock_disponible:
            msg = (f"Stock disponible para este producto: {stock_disponible} unidades.\n"
                   f"Stock total: {stock_total} | Otras cantidades en carrito: {cantidad_otros}")
            return False, stock_disponible, msg

        return True, stock_disponible, ""

    @staticmethod
    def actualizar_cantidad_en_carrito(
        carrito: List[Dict[str, Any]],
        item_index: int,
        nueva_cantidad: int
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Actualiza la cantidad y subtotal de un item en el carrito.
        Retorna (carrito_actualizado, item_actualizado).
        """
        item = carrito[item_index]
        item["cantidad"] = nueva_cantidad
        item["subtotal"] = nueva_cantidad * item["precio"]
        return carrito, item

    @staticmethod
    def eliminar_producto_del_carrito(
        carrito: List[Dict[str, Any]],
        item_index: int
    ) -> List[Dict[str, Any]]:
        """Elimina un producto del carrito por su índice."""
        del carrito[item_index]
        return carrito

    @staticmethod
    def calcular_total_general(carrito: List[Dict[str, Any]]) -> float:
        """Suma todos los subtotales del carrito."""
        return sum(item["subtotal"] for item in carrito)

    @staticmethod
    def agregar_al_carrito(
        carrito: List[Dict[str, Any]],
        producto_data: Dict[str, Any],
        cantidad: int,
        cliente_id: int,
        cliente_nombre: str,
    ) -> Tuple[List[Dict[str, Any]], str, Optional[Dict[str, Any]]]:
        stock = DeudasServicio.obtener_stock_actual(producto_data["id_producto"])
        if stock is None:
            return carrito, "", {"error": "No se pudo obtener el stock"}

        if cantidad > stock:
            return carrito, "", {"error": "Stock insuficiente"}

        for item in carrito:
            if item["id_producto"] == producto_data["id_producto"] and item.get("cliente") == cliente_nombre:
                return carrito, "", {"error": "duplicado"}

        subtotal = cantidad * producto_data["precio"]
        carrito.append({
            "cliente": cliente_nombre,
            "cliente_id": cliente_id,
            "producto": producto_data.get("producto", ""),
            "id_producto": producto_data["id_producto"],
            "cantidad": cantidad,
            "precio": producto_data["precio"],
            "subtotal": subtotal,
        })
        return carrito, "", None

    @staticmethod
    def confirmar_deuda(
        carrito: List[Dict[str, Any]],
        id_cliente: int,
        usuario: str,
    ) -> Dict[str, Any]:
        if not carrito:
            raise ValueError("El carrito está vacío")

        from retail.nucleo.base_datos import crear_deuda

        total = sum(item["subtotal"] for item in carrito)
        id_deuda = crear_deuda(id_cliente, carrito, usuario)
        return {"id_deuda": id_deuda, "total": total}