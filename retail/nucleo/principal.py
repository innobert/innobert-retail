import logging
import tkinter as tk
from tkinter import ttk
from retail.sesion.acceso import Acceso
from retail.vistas.contenedor import Contenedor
import retail.nucleo.base_datos as base_de_datos
from retail.nucleo.configuraciones import VENTANA_ACCESO_ANCHO, VENTANA_ACCESO_ALTO, VENTANA_CONTENEDOR_ANCHO, VENTANA_CONTENEDOR_ALTO


class Principal(tk.Tk):
    ACCESO_ANCHO = VENTANA_ACCESO_ANCHO
    ACCESO_ALTO = VENTANA_ACCESO_ALTO
    ACCESO_X = 100
    ACCESO_Y = 10
    CONTENEDOR_ANCHO = VENTANA_CONTENEDOR_ANCHO
    CONTENEDOR_ALTO = VENTANA_CONTENEDOR_ALTO
    CONTENEDOR_X = 100
    CONTENEDOR_Y = 10
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Innobert Retail")
        self.config(bg="#E6D9E3")
        self.resizable(False, False)
        self.maxsize(1400, 850)

        self.usuario_actual = None

        try:
            base_de_datos.crear_tablas()
        except Exception as e:
            logging.warning(f"Error al crear o asegurar la base de datos: {e}")

        # Configurar tema ttk
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background="#E6D9E3")
        style.configure("TLabel", background="#E6D9E3")
        style.configure("TFrame", background="#E6D9E3")
        style.configure("TButton", background="#E6D9E3")

        self.frames = {}
        self.frames["Acceso"] = Acceso(self, self)
        self.frames["Contenedor"] = Contenedor(self, self)
        self.show_frame("Acceso")

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.place_forget()
        frame = self.frames[frame_name]
        frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        if frame_name == "Acceso":
            self.geometry(f"{self.ACCESO_ANCHO}x{self.ACCESO_ALTO}+{self.ACCESO_X}+{self.ACCESO_Y}")
        else:
            self.geometry(f"{self.CONTENEDOR_ANCHO}x{self.CONTENEDOR_ALTO}+{self.CONTENEDOR_X}+{self.CONTENEDOR_Y}")