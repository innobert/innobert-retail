import json
import logging
import os
import sys
import shutil
import subprocess
import time
import threading
from typing import Optional

def _obtener_ruta_base_datos_usuario() -> str:
    """
    Devuelve la ruta base para los datos de la aplicación según el sistema operativo.
    """
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
    elif sys.platform == "darwin":
        appdata = os.path.expanduser("~/Library/Application Support")
    else:
        appdata = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(appdata, "InnobertRetail")

def configurar_logging():
    try:
        ruta_log = os.path.join(_obtener_ruta_base_datos_usuario(), "app.log")
        os.makedirs(os.path.dirname(ruta_log), exist_ok=True)
    except (OSError, PermissionError):
        ruta_log = "app.log"
    logging.basicConfig(
        filename=ruta_log,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

configurar_logging()

APPDATA_PATH = _obtener_ruta_base_datos_usuario()
FOTOS_PATH = os.path.join(APPDATA_PATH, "fotos")
LOGO_PATH = os.path.join(APPDATA_PATH, "Logo")

PRODUCTOS_POR_PAGINA = 12
VENTANA_ACCESO_ANCHO = 1000
VENTANA_ACCESO_ALTO = 700
VENTANA_CONTENEDOR_ANCHO = 1100
VENTANA_CONTENEDOR_ALTO = 650
VENTANA_GANANCIAS_ANCHO = 1300
VENTANA_GANANCIAS_ALTO = 700

def copiar_fotos_default():
    """
    Copia la carpeta 'fotos' (y su contenido) desde la raíz del proyecto a APPDATA_PATH/fotos si no existe.
    """
    ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    carpeta_fotos_origen = os.path.join(ruta_proyecto, "fotos")
    if os.path.exists(carpeta_fotos_origen):
        if not os.path.exists(FOTOS_PATH):
            try:
                shutil.copytree(carpeta_fotos_origen, FOTOS_PATH)
            except Exception as e:
                logging.error(f"Error al copiar la carpeta de fotos por defecto: {e}")
        else:
            default_src = os.path.join(carpeta_fotos_origen, "default.png")
            default_dst = os.path.join(FOTOS_PATH, "default.png")
            if os.path.exists(default_src) and not os.path.exists(default_dst):
                try:
                    shutil.copy2(default_src, default_dst)
                except Exception as e:
                    logging.error(f"Error al copiar default.png: {e}")
    # A veces el código busca default.png directamente en APPDATA_PATH
    # Para evitar errores, copiar también default.png a la raíz de APPDATA_PATH si no existe
    try:
        default_root_dst = os.path.join(APPDATA_PATH, "default.png")
        default_src = os.path.join(carpeta_fotos_origen, "default.png")
        if os.path.exists(default_src) and not os.path.exists(default_root_dst):
            try:
                shutil.copy2(default_src, default_root_dst)
            except Exception as e:
                logging.error(f"Error al copiar default.png a APPDATA_PATH: {e}")
    except Exception:
        pass

def copiar_logo_default():
    """
    Copia la imagen 'logo.png' desde la carpeta img del proyecto a APPDATA_PATH/Logo si no existe.
    """
    ruta_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    logo_src = os.path.join(ruta_proyecto, "img", "logo.png")
    logo_dst = os.path.join(LOGO_PATH, "logo.png")
    if os.path.exists(logo_src):
        if not os.path.exists(LOGO_PATH):
            os.makedirs(LOGO_PATH, exist_ok=True)
        if not os.path.exists(logo_dst):
            try:
                shutil.copy2(logo_src, logo_dst)
            except Exception as e:
                logging.error(f"Error al copiar logo.png por defecto: {e}")

def asegurar_directorios():
    os.makedirs(APPDATA_PATH, exist_ok=True)
    os.makedirs(FOTOS_PATH, exist_ok=True)
    os.makedirs(LOGO_PATH, exist_ok=True)
    os.makedirs(obtener_ruta_config_dir(), exist_ok=True)
    copiar_fotos_default()
    copiar_logo_default()

def rutas(rel_path):
    return os.path.join(APPDATA_PATH, rel_path)

def obtener_ruta_base_datos():
    return os.path.join(APPDATA_PATH, "pos.db")

def obtener_ruta_config_dir():
    """Devuelve la ruta de la carpeta de configuración dentro de APPDATA."""
    return os.path.join(APPDATA_PATH, "config")

def obtener_ruta_config():
    """Devuelve la ruta del archivo config.json dentro de la carpeta config."""
    return os.path.join(obtener_ruta_config_dir(), "config.json")

def obtener_ruta_pdf_config():
    """Devuelve la ruta del archivo pdf_config.json dentro de la carpeta config."""
    return os.path.join(obtener_ruta_config_dir(), "pdf_config.json")

def obtener_ruta_img(nombre_img=""):
    if nombre_img:
        return os.path.join(FOTOS_PATH, nombre_img)
    return FOTOS_PATH

def obtener_ruta_fotos(nombre_foto=""):
    if nombre_foto:
        return os.path.join(FOTOS_PATH, nombre_foto)
    return FOTOS_PATH

def obtener_ruta_icon(nombre_icon=""):
    if nombre_icon:
        return os.path.join(APPDATA_PATH, nombre_icon)
    return APPDATA_PATH

def obtener_ruta_logo(nombre_logo=""):
    if nombre_logo:
        return os.path.join(LOGO_PATH, nombre_logo)
    return LOGO_PATH

def obtener_ruta_carpeta_ventas():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    carpeta_ventas = os.path.join(desktop, "ventas")
    return carpeta_ventas

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

def eliminar_base_datos():
    db_path = obtener_ruta_base_datos()
    if os.path.exists(db_path):
        os.remove(db_path)

def eliminar_datos_completos():
    if os.path.exists(APPDATA_PATH):
        try:
            shutil.rmtree(APPDATA_PATH)
            return True
        except Exception as e:
            logging.error(f"Error al eliminar la carpeta de datos: {e}")
            return False
    return False

def guardar_usuario(usuario, contrasena, recordar):
    from retail.nucleo.cifrado import cifrar
    with open(obtener_ruta_config(), "w") as f:
        json.dump({"usuario": usuario, "contrasena": cifrar(contrasena), "recordar": recordar}, f)

def cargar_usuario():
    try:
        with open(obtener_ruta_config(), "r") as f:
            config = json.load(f)
            recordar = config.get("recordar", False)
            if recordar:
                from retail.nucleo.cifrado import descifrar
                return config.get("usuario", ""), descifrar(config.get("contrasena", "")), recordar
            else:
                return "", "", recordar
    except FileNotFoundError:
        return "", "", False

# ========== NUEVAS FUNCIONES PARA PDF CON TIPOS INDEPENDIENTES ==========

def _obtener_config_pdf() -> dict:
    """Carga el archivo pdf_config.json y devuelve un diccionario."""
    ruta_config = obtener_ruta_pdf_config()
    try:
        with open(ruta_config, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _guardar_config_pdf(config: dict):
    """Guarda el diccionario de configuración en pdf_config.json."""
    ruta_config = obtener_ruta_pdf_config()
    try:
        with open(ruta_config, "w") as f:
            json.dump(config, f)
    except Exception as e:
        logging.error(f"Error guardando configuración de PDF: {e}")

def guardar_ultima_carpeta_pdf(tipo: str, carpeta: str):
    """
    Guarda la última carpeta utilizada para un tipo específico de PDF.
    Tipos: 'ventas', 'deudas', 'ganancias'
    """
    config = _obtener_config_pdf()
    config[tipo] = carpeta
    _guardar_config_pdf(config)

def cargar_ultima_carpeta_pdf(tipo: str) -> str:
    """
    Carga la última carpeta utilizada para un tipo específico de PDF.
    Si no existe, devuelve el escritorio.
    Tipos: 'ventas', 'deudas', 'ganancias'
    """
    config = _obtener_config_pdf()
    carpeta = config.get(tipo, "")
    if carpeta and os.path.exists(carpeta):
        return carpeta
    return os.path.join(os.path.expanduser("~"), "Desktop")

def abrir_archivo(ruta: str):
    """Abre un archivo con la aplicación predeterminada del sistema y lo trae al frente."""
    if sys.platform == "win32":
        os.startfile(ruta)
        # Intenta traer la ventana al frente después de un breve retraso
        def traer_al_frente():
            time.sleep(0.5)
            try:
                import ctypes
                hwnd = ctypes.windll.user32.FindWindowW(None, os.path.basename(ruta))
                if hwnd:
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
            except Exception as e:
                logging.warning(f"No se pudo traer la ventana al frente: {e}")
        threading.Thread(target=traer_al_frente, daemon=True).start()
    elif sys.platform == "darwin":  # macOS
        subprocess.run(["open", ruta])
    else:  # Linux
        subprocess.run(["xdg-open", ruta])