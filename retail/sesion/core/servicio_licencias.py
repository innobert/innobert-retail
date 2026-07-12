from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any, Dict, Optional, Tuple

from retail.sesion.core.db import conexion

logger = logging.getLogger(__name__)


class ServicioLicencias:
    DIAS_PRUEBA = 30
    DIAS_LICENCIA_DEFAULT = 30

    @staticmethod
    def generar_licencia(
        usuario: str, dias: int = DIAS_LICENCIA_DEFAULT
    ) -> Dict[str, Any]:
        fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=dias)).strftime(
            "%Y-%m-%d"
        )
        serial = str(uuid.uuid4())

        return {
            "usuario": usuario,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "serial": serial,
            "dias": dias,
        }

    @staticmethod
    def crear_licencia_en_bd(
        usuario: str, fecha_inicio: str, fecha_fin: str, serial: str
    ) -> bool:
        try:
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE usuarios SET fecha_inicio = ?, fecha_fin = ?, serial = ? WHERE usuario = ?",
                    (fecha_inicio, fecha_fin, serial, usuario),
                )
            return True
        except Exception:
            logger.exception("Error al crear licencia")
            return False

    @staticmethod
    def validar_licencia(usuario: str, serial: str) -> Tuple[bool, str]:
        try:
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT fecha_fin FROM usuarios WHERE usuario = ? AND serial = ?",
                    (usuario, serial),
                )
                resultado = cursor.fetchone()

            if not resultado:
                return False, "Licencia no encontrada."

            fecha_fin_str = resultado[0]
            fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            hoy = datetime.datetime.now().date()

            if hoy > fecha_fin:
                dias_vencidos = (hoy - fecha_fin).days
                return False, f"Licencia vencida hace {dias_vencidos} días."

            return True, "Licencia válida."
        except Exception as e:
            return False, f"Error al validar licencia: {e}"

    @staticmethod
    def obtener_licencia(usuario: str) -> Optional[Dict[str, Any]]:
        try:
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT fecha_inicio, fecha_fin, serial FROM usuarios WHERE usuario = ?",
                    (usuario,),
                )
                resultado = cursor.fetchone()

            if not resultado:
                return None

            fecha_inicio, fecha_fin, serial = resultado
            return {
                "usuario": usuario,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "serial": serial,
            }
        except Exception:
            logger.exception("Error al obtener licencia")
            return None

    @staticmethod
    def renovar_licencia(usuario: str, dias: int = DIAS_LICENCIA_DEFAULT) -> bool:
        licencia = ServicioLicencias.generar_licencia(usuario, dias)
        return ServicioLicencias.crear_licencia_en_bd(
            licencia["usuario"],
            licencia["fecha_inicio"],
            licencia["fecha_fin"],
            licencia["serial"],
        )

    @staticmethod
    def dias_restantes(usuario: str) -> int:
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            return 0

        fecha_fin = datetime.datetime.strptime(licencia["fecha_fin"], "%Y-%m-%d").date()
        hoy = datetime.datetime.now().date()
        dias_restantes = (fecha_fin - hoy).days

        return max(0, dias_restantes)

    @staticmethod
    def licencia_proxima_a_vencer(usuario: str, dias_alerta: int = 7) -> bool:
        return 0 < ServicioLicencias.dias_restantes(usuario) <= dias_alerta

    @staticmethod
    def obtener_estado_licencia(usuario: str) -> Dict[str, Any]:
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            return {
                "estado": "no_encontrada",
                "mensaje": "Licencia no registrada",
                "dias_restantes": 0,
            }

        dias_restantes = ServicioLicencias.dias_restantes(usuario)

        if dias_restantes < 0:
            return {
                "estado": "vencida",
                "mensaje": f"Licencia vencida hace {abs(dias_restantes)} días",
                "dias_restantes": 0,
                "serial": licencia["serial"],
            }
        elif dias_restantes == 0:
            return {
                "estado": "vencido_hoy",
                "mensaje": "Licencia vence hoy",
                "dias_restantes": 0,
                "serial": licencia["serial"],
            }
        elif ServicioLicencias.licencia_proxima_a_vencer(usuario, 7):
            return {
                "estado": "proxima_a_vencer",
                "mensaje": f"Licencia vence en {dias_restantes} días",
                "dias_restantes": dias_restantes,
                "serial": licencia["serial"],
            }
        else:
            return {
                "estado": "vigente",
                "mensaje": f"Licencia vigente. Vence en {dias_restantes} días",
                "dias_restantes": dias_restantes,
                "serial": licencia["serial"],
            }
