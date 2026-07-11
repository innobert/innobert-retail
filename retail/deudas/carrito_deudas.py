"""
carrito_deudas.py

Módulo para mostrar y gestionar el carrito de deudas con un diseño
accesible y compacto. Prioriza la legibilidad (fuentes grandes, filas altas)
sin desperdiciar espacio en blanco. Permite editar cantidades, eliminar productos
y confirmar la deuda. La ventana es redimensionable.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from retail.nucleo.configuraciones import (
    COLOR_FONDO_EDITAR,
    COLOR_AZUL,
    COLOR_VERDE,
    COLOR_ROJO,
    crear_boton,
    DEUDAS_BOTON_EXITO,
    DEUDAS_BOTON_PELIGRO,
    FUENTE_BOTON_NEGRITA,
    FUENTE_BOTON_GRANDE,
)
from retail.nucleo.servicios.deudas.servicio_deudas import DeudasServicio
from retail.nucleo.servicios.deudas.servicio_carrito_deudas import ServicioCarritoDeudas


def peso_colombiano(value: float) -> str:
    """Formatea un número a pesos colombianos con separadores de miles."""
    return f"${value:,.0f}".replace(",", ".")


def ver_carrito_deuda(deudas_view: Any) -> None:
    """
    Muestra el carrito de deudas en una ventana redimensionable.
    """
    if not deudas_view.carrito_deuda:
        messagebox.showinfo(
            "Carrito vacío", "No hay productos en el carrito.", parent=deudas_view
        )
        return

    # Ventana redimensionable y más amplia inicialmente
    top = tk.Toplevel(deudas_view)
    top.title("Carrito de Deudas")
    top.geometry("850x550+150+30")
    top.configure(bg=COLOR_FONDO_EDITAR)
    # Bloquear redimensionamiento para mantener la integridad del diseño
    top.resizable(False, False)
    top.maxsize(850, 550)
    top.grab_set()
    top.focus_force()
    top.bind("<Escape>", lambda e: top.destroy())
    top.bind("<Return>", lambda e: confirmar_deuda())

    carrito = deudas_view.carrito_deuda

    # Frame principal con grid para control preciso
    main_frame = tk.Frame(top, bg=COLOR_FONDO_EDITAR)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---- Área de la tabla (se expande) ----
    frame_tabla = tk.Frame(main_frame, bg="#FFFFFF", bd=1, relief="solid")
    frame_tabla.pack(fill="both", expand=True, pady=(0, 8))

    # Configurar Treeview con estilo accesible (fuente más grande, filas altas)
    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure(
        "DeudasCarrito.Treeview.Heading",
        font=("Helvetica", 12, "bold"),
        background=COLOR_AZUL,
        foreground="#ffffff",
        relief="flat",
    )
    style.configure(
        "DeudasCarrito.Treeview",
        font=("Helvetica", 12),
        rowheight=38,  # Filas altas para mejor legibilidad
        background="#F8FAFB",
        fieldbackground="#F8FAFB",
        borderwidth=0,
    )
    style.map("DeudasCarrito.Treeview", background=[("selected", "#105A65")])

    tree = ttk.Treeview(
        frame_tabla,
        columns=("producto", "cantidad", "subtotal"),
        show="headings",
        style="DeudasCarrito.Treeview",
    )
    tree.heading("producto", text="Producto")
    tree.heading("cantidad", text="Cant.")
    tree.heading("subtotal", text="Subtotal")

    # Columnas expansibles: producto toma el espacio sobrante
    tree.column("producto", width=300, minwidth=200, stretch=True)
    tree.column("cantidad", width=80, minwidth=70, stretch=False, anchor="center")
    tree.column("subtotal", width=130, minwidth=100, stretch=False, anchor="e")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    # Cargar datos en el Treeview
    iid_map = {}  # mapea iid -> (índice real en carrito, diccionario del producto)
    for idx, item in enumerate(carrito):
        iid = str(idx)
        tree.insert(
            "",
            "end",
            iid=iid,
            values=(
                item["producto"],
                item["cantidad"],
                peso_colombiano(item["subtotal"]),
            ),
        )
        iid_map[iid] = (idx, item)

    # ---- Barra de herramientas compacta (Total + Eliminar) ----
    toolbar = tk.Frame(main_frame, bg=COLOR_FONDO_EDITAR)
    toolbar.pack(fill="x", pady=(0, 8))

    # Total (izquierda)
    total_label = tk.Label(
        toolbar, text="Total:", font=("Helvetica", 14, "bold"), bg=COLOR_FONDO_EDITAR, fg="#333"
    )
    total_label.pack(side="left", padx=(0, 8))
    total_valor = tk.Label(
        toolbar,
        text=peso_colombiano(sum(item["subtotal"] for item in carrito)),
        font=("Helvetica", 16, "bold"),
        bg=COLOR_FONDO_EDITAR,
        fg="#0B6623",
    )
    total_valor.pack(side="left")

    # Botón Eliminar producto (derecha)
    def eliminar_producto() -> None:
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia", "Seleccione un producto para eliminar.", parent=top
            )
            return
        iid = seleccion[0]
        orig_idx, prod = iid_map[iid]
        ServicioCarritoDeudas.eliminar_producto_del_carrito(carrito, orig_idx)
        tree.delete(iid)
        # Reconstruir iid_map y actualizar total
        if not carrito:
            top.destroy()
            messagebox.showinfo(
                "Carrito vacío", "No hay productos en el carrito.", parent=deudas_view
            )
            return
        # Actualizar total en toolbar
        nuevo_total = sum(item["subtotal"] for item in carrito)
        total_valor.config(text=peso_colombiano(nuevo_total))
        deudas_view.actualizar_total_carrito_display()

    btn_eliminar = crear_boton(
        toolbar,
        texto="Eliminar producto",
        comando=eliminar_producto,
        estilo=DEUDAS_BOTON_PELIGRO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=5,
        cursor="hand2",
    )
    btn_eliminar.pack(side="right")

    # ---- Botón CONFIRMAR DEUDA (rojo, grande) ----
    btn_confirmar = crear_boton(
        main_frame,
        texto="CONFIRMAR DEUDA",
        estilo=DEUDAS_BOTON_EXITO,
        fuente=FUENTE_BOTON_GRANDE,
        cursor="hand2",
        height=1,
        padx=20,
        pady=8,
    )
    btn_confirmar.pack(fill="x", pady=(0, 0))

    # ---- Funciones de edición de cantidad (doble clic) ----
    def editar_cantidad(event: Any) -> None:
        seleccion = tree.selection()
        if not seleccion:
            return
        iid = seleccion[0]
        orig_idx, prod = iid_map[iid]
        id_producto = prod["id_producto"]

        stock_actual = DeudasServicio.obtener_stock_actual(id_producto)
        if stock_actual is None:
            messagebox.showerror("Error", "No se pudo obtener el stock.", parent=top)
            return

        valido, _, msg = ServicioCarritoDeudas.validar_cantidad_para_edicion(
            carrito, id_producto, prod["cantidad"], prod
        )
        if not valido:
            messagebox.showwarning("Stock insuficiente", msg, parent=top)
            return

        # Diálogo compacto y legible
        popup = tk.Toplevel(top)
        popup.title("Editar cantidad")
        popup.geometry("320x200+500+250")
        popup.configure(bg=COLOR_FONDO_EDITAR)
        popup.resizable(False, False)
        popup.transient(top)
        popup.grab_set()

        def validar_entero(valor: str) -> bool:
            return valor == "" or (valor.isdigit() and int(valor) > 0)

        vcmd = (popup.register(validar_entero), "%P")

        tk.Label(
            popup, text=prod["producto"], font=("Helvetica", 13, "bold"), bg=COLOR_FONDO_EDITAR
        ).pack(pady=(12, 5))
        tk.Label(
            popup,
            text=f"Stock disponible: {stock_actual}",
            font=("Helvetica", 11),
            bg=COLOR_FONDO_EDITAR,
            fg="#008B8B",
        ).pack(pady=(0, 12))
        frame_cant = tk.Frame(popup, bg=COLOR_FONDO_EDITAR)
        frame_cant.pack(pady=5)
        tk.Label(
            frame_cant, text="Cantidad:", font=("Helvetica", 11), bg=COLOR_FONDO_EDITAR
        ).pack(side="left", padx=5)
        entry_cant = tk.Entry(
            frame_cant,
            font=("Helvetica", 12),
            width=10,
            validate="key",
            validatecommand=vcmd,
        )
        entry_cant.pack(side="left")
        entry_cant.insert(0, str(prod["cantidad"]))
        entry_cant.focus()
        entry_cant.select_range(0, tk.END)

        def guardar() -> None:
            try:
                nueva = int(entry_cant.get())
                if nueva <= 0:
                    messagebox.showwarning(
                        "Cantidad inválida", "Debe ser mayor a cero.", parent=popup
                    )
                    return
                stock_act2 = DeudasServicio.obtener_stock_actual(id_producto)
                if stock_act2 is None:
                    messagebox.showerror(
                        "Error", "No se pudo obtener stock.", parent=popup
                    )
                    return
                valido2, _, msg2 = ServicioCarritoDeudas.validar_cantidad_para_edicion(
                    carrito, id_producto, nueva, prod
                )
                if not valido2:
                    messagebox.showwarning("Stock insuficiente", msg2, parent=popup)
                    return
                # Actualizar carrito y UI
                ServicioCarritoDeudas.actualizar_cantidad_en_carrito(
                    carrito, orig_idx, nueva
                )
                tree.set(iid, "cantidad", nueva)
                tree.set(iid, "subtotal", peso_colombiano(prod["subtotal"]))
                # Recalcular total
                nuevo_total = sum(item["subtotal"] for item in carrito)
                total_valor.config(text=peso_colombiano(nuevo_total))
                deudas_view.actualizar_total_carrito_display()
                if (
                    nueva > prod["cantidad"]
                    and (stock_act2 - (nueva - prod["cantidad"])) == 0
                ):
                    messagebox.showinfo(
                        "Atención",
                        f"Stock agotado para '{prod['producto']}'.",
                        parent=top,
                    )
                popup.destroy()
            except ValueError:
                messagebox.showwarning(
                    "Error", "Ingrese un número válido.", parent=popup
                )

        entry_cant.bind("<Return>", lambda e: guardar())
        frame_btns = tk.Frame(popup, bg=COLOR_FONDO_EDITAR)
        frame_btns.pack(pady=15)
        crear_boton(
            frame_btns,
            texto="Guardar",
            comando=guardar,
            estilo=DEUDAS_BOTON_EXITO,
            width=10,
        ).pack(side="left", padx=8)
        crear_boton(
            frame_btns,
            texto="Cancelar",
            comando=popup.destroy,
            estilo=DEUDAS_BOTON_PELIGRO,
            width=10,
        ).pack(side="left", padx=8)

    tree.bind("<Double-1>", editar_cantidad)

    # ---- Confirmar deuda ----
    def confirmar_deuda() -> None:
        if not deudas_view.carrito_deuda:
            messagebox.showwarning(
                "Carrito vacío", "No hay productos para confirmar.", parent=top
            )
            return
        id_cliente = deudas_view.cliente_id_seleccionado
        if not id_cliente:
            messagebox.showerror(
                "Cliente requerido", "Debe seleccionar un cliente.", parent=top
            )
            return

        btn_confirmar.config(state="disabled", cursor="wait")
        top.config(cursor="wait")
        top.update_idletasks()
        try:
            result = ServicioCarritoDeudas.confirmar_deuda(
                carrito=deudas_view.carrito_deuda,
                cliente_id=id_cliente,
                usuario=deudas_view.controlador.usuario_actual,
            )
            deudas_view.carrito_deuda.clear()
            deudas_view.cliente_id_seleccionado = None
            deudas_view.entry_cliente.delete(0, tk.END)
            deudas_view.entry_producto.delete(0, tk.END)
            top.destroy()
            deudas_view.after(100, lambda: deudas_view.actualizar_canvas_productos())
            deudas_view.after(
                100, lambda: deudas_view.actualizar_total_carrito_display()
            )
            messagebox.showinfo(
                "✓ Deuda Confirmada",
                f"Se ha registrado la deuda correctamente.\nID: {result['id_deuda']}",
                parent=deudas_view,
            )
        except Exception as e:
            btn_confirmar.config(state="normal", cursor="hand2")
            top.config(cursor="")
            messagebox.showerror(
                "Error", f"No se pudo registrar la deuda: {e}", parent=top
            )

    btn_confirmar.config(command=confirmar_deuda)
