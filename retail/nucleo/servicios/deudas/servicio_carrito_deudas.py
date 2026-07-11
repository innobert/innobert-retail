"""Servicio para operaciones del carrito de deudas."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from retail.nucleo.base_datos import crear_deuda
from retail.nucleo.servicios.base.carrito_base import BaseCarritoServicio
from retail.nucleo.servicios.base.transaccion_base import BaseTransaccionServicio


class ServicioCarritoDeudas(BaseCarritoServicio):
    """Servicio para operaciones del carrito de deudas."""

    @staticmethod
    def agregar_al_carrito(
        carrito: List[Dict[str, Any]],
        producto_data: Dict[str, Any],
        cantidad: int,
        cliente_id: int,
        cliente_nombre: str,
    ) -> Tuple[List[Dict[str, Any]], str, Any]:
        id_producto = producto_data["id_producto"]

        valido, stock, msg = BaseTransaccionServicio.validar_cantidad(
            id_producto, cantidad, carrito
        )
        if not valido:
            return carrito, msg, {"error": msg, "producto": producto_data["producto"]}

        producto_en_carrito = any(
            item["producto"] == producto_data["producto"]
            and item["cliente"] == cliente_nombre
            for item in carrito
        )
        if producto_en_carrito:
            return (
                carrito,
                "El producto ya está en el carrito.",
                {"error": "duplicado", "producto": producto_data["producto"]},
            )

        nuevo_item = {
            "cliente": cliente_nombre,
            "cliente_id": cliente_id,
            "producto": producto_data["producto"],
            "id_producto": id_producto,
            "cantidad": cantidad,
            "precio": producto_data["precio"],
            "subtotal": cantidad * producto_data["precio"],
        }
        carrito.append(nuevo_item)
        return carrito, "", None

    @staticmethod
    def confirmar_deuda(
        carrito: List[Dict[str, Any]], cliente_id: int, usuario: str
    ) -> Dict[str, Any]:
        if not carrito:
            raise ValueError("El carrito está vacío.")

        items = [
            {
                "id_producto": item["id_producto"],
                "cantidad": item["cantidad"],
                "precio": item["precio"],
            }
            for item in carrito
        ]

        resultado = crear_deuda(cliente_id=cliente_id, items=items, usuario=usuario)
        return resultado
