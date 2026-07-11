from __future__ import annotations

import logging
from typing import Any
import tkinter as tk
from tkinter import ttk
from retail.sesion.acceso import Acceso
from retail.vistas.contenedor import Contenedor
import retail.nucleo.base_datos as base_de_datos
from retail.nucleo.configuraciones import configurar_logging, COLOR_FONDO

registrador = logging.getLogger(__name__)


class Principal(tk.Tk):
    ACCESO_ANCHO = 1000
    ACCESO_ALTO = 700
    ACCESO_X = 100
    ACCESO_Y = 10

    CONTENEDOR_ANCHO = 1100
    CONTENEDOR_ALTO = 650
    CONTENEDOR_X = 100
    CONTENEDOR_Y = 10

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title("Innobert Retail")
        self.config(bg=COLOR_FONDO)
        self.resizable(False, False)
        self.maxsize(1400, 850)

        self.usuario_actual = None

        configurar_logging()
        try:
            base_de_datos.crear_tablas()
        except Exception as e:
            registrador.warning("Error al crear o asegurar la base de datos: %s", e)

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background=COLOR_FONDO)
        estilo.configure("TLabel", background=COLOR_FONDO)
        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TButton", background=COLOR_FONDO)

        self.frames: dict[str, Any] = {}
        self.frames["Acceso"] = Acceso(self, self)
        self.frames["Contenedor"] = Contenedor(self, self)
        self.show_frame("Acceso")

    def show_frame(self, nombre_frame: str) -> None:
        for marco in self.frames.values():
            marco.place_forget()
        marco = self.frames[nombre_frame]
        marco.place(x=0, y=0, relwidth=1, relheight=1)

        if nombre_frame == "Acceso":
            self.geometry(
                f"{self.ACCESO_ANCHO}x{self.ACCESO_ALTO}+{self.ACCESO_X}+{self.ACCESO_Y}"
            )
        else:
            self.geometry(
                f"{self.CONTENEDOR_ANCHO}x{self.CONTENEDOR_ALTO}+{self.CONTENEDOR_X}+{self.CONTENEDOR_Y}"
            )
