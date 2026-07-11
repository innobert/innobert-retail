from __future__ import annotations

import json
import logging
import os
import sys
import shutil
import subprocess
import time
import threading
from pathlib import Path
from typing import Any

registrador = logging.getLogger(__name__)


def _cargar_dotenv(ruta: str | Path = ".env") -> None:
    archivo = Path(ruta).resolve()
    if not archivo.exists():
        archivo = Path(__file__).parent / ".env"
    if not archivo.exists():
        archivo = Path(__file__).parent.parent.parent / ".env"
    if not archivo.exists():
        return
    with open(archivo, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            clave = clave.strip()
            valor = valor.strip().strip("\"'")
            if clave and not os.environ.get(clave):
                os.environ[clave] = valor


_cargar_dotenv()


def configurar_logging() -> None:
    from logging.handlers import RotatingFileHandler

    log_dir = os.environ.get("RETAIL_LOG_DIR")
    if log_dir:
        carpeta_log = Path(log_dir)
    else:
        carpeta_log = Path(_obtener_ruta_datos_usuario()) / "logs"
    carpeta_log.mkdir(parents=True, exist_ok=True)
    ruta_log = carpeta_log / "app.log"

    manejador = RotatingFileHandler(
        ruta_log, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    manejador.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    nivel = getattr(logging, os.environ.get("RETAIL_LOG_LEVEL", "DEBUG").upper(), logging.DEBUG)
    raiz = logging.getLogger()
    raiz.setLevel(nivel)
    raiz.addHandler(manejador)


def _obtener_ruta_datos_usuario() -> str:
    sobreescrita = os.environ.get("RETAIL_DATA_DIR")
    if sobreescrita:
        return str(Path(sobreescrita))
    if sys.platform == "win32":
        datos_app = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        datos_app = str(Path.home() / "Library" / "Application Support")
    else:
        datos_app = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return str(Path(datos_app) / "InnobertRetail")


APPDATA_PATH = _obtener_ruta_datos_usuario()
FOTOS_PATH = str(Path(APPDATA_PATH) / "fotos")
LOGO_PATH = str(Path(APPDATA_PATH) / "Logo")

# =========================
# CONSTANTES DE TEMA Y UI
# =========================

# Colores
COLOR_FONDO = "#E6D9E3"
COLOR_FONDO_EDITAR = "#F4F6F8"
COLOR_FONDO_TABLA = "#F5F5F5"
COLOR_AZUL = "#2196F3"
COLOR_VERDE = "#4CAF50"
COLOR_ROJO = "#F44336"

# Fuentes
FUENTE_ETIQUETA = ("Helvetica", 12, "bold")
FUENTE_BOTON = ("Segoe UI", 10)
FUENTE_BOTON_NEGRITA = ("Segoe UI", 10, "bold")
FUENTE_BOTON_GRANDE = ("Segoe UI", 11, "bold")

# =========================
# ESTILOS DE BOTONES
# =========================
# Esquemas de color semánticos para botones clásicos de escritorio
BOTON_ACCION =       {"bg": "#1976D2", "fg": "#FFFFFF", "activebackground": "#1565C0", "activeforeground": "#FFFFFF"}
BOTON_EXITO =        {"bg": "#388E3C", "fg": "#FFFFFF", "activebackground": "#2E7D32", "activeforeground": "#FFFFFF"}
BOTON_PELIGRO =      {"bg": "#D32F2F", "fg": "#FFFFFF", "activebackground": "#C62828", "activeforeground": "#FFFFFF"}
BOTON_ADVERTENCIA =  {"bg": "#E65100", "fg": "#FFFFFF", "activebackground": "#D84315", "activeforeground": "#FFFFFF"}
BOTON_INFO =         {"bg": "#7B1FA2", "fg": "#FFFFFF", "activebackground": "#6A1B9A", "activeforeground": "#FFFFFF"}
BOTON_NEUTRO =       {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#455A64", "activeforeground": "#FFFFFF"}
BOTON_NAV =          {"bg": "#1976D2", "fg": "#FFFFFF", "activebackground": "#1565C0", "activeforeground": "#FFFFFF"}
BOTON_MENU =         {"bg": "#455A64", "fg": "#FFFFFF", "activebackground": "#37474F", "activeforeground": "#FFFFFF"}
BOTON_IMPORTAR =     {"bg": "#1976D2", "fg": "#FFFFFF", "activebackground": "#1565C0", "activeforeground": "#FFFFFF"}
BOTON_CERRAR =       {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#455A64", "activeforeground": "#FFFFFF"}
BOTON_CARITO =       {"bg": "#9CCC65", "fg": "#1B5E20", "activebackground": "#8BC34A", "activeforeground": "#1B5E20"}

# =========================
# PALETA VENTAS (tonos azules/fríos)
# =========================
VENTAS_BOTON_ACCION =      {"bg": "#1565C0", "fg": "#FFFFFF", "activebackground": "#0D47A1", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_EXITO =       {"bg": "#2E7D32", "fg": "#FFFFFF", "activebackground": "#1B5E20", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_PELIGRO =     {"bg": "#C62828", "fg": "#FFFFFF", "activebackground": "#B71C1C", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_ADVERTENCIA = {"bg": "#E65100", "fg": "#FFFFFF", "activebackground": "#BF360C", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_INFO =        {"bg": "#6A1B9A", "fg": "#FFFFFF", "activebackground": "#4A148C", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_NEUTRO =      {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#37474F", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_NAV =         {"bg": "#1565C0", "fg": "#FFFFFF", "activebackground": "#0D47A1", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_CERRAR =      {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#37474F", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_IMPORTAR =    {"bg": "#1565C0", "fg": "#FFFFFF", "activebackground": "#0D47A1", "activeforeground": "#FFFFFF"}
VENTAS_BOTON_CARITO =      {"bg": "#42A5F5", "fg": "#0D47A1", "activebackground": "#1E88E5", "activeforeground": "#FFFFFF"}

# =========================
# PALETA DEUDAS (tonos rojos/cálidos)
# =========================
DEUDAS_BOTON_ACCION =      {"bg": "#D84315", "fg": "#FFFFFF", "activebackground": "#BF360C", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_EXITO =       {"bg": "#558B2F", "fg": "#FFFFFF", "activebackground": "#33691E", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_PELIGRO =     {"bg": "#B71C1C", "fg": "#FFFFFF", "activebackground": "#880E4F", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_ADVERTENCIA = {"bg": "#E65100", "fg": "#FFFFFF", "activebackground": "#BF360C", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_INFO =        {"bg": "#7B1FA2", "fg": "#FFFFFF", "activebackground": "#4A148C", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_NEUTRO =      {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#37474F", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_NAV =         {"bg": "#D84315", "fg": "#FFFFFF", "activebackground": "#BF360C", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_CERRAR =      {"bg": "#546E7A", "fg": "#FFFFFF", "activebackground": "#37474F", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_IMPORTAR =    {"bg": "#D84315", "fg": "#FFFFFF", "activebackground": "#BF360C", "activeforeground": "#FFFFFF"}
DEUDAS_BOTON_CARITO =      {"bg": "#EF5350", "fg": "#B71C1C", "activebackground": "#E53935", "activeforeground": "#FFFFFF"}

_BASE_BOTON = {
    "font": FUENTE_BOTON,
    "relief": "groove",
    "bd": 1,
    "cursor": "hand2",
    "padx": 12,
    "pady": 4,
}


def crear_boton(
    parent: Any,
    texto: str,
    estilo: dict[str, str] | None = None,
    comando=None,
    fuente=None,
    **kwargs,
):
    import tkinter as tk

    props = dict(_BASE_BOTON)
    if estilo:
        props.update(estilo)
    if fuente:
        props["font"] = fuente
    props["text"] = texto
    if comando is not None:
        props["command"] = comando
    props.update(kwargs)
    return tk.Button(parent, **props)

# Paginación
PRODUCTOS_POR_PAGINA = 12
TAMANO_VENTANA = "1300x700"


def copiar_fotos_por_defecto() -> None:
    ruta_proyecto = Path(__file__).parent.parent.parent.resolve()
    carpeta_fotos_origen = ruta_proyecto / "fotos"
    if carpeta_fotos_origen.exists():
        if not Path(FOTOS_PATH).exists():
            try:
                shutil.copytree(str(carpeta_fotos_origen), FOTOS_PATH)
            except Exception as e:
                registrador.exception("Error al copiar la carpeta de fotos por defecto")
        else:
            origen_defecto = carpeta_fotos_origen / "default.png"
            destino_defecto = Path(FOTOS_PATH) / "default.png"
            if origen_defecto.exists() and not destino_defecto.exists():
                try:
                    shutil.copy2(str(origen_defecto), str(destino_defecto))
                except Exception as e:
                    registrador.exception("Error al copiar default.png")
    try:
        raiz_defecto_destino = Path(APPDATA_PATH) / "default.png"
        origen_defecto = carpeta_fotos_origen / "default.png"
        if origen_defecto.exists() and not raiz_defecto_destino.exists():
            try:
                shutil.copy2(str(origen_defecto), str(raiz_defecto_destino))
            except Exception as e:
                registrador.exception("Error al copiar default.png a APPDATA_PATH")
    except Exception:
        registrador.warning("Error al copiar default.png a la raíz de APPDATA_PATH", exc_info=True)


def copiar_logo_por_defecto() -> None:
    ruta_proyecto = Path(__file__).parent.parent.parent.resolve()
    logo_origen = ruta_proyecto / "img" / "logo.png"
    logo_destino = Path(LOGO_PATH) / "logo.png"
    if logo_origen.exists():
        if not Path(LOGO_PATH).exists():
            Path(LOGO_PATH).mkdir(parents=True, exist_ok=True)
        if not logo_destino.exists():
            try:
                shutil.copy2(str(logo_origen), str(logo_destino))
            except Exception as e:
                registrador.exception("Error al copiar logo.png por defecto")


def asegurar_directorios() -> None:
    Path(APPDATA_PATH).mkdir(parents=True, exist_ok=True)
    Path(FOTOS_PATH).mkdir(parents=True, exist_ok=True)
    Path(LOGO_PATH).mkdir(parents=True, exist_ok=True)
    Path(obtener_ruta_config_dir()).mkdir(parents=True, exist_ok=True)
    copiar_fotos_por_defecto()
    copiar_logo_por_defecto()


def rutas(ruta_relativa: str) -> str:
    return str(Path(APPDATA_PATH) / ruta_relativa)


def obtener_ruta_base_datos() -> str:
    nombre_db = os.environ.get("RETAIL_DB_NAME", "pos.db")
    return str(Path(APPDATA_PATH) / nombre_db)


def obtener_ruta_config_dir() -> str:
    return str(Path(APPDATA_PATH) / "config")


def obtener_ruta_config() -> str:
    return str(Path(obtener_ruta_config_dir()) / "config.json")


def obtener_ruta_pdf_config() -> str:
    return str(Path(obtener_ruta_config_dir()) / "pdf_config.json")


def obtener_ruta_img(nombre_img: str = "") -> str:
    if nombre_img:
        return str(Path(FOTOS_PATH) / nombre_img)
    return FOTOS_PATH


def obtener_ruta_fotos(nombre_foto: str = "") -> str:
    if nombre_foto:
        return str(Path(FOTOS_PATH) / nombre_foto)
    return FOTOS_PATH


def obtener_ruta_icon(nombre_icon: str = "") -> str:
    if nombre_icon:
        return str(Path(APPDATA_PATH) / nombre_icon)
    return APPDATA_PATH


def obtener_ruta_logo(nombre_logo: str = "") -> str:
    if nombre_logo:
        return str(Path(LOGO_PATH) / nombre_logo)
    return LOGO_PATH


def obtener_ruta_carpeta_ventas() -> str:
    return str(Path.home() / "Desktop" / "ventas")


def ruta_recurso(ruta_relativa: str) -> str:
    if getattr(sys, "frozen", False):
        ruta_base = sys._MEIPASS
    else:
        ruta_base = Path(__file__).parent.parent.parent.resolve()
    return str(Path(ruta_base) / ruta_relativa)


def eliminar_base_datos() -> None:
    ruta_bd = obtener_ruta_base_datos()
    try:
        if Path(ruta_bd).exists():
            Path(ruta_bd).unlink()
    except Exception as e:
        registrador.exception("Error al eliminar la base de datos")


def eliminar_datos_completos() -> bool:
    if Path(APPDATA_PATH).exists():
        try:
            shutil.rmtree(APPDATA_PATH)
            return True
        except Exception as e:
            registrador.exception("Error al eliminar la carpeta de datos")
            return False
    return False


def guardar_usuario(usuario: str, contrasena: str, recordar: bool) -> None:
    from retail.nucleo.cifrado import cifrar

    try:
        with open(obtener_ruta_config(), "w") as f:
            json.dump(
                {
                    "usuario": usuario if recordar else "",
                    "contrasena": cifrar(contrasena) if recordar else "",
                    "recordar": recordar,
                },
                f,
            )
    except Exception as e:
        registrador.exception("Error al guardar la configuración de usuario")


def cargar_usuario() -> tuple[str, str, bool]:
    from retail.nucleo.cifrado import descifrar

    try:
        with open(obtener_ruta_config(), "r") as f:
            config = json.load(f)
            recordar = config.get("recordar", False)
            if recordar:
                usuario = config.get("usuario", "")
                contrasena = descifrar(config.get("contrasena", ""))
                return usuario, contrasena, recordar
            else:
                return "", "", recordar
    except FileNotFoundError:
        return "", "", False


# ========== FUNCIONES PARA PDF ==========


def _obtener_config_pdf() -> Any:
    ruta_config = obtener_ruta_pdf_config()
    try:
        with open(ruta_config, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _guardar_config_pdf(config: dict[str, Any]) -> None:
    ruta_config = obtener_ruta_pdf_config()
    try:
        with open(ruta_config, "w") as f:
            json.dump(config, f)
    except Exception as e:
        registrador.exception("Error guardando configuración de PDF")


def guardar_ultima_carpeta_pdf(tipo: str, carpeta: str) -> None:
    config = _obtener_config_pdf()
    config[tipo] = carpeta
    _guardar_config_pdf(config)


def cargar_ultima_carpeta_pdf(tipo: str) -> Any:
    config = _obtener_config_pdf()
    carpeta = config.get(tipo, "")
    if carpeta and Path(carpeta).exists():
        return carpeta
    return str(Path.home() / "Desktop")


def abrir_archivo(ruta: str) -> None:
    if sys.platform == "win32":
        os.startfile(ruta)

        def traer_al_frente() -> None:
            time.sleep(0.5)
            try:
                import ctypes

                manejador_ventana = ctypes.windll.user32.FindWindowW(None, Path(ruta).name)
                if manejador_ventana:
                    ctypes.windll.user32.SetForegroundWindow(manejador_ventana)
                    ctypes.windll.user32.ShowWindow(manejador_ventana, 5)
            except Exception as e:
                registrador.warning("No se pudo traer la ventana al frente: %s", e)

        threading.Thread(target=traer_al_frente, daemon=True).start()
    elif sys.platform == "darwin":
        subprocess.run(["open", ruta])
    else:
        subprocess.run(["xdg-open", ruta])
