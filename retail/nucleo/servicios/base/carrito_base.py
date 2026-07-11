from __future__ import annotations

from typing import Any, Dict, List, Tuple

from retail.nucleo.servicios.base.transaccion_base import BaseTransaccionServicio


class BaseCarritoServicio:
    """Base compartida para servicios de carrito (Ventas/Deudas)."""

    @staticmethod
    def validar_cantidad_para_edicion(
        carrito: List[Dict[str, Any]],
        id_producto: int,
        nueva_cantidad: int,
        item_actual: Dict[str, Any],
    ) -> Tuple[bool, int, str]:
        stock_total = BaseTransaccionServicio.obtener_stock_actual(id_producto)
        if stock_total is None:
            return False, 0, "No se pudo obtener el stock del producto."

        cantidad_otros = sum(
            item["cantidad"]
            for item in carrito
            if item["id_producto"] == id_producto and item is not item_actual
        )
        stock_disponible = stock_total - cantidad_otros

        if nueva_cantidad <= 0:
            return False, stock_disponible, "La cantidad debe ser mayor a cero."

        if nueva_cantidad > stock_disponible:
            msg = (
                f"Stock disponible para este producto: {stock_disponible} unidades.\n"
                f"Stock total: {stock_total} | Otras cantidades en carrito: {cantidad_otros}"
            )
            return False, stock_disponible, msg

        return True, stock_disponible, ""

    @staticmethod
    def actualizar_cantidad_en_carrito(
        carrito: List[Dict[str, Any]], item_index: int, nueva_cantidad: int
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        item = carrito[item_index]
        item["cantidad"] = nueva_cantidad
        item["subtotal"] = nueva_cantidad * item["precio"]
        return carrito, item

    @staticmethod
    def eliminar_producto_del_carrito(
        carrito: List[Dict[str, Any]], item_index: int
    ) -> List[Dict[str, Any]]:
        del carrito[item_index]
        return carrito

    @staticmethod
    def calcular_total_general(carrito: List[Dict[str, Any]]) -> Any:
        return sum(item["subtotal"] for item in carrito)
