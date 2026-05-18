"""
servicio_acceso.py

Servicio para gestionar la autenticación de usuarios, validación de suscripción y gestión de sesión.
"""
import datetime
import hashlib
from typing import Optional, Tuple
from retail.nucleo.base_datos import get_connection, buscar_usuario as db_buscar_usuario
from retail.nucleo.configuraciones import guardar_usuario, cargar_usuario


class ServicioAcceso:
    """Servicio para operaciones de acceso y autenticación."""

    @staticmethod
    def autenticar_usuario(usuario: str, contrasena: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Autentica al usuario. Retorna (éxito, mensaje, datos_usuario).
        Datos_usuario puede contener: usuario, serial, fecha_inicio, fecha_fin.
        """
        if not usuario or not contrasena:
            return False, "Usuario y contraseña son requeridos.", None

        # Bloquear usuario 'admin'
        if usuario.lower() == "admin":
            return False, "Acceso denegado para este usuario.", None

        resultado = db_buscar_usuario(usuario, contrasena)
        if not resultado:
            return False, "Usuario o contraseña incorrectos.", None

        # resultado es una tupla: (id, usuario, contrasena_hash, fecha_inicio, fecha_fin, serial)
        _, _, _, fecha_inicio, fecha_fin, serial = resultado

        # Validar suscripción
        hoy = datetime.datetime.now().date()
        fecha_fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        if hoy > fecha_fin_dt:
            return False, f"Su suscripción ha vencido. Inicio: {fecha_inicio} | Fin: {fecha_fin} | Serial: {serial}", None

        return True, "Autenticación exitosa", {
            "usuario": usuario,
            "serial": serial,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }

    @staticmethod
    def guardar_preferencias_sesion(usuario: str, contrasena: str, recordar: bool) -> None:
        """Guarda las preferencias de recordar usuario en config.json."""
        if recordar:
            guardar_usuario(usuario, contrasena, True)
        else:
            guardar_usuario("", "", False)

    @staticmethod
    def cargar_preferencias_sesion() -> Tuple[str, str, bool]:
        """Carga las preferencias guardadas (usuario, contraseña, recordar)."""
        return cargar_usuario()

    @staticmethod
    def es_desarrollador(usuario: str, contrasena: str) -> bool:
        """Verifica si es el usuario desarrollador (innobertdev)."""
        # En una implementación real, se consultaría la tabla desarrollador.
        # Por ahora, comparación directa.
        return usuario == "innobertdev" and contrasena == "ingsoftware.99"