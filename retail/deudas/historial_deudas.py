import tkinter as tk
from tkinter import ttk, messagebox
from retail.nucleo.servicios.deudas.servicio_historial_deudas import ServicioHistorialDeudas


def peso_colombiano(value):
    return f"${value:,.0f}".replace(",", ".")


def abrir_historial_deudas(parent, nombre_cliente="Cliente", cliente_rapido=None, id_deuda=None):
    """
    Muestra el historial de deudas para una deuda específica (id_deuda) o,
    si no se proporciona, para un cliente (por nombre o cliente_rapido).
    Se recomienda siempre usar id_deuda para evitar ambigüedades.
    """
    # --- Determinar el identificador a usar (prioridad: id_deuda) ---
    if id_deuda is not None:
        historial = ServicioHistorialDeudas.obtener_por_deuda(id_deuda)
        if not historial:
            messagebox.showinfo("Información", f"No se encontró historial para la deuda #{id_deuda}.", parent=parent)
            return
        cliente_nombre = nombre_cliente if nombre_cliente and nombre_cliente != "Cliente" else ServicioHistorialDeudas.obtener_nombre_cliente_por_deuda(id_deuda)
        numero_factura = ServicioHistorialDeudas.obtener_numero_factura_por_deuda(id_deuda)
        cliente_mostrar = f"N° {numero_factura} - {cliente_nombre}"
        titulo = f"Historial de Deuda N° {numero_factura} - {cliente_nombre}"
    else:
        # Buscar por cliente
        # Intentar obtener id_cliente desde el nombre (si es numérico)
        id_cliente = None
        if nombre_cliente and nombre_cliente.isdigit():
            id_cliente = int(nombre_cliente)
            # No tenemos el nombre real aquí, pero se puede mostrar el ID
            cliente_mostrar = f"Cliente ID {id_cliente}"
        else:
            cliente_mostrar = nombre_cliente if nombre_cliente else (cliente_rapido if cliente_rapido else "Cliente")
        historial = ServicioHistorialDeudas.obtener_por_cliente(cliente_mostrar, id_cliente)
        if not historial:
            messagebox.showinfo("Información", f"No se encontraron deudas para {cliente_mostrar}.", parent=parent)
            return
        titulo = f"Historial de Deudas de: {cliente_mostrar}"

    # --- Crear ventana principal ---
    ventana = tk.Toplevel(parent)
    ventana.title(titulo)
    ventana.geometry("1300x700+10+10")
    ventana.configure(bg="#E6D9E3")
    ventana.resizable(False, False)
    try:
        ventana.transient(parent)
        ventana.grab_set()
        ventana.attributes("-topmost", True)
    except Exception:
        pass

    # Título
    label_titulo = tk.Label(
        ventana,
        text=titulo,
        font=("Helvetica", 17, "bold"),
        bg="#8e24aa",
        fg="white",
        pady=12
    )
    label_titulo.pack(fill="x")

    saldo_actual = historial[-1]["saldo_numerico"] if historial else 0
    label_saldo_actual = tk.Label(
        ventana,
        text=f"Saldo actual: {peso_colombiano(saldo_actual)}",
        font=("Helvetica", 16, "bold"),
        bg="#E6D9E3",
        fg="#B22222",
        pady=12
    )
    label_saldo_actual.pack(fill="x", padx=30, pady=(10, 5))

    # Frame para la tabla
    frame_tabla = tk.Frame(ventana, bg="#F5F5F5")
    frame_tabla.pack(padx=30, pady=(10, 5), fill="both", expand=True)

    # Columnas: ID (oculto), N°, Producto, Día, Fecha, Hora, Acción,
    # Cantidad, Subtotal, Saldo, Abono, Recibido, Vuelto
    columnas = (
        "ID", "N°", "Producto", "Día", "Fecha", "Hora", "Acción",
        "Cantidad", "Subtotal", "Saldo", "Abono", "Recibido", "Vuelto"
    )
    tree = ttk.Treeview(
        frame_tabla,
        columns=columnas,
        show="headings",
        height=10,
    )
    # Anchos de columna
    anchos = [0, 50, 240, 90, 100, 80, 80, 70, 110, 110, 130, 100, 110]
    for col, ancho in zip(columnas, anchos):
        tree.heading(col, text=col)
        tree.column(col, width=ancho, anchor="center")
    tree.column("ID", width=0, stretch=tk.NO)
    tree.column("Producto", anchor="w")
    tree.column("Subtotal", anchor="e")
    tree.column("Saldo", anchor="e")
    tree.column("Abono", anchor="e")
    tree.column("Recibido", anchor="e")
    tree.column("Vuelto", anchor="e")

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # Scroll con rueda del mouse
    def _on_mousewheel(event):
        tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
    tree.bind("<Enter>", lambda e: tree.bind_all("<MouseWheel>", _on_mousewheel))
    tree.bind("<Leave>", lambda e: tree.unbind_all("<MouseWheel>"))

    # Cargar datos en la tabla (en orden inverso: más reciente primero)
    for registro in reversed(historial):
        # Asignar tag "abono" si la acción es 'ABONO'
        tag = "abono" if registro["accion"] == "ABONO" else ""
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
                registro["saldo"],
                registro["abono"],
                registro["recibido"],
                registro["vuelto"],
            ),
            tags=(tag,)
        )
    tree.tag_configure("abono", foreground="#0B6623")  # Verde oscuro para abonos

    frame_totales = tk.Frame(ventana, bg="#E6D9E3")
    ventana.mainloop()