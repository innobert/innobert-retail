"""
servicio_registro.py

Servicio para gestionar el registro, actualización y eliminación de usuarios.
"""

import datetime
import hashlib
import uuid
from typing import List, Dict, Any
from retail.nucleo.base_datos import get_connection


class ServicioRegistro:
    """Servicio para operaciones CRUD de usuarios."""

    @staticmethod
    def registrar_usuario(usuario: str, contrasena: str) -> bool:
        """
        Registra un nuevo usuario con fechas de suscripción (30 días) y serial único.
        Retorna True si fue exitoso, lanza excepción en caso de error.
        """
        fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        serial = str(uuid.uuid4())
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
            (usuario, contrasena_hash, fecha_inicio, fecha_fin, serial)
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def obtener_todos_usuarios(excluir_desarrollador: bool = True) -> List[Dict[str, Any]]:
        """
        Retorna lista de diccionarios con los datos de usuarios.
        Si excluir_desarrollador es True, omite al usuario 'innobertdev'.
        """
        conn = get_connection()
        cursor = conn.cursor()
        if excluir_desarrollador:
            cursor.execute(
                "SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios WHERE usuario != ? ORDER BY id ASC",
                ("innobertdev",)
            )
        else:
            cursor.execute("SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        usuarios = []
        for row in rows:
            usuarios.append({
                "usuario": row[0],
                "fecha_inicio": row[1],
                "fecha_fin": row[2],
                "serial": row[3],
            })
        return usuarios

    @staticmethod
    def actualizar_usuario(usuario_actual: str, nuevo_usuario: str, nueva_contrasena: str = None) -> bool:
        """
        Actualiza el nombre de usuario y opcionalmente la contraseña.
        Retorna True si fue exitoso.
        """
        conn = get_connection()
        cursor = conn.cursor()
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
        conn.close()
        return True

    @staticmethod
    def renovar_suscripcion(usuario: str) -> bool:
        """
        Renueva la suscripción de un usuario: actualiza fecha_inicio, fecha_fin y serial.
        """
        fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        serial = str(uuid.uuid4())
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET fecha_inicio = ?, fecha_fin = ?, serial = ? WHERE usuario = ?",
            (fecha_inicio, fecha_fin, serial, usuario)
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def eliminar_usuario(usuario: str) -> bool:
        """Elimina un usuario por su nombre."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
        conn.commit()
        conn.close()
        return True