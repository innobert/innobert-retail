from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from retail.nucleo.base_datos import (
    buscar_productos_por_nombre,
    contar_productos,
    obtener_clientes,
    obtener_nombres_productos,
    obtener_productos,
    paginar_productos,
    producto_a_dict,
)

logger = logging.getLogger(__name__)


class BaseTransaccionServicio:
    """Base compartida para servicios de transacciones (Ventas/Deudas).

    Contiene los métodos que son idénticos entre VentasServicio y DeudasServicio.
    Cada subclase implementa su propia lógica de confirmación y agregado al carrito.
    """

    # ── Stock ──────────────────────────────────────────────────────────

    @staticmethod
    def obtener_stock_actual(id_producto: int) -> Any:
        productos = obtener_productos()
        for p in productos:
            if p[0] == id_producto:
                return p[4]
        logger.warning("No se encontró stock para el producto %s", id_producto)
        return None

    @staticmethod
    def validar_cantidad(
        id_producto: int, cantidad_solicitada: int, carrito_actual: List[Dict[str, Any]]
    ) -> Tuple[bool, int, str]:
        stock_total = BaseTransaccionServicio.obtener_stock_actual(id_producto)
        if stock_total is None:
            return False, 0, "No se pudo obtener el stock del producto."

        cantidad_reservada = sum(
            item["cantidad"]
            for item in carrito_actual
            if item["id_producto"] == id_producto
        )
        stock_disponible = stock_total - cantidad_reservada

        if cantidad_solicitada <= 0:
            return False, stock_disponible, "La cantidad debe ser mayor a cero."

        if cantidad_solicitada > stock_disponible:
            msg = (
                f"Stock disponible para agregar: {stock_disponible} unidades.\n"
                f"Stock total: {stock_total} | Ya en carrito: {cantidad_reservada}"
            )
            return False, stock_disponible, msg

        return True, stock_disponible, ""

    # ── Clientes ───────────────────────────────────────────────────────

    @staticmethod
    def obtener_clientes_formateados() -> Tuple[List[str], Dict[str, int]]:
        clientes = obtener_clientes()
        nombres = [f"{c[1]} {c[2]}" for c in clientes]
        mapeo = {f"{c[1]} {c[2]}": c[0] for c in clientes}
        return nombres, mapeo

    @staticmethod
    def filtrar_clientes_por_texto(texto: str) -> List[Dict[str, Any]]:
        texto_lower = texto.lower()
        clientes = obtener_clientes()
        resultado = []
        for c in clientes:
            if texto_lower in c[1].lower() or texto_lower in c[2].lower():
                nombre_completo = f"{c[1]} {c[2]}"
                resultado.append({
                    "id_cliente": c[0],
                    "nombres": c[1],
                    "apellidos": c[2],
                    "nombre_completo": nombre_completo,
                })
        return resultado

    @staticmethod
    def obtener_cliente_por_nombre_completo(
        nombre_completo: str,
    ) -> Optional[Dict[str, Any]]:
        clientes = obtener_clientes()
        for c in clientes:
            if f"{c[1]} {c[2]}" == nombre_completo:
                return {
                    "id_cliente": c[0],
                    "nombres": c[1],
                    "apellidos": c[2],
                    "nombre_completo": nombre_completo,
                }
        logger.warning("Cliente '%s' no encontrado", nombre_completo)
        return None

    @staticmethod
    def obtener_nombre_cliente_por_id(cliente_id: int) -> Optional[str]:
        clientes = obtener_clientes()
        for c in clientes:
            if c[0] == cliente_id:
                return f"{c[1]} {c[2]}"
        logger.warning("Cliente con id %s no encontrado", cliente_id)
        return None

    # ── Productos ──────────────────────────────────────────────────────

    @staticmethod
    def obtener_productos_para_busqueda(termino: str = "") -> List[Dict[str, Any]]:
        if not termino:
            productos = obtener_productos()
        else:
            productos = buscar_productos_por_nombre(termino)
        return [producto_a_dict(p) for p in productos]

    @staticmethod
    def obtener_productos_paginado(
        offset: int, limit: int, filtro: str = ""
    ) -> List[Dict[str, Any]]:
        return paginar_productos(offset, limit, filtro)

    @staticmethod
    def contar_productos(filtro: str = "") -> Any:
        return contar_productos(filtro)

    @staticmethod
    def obtener_nombres_productos_para_busqueda(filtro: str = "") -> List[str]:
        return obtener_nombres_productos(filtro)

    # ── Carrito ────────────────────────────────────────────────────────

    @staticmethod
    def calcular_total_carrito(carrito: List[Dict[str, Any]]) -> int:
        total = 0.0
        for item in carrito:
            try:
                total += float(item.get("subtotal", 0))
            except Exception:
                logger.debug("Subtotal inválido en item del carrito, se ignora")
                total += 0
        return int(total)
