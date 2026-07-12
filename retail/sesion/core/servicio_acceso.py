from __future__ import annotations

import logging
from typing import Any, Optional, Tuple

from retail.nucleo.base_datos.usuarios import verificar_desarrollador
from retail.nucleo.seguridad import hash_contrasena
from retail.sesion.core.db import conexion, buscar_usuario as db_buscar_usuario
from retail.traducciones import _

logger = logging.getLogger(__name__)
from retail.nucleo.configuraciones import guardar_usuario, cargar_usuario
from retail.sesion.core.servicio_licencias import ServicioLicencias


class ServicioAcceso:
    USUARIOS_RESERVADOS = {"admin", "administrator", "root", "sistema"}
    DESARROLLADOR_USUARIO = "innobertdev"

    @staticmethod
    def autenticar_usuario(
        usuario: str, contrasena: str
    ) -> Tuple[bool, str, Optional[dict[str, Any]]]:
        if not usuario or not contrasena:
            return False, _("Credenciales incompletas."), None

        if usuario.lower() in ServicioAcceso.USUARIOS_RESERVADOS:
            return False, _("Acceso denegado."), None

        resultado = db_buscar_usuario(usuario, contrasena)
        if not resultado:
            return False, _("Credenciales inválidas."), None

        __, usuario_bd, __, fecha_inicio, fecha_fin, serial = resultado

        es_valida, mensaje_validacion = ServicioLicencias.validar_licencia(
            usuario_bd, serial
        )
        if not es_valida:
            return False, _("Licencia: {0}").format(mensaje_validacion), None

        dias_restantes = ServicioLicencias.dias_restantes(usuario_bd)

        return (
            True,
            _("Autenticación exitosa"),
            {
                "usuario": usuario_bd,
                "serial": serial,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "dias_restantes": dias_restantes,
            },
        )

    @staticmethod
    def guardar_preferencias_sesion(
        usuario: str, contrasena: str, recordar: bool
    ) -> None:
        if recordar:
            guardar_usuario(usuario, contrasena, True)
        else:
            guardar_usuario("", "", False)

    @staticmethod
    def cargar_preferencias_sesion() -> Tuple[str, str, bool]:
        return cargar_usuario()

    @staticmethod
    def verificar_acceso_desarrollador(usuario: str, contrasena: str) -> bool:
        if usuario != ServicioAcceso.DESARROLLADOR_USUARIO:
            return False

        return verificar_desarrollador(usuario, contrasena)

    @staticmethod
    def puede_acceder_a_registro(usuario: str, contrasena: str) -> bool:
        return ServicioAcceso.verificar_acceso_desarrollador(usuario, contrasena)

    @staticmethod
    def crear_usuario_prueba() -> bool:
        usuario_prueba = "prueba"
        contrasena_prueba = "prueba"

        try:
            resultado = db_buscar_usuario(usuario_prueba, contrasena_prueba)
            if resultado:
                return True

            licencia = ServicioLicencias.generar_licencia(
                usuario_prueba, ServicioLicencias.DIAS_PRUEBA
            )

            contrasena_hash = hash_contrasena(contrasena_prueba)
            with conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
                    (
                        usuario_prueba,
                        contrasena_hash,
                        licencia["fecha_inicio"],
                        licencia["fecha_fin"],
                        licencia["serial"],
                    ),
                )

            return True
        except Exception:
            logger.exception("Error al crear usuario de prueba")
            return False
