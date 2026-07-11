from __future__ import annotations

import logging
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any
from PIL import Image, ImageTk
from retail.nucleo.configuraciones import obtener_ruta_logo, COLOR_FONDO, COLOR_AZUL, COLOR_ROJO, crear_boton, BOTON_IMPORTAR, BOTON_CERRAR

registrador = logging.getLogger(__name__)


def cambiar_logo(parent: Any) -> None:
    logo_dir = obtener_ruta_logo()
    Path(logo_dir).mkdir(parents=True, exist_ok=True)
    logo_default = obtener_ruta_logo("logo.png")  # <-- Cambiado aquí

    # Ventana modal
    top = tk.Toplevel(parent)
    top.title("Cambiar Logo de Factura")
    top.geometry("420x420+400+120")
    top.configure(bg=COLOR_FONDO)
    top.resizable(False, False)
    top.grab_set()

    # LabelFrame para la imagen
    lf_img = tk.LabelFrame(
        top, text="Logo Actual", font=("Helvetica", 12, "bold"), bg=COLOR_FONDO
    )
    lf_img.place(x=30, y=20, width=360, height=280)

    # Cargar logo actual o default
    logo_path = logo_default if Path(logo_default).exists() else None
    img_label = tk.Label(lf_img, bg="white")
    img_label.pack(fill="both", expand=True, padx=10, pady=10)
    image_tk = None

    def mostrar_logo(path: str | Path) -> None:
        nonlocal image_tk
        try:
            img = Image.open(path)
            img = img.resize((300, 200), Image.Resampling.LANCZOS)
            image_tk = ImageTk.PhotoImage(img)
            img_label.config(image=image_tk, text="")
        except Exception:
            registrador.warning("No se pudo cargar el logo desde %s", path)
            img_label.config(image="", text="Sin logo")

    if logo_path:
        mostrar_logo(logo_path)
    else:
        img_label.config(text="Sin logo")

    # Función para cargar imagen nueva
    def cargar_imagen() -> None:
        file_path = filedialog.askopenfilename(
            parent=top,
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp;*.tiff;*.ico"),
                ("Todos los archivos", "*.*"),
            ],
            initialdir=Path.home(),
        )
        if file_path:
            try:
                img = Image.open(file_path)
                img = img.convert("RGBA")
                img = img.resize((300, 200), Image.Resampling.LANCZOS)

                logo_actual = Path(logo_dir) / "logo.png"
                img.save(logo_actual, format="PNG")

                mostrar_logo(logo_actual)
                messagebox.showinfo(
                    "Éxito", "Logo actualizado correctamente.", parent=top
                )
            except Exception as e:
                messagebox.showerror(
                    "Error", f"No se pudo actualizar el logo:\n{e}", parent=top
                )

    btn_cargar = crear_boton(
        top,
        texto="Cargar Imagen",
        estilo=BOTON_IMPORTAR,
        comando=cargar_imagen,
        padx=10,
        pady=4,
        cursor="hand2",
    )
    btn_cargar.place(x=140, y=320, width=140, height=40)

    btn_cerrar = crear_boton(
        top,
        texto="Cerrar",
        estilo=BOTON_CERRAR,
        comando=top.destroy,
        padx=10,
        pady=4,
        cursor="hand2",
    )
    btn_cerrar.place(x=140, y=370, width=140, height=35)
