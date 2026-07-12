from __future__ import annotations

from typing import Any, Dict, List, Optional

from retail.sesion.core.db import conexion
from retail.nucleo.seguridad import hash_contrasena
from retail.sesion.core.servicio_licencias import ServicioLicencias
from retail.traducciones import _


class ServicioRegistro:
    @staticmethod
    def registrar_usuario(
        usuario: str, contrasena: str, dias_licencia: int = 30
    ) -> bool:
        if not usuario or not contrasena:
            raise ValueError(_("Usuario y contraseña son requeridos."))

        if len(usuario) < 3:
            raise ValueError(_("Usuario debe tener al menos 3 caracteres."))

        if len(contrasena) < 6:
            raise ValueError(_("Contraseña debe tener al menos 6 caracteres."))

        licencia = ServicioLicencias.generar_licencia(usuario, dias_licencia)
        contrasena_hash = hash_contrasena(contrasena)

        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
                (
                    usuario,
                    contrasena_hash,
                    licencia["fecha_inicio"],
                    licencia["fecha_fin"],
                    licencia["serial"],
                ),
            )
            return True

    @staticmethod
    def obtener_todos_usuarios(
        excluir_desarrollador: bool = True,
    ) -> List[Dict[str, Any]]:
        with conexion() as conn:
            cursor = conn.cursor()
            if excluir_desarrollador:
                cursor.execute(
                    "SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios WHERE usuario != ? ORDER BY id ASC",
                    ("innobertdev",),
                )
            else:
                cursor.execute(
                    "SELECT usuario, fecha_inicio, fecha_fin, serial FROM usuarios ORDER BY id ASC"
                )

            rows = cursor.fetchall()
            usuarios = []
            for row in rows:
                usuario, fecha_inicio, fecha_fin, serial = row
                dias_restantes = ServicioLicencias.dias_restantes(usuario)
                usuarios.append(
                    {
                        "usuario": usuario,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "serial": serial,
                        "dias_restantes": dias_restantes,
                    }
                )
            return usuarios

    @staticmethod
    def actualizar_usuario(
        usuario_actual: str, nuevo_usuario: str, nueva_contrasena: Optional[str] = None
    ) -> bool:
        if not nuevo_usuario:
            raise ValueError(_("Nuevo usuario no puede estar vacío."))

        if nueva_contrasena and len(nueva_contrasena) < 6:
            raise ValueError(_("Contraseña debe tener al menos 6 caracteres."))

        with conexion() as conn:
            cursor = conn.cursor()
            if nueva_contrasena:
                contrasena_hash = hash_contrasena(nueva_contrasena)
                cursor.execute(
                    "UPDATE usuarios SET usuario = ?, contrasena = ? WHERE usuario = ?",
                    (nuevo_usuario, contrasena_hash, usuario_actual),
                )
            else:
                cursor.execute(
                    "UPDATE usuarios SET usuario = ? WHERE usuario = ?",
                    (nuevo_usuario, usuario_actual),
                )
            return True

    @staticmethod
    def renovar_suscripcion(usuario: str, dias: int = 30) -> bool:
        return ServicioLicencias.renovar_licencia(usuario, dias)

    @staticmethod
    def eliminar_usuario(usuario: str) -> bool:
        with conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
            return True
