"""
contenedor.py

Vista principal del sistema de gestión de licorería.
Contiene el contenedor principal que organiza y muestra las diferentes secciones del software:
Ventas, Clientes, Inventario y Deudas. Proporciona un menú superior para navegar entre ellas.

Autor: [Innobert]
"""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from typing import Any
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)
from retail.vistas.ventas import Ventas
from retail.vistas.clientes import Clientes
from retail.vistas.inventario import Inventario
from retail.vistas.deudas import Deudas
from retail.nucleo.configuraciones import crear_boton, BOTON_MENU, FUENTE_BOTON_NEGRITA

VENTANA_ANCHO = 1100
VENTANA_ALTO = 650
MENU_ALTO = 60


class Contenedor(tk.Frame):
    """
    Contenedor principal de la aplicación.
    Gestiona la visualización de las diferentes secciones mediante un menú superior.
    """

    def __init__(self, padre: Any, controlador: Any) -> None:
        super().__init__(padre, bg="#E6D9E3")
        self.controlador = controlador
        self.frames: dict[str, Any] = {}
        self.menu_buttons: dict[str, Any] = {}
        self.seccion_activa = "Ventas"

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Ruta absoluta a la carpeta img en la raíz del proyecto
        RUTA_IMG = (Path(__file__).parent / ".." / ".." / "img").resolve()

        # Cargar imágenes y mantener referencias
        self.iconos = {}
        for key, archivo in [("Ventas", "ventas.png"), ("Clientes", "clientes.png"),
                              ("Inventario", "inventario.png"), ("Deudas", "deuda.png")]:
            try:
                self.iconos[key] = ImageTk.PhotoImage(
                    Image.open(RUTA_IMG / archivo).resize((32, 32))
                )
            except Exception:
                self.iconos[key] = None
                logger.warning("No se pudo cargar la imagen %s", archivo)

        # Exponer métodos de navegación a través del controlador
        self._registrar_metodos_navegacion()

        self.crear_frames()
        self.crear_menu()

    def _registrar_metodos_navegacion(self) -> None:
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
    def abrir_edicion_deuda(self, id_deuda: int, cliente: str, usuario: str, callbacks: dict[str, Any]) -> None:
        from retail.deudas.edicion_deudas import abrir_ventana_edicion_deuda

        abrir_ventana_edicion_deuda(self, id_deuda, cliente, usuario, callbacks)

    def abrir_historial_deuda(self, parent: Any, nombre_cliente: str = "Cliente", id_deuda: int | None = None) -> None:
        from retail.deudas.historial_deudas import abrir_historial_deudas

        abrir_historial_deudas(parent, nombre_cliente=nombre_cliente, id_deuda=id_deuda)

    def abrir_facturas_deudas(self, parent: Any | None = None) -> None:
        from retail.deudas.facturas_deudas import ver_facturas_deudas

        ver_facturas_deudas(parent if parent else self)

    def abrir_deudas_pagadas(self, parent: Any | None = None) -> None:
        from retail.deudas.pagadas import ver_deudas_pagadas

        ver_deudas_pagadas(parent if parent else self)

    def abrir_carrito_deuda(self, deudas_view: Any) -> None:
        from retail.deudas.carrito_deudas import ver_carrito_deuda

        ver_carrito_deuda(deudas_view)

    def abrir_papelera_deudas(self, parent: Any | None = None) -> None:
        """Abre la ventana de la papelera de deudas."""
        from retail.deudas.papelera_deudas import ver_papelera_deudas

        ver_papelera_deudas(parent if parent else self)

    # ---------- Métodos de navegación para Ventas ----------
    def abrir_edicion_factura(self, parent: Any, id_ventas: int, cliente: str, usuario: str, callbacks: dict[str, Any]) -> None:
        from retail.ventas.edicion_ventas import abrir_ventana_edicion_factura

        abrir_ventana_edicion_factura(parent, id_ventas, cliente, usuario, callbacks)

    def abrir_historial_venta(
        self, parent: Any, id_ventas: int | None = None, nombre_cliente: str = "Cliente", facturas_window: Any | None = None
    ) -> None:
        from retail.ventas.historial_ventas import abrir_historial_ventas

        abrir_historial_ventas(
            parent,
            id_ventas=id_ventas,
            nombre_cliente=nombre_cliente,
            facturas_window=facturas_window,
        )

    def abrir_facturas_ventas(self, parent: Any | None = None) -> None:
        from retail.ventas.facturas_ventas import ver_facturas

        ver_facturas(parent if parent else self)

    def abrir_papelera_ventas(self, parent: Any | None = None) -> None:
        from retail.ventas.papelera_ventas import ver_papelera_ventas

        ver_papelera_ventas(parent if parent else self)

    def abrir_carrito_venta(self, ventas_view: Any) -> None:
        from retail.ventas.carrito_ventas import ver_carrito

        ver_carrito(ventas_view)

    def abrir_ganancias(self, parent: Any | None = None) -> None:
        from retail.vistas.ganancias import ver_ganancias

        ver_ganancias(parent if parent else self)

    # ---------- Resto de la clase sin cambios ----------
    def crear_frames(self) -> None:
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

    def crear_menu(self) -> None:
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
            btn = crear_boton(
                frame_menu,
                nombre,
                estilo=BOTON_MENU,
                image=self.iconos[nombre],
                compound="left",
                fuente=FUENTE_BOTON_NEGRITA,
                padx=15,
                comando=lambda c=clase, n=nombre: self.cambiar_seccion(c, n),
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=3, pady=3)
            self.menu_buttons[nombre] = btn
        self.frame_menu.bind("<Configure>", lambda e: self.actualizar_menu_visual())
        self.actualizar_menu_visual()

    def cambiar_seccion(self, clase_ventana: type, nombre: str) -> None:
        self.seccion_activa = nombre
        self.show_frames(clase_ventana)
        self.actualizar_menu_visual()

    def actualizar_menu_visual(self) -> None:
        colores = {
            "Ventas": "#4CAF50",
            "Clientes": "#FF9800",
            "Inventario": "#2196F3",
            "Deudas": "#F44336",
        }
        for nombre, btn in self.menu_buttons.items():
            if nombre == self.seccion_activa:
                btn.config(
                    bg="#212121",
                    fg="#FFD600",
                )
            else:
                btn.config(
                    bg=colores[nombre],
                    fg="#fff",
                )

    def show_frames(self, clase_ventana: type) -> None:
        """Muestra el frame correspondiente a la sección seleccionada."""
        frame = self.frames[clase_ventana]
        frame.tkraise()
        self.actualizar_menu_visual()

    
