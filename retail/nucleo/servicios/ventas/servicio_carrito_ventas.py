from __future__ import annotations

from typing import Any, Dict, List

from retail.nucleo.servicios.base.carrito_base import BaseCarritoServicio


class ServicioCarritoVentas(BaseCarritoServicio):
    """Servicio para operaciones del carrito de ventas."""

    @staticmethod
    def calcular_totales_por_cliente(carrito: List[Dict[str, Any]]) -> Dict[str, float]:
        totales: dict[str, float] = {}
        for item in carrito:
            cliente = item.get("cliente", "")
            totales[cliente] = totales.get(cliente, 0) + item["subtotal"]
        return totales
