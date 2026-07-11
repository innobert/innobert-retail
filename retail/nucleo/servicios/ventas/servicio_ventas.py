from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from retail.nucleo.base_datos import crear_venta, actualizar_cuentas, obtener_clientes
from retail.nucleo.servicios.base.transaccion_base import BaseTransaccionServicio

logger = logging.getLogger(__name__)


class VentasServicio(BaseTransaccionServicio):
    """
    Servicio para operaciones de ventas.
    Hereda los métodos compartidos de BaseTransaccionServicio.
    """

    @staticmethod
    def agregar_al_carrito(
        carrito: List[Dict[str, Any]],
        producto_data: Dict[str, Any],
        cantidad: int,
        cliente_id: Optional[int],
        tipo_venta: str,
    ) -> Tuple[List[Dict[str, Any]], str, Optional[Dict[str, Any]]]:
        id_producto = producto_data["id_producto"]

        valido, stock, msg = VentasServicio.validar_cantidad(
            id_producto, cantidad, carrito
        )
        if not valido:
            return carrito, msg, {"error": msg, "producto": producto_data["producto"]}

        cliente_carrito = ""
        if tipo_venta == "mayorista" and cliente_id:
            try:
                clientes = obtener_clientes()
                for c in clientes:
                    if c[0] == cliente_id:
                        cliente_carrito = f"{c[1]} {c[2]}"
                        break
            except Exception:
                logger.warning("Error al obtener datos del cliente para el carrito", exc_info=True)

        producto_en_carrito = any(
            item["producto"] == producto_data["producto"]
            and item["cliente"] == cliente_carrito
            for item in carrito
        )
        if producto_en_carrito:
            return (
                carrito,
                "El producto ya está en el carrito.",
                {"error": "duplicado", "producto": producto_data["producto"]},
            )

        nuevo_item = {
            "cliente": cliente_carrito,
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
    def confirmar_venta(
        carrito: List[Dict[str, Any]],
        cliente_id: Optional[int],
        monto_recibido: float,
        usuario: str,
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

        resultado = crear_venta(
            cliente_id=cliente_id,
            items=items,
            monto_recibido=monto_recibido,
            usuario=usuario,
        )
        actualizar_cuentas()
        return resultado
