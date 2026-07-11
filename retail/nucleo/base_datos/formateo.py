"""Funciones auxiliares de formateo de datos."""

from __future__ import annotations

from typing import Any

from retail.nucleo.base_datos.indices import producto_a_dict


def peso_colombiano(value: float) -> str:
    return f"${value:,.0f}".replace(",", ".")


def formatear_inventario(productos: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [producto_a_dict(p) for p in productos]


def formatear_venta(venta: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "id_ventas": venta[0],
        "numero_factura": venta[1],
        "cliente_id": venta[2],
        "cliente_rapido": venta[3],
        "fecha": venta[4],
        "hora": venta[5],
        "total": venta[6],
        "ganancia": venta[7],
        "monto_recibido": venta[8],
        "vuelto": venta[9],
    }
