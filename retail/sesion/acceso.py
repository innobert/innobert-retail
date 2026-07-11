from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Any
from PIL import Image, ImageTk
from retail.sesion.registro import VentanaRegistro
from retail.nucleo.configuraciones import COLOR_VERDE, COLOR_AZUL, crear_boton, BOTON_EXITO, FUENTE_BOTON_GRANDE
from retail.sesion.core.servicio_acceso import ServicioAcceso

logger = logging.getLogger(__name__)


class Acceso(tk.Frame):
    def __init__(self, padre: Any, controlador: Any) -> None:
        super().__init__(padre)
        self.controlador = controlador
        self.pack(fill=tk.BOTH, expand=True)
        self.widgets()
        self.cargar_usuario()
        self.bind("<Return>", lambda event: self.login())
        self.controlador.geometry("800x600+200+60")

    def widgets(self) -> None:
        # Frame principal para los campos de login
        frame2 = tk.Frame(
            self, bg="#FFFFFF", highlightthickness=1, highlightbackground="black"
        )
        frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        titulo = tk.Label(
            frame2,
            text="INICIO DE SESIÓN",
            font=("Calibri", 20, "bold"),
            bg="#FFFFFF",
            fg="#333333",
        )
        titulo.pack(pady=5)

        # Campo Usuario
        tk.Label(
            frame2, text="Usuario", font=("Calibri", 14), bg="#FFFFFF", fg="#333333"
        ).pack(anchor="w", pady=5)
        self.entry_usuario = ttk.Entry(frame2, font=("Calibri", 14))
        self.entry_usuario.pack(fill=tk.X, pady=5)

        # Campo Contraseña
        tk.Label(
            frame2, text="Contraseña", font=("Calibri", 14), bg="#FFFFFF", fg="#333333"
        ).pack(anchor="w", pady=5)
        self.entry_contrasena = ttk.Entry(frame2, font=("Calibri", 14), show="*")
        self.entry_contrasena.pack(fill=tk.X, pady=5)

        # Checkbox recordar
        self.recordar_var = tk.IntVar()
        self.checkbox_recordar = tk.Checkbutton(
            frame2,
            text="Recordar Datos",
            variable=self.recordar_var,
            bg="#FFFFFF",
            font=("Calibri", 12),
            fg="#333333",
            activebackground="#FFFFFF",
            activeforeground="#333333",
            highlightthickness=0,
        )
        self.checkbox_recordar.pack(anchor="w", pady=10)

        # Botón Iniciar Sesión
        self.btn_login = crear_boton(
            frame2,
            texto="Iniciar Sesión",
            estilo=BOTON_EXITO,
            comando=self.login,
            fuente=FUENTE_BOTON_GRANDE,
            cursor="hand2",
        )
        self.btn_login.pack(pady=20, fill=tk.X)

        # Botón Registrar
        self.btn_registrar = crear_boton(
            frame2,
            texto="Registrar",
            estilo=BOTON_EXITO,
            comando=self.abrir_registro,
            cursor="hand2",
        )
        self.btn_registrar.pack(pady=10, fill=tk.X)

        # Frame para la imagen del negocio
        frame_imagen = tk.Frame(
            self, bg="#ffffff", highlightthickness=1, highlightbackground="white"
        )
        frame_imagen.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=0)

        # Cargar imagen de login
        ruta_login = (Path(__file__).parent / ".." / ".." / "img" / "login.png").resolve()
        try:
            self.img_negocio = ImageTk.PhotoImage(Image.open(ruta_login))
            label_imagen = tk.Label(frame_imagen, image=self.img_negocio, bg="#FFFFFF")
            label_imagen.pack(expand=True)
        except Exception:
            logger.warning("No se pudo cargar la imagen de login")
            tk.Label(
                frame_imagen, text="No se pudo cargar la imagen", bg="#FFFFFF", fg="red"
            ).pack()

        # Footer con información de contacto
        frame_footer = tk.Frame(frame_imagen, bg="#ffffff", highlightthickness=0)
        frame_footer.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Cargar imágenes del footer
        ruta_software = (Path(__file__).parent / ".." / ".." / "img" / "software.png").resolve()
        ruta_wpp = (Path(__file__).parent / ".." / ".." / "img" / "wpp.png").resolve()
        ruta_instagram = (Path(__file__).parent / ".." / ".." / "img" / "instagram.png").resolve()
        ruta_gmail = (Path(__file__).parent / ".." / ".." / "img" / "gmail.png").resolve()

        def cargar_img_footer(ruta: str) -> ImageTk.PhotoImage | None:
            try:
                return ImageTk.PhotoImage(
                    Image.open(ruta).resize((22, 22), Image.Resampling.LANCZOS)
                )
            except Exception:
                logger.error("No se pudo cargar imagen del footer: %s", ruta)
                return None

        img_software = cargar_img_footer(ruta_software)
        img_wpp = cargar_img_footer(ruta_wpp)
        img_instagram = cargar_img_footer(ruta_instagram)
        img_gmail = cargar_img_footer(ruta_gmail)

        # Nombre y software
        nombre_frame = tk.Frame(frame_footer, bg="#FFFFFF")
        nombre_frame.pack(anchor="center", pady=2)
        if img_software:
            tk.Label(nombre_frame, image=img_software, bg="#FFFFFF").pack(
                side=tk.LEFT, padx=(0, 5)
            )
        tk.Label(
            nombre_frame,
            text="Roberto Vásquez",
            font=("Calibri", 10, "bold"),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT)
        tk.Label(
            nombre_frame,
            text="Ingeniero de Software",
            font=("Calibri", 10),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT, padx=(5, 0))

        # WhatsApp
        wpp_frame = tk.Frame(frame_footer, bg="#FFFFFF")
        wpp_frame.pack(anchor="center", pady=2)
        if img_wpp:
            tk.Label(wpp_frame, image=img_wpp, bg="#FFFFFF").pack(
                side=tk.LEFT, padx=(0, 5)
            )
        tk.Label(
            wpp_frame,
            text="304 210 4313",
            font=("Calibri", 10, "bold"),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT)
        tk.Label(
            wpp_frame, text="WhatsApp", font=("Calibri", 10), bg="#FFFFFF", fg="#666666"
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Instagram
        insta_frame = tk.Frame(frame_footer, bg="#FFFFFF")
        insta_frame.pack(anchor="center", pady=2)
        if img_instagram:
            tk.Label(insta_frame, image=img_instagram, bg="#FFFFFF").pack(
                side=tk.LEFT, padx=(0, 5)
            )
        tk.Label(
            insta_frame,
            text="innobertdev",
            font=("Calibri", 10, "bold"),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT)
        tk.Label(
            insta_frame,
            text="Instagram",
            font=("Calibri", 10),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Gmail
        gmail_frame = tk.Frame(frame_footer, bg="#FFFFFF")
        gmail_frame.pack(anchor="center", pady=2)
        if img_gmail:
            tk.Label(gmail_frame, image=img_gmail, bg="#FFFFFF").pack(
                side=tk.LEFT, padx=(0, 5)
            )
        tk.Label(
            gmail_frame,
            text="innobert07@gmail.com",
            font=("Calibri", 10, "bold"),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(side=tk.LEFT)
        tk.Label(
            gmail_frame, text="Gmail", font=("Calibri", 10), bg="#FFFFFF", fg="#666666"
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Marca
        tk.Label(
            frame_footer,
            text="®INNOBERTDEV",
            font=("Calibri", 10, "bold"),
            bg="#FFFFFF",
            fg="#666666",
        ).pack(anchor="center", pady=2)

        # Guardar referencias de imágenes
        self.img_software = img_software
        self.img_wpp = img_wpp
        self.img_instagram = img_instagram
        self.img_gmail = img_gmail

        self.cargar_usuario()

    def login(self) -> None:
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()
        recordar = self.recordar_var.get()

        if not usuario or not contrasena:
            messagebox.showwarning("Advertencia", "Ingrese usuario y contraseña.")
            return

        # Autenticación con validación de licencia (módulo independizado)
        exito, mensaje, datos_usuario = ServicioAcceso.autenticar_usuario(
            usuario, contrasena
        )
        if exito:
            # Mostrar info de licencia (sin rutas de BD)
            msg_bienvenida = f"Bienvenido, {usuario}!"

            if datos_usuario.get("dias_restantes") is not None:
                dias = datos_usuario["dias_restantes"]
                if dias <= 7:
                    msg_bienvenida += f"\n⚠️ Licencia vence en {dias} días."

            messagebox.showinfo("Éxito", msg_bienvenida)
            ServicioAcceso.guardar_preferencias_sesion(usuario, contrasena, bool(recordar))
            self.controlador.usuario_actual = usuario
            self.controlador.geometry("1100x650+130+20")
            self.controlador.show_frame("Contenedor")
        else:
            messagebox.showerror("Error", mensaje)

    def cargar_usuario(self) -> None:
        usuario, contrasena, recordar = ServicioAcceso.cargar_preferencias_sesion()
        self.entry_usuario.delete(0, tk.END)
        self.entry_contrasena.delete(0, tk.END)
        if recordar:
            self.entry_usuario.insert(0, usuario)
            self.entry_contrasena.insert(0, contrasena)
            self.recordar_var.set(1)
        else:
            self.recordar_var.set(0)

    def abrir_registro(self) -> None:
        usuario = self.entry_usuario.get().strip()
        contrasena = self.entry_contrasena.get().strip()

        # Solo desarrollador puede acceder a registro
        if not ServicioAcceso.puede_acceder_a_registro(usuario, contrasena):
            messagebox.showwarning(
                "Acceso restringido",
                "Registro de usuarios restringido para mantenimiento.",
            )
            return

        VentanaRegistro(self)
