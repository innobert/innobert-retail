"""
servicio_mensual.py

Servicio para gestionar la lógica de negocio del reporte mensual de ganancias.
- Obtener datos agregados por períodos de 30 días consecutivos desde la primera transacción.
- Calcular totales globales.
"""

from __future__ import annotations

import datetime
from typing import Any, List, Tuple
from retail.nucleo.base_datos import conexion, obtener_totales_globales_ganancias

MESES_ES = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


class ServicioMensual:
    """Servicio para el reporte mensual de ganancias."""

    @staticmethod
    def obtener_periodos() -> List[Tuple[Any, ...]]:
        """
        Realiza una sola consulta SQL que agrupa todas las transacciones en períodos
        de 30 días consecutivos a partir de la fecha de la primera transacción.
        Retorna lista de tuplas:
        (periodo_num, nombre_mes, start_date, end_date, total_ventas_str, total_ganancia_str, prod_vendidos, clientes)
        """
        with conexion() as conn:
            cursor = conn.cursor()

            # Obtener la fecha de la primera transacción
            cursor.execute("SELECT MIN(fecha) FROM ventas")
            min_venta = cursor.fetchone()[0]
            cursor.execute("SELECT MIN(fecha) FROM pagos_deuda")
            min_deuda = cursor.fetchone()[0]
            fechas = [f for f in (min_venta, min_deuda) if f]
            if not fechas:
                return []
            first_date = min(fechas)
            first_date_dt = datetime.datetime.strptime(first_date, "%Y-%m-%d")

            query = """
            WITH combined AS (
                SELECT fecha,
                       COALESCE(c.nombres || ' ' || c.apellidos, v.cliente_rapido) AS cliente,
                       i.precio * dv.cantidad AS monto,
                       (i.precio - i.costo) * dv.cantidad AS ganancia,
                       dv.cantidad AS cantidad
                FROM ventas v
                JOIN detalle_venta dv ON v.id_ventas = dv.id_ventas
                JOIN inventario i ON dv.id_producto = i.id_producto
                LEFT JOIN clientes c ON v.cliente_id = c.id_cliente
                UNION ALL
                SELECT p.fecha,
                       c.nombres || ' ' || c.apellidos AS cliente,
                       dd.precio_unitario * dd.cantidad AS monto,
                       (dd.precio_unitario - i.costo) * dd.cantidad AS ganancia,
                       dd.cantidad AS cantidad
                FROM pagos_deuda p
                JOIN deudas d ON p.id_deuda = d.id_deuda
                JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                JOIN inventario i ON dd.id_producto = i.id_producto
                JOIN clientes c ON d.cliente_id = c.id_cliente
                WHERE d.estado = 'PAGADA'
            )
            SELECT 
                CAST((JULIANDAY(fecha) - JULIANDAY(?)) / 30 AS INTEGER) + 1 AS periodo,
                SUM(monto) AS total_ventas,
                SUM(ganancia) AS total_ganancia,
                SUM(cantidad) AS productos_vendidos,
                COUNT(DISTINCT cliente) AS clientes
            FROM combined
            GROUP BY periodo
            ORDER BY periodo
            """
            cursor.execute(query, (first_date,))
            rows = cursor.fetchall()

        periods = []
        for row in rows:
            periodo, total_ventas, total_ganancia, prod_vendidos, clientes = row
            start_date = first_date_dt + datetime.timedelta(days=(periodo - 1) * 30)
            end_date = start_date + datetime.timedelta(days=29)

            mes_inicio = MESES_ES[start_date.month - 1]
            mes_fin = MESES_ES[end_date.month - 1]
            nombre_mes = (
                mes_inicio if mes_inicio == mes_fin else f"{mes_inicio} - {mes_fin}"
            )

            periods.append(
                (
                    periodo,
                    nombre_mes,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    f"${total_ventas:,.0f}".replace(",", "."),
                    f"${total_ganancia:,.0f}".replace(",", "."),
                    prod_vendidos,
                    clientes,
                )
            )
        return periods

    @staticmethod
    def obtener_totales_globales() -> Tuple[float, float]:
        """Suma totales de todas las transacciones (sin paginación)."""
        return obtener_totales_globales_ganancias()
