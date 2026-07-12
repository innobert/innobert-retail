import tkinter as tk
import os
from PIL import Image, ImageTk
from retail.nucleo.configuraciones import rutas


ANCHO_PRODUCTO = 220
ALTO_PRODUCTO = 240
SEPARACION_X = 8
SEPARACION_Y = 8
MAX_IMAGE_SIZE = 150


def peso_colombiano(value):
    return f"${value:,.0f}".replace(",", ".")


def crear_producto_card(frame_contenedor, producto, row, col,
                        on_select=None, on_double_click=None,
                        formatear_precio=None, texto_estado=None):
    if formatear_precio is None:
        formatear_precio = peso_colombiano
    if texto_estado is None:
        def texto_estado(e): return str(e)

    frame_producto = tk.Frame(
        frame_contenedor,
        bg="white",
        width=ANCHO_PRODUCTO,
        height=ALTO_PRODUCTO,
        bd=1,
        relief="solid",
        highlightbackground="#DADADA",
        highlightthickness=1,
    )
    frame_producto.grid(row=row, column=col, padx=SEPARACION_X, pady=SEPARACION_Y, sticky="nsew")
    frame_producto.grid_propagate(False)
    frame_producto.producto_data = {
        "id_producto": producto["id_producto"],
        "producto": producto["producto"],
        "precio": producto["precio"],
        "costo": producto["costo"],
        "stock": producto["stock"],
        "estado": texto_estado(producto["estado"]),
        "imagen": producto["imagen"],
    }

    try:
        img_path = producto.get("imagen") or "default.png"
        img_file = rutas(img_path) if not os.path.isabs(img_path) else img_path
        imagen = Image.open(img_file)
    except Exception:
        try:
            imagen = Image.open(rutas(os.path.join("fotos", "default.png")))
        except Exception:
            imagen = None

    if imagen:
        try:
            imagen.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.LANCZOS)
            imagen_tk = ImageTk.PhotoImage(imagen)
            img_label = tk.Label(frame_producto, image=imagen_tk, bg="white")
            img_label.image = imagen_tk
            img_label.pack(fill="x", pady=(10, 6))
        except Exception:
            img_label = tk.Label(frame_producto, text="Sin imagen", bg="white", font=("Helvetica", 10))
            img_label.pack(fill="x", pady=(20, 6))
    else:
        img_label = tk.Label(frame_producto, text="Sin imagen", bg="white", font=("Helvetica", 10))
        img_label.pack(fill="x", pady=(20, 6))

    if on_select:
        img_label.bind("<Button-1>", lambda e, f=frame_producto: on_select(f))
        frame_producto.bind("<Button-1>", lambda e, f=frame_producto: on_select(f))
    if on_double_click:
        img_label.bind("<Double-Button-1>", lambda e, d=frame_producto.producto_data, f=frame_producto: on_double_click(d, f))
        frame_producto.bind("<Double-Button-1>", lambda e, d=frame_producto.producto_data, f=frame_producto: on_double_click(d, f))

    tk.Label(
        frame_producto,
        text=producto["producto"].upper(),
        font=("Helvetica", 11, "bold"),
        bg="white",
        anchor="center",
        wraplength=180,
        justify="center"
    ).pack(fill="both", expand=True, padx=6, pady=(4, 2))

    tk.Label(
        frame_producto,
        text=formatear_precio(producto["precio"]),
        font=("Helvetica", 12, "bold"),
        bg="white",
        fg="#1B5E20",
        anchor="w"
    ).pack(fill="x", padx=6, pady=(0, 6))

    return frame_producto
