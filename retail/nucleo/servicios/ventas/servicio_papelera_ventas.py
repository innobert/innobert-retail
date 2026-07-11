from __future__ import annotations

from typing import Any, Dict, List

from retail.nucleo.base_datos import conexion
from retail.nucleo.servicios.base.papelera_base import BasePapeleraServicio


class ServicioPapeleraVentas(BasePapeleraServicio):
    """Servicio para operaciones de la papelera de ventas."""

    TABLA = "papelera_ventas"

    @staticmethod
    def obtener_pagina(
        offset: int, limit: int, filtro_factura: str = ""
    ) -> List[Dict[str, Any]]:
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_factura:
                cursor.execute(
                    """
                    SELECT p.id_papelera, p.id_ventas, p.numero_factura,
                           p.cliente_rapido, p.cliente_id,
                           p.fecha, p.hora, p.total, p.usuario_elimino, p.fecha_eliminacion,
                           c.nombres, c.apellidos
                    FROM papelera_ventas p
                    LEFT JOIN clientes c ON p.cliente_id = c.id_cliente
                    WHERE p.numero_factura LIKE ?
                    ORDER BY p.fecha_eliminacion DESC
                    LIMIT ? OFFSET ?
                    """,
                    (f"%{filtro_factura}%", limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT p.id_papelera, p.id_ventas, p.numero_factura,
                           p.cliente_rapido, p.cliente_id,
                           p.fecha, p.hora, p.total, p.usuario_elimino, p.fecha_eliminacion,
                           c.nombres, c.apellidos
                    FROM papelera_ventas p
                    LEFT JOIN clientes c ON p.cliente_id = c.id_cliente
                    ORDER BY p.fecha_eliminacion DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
            rows = cursor.fetchall()

        registros = []
        for row in rows:
            (
                id_papelera, id_ventas, numero_factura,
                cliente_rapido, cliente_id,
                fecha_venta, hora_venta, total,
                usuario_elimino, fecha_eliminacion,
                nombres, apellidos,
            ) = row

            if cliente_rapido:
                cliente = cliente_rapido
            else:
                cliente = f"{nombres} {apellidos}" if nombres else "Cliente desconocido"

            registros.append({
                "id_papelera": id_papelera,
                "id_ventas": id_ventas,
                "numero_factura": numero_factura,
                "cliente": cliente,
                "fecha_venta": fecha_venta,
                "hora_venta": hora_venta,
                "total": float(total) if total else 0.0,
                "usuario_elimino": usuario_elimino,
                "fecha_eliminacion": fecha_eliminacion,
            })
        return registros
