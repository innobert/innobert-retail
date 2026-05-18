"""
carrito_ventas.py

Módulo para mostrar y gestionar el carrito de ventas con un diseño claro,
espacioso y accesible. Permite editar cantidades, eliminar productos,
ingresar el monto recibido (con fuente grande), ver el vuelto calculado
y confirmar la venta. Teclas rápidas: Esc cierra la ventana, Enter confirma la venta.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from retail.nucleo.servicios.ventas.servicio_ventas import VentasServicio
from retail.nucleo.servicios.ventas.servicio_carrito_ventas import ServicioCarritoVentas


def peso_colombiano(value: float) -> str:
    """Formatea un número a pesos colombianos con separadores de miles."""
    return f"${value:,.0f}".replace(",", ".")


def ver_carrito(ventas_view) -> None:
    """
    Muestra el carrito de ventas en una ventana con diseño claro y legible.
    """
    if not ventas_view.carrito:
        messagebox.showinfo("Carrito vacío", "No hay productos en el carrito.", parent=ventas_view)
        return

    top = tk.Toplevel(ventas_view)
    top.title("Carrito de Ventas")
    top.geometry("900x650+150+30")
    top.configure(bg="#F4F6F8")
    # Bloquear redimensionamiento para mantener la integridad del diseño
    top.resizable(False, False)
    top.maxsize(900, 650)
    top.grab_set()
    top.focus_force()

    # ----- Bindings de teclado (sin afectar otras ventanas) -----
    top.bind("<Escape>", lambda e: top.destroy())   # Cerrar con Esc
    top.bind("<Return>", lambda e: confirmar_venta())  # Confirmar con Enter

    carrito = ventas_view.carrito
    clientes = {}
    for idx, item in enumerate(carrito):
        cliente = item["cliente"] if item["cliente"] else "Venta rápida"
        clientes.setdefault(cliente, []).append((idx, item))

    frame_main = tk.Frame(top, bg="#F4F6F8")
    frame_main.pack(fill="both", expand=True, padx=15, pady=15)

    totales_por_cliente = {}

    for cliente, items_con_indice in clientes.items():
        lf_cliente = tk.LabelFrame(
            frame_main,
            text=cliente,
            font=("Helvetica", 13, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            relief="groove",
            bd=2,
            padx=10,
            pady=10,
        )
        lf_cliente.pack(fill="both", expand=True, pady=(0, 15))

        frame_tabla = tk.Frame(lf_cliente, bg="#FFFFFF")
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))

        style = ttk.Style(top)
        style.theme_use("clam")
        style.configure(
            "VentasCarrito.Treeview.Heading",
            font=("Helvetica", 12, "bold"),
            background="#2196F3",
            foreground="#ffffff",
        )
        style.configure(
            "VentasCarrito.Treeview",
            font=("Helvetica", 11),
            rowheight=36,
            background="#F8FAFB",
            fieldbackground="#F8FAFB",
        )
        style.map("VentasCarrito.Treeview", background=[("selected", "#105A65")])

        tree = ttk.Treeview(
            frame_tabla,
            columns=("producto", "cantidad", "subtotal"),
            show="headings",
            style="VentasCarrito.Treeview",
        )
        tree.heading("producto", text="Producto")
        tree.heading("cantidad", text="Cantidad")
        tree.heading("subtotal", text="Subtotal")

        tree.column("producto", width=400, minwidth=250, stretch=True)
        tree.column("cantidad", width=100, minwidth=80, stretch=False, anchor="center")
        tree.column("subtotal", width=150, minwidth=120, stretch=False, anchor="e")
        tree.config(height=min(8, len(items_con_indice)))

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        iid_map = {}
        for orig_idx, prod in items_con_indice:
            iid = str(orig_idx)
            tree.insert(
                "", "end", iid=iid,
                values=(prod["producto"], prod["cantidad"], peso_colombiano(prod["subtotal"]))
            )
            iid_map[iid] = (orig_idx, prod)

        panel_total = tk.Frame(lf_cliente, bg="#FFFFFF", height=50)
        panel_total.pack(fill="x", pady=(0, 10))
        panel_total.pack_propagate(False)

        total_cliente = sum(prod["subtotal"] for _, prod in items_con_indice)
        lbl_total_texto = tk.Label(panel_total, text="Total:", font=("Helvetica", 14, "bold"),
                                   bg="#FFFFFF", fg="#333")
        lbl_total_texto.pack(side="left", padx=(0, 10))
        lbl_total_valor = tk.Label(panel_total, text=peso_colombiano(total_cliente),
                                   font=("Helvetica", 18, "bold"), bg="#FFFFFF", fg="#0B6623")
        lbl_total_valor.pack(side="left", padx=(0, 30))

        def eliminar_producto(tree=tree, iid_map=iid_map, cliente=cliente):
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un producto.", parent=top)
                return
            iid = seleccion[0]
            orig_idx, prod = iid_map[iid]
            ServicioCarritoVentas.eliminar_producto_del_carrito(carrito, orig_idx)
            tree.delete(iid)
            if not carrito:
                top.destroy()
                messagebox.showinfo("Carrito vacío", "No hay productos en el carrito.", parent=ventas_view)
                return
            if not any(item["cliente"] == cliente or (not item["cliente"] and cliente == "Venta rápida") for item in carrito):
                top.destroy()
                messagebox.showinfo("Carrito vacío", "No hay productos en el carrito.", parent=ventas_view)
                return
            nuevo_total = sum(item[1]["subtotal"] for item in clientes.get(cliente, []))
            lbl_total_valor.config(text=peso_colombiano(nuevo_total))
            actualizar_vuelto_cliente()
            ventas_view.actualizar_total_carrito_display()

        btn_eliminar = tk.Button(
            panel_total, text="Eliminar producto", command=eliminar_producto,
            bg="#F44336", fg="white", font=("Helvetica", 11, "bold"),
            relief="flat", padx=15, pady=5, cursor="hand2"
        )
        btn_eliminar.pack(side="right")

        panel_pago = tk.Frame(lf_cliente, bg="#FFFFFF", height=70)
        panel_pago.pack(fill="x", pady=(0, 10))
        panel_pago.pack_propagate(False)

        lbl_recibido = tk.Label(panel_pago, text="Monto recibido:", font=("Helvetica", 13, "bold"),
                                bg="#FFFFFF", fg="#333")
        lbl_recibido.pack(side="left", padx=(10, 10))
        monto_var = tk.StringVar(value="")
        entry_monto = tk.Entry(
            panel_pago, textvariable=monto_var, font=("Helvetica", 16, "bold"),
            width=12, justify="right", bg="#FFFFFF", relief="solid", bd=2
        )
        entry_monto.pack(side="left", padx=(0, 30))

        # Permitir que Enter en el campo monto también confirme la venta
        entry_monto.bind("<Return>", lambda e: confirmar_venta())

        lbl_vuelto_texto = tk.Label(panel_pago, text="Vuelto:", font=("Helvetica", 13, "bold"),
                                    bg="#FFFFFF", fg="#333")
        lbl_vuelto_texto.pack(side="left", padx=(0, 10))
        vuelto_var = tk.StringVar(value=peso_colombiano(0))
        lbl_vuelto = tk.Label(
            panel_pago, textvariable=vuelto_var, font=("Helvetica", 16, "bold"),
            bg="#FFFFFF", fg="#0B6623", width=12, relief="solid", bd=2, anchor="e"
        )
        lbl_vuelto.pack(side="left")

        def actualizar_vuelto_cliente():
            try:
                monto = float(monto_var.get().strip()) if monto_var.get().strip() else 0
            except ValueError:
                monto = 0
            total_actual = float(lbl_total_valor.cget("text").replace("$", "").replace(".", ""))
            vuelto = max(0, monto - total_actual)
            vuelto_var.set(peso_colombiano(vuelto))
            try:
                ventas_view.monto_recibido = monto_var.get().strip()
            except Exception:
                pass

        monto_var.trace_add("write", lambda *args: actualizar_vuelto_cliente())
        actualizar_vuelto_cliente()

        totales_por_cliente[cliente] = {
            "lbl_total": lbl_total_valor,
            "monto_var": monto_var,
            "vuelto_var": vuelto_var,
            "actualizar_vuelto": actualizar_vuelto_cliente,
            "tree": tree,
            "iid_map": iid_map,
            "items_indices": items_con_indice,
        }

        def editar_cantidad(event, tree=tree, iid_map=iid_map, cliente=cliente):
            seleccion = tree.selection()
            if not seleccion:
                return
            iid = seleccion[0]
            orig_idx, prod = iid_map[iid]
            id_producto = prod["id_producto"]

            stock_actual = VentasServicio.obtener_stock_actual(id_producto)
            if stock_actual is None:
                messagebox.showerror("Error", "No se pudo obtener el stock.", parent=top)
                return

            valido, _, msg = ServicioCarritoVentas.validar_cantidad_para_edicion(
                carrito, id_producto, prod["cantidad"], prod
            )
            if not valido:
                messagebox.showwarning("Stock insuficiente", msg, parent=top)
                return

            popup = tk.Toplevel(top)
            popup.title("Editar cantidad")
            popup.geometry("350x220+500+250")
            popup.configure(bg="#F4F6F8")
            popup.resizable(False, False)
            popup.transient(top)
            popup.grab_set()

            def validar_entero(valor):
                return valor == "" or (valor.isdigit() and int(valor) > 0)
            vcmd = (popup.register(validar_entero), "%P")

            tk.Label(popup, text=prod["producto"], font=("Helvetica", 14, "bold"),
                     bg="#F4F6F8").pack(pady=(15, 5))
            tk.Label(popup, text=f"Stock disponible: {stock_actual}", font=("Helvetica", 12),
                     bg="#F4F6F8", fg="#008B8B").pack(pady=(0, 15))
            frame_cant = tk.Frame(popup, bg="#F4F6F8")
            frame_cant.pack(pady=5)
            tk.Label(frame_cant, text="Cantidad:", font=("Helvetica", 12), bg="#F4F6F8").pack(side="left", padx=5)
            entry_cant = tk.Entry(frame_cant, font=("Helvetica", 13), width=8, validate="key", validatecommand=vcmd)
            entry_cant.pack(side="left")
            entry_cant.insert(0, str(prod["cantidad"]))
            entry_cant.focus()
            entry_cant.select_range(0, tk.END)

            def guardar():
                try:
                    nueva = int(entry_cant.get())
                    if nueva <= 0:
                        messagebox.showwarning("Cantidad inválida", "Debe ser mayor a cero.", parent=popup)
                        return
                    stock_act2 = VentasServicio.obtener_stock_actual(id_producto)
                    if stock_act2 is None:
                        messagebox.showerror("Error", "No se pudo obtener stock.", parent=popup)
                        return
                    valido2, _, msg2 = ServicioCarritoVentas.validar_cantidad_para_edicion(
                        carrito, id_producto, nueva, prod
                    )
                    if not valido2:
                        messagebox.showwarning("Stock insuficiente", msg2, parent=popup)
                        return
                    ServicioCarritoVentas.actualizar_cantidad_en_carrito(carrito, orig_idx, nueva)
                    tree.set(iid, "cantidad", nueva)
                    tree.set(iid, "subtotal", peso_colombiano(prod["subtotal"]))
                    nuevo_total_cliente = sum(item[1]["subtotal"] for item in clientes.get(cliente, []))
                    totales_por_cliente[cliente]["lbl_total"].config(text=peso_colombiano(nuevo_total_cliente))
                    totales_por_cliente[cliente]["actualizar_vuelto"]()
                    ventas_view.actualizar_total_carrito_display()
                    if nueva > prod["cantidad"] and (stock_act2 - (nueva - prod["cantidad"])) == 0:
                        messagebox.showinfo("Atención", f"Stock agotado para '{prod['producto']}'.", parent=top)
                    popup.destroy()
                except ValueError:
                    messagebox.showwarning("Error", "Ingrese un número válido.", parent=popup)

            entry_cant.bind("<Return>", lambda e: guardar())
            frame_btns = tk.Frame(popup, bg="#F4F6F8")
            frame_btns.pack(pady=15)
            tk.Button(frame_btns, text="Guardar", command=guardar, bg="#4CAF50", fg="white", width=10).pack(side="left", padx=8)
            tk.Button(frame_btns, text="Cancelar", command=popup.destroy, bg="#F44336", fg="white", width=10).pack(side="left", padx=8)

        tree.bind("<Double-1>", editar_cantidad)

    frame_confirmar = tk.Frame(frame_main, bg="#F4F6F8")
    frame_confirmar.pack(fill="x", pady=(10, 0))

    def confirmar_venta():
        if not ventas_view.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito.", parent=top)
            return

        monto_str = ""
        for data in totales_por_cliente.values():
            if data["monto_var"].get().strip():
                monto_str = data["monto_var"].get().strip()
                break
        if not monto_str:
            total = ServicioCarritoVentas.calcular_total_general(ventas_view.carrito)
            messagebox.showerror(
                "Monto requerido",
                f"Debe ingresar el monto recibido.\nTotal de la venta: {peso_colombiano(total)}",
                parent=top
            )
            return

        try:
            monto_recibido = float(monto_str)
        except ValueError:
            total = ServicioCarritoVentas.calcular_total_general(ventas_view.carrito)
            messagebox.showerror(
                "Monto inválido",
                f"Monto no válido.\nTotal: {peso_colombiano(total)}",
                parent=top
            )
            return

        total_carrito = ServicioCarritoVentas.calcular_total_general(ventas_view.carrito)
        if monto_recibido < total_carrito:
            messagebox.showerror(
                "Monto insuficiente",
                f"Monto recibido: {peso_colombiano(monto_recibido)}\nTotal: {peso_colombiano(total_carrito)}",
                parent=top
            )
            return

        id_cliente = None
        if ventas_view.entry_cliente.get().strip() and hasattr(ventas_view, 'cliente_id_seleccionado'):
            id_cliente = ventas_view.cliente_id_seleccionado

        btn_confirmar.config(state="disabled", cursor="wait")
        top.config(cursor="wait")
        top.update_idletasks()

        try:
            result = VentasServicio.confirmar_venta(
                carrito=ventas_view.carrito,
                cliente_id=id_cliente,
                monto_recibido=monto_recibido,
                usuario=ventas_view.controlador.usuario_actual
            )
            ventas_view.carrito.clear()
            ventas_view.cliente_id_seleccionado = None
            ventas_view.entry_cliente.delete(0, tk.END)
            ventas_view.entry_stock.delete(0, tk.END)
            top.destroy()
            ventas_view.after(100, lambda: ventas_view.actualizar_canvas_productos())
            ventas_view.after(100, lambda: ventas_view.actualizar_total_carrito_display())
            messagebox.showinfo(
                "✓ Venta Confirmada",
                f"Vuelto: {peso_colombiano(result['vuelto'])}",
                parent=ventas_view
            )
        except Exception as e:
            btn_confirmar.config(state="normal", cursor="hand2")
            top.config(cursor="")
            messagebox.showerror("Error", f"No se pudo registrar la venta: {e}", parent=top)

    btn_confirmar = tk.Button(
        frame_confirmar,
        text="CONFIRMAR VENTA",
        font=("Helvetica", 16, "bold"),
        bg="#2E7D32",
        fg="#FFFFFF",
        activebackground="#1B5E20",
        activeforeground="#FFFFFF",
        relief="raised",
        cursor="hand2",
        command=confirmar_venta,
        padx=20,
        pady=10,
    )
    btn_confirmar.pack(fill="x")