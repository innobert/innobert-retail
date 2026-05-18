"""
visualizar_deudas.py

Módulo que muestra una ventana con el detalle completo de una deuda,
incluyendo información de cliente, totales y productos.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from retail.nucleo.servicios.deudas.servicio_visualizar_deudas import ServicioVisualizarDeudas


def peso_colombiano(value: float) -> str:
    """Formatea un número a pesos colombianos con separadores de miles."""
    return f"${value:,.0f}".replace(",", ".")


def ver_detalle_deuda(parent, id_deuda: int):
    """
    Muestra una ventana con el detalle de la deuda seleccionada.
    """
    datos = ServicioVisualizarDeudas.obtener_detalles_deuda(id_deuda)
    if not datos:
        return

    try:
        fecha_dt = datetime.strptime(datos["fecha"], "%Y-%m-%d")
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_semana = dias[fecha_dt.weekday()]
    except Exception:
        dia_semana = ""

    top = tk.Toplevel(parent)
    top.title(f"Detalle Deuda N° {datos['numero_factura']}")
    top.geometry("950x600+150+30")
    top.configure(bg="#E6D9E3")
    top.resizable(False, False)
    top.transient(parent)
    top.grab_set()
    top.lift()
    top.focus_force()

    main_frame = tk.Frame(top, bg="#E6D9E3", padx=15, pady=15)
    main_frame.pack(fill="both", expand=True)

    frame_info = tk.LabelFrame(
        main_frame,
        text="Información de la Deuda",
        font=("Helvetica", 13, "bold"),
        bg="#FFFFFF",
        fg="#333333",
        relief="groove",
        bd=2,
        padx=10,
        pady=10,
    )
    frame_info.pack(fill="x", pady=(0, 15))

    info_grid = tk.Frame(frame_info, bg="#FFFFFF")
    info_grid.pack(fill="x", padx=10, pady=5)

    tk.Label(info_grid, text="N° Factura:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=0, column=0, sticky="w", padx=5, pady=4
    )
    tk.Label(info_grid, text=datos["numero_factura"], font=("Helvetica", 12), bg="#FFFFFF", fg="#333").grid(
        row=0, column=1, sticky="w", padx=5, pady=4
    )

    tk.Label(info_grid, text="Cliente:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=0, column=2, sticky="w", padx=(30, 5), pady=4
    )
    tk.Label(info_grid, text=datos["cliente"], font=("Helvetica", 12), bg="#FFFFFF", fg="#333").grid(
        row=0, column=3, sticky="w", padx=5, pady=4
    )

    tk.Label(info_grid, text="Fecha:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=1, column=0, sticky="w", padx=5, pady=4
    )
    tk.Label(info_grid, text=datos["fecha"], font=("Helvetica", 12), bg="#FFFFFF", fg="#333").grid(
        row=1, column=1, sticky="w", padx=5, pady=4
    )

    tk.Label(info_grid, text="Día:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=1, column=2, sticky="w", padx=(30,5), pady=4
    )
    tk.Label(info_grid, text=dia_semana, font=("Helvetica", 12), bg="#FFFFFF", fg="#333").grid(
        row=1, column=3, sticky="w", padx=5, pady=4
    )

    tk.Label(info_grid, text="Total:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=2, column=0, sticky="w", padx=5, pady=4
    )
    tk.Label(info_grid, text=peso_colombiano(datos["total"]), font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#0B6623").grid(
        row=2, column=1, sticky="w", padx=5, pady=4
    )

    tk.Label(info_grid, text="Saldo:", font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#333").grid(
        row=2, column=2, sticky="w", padx=(30, 5), pady=4
    )
    tk.Label(info_grid, text=peso_colombiano(datos["saldo"]), font=("Helvetica", 12, "bold"), bg="#FFFFFF", fg="#C62828").grid(
        row=2, column=3, sticky="w", padx=5, pady=4
    )

    frame_tabla = tk.LabelFrame(
        main_frame,
        text="Productos",
        font=("Helvetica", 13, "bold"),
        bg="#FFFFFF",
        fg="#333333",
        relief="groove",
        bd=2,
        padx=10,
        pady=10,
    )
    frame_tabla.pack(fill="both", expand=True, pady=(0, 15))

    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure(
        "DetalleDeuda.Treeview.Heading",
        font=("Helvetica", 12, "bold"),
        background="#2196F3",
        foreground="#ffffff",
        relief="flat",
    )
    style.configure(
        "DetalleDeuda.Treeview",
        font=("Helvetica", 11),
        rowheight=34,
        background="#F8FAFB",
        fieldbackground="#F8FAFB",
        borderwidth=0,
    )
    style.map("DetalleDeuda.Treeview", background=[("selected", "#105A65")])

    columns = ("producto", "cantidad", "precio", "subtotal")
    tree = ttk.Treeview(frame_tabla, columns=columns, show="headings", style="DetalleDeuda.Treeview")
    tree.heading("producto", text="Producto")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("precio", text="Precio Unitario")
    tree.heading("subtotal", text="Subtotal")

    tree.column("producto", width=340, anchor="w", minwidth=250, stretch=True)
    tree.column("cantidad", width=90, anchor="center", minwidth=70, stretch=False)
    tree.column("precio", width=150, anchor="e", minwidth=120, stretch=False)
    tree.column("subtotal", width=160, anchor="e", minwidth=130, stretch=False)

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scroll_y.pack(side="right", fill="y", pady=5)

    for prod in datos["productos"]:
        tree.insert(
            "",
            "end",
            values=(
                prod["producto"],
                prod["cantidad"],
                peso_colombiano(prod["precio_unitario"]),
                peso_colombiano(prod["subtotal"]),
            ),
        )

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
        command=top.destroy,
    )
    btn_cerrar.pack(pady=(5, 0))