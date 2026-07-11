"""
servicio_registro.py

Servicio para gestionar el registro, actualización y eliminación de usuarios.
Módulo independizado accesible solo al desarrollador principal.
"""

import datetime
import hashlib
import uuid
from typing import List, Dict, Any
from retail.nucleo.base_datos import get_connection
from retail.nucleo.servicios.sesion.servicio_licencias import ServicioLicencias


class ServicioRegistro:
    """
    Servicio para operaciones CRUD de usuarios.
    Este servicio solo debe ser accesible al desarrollador.
    """

    @staticmethod
    def registrar_usuario(usuario: str, contrasena: str, dias_licencia: int = 30) -> bool:
        """
        Registra un nuevo usuario con licencia.
        
        Args:
            usuario: Nombre de usuario
            contrasena: Contraseña del usuario
            dias_licencia: Días de validez de la licencia (default: 30)
            
        Returns:
            True si fue exitoso
        """
        # Validar entrada
        if not usuario or not contrasena:
            raise ValueError("Usuario y contraseña son requeridos.")
        
        if len(usuario) < 3:
            raise ValueError("Usuario debe tener al menos 3 caracteres.")
        
        if len(contrasena) < 6:
            raise ValueError("Contraseña debe tener al menos 6 caracteres.")
        
        # Generar licencia usando servicio independizado
        licencia = ServicioLicencias.generar_licencia(usuario, dias_licencia)
        
        # Hash de contraseña
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        
        # Insertar en BD
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
                (usuario, contrasena_hash, licencia["fecha_inicio"], licencia["fecha_fin"], licencia["serial"])
            )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def obtener_todos_usuarios(excluir_desarrollador: bool = True) -> List[Dict[str, Any]]:
        """
        Retorna lista de usuarios con sus datos de licencia.
        Si excluir_desarrollador es True, omite al usuario 'innobertdev'.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if excluir_desarrollador:
                cursor.execute(
                    "SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios WHERE usuario != ? ORDER BY id ASC",
                    ("innobertdev",)
                )
            else:
                cursor.execute("SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios ORDER BY id ASC")
            
            rows = cursor.fetchall()
            usuarios = []
            for row in rows:
                usuario, fecha_inicio, fecha_fin, serial = row
                dias_restantes = ServicioLicencias.dias_restantes(usuario)
                usuarios.append({
                    "usuario": usuario,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "serial": serial,
                    "dias_restantes": dias_restantes
                })
            return usuarios
        finally:
            conn.close()

    @staticmethod
    def actualizar_usuario(usuario_actual: str, nuevo_usuario: str, nueva_contrasena: str = None) -> bool:
        """
        Actualiza el nombre de usuario y opcionalmente la contraseña.
        """
        if not nuevo_usuario:
            raise ValueError("Nuevo usuario no puede estar vacío.")
        
        if nueva_contrasena and len(nueva_contrasena) < 6:
            raise ValueError("Contraseña debe tener al menos 6 caracteres.")
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            if nueva_contrasena:
                contrasena_hash = hashlib.sha256(nueva_contrasena.encode()).hexdigest()
                cursor.execute(
                    "UPDATE usuarios SET usuario = ?, contrasena = ? WHERE usuario = ?",
                    (nuevo_usuario, contrasena_hash, usuario_actual)
                )
            else:
                cursor.execute(
                    "UPDATE usuarios SET usuario = ? WHERE usuario = ?",
                    (nuevo_usuario, usuario_actual)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def renovar_suscripcion(usuario: str, dias: int = 30) -> bool:
        """
        Renueva la licencia de un usuario usando el servicio de licencias.
        """
        return ServicioLicencias.renovar_licencia(usuario, dias)

    @staticmethod
    def eliminar_usuario(usuario: str) -> bool:
        """Elimina un usuario de la BD."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
            conn.commit()
            return True
        finally:
            conn.close()