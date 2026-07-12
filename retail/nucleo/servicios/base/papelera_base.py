from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from retail.nucleo.base_datos import conexion

logger = logging.getLogger(__name__)


class BasePapeleraServicio:
    """Base compartida para servicios de papelera (Ventas/Deudas)."""

    TABLA: str = ""
    COLUMNA_NUMERO = "numero_factura"
    COLUMNA_FECHA_ELIMINACION = "fecha_eliminacion"
    COLUMNA_TOTAL = "total"

    @classmethod
    def contar_papelera(cls, filtro_factura: str = "") -> Any:
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_factura:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {cls.TABLA} WHERE {cls.COLUMNA_NUMERO} LIKE ?",
                    (f"%{filtro_factura}%",),
                )
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {cls.TABLA}")
            return cursor.fetchone()[0]

    @classmethod
    def limpiar_registros_antiguos(cls, dias: int = 30) -> int:
        try:
            with conexion() as conn:
                cursor = conn.cursor()
                fecha_limite = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")
                cursor.execute(
                    f"DELETE FROM {cls.TABLA} WHERE {cls.COLUMNA_FECHA_ELIMINACION} <= ?",
                    (fecha_limite,),
                )
                return cursor.rowcount
        except Exception:
            logger.exception("Error limpiando papelera %s", cls.TABLA)
            return 0

    @classmethod
    def obtener_total_eliminado(cls, filtro_factura: str = "") -> float:
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_factura:
                cursor.execute(
                    f"SELECT SUM({cls.COLUMNA_TOTAL}) FROM {cls.TABLA} WHERE {cls.COLUMNA_NUMERO} LIKE ?",
                    (f"%{filtro_factura}%",),
                )
            else:
                cursor.execute(f"SELECT SUM({cls.COLUMNA_TOTAL}) FROM {cls.TABLA}")
            resultado = cursor.fetchone()
        return float(resultado[0]) if resultado and resultado[0] else 0.0
