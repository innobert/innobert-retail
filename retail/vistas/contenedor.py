"""
contenedor.py

Vista principal del sistema de gestión de licorería.
Contiene el contenedor principal que organiza y muestra las diferentes secciones del software:
Ventas, Clientes, Inventario y Deudas. Proporciona un menú superior para navegar entre ellas.

Autor: [Innobert]
"""

import tkinter as tk
import os
from PIL import Image, ImageTk
from retail.vistas.ventas import Ventas
from retail.vistas.clientes import Clientes
from retail.vistas.inventario import Inventario
from retail.vistas.deudas import Deudas
from retail.nucleo.configuraciones import rutas

from retail.nucleo.configuraciones import VENTANA_CONTENEDOR_ANCHO, VENTANA_CONTENEDOR_ALTO
VENTANA_ANCHO = VENTANA_CONTENEDOR_ANCHO
VENTANA_ALTO = VENTANA_CONTENEDOR_ALTO
MENU_ALTO = 40


class Contenedor(tk.Frame):
    """
    Contenedor principal de la aplicación.
    Gestiona la visualización de las diferentes secciones mediante un menú superior.
    """

    def __init__(self, padre, controlador):
        super().__init__(padre, bg="#E6D9E3")
        self.controlador = controlador
        self.frames = {}
        self.menu_buttons = {}
        self.seccion_activa = "Ventas"

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Ruta absoluta a la carpeta img en la raíz del proyecto
        RUTA_IMG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))

        # Cargar imágenes y mantener referencias
        self.iconos = {
            "Ventas": ImageTk.PhotoImage(
                Image.open(os.path.join(RUTA_IMG, "ventas.png")).resize((26, 26))
            ),
            "Clientes": ImageTk.PhotoImage(
                Image.open(os.path.join(RUTA_IMG, "clientes.png")).resize((26, 26))
            ),
            "Inventario": ImageTk.PhotoImage(
                Image.open(os.path.join(RUTA_IMG, "inventario.png")).resize((26, 26))
            ),
            "Deudas": ImageTk.PhotoImage(
                Image.open(os.path.join(RUTA_IMG, "deuda.png")).resize((26, 26))
            ),
        }

        # Exponer métodos de navegación a través del controlador
        self._registrar_metodos_navegacion()

        self.crear_frames()
        self.crear_menu()

    def _registrar_metodos_navegacion(self):
        """Asigna métodos de navegación al controlador para que las vistas puedan usarlos sin acoplamiento."""
        self.controlador.abrir_edicion_deuda = self.abrir_edicion_deuda
        self.controlador.abrir_historial_deuda = self.abrir_historial_deuda
        self.controlador.abrir_facturas_deudas = self.abrir_facturas_deudas
        self.controlador.abrir_deudas_pagadas = self.abrir_deudas_pagadas
        self.controlador.abrir_carrito_deuda = self.abrir_carrito_deuda
        self.controlador.abrir_papelera_deudas = self.abrir_papelera_deudas  # NUEVO
        # Métodos para ventas (si se necesitan)
        self.controlador.abrir_edicion_factura = self.abrir_edicion_factura
        self.controlador.abrir_historial_venta = self.abrir_historial_venta
        self.controlador.abrir_facturas_ventas = self.abrir_facturas_ventas
        self.controlador.abrir_papelera_ventas = self.abrir_papelera_ventas
        self.controlador.abrir_carrito_venta = self.abrir_carrito_venta
        self.controlador.abrir_ganancias = self.abrir_ganancias

    # ---------- Métodos de navegación para Deudas ----------
    def abrir_edicion_deuda(self, id_deuda, cliente, usuario, callbacks):
        from retail.deudas.edicion_deudas import abrir_ventana_edicion_deuda
        abrir_ventana_edicion_deuda(self, id_deuda, cliente, usuario, callbacks)

    def abrir_historial_deuda(self, parent, nombre_cliente="Cliente", id_deuda=None):
        from retail.deudas.historial_deudas import abrir_historial_deudas
        abrir_historial_deudas(parent, nombre_cliente=nombre_cliente, id_deuda=id_deuda)

    def abrir_facturas_deudas(self, parent=None):
        from retail.deudas.facturas_deudas import ver_facturas_deudas
        ver_facturas_deudas(parent if parent else self)

    def abrir_deudas_pagadas(self, parent=None):
        from retail.deudas.pagadas import ver_deudas_pagadas
        ver_deudas_pagadas(parent if parent else self)

    def abrir_carrito_deuda(self, deudas_view):
        from retail.deudas.carrito_deudas import ver_carrito_deuda
        ver_carrito_deuda(deudas_view)

    def abrir_papelera_deudas(self, parent=None):
        """Abre la ventana de la papelera de deudas."""
        from retail.deudas.papelera_deudas import ver_papelera_deudas
        ver_papelera_deudas(parent if parent else self)

    # ---------- Métodos de navegación para Ventas ----------
    def abrir_edicion_factura(self, parent, id_ventas, cliente, usuario, callbacks):
        from retail.ventas.edicion_ventas import abrir_ventana_edicion_factura
        abrir_ventana_edicion_factura(parent, id_ventas, cliente, usuario, callbacks)

    def abrir_historial_venta(self, parent, id_ventas=None, nombre_cliente="Cliente", facturas_window=None):
        from retail.ventas.historial_ventas import abrir_historial_ventas
        abrir_historial_ventas(parent, id_ventas=id_ventas, nombre_cliente=nombre_cliente, facturas_window=facturas_window)

    def abrir_facturas_ventas(self, parent=None):
        from retail.ventas.facturas_ventas import ver_facturas
        ver_facturas(parent if parent else self)

    def abrir_papelera_ventas(self, parent=None):
        from retail.ventas.papelera_ventas import ver_papelera_ventas
        ver_papelera_ventas(parent if parent else self)

    def abrir_carrito_venta(self, ventas_view):
        from retail.ventas.carrito_ventas import ver_carrito
        ver_carrito(ventas_view)

    def abrir_ganancias(self, parent=None):
        from retail.vistas.ganancias import ver_ganancias
        ver_ganancias(parent if parent else self)

    # ---------- Resto de la clase sin cambios ----------
    def crear_frames(self):
        """
        Crea y configura los frames de cada sección (Ventas, Clientes, Inventario, Deudas).
        Los frames se apilan y se muestran según la selección del menú.
        """
        ventanas = {
            Ventas: "Ventas",
            Deudas: "Deudas",
            Clientes: "Clientes",
            Inventario: "Inventario",
        }

        self.frame_contenido = tk.Frame(self, bg="#E6D9E3")
        self.frame_contenido.grid(row=1, column=0, sticky="nsew")
        self.frame_contenido.grid_rowconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(0, weight=1)

        for clase_ventana, nombre in ventanas.items():
            frame = clase_ventana(self.frame_contenido, self.controlador)
            self.frames[clase_ventana] = frame
            if clase_ventana is Ventas:
                self.ventas_view = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.frames[Ventas].tkraise()

    def crear_menu(self):
        """
        Crea el menú superior con botones para cambiar entre las diferentes secciones.
        """
        frame_menu = tk.Frame(self, bg="#E6D9E3")
        frame_menu.grid(row=0, column=0, sticky="ew")
        for idx in range(4):
            frame_menu.grid_columnconfigure(idx, weight=1)
        self.frame_menu = frame_menu

        secciones = [
            ("Ventas", Ventas, "#4CAF50"), 
            ("Deudas", Deudas, "#F44336"),
            ("Inventario", Inventario, "#2196F3"),
            ("Clientes", Clientes, "#FF9800"),
        ]

        for idx, (nombre, clase, color) in enumerate(secciones):
            btn = tk.Button(
                frame_menu,
                text=nombre,
                image=self.iconos[nombre],
                compound="left",
                font=("Calibri", 13, "bold"),
                bg=color,
                fg="#fff" if nombre == self.seccion_activa else "#222",
                bd=3,
                relief="ridge",
                activebackground=color,
                activeforeground="#fff",
                cursor="hand2",
                highlightthickness=0,
                command=lambda c=clase, n=nombre: self.cambiar_seccion(c, n),
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=2, pady=2)
            self.menu_buttons[nombre] = btn

        tk.Frame(self, bg="#BDBDBD", height=2).place(relx=0, y=MENU_ALTO, relwidth=1, height=2)
        self.frame_menu.bind("<Configure>", lambda e: self.actualizar_menu_visual())
        self.actualizar_menu_visual()

    def cambiar_seccion(self, clase_ventana, nombre):
        self.seccion_activa = nombre
        self.show_frames(clase_ventana)
        self.actualizar_menu_visual()

    def actualizar_menu_visual(self):
        for nombre, btn in self.menu_buttons.items():
            if nombre == self.seccion_activa:
                btn.config(
                    bg="#212121",
                    fg="#FFD600",
                    relief="flat",
                    bd=0,
                )
                if not hasattr(btn, "underline"):
                    underline = tk.Frame(btn.master, bg="#FFD600", height=4)
                    underline.place(x=btn.winfo_x(), y=MENU_ALTO-4, width=btn.winfo_width())
                    btn.underline = underline
                else:
                    btn.underline.place(x=btn.winfo_x(), y=MENU_ALTO-4, width=btn.winfo_width())
            else:
                color = {
                    "Ventas": "#4CAF50",
                    "Clientes": "#FF9800",
                    "Inventario": "#2196F3",
                    "Deudas": "#F44336",
                }[nombre]
                btn.config(
                    bg=color,
                    fg="#fff",
                    relief="raised",
                    bd=3,
                )
                if hasattr(btn, "underline"):
                    btn.underline.place_forget()

    def show_frames(self, clase_ventana):
        """Muestra el frame correspondiente a la sección seleccionada."""
        for frame in self.frames.values():
            if hasattr(frame, "_desactivar_bindings"):
                frame._desactivar_bindings()
        frame = self.frames[clase_ventana]
        if hasattr(frame, "_activar_bindings"):
            frame._activar_bindings()
        frame.tkraise()
        self.actualizar_menu_visual()