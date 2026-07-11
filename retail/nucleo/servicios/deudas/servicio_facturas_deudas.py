"""
servicio_facturas_deudas.py

Servicio para gestionar la lógica de negocio de las facturas de deudas abiertas.
Incluye consultas SQL, paginación, totales, filtros y registro de pagos.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple
from retail.nucleo.base_datos import conexion, registrar_historial_deuda


class ServicioFacturasDeudas:
    """Servicio para operaciones de facturas de deudas (solo ABIERTAS)."""

    @staticmethod
    def contar_deudas(filtro_cliente: str = "") -> Any:
        """
        Cuenta las deudas con estado 'ABIERTA' que coinciden con el filtro de cliente.
        """
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_cliente:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    WHERE d.estado = 'ABIERTA'
                      AND (c.nombres || ' ' || c.apellidos) LIKE ?
                    """,
                    (f"%{filtro_cliente}%",),
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM deudas WHERE estado = 'ABIERTA'")
            count = cursor.fetchone()[0]
        return count

    @staticmethod
    def obtener_pagina(
        offset: int, limit: int, filtro_cliente: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Retorna una página de deudas abiertas como lista de diccionarios.
        Cada diccionario contiene: id_deuda, numero_factura, cliente, productos,
        fecha, total, saldo.
        """
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_cliente:
                cursor.execute(
                    """
                    SELECT d.id_deuda,
                           d.numero_factura,
                           c.nombres || ' ' || c.apellidos AS cliente,
                           GROUP_CONCAT(i.producto || ' x' || dd.cantidad, ', ') AS productos,
                           d.fecha,
                           d.total,
                           d.saldo
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    LEFT JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                    LEFT JOIN inventario i ON dd.id_producto = i.id_producto
                    WHERE d.estado = 'ABIERTA'
                      AND (c.nombres || ' ' || c.apellidos) LIKE ?
                    GROUP BY d.id_deuda
                    ORDER BY d.id_deuda DESC
                    LIMIT ? OFFSET ?
                    """,
                    (f"%{filtro_cliente}%", limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT d.id_deuda,
                           d.numero_factura,
                           c.nombres || ' ' || c.apellidos AS cliente,
                           GROUP_CONCAT(i.producto || ' x' || dd.cantidad, ', ') AS productos,
                           d.fecha,
                           d.total,
                           d.saldo
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    LEFT JOIN detalle_deuda dd ON d.id_deuda = dd.id_deuda
                    LEFT JOIN inventario i ON dd.id_producto = i.id_producto
                    WHERE d.estado = 'ABIERTA'
                    GROUP BY d.id_deuda
                    ORDER BY d.id_deuda DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
            rows = cursor.fetchall()

        deudas = []
        for row in rows:
            deudas.append(
                {
                    "id_deuda": row[0],
                    "numero_factura": row[1],
                    "cliente": row[2],
                    "productos": row[3] if row[3] else "Sin productos",
                    "fecha": row[4],
                    "total": float(row[5]),
                    "saldo": float(row[6]),
                }
            )
        return deudas

    @staticmethod
    def calcular_total_deudas(filtro_cliente: str = "") -> float:
        """Suma el saldo de todas las deudas abiertas que coinciden con el filtro."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_cliente:
                cursor.execute(
                    """
                    SELECT SUM(d.saldo)
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    WHERE d.estado = 'ABIERTA'
                      AND (c.nombres || ' ' || c.apellidos) LIKE ?
                    """,
                    (f"%{filtro_cliente}%",),
                )
            else:
                cursor.execute("SELECT SUM(saldo) FROM deudas WHERE estado = 'ABIERTA'")
            resultado = cursor.fetchone()
        return float(resultado[0]) if resultado and resultado[0] else 0.0

    @staticmethod
    def obtener_lista_clientes(filtro_cliente: str = "") -> List[str]:
        """Retorna lista de nombres de clientes con deudas abiertas, opcionalmente filtrados."""
        with conexion() as conn:
            cursor = conn.cursor()
            if filtro_cliente:
                cursor.execute(
                    """
                    SELECT DISTINCT c.nombres || ' ' || c.apellidos
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    WHERE d.estado = 'ABIERTA'
                      AND (c.nombres || ' ' || c.apellidos) LIKE ?
                    ORDER BY c.nombres
                    """,
                    (f"%{filtro_cliente}%",),
                )
            else:
                cursor.execute("""
                    SELECT DISTINCT c.nombres || ' ' || c.apellidos
                    FROM deudas d
                    INNER JOIN clientes c ON d.cliente_id = c.id_cliente
                    WHERE d.estado = 'ABIERTA'
                    ORDER BY c.nombres
                    """)
            clientes = [row[0] for row in cursor.fetchall()]
        return clientes

    @staticmethod
    def registrar_pago(
        id_deuda: int, monto: float, saldo_actual: float, usuario: str, deudas_view: Any | None = None
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Registra un pago (abono o pago total) en la base de datos.
        Retorna (éxito, mensaje, vuelto). El vuelto solo es relevante si se paga más del saldo.
        """
        if monto <= 0:
            return False, "El monto debe ser mayor a cero.", None

        # Lógica de pago
        if monto < saldo_actual:
            pago_efectivo = monto
            vuelto = 0.0
            nuevo_saldo = saldo_actual - pago_efectivo
            nuevo_estado = "ABIERTA"
            mensaje = f"Abono registrado correctamente por {ServicioFacturasDeudas._formato_pesos(pago_efectivo)}"
        elif monto == saldo_actual:
            pago_efectivo = monto
            vuelto = 0.0
            nuevo_saldo = 0.0
            nuevo_estado = "PAGADA"
            mensaje = "La deuda ha sido pagada completamente. Será movida a la sección Pagadas."
        else:  # monto > saldo_actual
            pago_efectivo = saldo_actual
            vuelto = monto - saldo_actual
            nuevo_saldo = 0.0
            nuevo_estado = "PAGADA"
            mensaje = f"Pago registrado por {ServicioFacturasDeudas._formato_pesos(monto)}. Vuelto a entregar: {ServicioFacturasDeudas._formato_pesos(vuelto)}\n\nLa deuda ha sido pagada completamente y será movida a la sección Pagadas."

        try:
            with conexion() as conn:
                cursor = conn.cursor()
                fecha_hoy = datetime.datetime.now().date().isoformat()
                hora_hoy = datetime.datetime.now().strftime("%H:%M:%S")

                # Insertar en pagos_deuda
                cursor.execute(
                    "INSERT INTO pagos_deuda (id_deuda, monto, fecha, hora, usuario) VALUES (?, ?, ?, ?, ?)",
                    (id_deuda, monto, fecha_hoy, hora_hoy, usuario),
                )

                # Actualizar saldo y estado de la deuda
                cursor.execute(
                    "UPDATE deudas SET saldo = ?, estado = ? WHERE id_deuda = ?",
                    (nuevo_saldo, nuevo_estado, id_deuda),
                )

                # Registrar en historial_deudas
                registrar_historial_deuda(
                    id_deuda=id_deuda,
                    id_producto=None,
                    cantidad=0,
                    subtotal=pago_efectivo,
                    accion="ABONO",
                    usuario=usuario,
                    detalle=f'{"Abono" if nuevo_saldo > 0 else "Pago total"} de {ServicioFacturasDeudas._formato_pesos(pago_efectivo)}',
                    cursor=cursor,
                    abono=pago_efectivo,
                    recibido=monto,
                    vuelto=vuelto,
                )

            return True, mensaje, vuelto
        except Exception as e:
            return False, f"Error al registrar pago: {str(e)}", None

    @staticmethod
    def _formato_pesos(valor: float) -> str:
        """Formatea un número a pesos colombianos."""
        return f"${valor:,.0f}".replace(",", ".")

    @staticmethod
    def obtener_detalles_para_pdf(id_deuda: int) -> Dict[str, Any]:
        """Obtiene los detalles de productos y cliente para generar el PDF de la deuda."""
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT h.id_producto, COALESCE(i.producto, 'ABONO') as producto,
                       h.cantidad, h.subtotal
                FROM historial_deudas h
                LEFT JOIN inventario i ON h.id_producto = i.id_producto
                WHERE h.id_deuda = ? AND UPPER(h.accion) IN ('DEUDA', 'DEUDA DIRECTA', 'EDITADO', 'ABONO')
                ORDER BY h.id_historial
                """,
                (id_deuda,),
            )
            productos_detalle = cursor.fetchall()
        return {"productos": productos_detalle}
