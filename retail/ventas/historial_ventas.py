"""
historial_ventas.py

Módulo que muestra el historial de transacciones de una venta específica o de un cliente.
Permite visualizar productos, cantidades, subtotales, montos recibidos, vueltos y acciones
(venta, edición, eliminación, etc.). La ventana es redimensionable y las columnas se pueden
ajustar manualmente para adaptarse a textos largos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List

from retail.nucleo.servicios.ventas.servicio_historial_ventas import ServicioHistorialVentas


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def abrir_historial_ventas(
    parent: tk.Tk,
    id_ventas: Optional[int] = None,
    nombre_cliente: str = "Cliente",
    facturas_window: Optional[tk.Toplevel] = None
) -> None:
    """
    Abre una ventana con el historial de ventas.

    Args:
        parent: Ventana padre (normalmente el controlador o la ventana de facturas).
        id_ventas: ID de la venta específica (si se proporciona, muestra el historial de esa venta).
        nombre_cliente: Nombre del cliente o ID como cadena (para buscar historial por cliente).
        facturas_window: Ventana de facturas opcional, usada para obtener el nombre del cliente.
    """
    # 1. Obtener los datos del historial según el parámetro recibido
    historial, titulo = _obtener_historial_y_titulo(parent, id_ventas, nombre_cliente, facturas_window)
    if not historial:
        return

    # 2. Crear la ventana principal
    ventana = _crear_ventana(parent, titulo)

    # 3. Construir la tabla (Treeview)
    tree, frame_tabla = _crear_tabla(ventana)

    # 4. Cargar los datos en la tabla
    _cargar_datos_en_tabla(tree, historial)

    # 5. Configurar tooltips para mostrar texto completo al pasar el ratón
    _configurar_tooltips(tree)

    # 6. Iniciar el bucle de eventos (se mantiene abierta)
    ventana.mainloop()


# ----------------------------------------------------------------------------
# SUBFUNCIONES DE LÓGICA DE DATOS
# ----------------------------------------------------------------------------
def _obtener_historial_y_titulo(
    parent: tk.Tk,
    id_ventas: Optional[int],
    nombre_cliente: str,
    facturas_window: Optional[tk.Toplevel]
) -> tuple:
    """
    Obtiene el historial y el título de la ventana según los parámetros.

    Returns:
        (historial, titulo) donde historial es una lista de diccionarios
        o None si no hay datos, y titulo es un string.
    """
    if id_ventas is not None:
        historial = ServicioHistorialVentas.obtener_por_venta(id_ventas)
        if not historial:
            messagebox.showinfo(
                "Información",
                f"No se encontró historial para la venta #{id_ventas}.",
                parent=parent
            )
            return None, ""

        # Intentar obtener el nombre del cliente desde la ventana de facturas
        if facturas_window and hasattr(facturas_window, "obtener_cliente_por_venta"):
            cliente_titulo = facturas_window.obtener_cliente_por_venta(id_ventas)
        else:
            cliente_titulo = f"Factura N° {id_ventas}"
        titulo = f"Historial de Ventas - {cliente_titulo}"
    else:
        # Buscar por cliente: puede ser un ID numérico o un nombre
        id_cliente = None
        cliente_rapido = nombre_cliente
        if str(nombre_cliente).isdigit():
            id_cliente = int(nombre_cliente)
            cliente_rapido = ""  # Si tenemos ID, no usamos cliente_rapido
        else:
            id_cliente = 0  # Placeholder, se usará cliente_rapido

        historial = ServicioHistorialVentas.obtener_por_cliente(id_cliente, cliente_rapido)
        if not historial:
            messagebox.showinfo(
                "Información",
                f"No se encontró historial para el cliente: {nombre_cliente}.",
                parent=parent
            )
            return None, ""
        titulo = f"Historial de Ventas - Cliente: {nombre_cliente}"

    return historial, titulo


# ----------------------------------------------------------------------------
# CONSTRUCCIÓN DE LA INTERFAZ
# ----------------------------------------------------------------------------
def _crear_ventana(parent: tk.Tk, titulo: str) -> tk.Toplevel:
    """
    Crea y configura la ventana principal del historial.

    Returns:
        La ventana Toplevel creada.
    """
    ventana = tk.Toplevel(parent)
    ventana.title(titulo)
    ventana.geometry("1300x700+10+10")
    ventana.configure(bg="#E6D9E3")
    # Bloquear redimensionamiento para mantener la integridad del diseño
    ventana.resizable(False, False)
    ventana.maxsize(1300, 700)

    try:
        ventana.transient(parent)
        ventana.grab_set()
        ventana.attributes("-topmost", True)
    except Exception:
        pass

    # Título superior
    label_titulo = tk.Label(
        ventana,
        text=titulo,
        font=("Helvetica", 17, "bold"),
        bg="#8e24aa",
        fg="white",
        pady=12
    )
    label_titulo.pack(fill="x")

    return ventana


def _crear_tabla(ventana: tk.Toplevel) -> tuple:
    """
    Crea el TreeView con las columnas del historial y sus scrollbars.

    Returns:
        (tree, frame_tabla) donde tree es el widget Treeview y frame_tabla su contenedor.
    """
    frame_tabla = tk.Frame(ventana, bg="#F5F5F5")
    frame_tabla.pack(padx=30, pady=(20, 5), fill="both", expand=True)

    columnas = (
        "ID", "N°", "Producto", "Día", "Fecha", "Hora",
        "Acción", "Stock", "Subtotal", "Recibido", "Vuelto"
    )
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)

    # Configuración de anchos iniciales (el usuario podrá redimensionar)
    anchos = {
        "ID": 0,
        "N°": 60,
        "Producto": 350,    # Suficiente para nombres largos
        "Día": 100,
        "Fecha": 110,
        "Hora": 90,
        "Acción": 100,
        "Stock": 90,
        "Subtotal": 130,
        "Recibido": 130,
        "Vuelto": 130,
    }
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=anchos[col], anchor="center", minwidth=50)
    tree.column("ID", width=0, stretch=False)
    tree.column("Producto", anchor="w")  # Alinear a la izquierda para mejor lectura

    # Scrollbars
    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # Rueda del mouse para scroll vertical
    def _on_mousewheel(event):
        tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
    tree.bind("<Enter>", lambda e: tree.bind_all("<MouseWheel>", _on_mousewheel))
    tree.bind("<Leave>", lambda e: tree.unbind_all("<MouseWheel>"))

    return tree, frame_tabla


def _cargar_datos_en_tabla(tree: ttk.Treeview, historial: List[Dict[str, Any]]) -> None:
    """
    Inserta cada registro del historial en el TreeView.
    """
    for registro in historial:
        tree.insert(
            "",
            "end",
            values=(
                registro["id_historial"],
                registro["idx"],
                registro["producto"],
                registro["dia_semana"],
                registro["fecha"],
                registro["hora"],
                registro["accion"],
                registro["cantidad"],
                registro["subtotal"],
                registro["monto_recibido"],
                registro["vuelto"],
            )
        )


# ----------------------------------------------------------------------------
# TOOLTIPS PARA VER TEXTO COMPLETO
# ----------------------------------------------------------------------------
def _configurar_tooltips(tree: ttk.Treeview) -> None:
    """
    Asigna un tooltip a cada celda del Treeview para mostrar el contenido completo
    cuando el mouse pasa sobre ella (útil para productos o textos muy largos).
    """
    # Usamos una etiqueta flotante que aparece y desaparece
    tooltip = tk.Label(tree, bg="#FFFFE0", fg="#000", relief="solid", borderwidth=1)
    tooltip.place_forget()

    def mostrar_tooltip(event):
        # Obtener la fila y columna bajo el cursor
        item = tree.identify_row(event.y)
        if not item:
            return
        column = tree.identify_column(event.x)
        if not column or column == "#0":
            return
        col_index = int(column.replace("#", "")) - 1
        valores = tree.item(item, "values")
        if col_index < len(valores):
            texto = str(valores[col_index])
            if not texto.strip():
                return
            # Posicionar el tooltip cerca del cursor
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.config(text=texto)
            tooltip.place(x=x, y=y)
            # Configurar temporizador para ocultar después de 3 segundos
            tooltip.after(3000, tooltip.place_forget)

    def ocultar_tooltip(event):
        tooltip.place_forget()

    tree.bind("<Motion>", mostrar_tooltip)
    tree.bind("<Leave>", ocultar_tooltip)