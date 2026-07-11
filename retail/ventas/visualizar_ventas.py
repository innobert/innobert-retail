"""
visualizar_ventas.py

Módulo que muestra una ventana con el detalle completo de los productos
de una factura de venta, incluyendo información de cliente, totales, etc.
Solo lectura: no permite ediciones ni modificaciones.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from retail.nucleo.servicios.ventas.servicio_visualizar_ventas import ServicioVisualizarVentas


def peso_colombiano(value: float) -> str:
    """Formatea un número a pesos colombianos con separadores de miles."""
    return f"${value:,.0f}".replace(",", ".")


def ver_detalle_venta(parent, id_ventas: int):
    """
    Muestra una ventana con el detalle de la factura de venta (solo lectura).
    """
    datos = ServicioVisualizarVentas.obtener_detalles_factura(id_ventas)
    if not datos:
        return

    try:
        try:
            fecha_dt = datetime.strptime(datos["fecha"], "%Y-%m-%d")
        except ValueError:
            fecha_dt = datetime.strptime(datos["fecha"], "%d/%m/%Y")
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_semana = dias[fecha_dt.weekday()]
    except Exception:
        dia_semana = ""

    top = tk.Toplevel(parent)
    top.title(f"Detalle Factura N° {datos['numero_factura']}")
    top.geometry("950x650+150+30")
    top.configure(bg="#E6D9E3")
    top.resizable(False, False)
    top.transient(parent)
    top.grab_set()
    top.lift()
    top.focus_force()

    main_frame = tk.Frame(top, bg="#E6D9E3", padx=15, pady=15)
    main_frame.pack(fill="both", expand=True)

    # Información de la factura
    frame_info = tk.LabelFrame(
        main_frame,
        text="Información de la factura",
        font=("Helvetica", 13, "bold"),
        bg="#FFFFFF",
        fg="#333333",
        relief="groove",
        bd=2,
        padx=10,
        pady=10
    )
    frame_info.pack(fill="x", pady=(0, 15))

    info_grid = tk.Frame(frame_info, bg="#FFFFFF")
    info_grid.pack(fill="x", padx=10, pady=5)

    # Fila 1
    tk.Label(info_grid, text="N° Factura:", font=("Helvetica", 12, "bold"),
            bg="#FFFFFF", fg="#333").grid(row=0, column=0, sticky="w", padx=5, pady=4)
    tk.Label(info_grid, text=datos["numero_factura"], font=("Helvetica", 12),
            bg="#FFFFFF", fg="#333").grid(row=0, column=1, sticky="w", padx=5, pady=4)

    tk.Label(info_grid, text="Cliente:", font=("Helvetica", 12, "bold"),
            bg="#FFFFFF", fg="#333").grid(row=0, column=2, sticky="w", padx=(30,5), pady=4)
    tk.Label(info_grid, text=datos["cliente"], font=("Helvetica", 12),
            bg="#FFFFFF", fg="#333").grid(row=0, column=3, sticky="w", padx=5, pady=4)

    # Fila 2
    tk.Label(info_grid, text="Fecha:", font=("Helvetica", 12, "bold"),
            bg="#FFFFFF", fg="#333").grid(row=1, column=0, sticky="w", padx=5, pady=4)
    tk.Label(info_grid, text=datos["fecha"], font=("Helvetica", 12),
             bg="#FFFFFF", fg="#333").grid(row=1, column=1, sticky="w", padx=5, pady=4)

    tk.Label(info_grid, text="Hora:", font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#333").grid(row=1, column=2, sticky="w", padx=(30,5), pady=4)
    tk.Label(info_grid, text=datos["hora"], font=("Helvetica", 12),
             bg="#FFFFFF", fg="#333").grid(row=1, column=3, sticky="w", padx=5, pady=4)

    tk.Label(info_grid, text="Día:", font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#333").grid(row=2, column=0, sticky="w", padx=5, pady=4)
    tk.Label(info_grid, text=dia_semana, font=("Helvetica", 12),
             bg="#FFFFFF", fg="#333").grid(row=2, column=1, sticky="w", padx=5, pady=4)

    tk.Label(info_grid, text="Total:", font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#333").grid(row=3, column=0, sticky="w", padx=5, pady=4)
    tk.Label(info_grid, text=peso_colombiano(datos["total"]), font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#0B6623").grid(row=3, column=1, sticky="w", padx=5, pady=4)

    tk.Label(info_grid, text="Monto recibido:", font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#333").grid(row=3, column=2, sticky="w", padx=(30,5), pady=4)
    tk.Label(info_grid, text=peso_colombiano(datos["monto_recibido"]), font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#0D47A1").grid(row=3, column=3, sticky="w", padx=5, pady=4)

    # Fila 5
    tk.Label(info_grid, text="Vuelto:", font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#333").grid(row=4, column=0, sticky="w", padx=5, pady=4)
    tk.Label(info_grid, text=peso_colombiano(datos["vuelto"]), font=("Helvetica", 12, "bold"),
             bg="#FFFFFF", fg="#0B6623").grid(row=4, column=1, sticky="w", padx=5, pady=4)

    # Tabla de productos
    frame_tabla = tk.LabelFrame(
        main_frame,
        text="Productos",
        font=("Helvetica", 13, "bold"),
        bg="#FFFFFF",
        fg="#333333",
        relief="groove",
        bd=2,
        padx=10,
        pady=10
    )
    frame_tabla.pack(fill="both", expand=True, pady=(0, 15))

    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure(
        "DetalleVenta.Treeview.Heading",
        font=("Helvetica", 12, "bold"),
        background="#2196F3",
        foreground="#ffffff",
        relief="flat"
    )
    style.configure(
        "DetalleVenta.Treeview",
        font=("Helvetica", 11),
        rowheight=36,
        background="#F8FAFB",
        fieldbackground="#F8FAFB",
        borderwidth=0
    )
    style.map("DetalleVenta.Treeview", background=[("selected", "#105A65")])

    columns = ("producto", "cantidad", "precio", "subtotal")
    tree = ttk.Treeview(frame_tabla, columns=columns, show="headings", style="DetalleVenta.Treeview")
    tree.heading("producto", text="Producto")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("precio", text="Precio Unitario")
    tree.heading("subtotal", text="Subtotal")

    # NUEVOS ANCHOS: producto más reducido, precio y subtotal con buen espacio
    tree.column("producto", width=340, anchor="w", minwidth=250, stretch=True)
    tree.column("cantidad", width=90, anchor="center", minwidth=70, stretch=False)
    tree.column("precio", width=150, anchor="e", minwidth=120, stretch=False)
    tree.column("subtotal", width=160, anchor="e", minwidth=130, stretch=False)

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scroll_y.pack(side="right", fill="y", pady=5)

    for prod in datos["productos"]:
        tree.insert("", "end", values=(
            prod["producto"],
            prod["cantidad"],
            peso_colombiano(prod["precio_unit"]),
            peso_colombiano(prod["subtotal"])
        ))

    # Botón cerrar
    btn_cerrar = tk.Button(
        main_frame,
        text="Cerrar",
        font=("Helvetica", 12, "bold"),
        bg="#1976D2",
        fg="#FFFFFF",
        activebackground="#115293",
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        padx=20,
        pady=6,
        command=top.destroy
    )
    btn_cerrar.pack(pady=(5, 0))