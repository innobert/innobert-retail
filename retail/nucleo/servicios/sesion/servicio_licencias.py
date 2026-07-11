"""
servicio_licencias.py

Servicio independizado para gestionar licencias de usuarios.
Controla la validación, generación y renovación de licencias.
"""

import logging
import datetime
import hashlib
import uuid
from typing import Optional, Tuple, Dict, Any
from retail.nucleo.base_datos import obtener_conexion


class ServicioLicencias:
    """Servicio para gestionar licencias de usuarios de forma independizada."""

    DIAS_PRUEBA = 30
    DIAS_LICENCIA_DEFAULT = 30

    @staticmethod
    def generar_licencia(usuario: str, dias: int = DIAS_LICENCIA_DEFAULT) -> Dict[str, str]:
        """
        Genera una nueva licencia para un usuario.
        
        Args:
            usuario: Nombre del usuario
            dias: Días de validez (default: 30)
            
        Returns:
            Diccionario con datos de la licencia generada
        """
        fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
        serial = str(uuid.uuid4())
        
        return {
            "usuario": usuario,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "serial": serial,
            "dias": dias
        }

    @staticmethod
    def crear_licencia_en_bd(usuario: str, fecha_inicio: str, fecha_fin: str, serial: str) -> bool:
        """Crea una licencia en la base de datos."""
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO usuarios (usuario, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?)",
                (usuario, fecha_inicio, fecha_fin, serial)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error al crear licencia: {e}")
            return False

    @staticmethod
    def validar_licencia(usuario: str, serial: str) -> Tuple[bool, str]:
        """
        Valida si la licencia de un usuario es válida.
        
        Returns:
            (es_válida, mensaje_error)
        """
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fecha_fin FROM usuarios WHERE usuario = ? AND serial = ?",
                (usuario, serial)
            )
            resultado = cursor.fetchone()
            conn.close()
            
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
        """Obtiene datos de la licencia actual de un usuario."""
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fecha_inicio, fecha_fin, serial FROM usuarios WHERE usuario = ?",
                (usuario,)
            )
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                return None
            
            fecha_inicio, fecha_fin, serial = resultado
            return {
                "usuario": usuario,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "serial": serial
            }
        except Exception as e:
            logging.error(f"Error al obtener licencia: {e}")
            return None

    @staticmethod
    def renovar_licencia(usuario: str, dias: int = DIAS_LICENCIA_DEFAULT) -> bool:
        """
        Renueva la licencia de un usuario.
        
        Args:
            usuario: Nombre del usuario
            dias: Días de validez nueva (default: 30)
            
        Returns:
            True si se renovó exitosamente
        """
        licencia = ServicioLicencias.generar_licencia(usuario, dias)
        return ServicioLicencias.crear_licencia_en_bd(
            licencia["usuario"],
            licencia["fecha_inicio"],
            licencia["fecha_fin"],
            licencia["serial"]
        )

    @staticmethod
    def dias_restantes(usuario: str) -> int:
        """Retorna los días restantes de licencia."""
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            return 0
        
        fecha_fin = datetime.datetime.strptime(licencia["fecha_fin"], "%Y-%m-%d").date()
        hoy = datetime.datetime.now().date()
        dias_restantes = (fecha_fin - hoy).days
        
        return max(0, dias_restantes)

    @staticmethod
    def licencia_proxima_a_vencer(usuario: str, dias_alerta: int = 7) -> bool:
        """Verifica si la licencia está próxima a vencer (dentro de N días)."""
        dias_restantes = ServicioLicencias.dias_restantes(usuario)
        return 0 < dias_restantes <= dias_alerta

    @staticmethod
    def obtener_estado_licencia(usuario: str) -> Dict[str, Any]:
        """
        Obtiene el estado completo de la licencia.
        
        Returns:
            Diccionario con estado, días restantes y detalles
        """
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            return {
                "estado": "no_encontrada",
                "mensaje": "Licencia no registrada",
                "dias_restantes": 0
            }
        
        dias_restantes = ServicioLicencias.dias_restantes(usuario)
        
        if dias_restantes < 0:
            return {
                "estado": "vencida",
                "mensaje": f"Licencia vencida hace {abs(dias_restantes)} días",
                "dias_restantes": 0,
                "serial": licencia["serial"]
            }
        elif dias_restantes == 0:
            return {
                "estado": "vencido_hoy",
                "mensaje": "Licencia vence hoy",
                "dias_restantes": 0,
                "serial": licencia["serial"]
            }
        elif ServicioLicencias.licencia_proxima_a_vencer(usuario, 7):
            return {
                "estado": "proxima_a_vencer",
                "mensaje": f"Licencia vence en {dias_restantes} días",
                "dias_restantes": dias_restantes,
                "serial": licencia["serial"]
            }
        else:
            return {
                "estado": "vigente",
                "mensaje": f"Licencia vigente. Vence en {dias_restantes} días",
                "dias_restantes": dias_restantes,
                "serial": licencia["serial"]
            }
