"""
servicio_acceso.py

Servicio para gestionar la autenticación de usuarios, validación de licencia y gestión de sesión.
El módulo de sesión está independizado y desacoplado del resto del sistema.
"""
import logging
from typing import Optional, Tuple
from retail.nucleo.base_datos import obtener_conexion, buscar_usuario as db_buscar_usuario
from retail.nucleo.configuraciones import guardar_usuario, cargar_usuario
from retail.nucleo.seguridad import hash_contrasena, verificar_contrasena
from retail.nucleo.servicios.sesion.servicio_licencias import ServicioLicencias


class ServicioAcceso:
    """
    Servicio para operaciones de acceso y autenticación.
    Módulo independizado de sesión que valida usuario, contraseña y licencia.
    """

    # Usuarios protegidos
    USUARIOS_RESERVADOS = {"admin", "administrator", "root", "sistema"}
    
    # Información del desarrollador (hash seguro, no almacenar credenciales en texto)
    DESARROLLADOR_USUARIO = "innobertdev"
    DESARROLLADOR_HASH = hash_contrasena("ingsoftware.99")

    @staticmethod
    def autenticar_usuario(usuario: str, contrasena: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Autentica al usuario. Valida usuario, contraseña y licencia.
        
        Retorna: (éxito, mensaje, datos_usuario)
        Datos_usuario contiene: usuario, serial, fecha_inicio, fecha_fin, dias_restantes
        """
        if not usuario or not contrasena:
            return False, "Credenciales incompletas.", None

        # Bloquear usuarios reservados
        if usuario.lower() in ServicioAcceso.USUARIOS_RESERVADOS:
            # Mensaje genérico para mayor seguridad
            return False, "Acceso denegado.", None

        # Buscar usuario en BD
        resultado = db_buscar_usuario(usuario, contrasena)
        if not resultado:
            # Mensaje genérico (no revelar si existe usuario o no)
            return False, "Credenciales inválidas.", None

        # resultado es una tupla: (id, usuario, contrasena_hash, fecha_inicio, fecha_fin, serial)
        _, usuario_bd, _, fecha_inicio, fecha_fin, serial = resultado

        # Validar licencia usando el servicio independizado
        es_valida, mensaje_validacion = ServicioLicencias.validar_licencia(usuario_bd, serial)
        if not es_valida:
            # Mostrar estado real de licencia sin rutas de BD
            return False, f"Licencia: {mensaje_validacion}", None

        # Calcular días restantes
        dias_restantes = ServicioLicencias.dias_restantes(usuario_bd)

        return True, "Autenticación exitosa", {
            "usuario": usuario_bd,
            "serial": serial,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias_restantes": dias_restantes
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
    def verificar_acceso_desarrollador(usuario: str, contrasena: str) -> bool:
        """
        Verifica si el usuario tiene permisos de desarrollador.
        NOTA: Esta verificación está oculta para mayor seguridad en compilados.
        """
        if usuario != ServicioAcceso.DESARROLLADOR_USUARIO:
            return False
        
        return verificar_contrasena(contrasena, ServicioAcceso.DESARROLLADOR_HASH)

    @staticmethod
    def puede_acceder_a_registro(usuario: str, contrasena: str) -> bool:
        """
        Solo el desarrollador puede acceder al registro de usuarios.
        Esto está restringido por seguridad.
        """
        return ServicioAcceso.verificar_acceso_desarrollador(usuario, contrasena)

    @staticmethod
    def crear_usuario_prueba() -> bool:
        """
        Crea usuario de prueba con licencia de 30 días.
        Esto se ejecuta una única vez en inicialización.
        """
        usuario_prueba = "prueba"
        contrasena_prueba = "prueba"
        
        try:
            # Verificar si ya existe
            resultado = db_buscar_usuario(usuario_prueba, contrasena_prueba)
            if resultado:
                return True  # Ya existe
            
            # Generar licencia
            licencia = ServicioLicencias.generar_licencia(usuario_prueba, ServicioLicencias.DIAS_PRUEBA)
            
            # Crear en BD
            contrasena_hash = hash_contrasena(contrasena_prueba)
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
                (usuario_prueba, contrasena_hash, licencia["fecha_inicio"], licencia["fecha_fin"], licencia["serial"])
            )
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            logging.error(f"Error al crear usuario de prueba: {e}")
            return False
