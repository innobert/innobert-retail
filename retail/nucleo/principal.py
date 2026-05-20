import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import re
from retail.sesion.acceso import Acceso
from retail.vistas.contenedor import Contenedor
import retail.nucleo.base_datos as base_de_datos


class Principal(tk.Tk):
    # Configuración de tamaños y posiciones
    ACCESO_ANCHO = 1000
    ACCESO_ALTO = 700
    ACCESO_X = 100
    ACCESO_Y = 10
    
    CONTENEDOR_ANCHO = 1100
    CONTENEDOR_ALTO = 650
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
            base_de_datos.create_tables()
        except Exception as e:
            print(f"Warning: error al crear o asegurar la base de datos: {e}")

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