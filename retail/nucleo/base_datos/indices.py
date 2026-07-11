"""Constantes de índice para tuplas de productos y utilerías de conversión."""

from __future__ import annotations

from typing import Any

IDX_PROD_ID = 0
IDX_PROD_NOMBRE = 1
IDX_PROD_PRECIO = 2
IDX_PROD_COSTO = 3
IDX_PROD_STOCK = 4
IDX_PROD_ESTADO = 5
IDX_PROD_IMAGEN = 6


def producto_a_dict(p: tuple[Any, ...]) -> dict[str, Any]:
    return {
        "id_producto": p[IDX_PROD_ID],
        "producto": p[IDX_PROD_NOMBRE],
        "precio": p[IDX_PROD_PRECIO],
        "costo": p[IDX_PROD_COSTO],
        "stock": p[IDX_PROD_STOCK],
        "estado": p[IDX_PROD_ESTADO],
        "imagen": p[IDX_PROD_IMAGEN],
    }
