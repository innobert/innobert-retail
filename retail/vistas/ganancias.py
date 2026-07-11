from __future__ import annotations

import tkinter as tk
from typing import Any
from retail.ganancias.diario import Dia
from retail.ganancias.semanal import Semana
from retail.ganancias.mensual import Mes
from retail.ganancias.anual import Year
from retail.nucleo.configuraciones import crear_boton, BOTON_MENU, FUENTE_BOTON_NEGRITA

# Tamaño de ventana aumentado para mejor visualización
VENTANA_ANCHO = 1300
VENTANA_ALTO = 700
MENU_ALTO = 40


class GananciasContenedor(tk.Frame):
    def __init__(self, padre: Any, controlador: Any | None = None) -> None:
        super().__init__(padre, width=VENTANA_ANCHO, height=VENTANA_ALTO, bg="#F5F5F5")
        self.controlador = controlador
        self.frames: dict[str, Any] = {}
        self.menu_buttons: dict[str, Any] = {}
        self.seccion_activa = "Día"

        # Frame contenedor para las secciones
        self.frame_contenido = tk.Frame(self, bg="#F5F5F5")
        self.frame_contenido.place(
            x=0, y=MENU_ALTO, width=VENTANA_ANCHO, height=VENTANA_ALTO - MENU_ALTO
        )

        self.crear_frames()
        self.crear_menu()
        self.show_frames("Día")

    def crear_frames(self) -> None:
        secciones = {
            "Día": Dia,
            "Semana": Semana,
            "Mes": Mes,
            "Año": Year,
        }
        for nombre, clase in secciones.items():
            frame = clase(self.frame_contenido)
            self.frames[nombre] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

    def crear_menu(self) -> None:
        frame_menu = tk.Frame(self, height=MENU_ALTO, bg="#E6D9E3")
        frame_menu.place(x=0, y=0, width=VENTANA_ANCHO, height=MENU_ALTO)

        secciones = [
            ("Día", "#00B8D4"),
            ("Semana", "#8E24AA"),
            ("Mes", "#FFB300"),
            ("Año", "#43A047"),
        ]
        ancho_boton = VENTANA_ANCHO // len(secciones)

        for idx, (nombre, color) in enumerate(secciones):
            btn = crear_boton(
                frame_menu,
                nombre,
                estilo=BOTON_MENU,
                fuente=FUENTE_BOTON_NEGRITA,
                comando=lambda n=nombre: self.cambiar_seccion(n),
            )
            btn.place(x=idx * ancho_boton, y=0, width=ancho_boton, height=MENU_ALTO)
            self.menu_buttons[nombre] = btn

        # Línea divisoria bajo el menú
        tk.Frame(self, bg="#BDBDBD", height=2).place(
            x=0, y=MENU_ALTO, width=VENTANA_ANCHO
        )
        self.actualizar_menu_visual()

    def cambiar_seccion(self, nombre: str) -> None:
        self.seccion_activa = nombre
        self.show_frames(nombre)
        self.actualizar_menu_visual()

    def actualizar_menu_visual(self) -> None:
        color_normal = {
            "Día": "#00B8D4",
            "Semana": "#8E24AA",
            "Mes": "#FFB300",
            "Año": "#43A047",
        }
        for nombre, btn in self.menu_buttons.items():
            if nombre == self.seccion_activa:
                btn.config(
                    bg="#212121",
                    fg="#FFD600",
                )
            else:
                btn.config(
                    bg=color_normal[nombre],
                    fg="#fff",
                )

    def show_frames(self, nombre: str) -> None:
        for n, frame in self.frames.items():
            if n == nombre:
                frame.tkraise()
            else:
                frame.lower()


def ver_ganancias(parent: Any, pos_x: int = 10, pos_y: int = 5) -> None:
    ventana_ganancias = tk.Toplevel(parent)
    ventana_ganancias.title("Ganancias")
    ventana_ganancias.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}+{pos_x}+{pos_y}")
    ventana_ganancias.resizable(False, False)
    ventana_ganancias.configure(bg="#F5F5F5")
    ventana_ganancias.transient(parent)
    ventana_ganancias.grab_set()
    ventana_ganancias.lift()
    GananciasContenedor(ventana_ganancias).pack(fill="both", expand=True)
