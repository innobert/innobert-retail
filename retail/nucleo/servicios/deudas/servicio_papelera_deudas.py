from __future__ import annotations

import logging
from typing import Any, Dict, List

from retail.nucleo.base_datos import conexion
from retail.nucleo.servicios.base.papelera_base import BasePapeleraServicio

logger = logging.getLogger(__name__)


class ServicioPapeleraDeudas(BasePapeleraServicio):
    """Servicio para operaciones de la papelera de deudas."""

    TABLA = "papelera_deudas"

    @staticmethod
    def obtener_pagina(
        offset: int, limit: int, filtro_factura: str = ""
    ) -> List[Dict[str, Any]]:
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_factura:
                cursor.execute(
                    """
                    SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha,
                           total, saldo, usuario_elimino, fecha_eliminacion, detalle
                    FROM papelera_deudas
                    WHERE numero_factura LIKE ?
                    ORDER BY fecha_eliminacion DESC
                    LIMIT ? OFFSET ?
                    """,
                    (f"%{filtro_factura}%", limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha,
                           total, saldo, usuario_elimino, fecha_eliminacion, detalle
                    FROM papelera_deudas
                    ORDER BY fecha_eliminacion DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
            rows = cursor.fetchall()

        registros = []
        for row in rows:
            cliente_nombre = "Cliente eliminado"
            if row[3]:
                try:
                    with conexion() as conn2:
                        cursor2 = conn2.cursor()
                        cursor2.execute(
                            "SELECT nombres || ' ' || apellidos FROM clientes WHERE id_cliente = ?",
                            (row[3],),
                        )
                        res = cursor2.fetchone()
                        if res:
                            cliente_nombre = res[0]
                except Exception:
                    logger.exception("Error al buscar nombre de cliente en papelera")
            registros.append({
                "id_papelera": row[0],
                "id_deuda": row[1],
                "numero_factura": row[2],
                "cliente_id": row[3],
                "cliente": cliente_nombre,
                "fecha": row[4],
                "total": float(row[5]) if row[5] else 0.0,
                "saldo": float(row[6]) if row[6] else 0.0,
                "usuario_elimino": row[7],
                "fecha_eliminacion": row[8],
                "detalle": row[9] if row[9] else "",
            })
        return registros
