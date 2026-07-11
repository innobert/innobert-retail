from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from retail.nucleo.configuraciones import COLOR_FONDO, COLOR_FONDO_TABLA, COLOR_VERDE, crear_boton, BOTON_CERRAR
from retail.nucleo.base_datos import obtener_productos, conexion

logger = logging.getLogger(__name__)


def mostrar_historial_inventario(parent: Any) -> None:
    # Buscar el producto seleccionado en el frame de selección
    try:
        producto_nombre = parent.seleccion_vars["producto"].get()
    except Exception:
        logger.debug("No se pudo obtener el producto seleccionado del frame de selección")
        producto_nombre = ""

    if not producto_nombre:
        messagebox.showwarning(
            "Selecciona un producto",
            "Debes seleccionar un producto para ver su historial.",
            parent=parent,
        )
        return

    # Buscar el producto en la base de datos
    productos = obtener_productos()
    producto = next((p for p in productos if p[1] == producto_nombre), None)
    if not producto:
        messagebox.showerror(
            "Producto no encontrado",
            "No se encontró el producto seleccionado.",
            parent=parent,
        )
        return

    id_producto = producto[0]

    # Obtener historial de la base de datos (sin mostrar el campo ID)
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_historial, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total
            FROM historial_inventario
            WHERE id_producto = ?
            ORDER BY fecha DESC, hora DESC
            """,
            (id_producto,),
        )
        historial = cursor.fetchall()

    # Días de la semana en español
    dias_es = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
        "Lunes": "Lunes",
        "Martes": "Martes",
        "Miércoles": "Miércoles",
        "Jueves": "Jueves",
        "Viernes": "Viernes",
        "Sábado": "Sábado",
        "Domingo": "Domingo",
    }

    # Crear ventana modal profesional (más angosta)
    top = tk.Toplevel(parent)
    top.title(f"Historial de {producto_nombre}")
    top.geometry("1100x520+110+50")
    top.configure(bg=COLOR_FONDO_TABLA)
    top.resizable(False, False)
    top.maxsize(1100, 520)
    top.transient(parent)
    top.grab_set()
    # Permitir cerrar con Esc
    top.bind("<Escape>", lambda e: top.destroy())

    # Título principal
    frame_titulo = tk.Frame(top, bg=COLOR_VERDE)
    frame_titulo.pack(fill="x")
    tk.Label(
        frame_titulo,
        text=f"Historial de {producto_nombre}",
        font=("Helvetica", 18, "bold"),
        bg=COLOR_VERDE,
        fg="white",
        pady=14,
    ).pack(side="left", fill="x", expand=True, padx=(10, 0))

    # Frame para la tabla y scrollbar
    frame_tabla = tk.Frame(top, bg=COLOR_FONDO_TABLA)
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=(18, 10))

    columnas = [
        "Día",
        "Fecha",
        "Hora",
        "Acción",
        "Pedido",
        "Stock",
        "Precio",
        "Costo",
        "Ganancia",
        "Total",
    ]

    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure(
        "Treeview.Heading",
        font=("Calibri", 14, "bold"),
        background=COLOR_FONDO,
        foreground="#333",
    )
    style.configure(
        "Treeview",
        font=("Calibri", 13),
        rowheight=32,
        background="#fff",
        fieldbackground="#fff",
    )
    style.map(
        "Treeview", background=[("selected", "#222")], foreground=[("selected", "#fff")]
    )

    tree = ttk.Treeview(
        frame_tabla, columns=columnas, show="headings", height=12, style="Treeview"
    )
    # Ajustar anchos y alineación para aprovechar el ancho de la ventana
    col_widths = [100, 110, 90, 110, 90, 90, 110, 110, 120, 120]
    for idx, col in enumerate(columnas):
        tree.heading(col, text=col)
        tree.column(
            col, anchor="center", width=col_widths[idx], minwidth=col_widths[idx]
        )

    tree.pack(side="left", fill="both", expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Formato de moneda
    def peso_colombiano(value: Any) -> Any:
        try:
            return f"${float(value):,.0f}".replace(",", ".")
        except Exception:
            return value

    # Insertar datos en la tabla (sin mostrar ID, pero lo guardamos en tags para eliminar)
    for row in historial:
        dia = dias_es.get(row[1], row[1])
        accion = row[4]
        tree.insert(
            "",
            "end",
            values=(
                dia,  # Día en español
                row[2],  # Fecha
                row[3],  # Hora
                accion,  # Acción
                row[5],  # Pedido
                row[6],  # Stock
                peso_colombiano(row[7]),  # Precio
                peso_colombiano(row[8]),  # Costo
                peso_colombiano(row[9]),  # Ganancia
                peso_colombiano(row[10]),  # Total
            ),
            tags=(row[0],),  # Guardar id_historial en tags para eliminar
        )

    # Pie de ventana con botón cerrar
    frame_footer = tk.Frame(top, bg=COLOR_FONDO_TABLA)
    frame_footer.pack(fill="x", pady=(0, 10))
    crear_boton(
        frame_footer,
        texto="Cerrar",
        estilo=BOTON_CERRAR,
        comando=top.destroy,
        width=12,
    ).pack(pady=8)

    # Mejorar visualización y experiencia
    tree.focus_set()
    if tree.get_children():
        tree.selection_set(tree.get_children()[0])
        tree.yview_moveto(0)
