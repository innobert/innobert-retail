import tkinter as tk
from retail.traducciones import _
from retail.ganancias.diario import Dia
from retail.ganancias.semanal import Semana
from retail.ganancias.mensual import Mes
from retail.ganancias.anual import Year

# Tamaño de ventana aumentado para mejor visualización
from retail.nucleo.configuraciones import VENTANA_GANANCIAS_ANCHO, VENTANA_GANANCIAS_ALTO
VENTANA_ANCHO = VENTANA_GANANCIAS_ANCHO
VENTANA_ALTO = VENTANA_GANANCIAS_ALTO
MENU_ALTO = 40


class GananciasContenedor(tk.Frame):
    def __init__(self, padre, controlador=None):
        super().__init__(padre, width=VENTANA_ANCHO, height=VENTANA_ALTO, bg="#F5F5F5")
        self.controlador = controlador
        self.frames = {}
        self.menu_buttons = {}
        self.seccion_activa = "Día"

        # Frame contenedor para las secciones
        self.frame_contenido = tk.Frame(self, bg="#F5F5F5")
        self.frame_contenido.place(x=0, y=MENU_ALTO, width=VENTANA_ANCHO, height=VENTANA_ALTO - MENU_ALTO)

        self.crear_frames()
        self.crear_menu()
        self.show_frames("Día")

    def crear_frames(self):
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

    def crear_menu(self):
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
            btn = tk.Button(
                frame_menu,
                text=_(nombre),
                font=("Calibri", 13, "bold"),
                bg=color,
                fg="#fff" if nombre == self.seccion_activa else "#222",
                bd=3,               # Borde grueso como en container
                relief="ridge",     # Estilo elevado
                activebackground=color,
                activeforeground="#fff",
                cursor="hand2",
                highlightthickness=0,
                command=lambda n=nombre: self.cambiar_seccion(n),
            )
            btn.place(x=idx * ancho_boton, y=0, width=ancho_boton, height=MENU_ALTO)
            self.menu_buttons[nombre] = btn

        # Línea divisoria bajo el menú
        tk.Frame(self, bg="#BDBDBD", height=2).place(x=0, y=MENU_ALTO, width=VENTANA_ANCHO)
        self.actualizar_menu_visual()

    def cambiar_seccion(self, nombre):
        self.seccion_activa = nombre
        self.show_frames(nombre)
        self.actualizar_menu_visual()

    def actualizar_menu_visual(self):
        """Aplica el efecto de selección: fondo oscuro, texto amarillo y subrayado."""
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
                    relief="flat",
                    bd=0,
                )
                btn.place_configure(rely=0, height=MENU_ALTO - 2)
                if not hasattr(btn, "underline"):
                    underline = tk.Frame(btn.master, bg="#FFD600", height=4)
                    underline.place(x=btn.winfo_x(), y=MENU_ALTO-4, width=btn.winfo_width())
                    btn.underline = underline
                else:
                    btn.underline.place(x=btn.winfo_x(), y=MENU_ALTO-4, width=btn.winfo_width())
            else:
                btn.config(
                    bg=color_normal[nombre],
                    fg="#fff",
                    relief="ridge",
                    bd=3,
                )
                if hasattr(btn, "underline"):
                    btn.underline.place_forget()

    def show_frames(self, nombre):
        for n, frame in self.frames.items():
            if n == nombre:
                frame.tkraise()
            else:
                frame.lower()


def ver_ganancias(parent, pos_x=10, pos_y=5):
    ventana_ganancias = tk.Toplevel(parent)
    ventana_ganancias.title(_("Ganancias"))
    ventana_ganancias.geometry(f"{VENTANA_ANCHO}x{VENTANA_ALTO}+{pos_x}+{pos_y}")
    ventana_ganancias.resizable(False, False)
    ventana_ganancias.configure(bg="#F5F5F5")
    ventana_ganancias.transient(parent)
    ventana_ganancias.grab_set()
    ventana_ganancias.lift()
    GananciasContenedor(ventana_ganancias).pack(fill="both", expand=True)