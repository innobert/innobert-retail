"""
edicion_ventas.py

Módulo para gestionar la edición profesional de facturas de ventas.

Flujo principal:
1. Se solicita el nuevo monto recibido (debe ser >= total actual de la factura).
2. Se muestra un selector con dos opciones:
   - Editar factura: tabla con productos de la factura, permite editar cantidades y eliminar.
   - Agregar productos: canvas con inventario, buscador y paginación, para añadir nuevos productos.
3. Desde las ventanas secundarias se puede regresar al selector (botón "Regresar").
Los cambios se aplican directamente a la base de datos y se registran en el historial con la acción correspondiente.

VALIDACIONES CLAVE:
- Nunca se permite que el total de la factura supere el monto recibido.
- El vuelto siempre se mantiene >= 0.
- Se informa al usuario la cantidad máxima permitida antes de editar/agregar.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

from retail.nucleo.base_datos import get_connection
from retail.nucleo.servicios.ventas.servicio_edicion_ventas import ServicioEdicionVentas
from retail.nucleo.servicios.ventas.servicio_ventas import VentasServicio
from retail.nucleo.configuraciones import rutas


# ---------------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA CÁLCULO DE CANTIDAD MÁXIMA
# ---------------------------------------------------------------------------
def calcular_cantidad_maxima(total_actual: float, precio_unitario: float, monto_recibido: float) -> int:
    """
    Calcula la cantidad adicional permitida para un producto sin superar
    el monto recibido.

    Args:
        total_actual: Total actual de la factura (sin el producto en cuestión)
        precio_unitario: Precio unitario del producto
        monto_recibido: Monto que el cliente pagó

    Returns:
        Cantidad adicional permitida (mínimo 0).
    """
    if precio_unitario <= 0:
        return 0
    espacio_disponible = monto_recibido - total_actual
    if espacio_disponible <= 0:
        return 0
    return int(espacio_disponible // precio_unitario)


# ---------------------------------------------------------------------------
# DIÁLOGO PARA SOLICITAR EL MONTO RECIBIDO
# ---------------------------------------------------------------------------
def _solicitar_monto_recibido(ventana_padre, cliente, total_actual, monto_anterior):
    """
    Abre una ventana modal para que el usuario ingrese el nuevo monto recibido.
    Valida que el monto sea mayor o igual al total actual y mayor a cero.
    Retorna el monto ingresado como float, o None si se cancela.
    """
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Ingrese Monto Recibido")
    ventana.geometry("400x300+400+200")
    ventana.configure(bg="#E6D9E3")
    ventana.resizable(False, False)
    ventana.maxsize(400, 300)
    ventana.transient(ventana_padre)
    ventana.grab_set()

    monto_resultado = [None]  # Usamos lista mutable para modificar desde funciones anidadas
    var_vuelto = tk.StringVar(value=f"${monto_anterior - total_actual:,.0f}".replace(",", "."))

    def cerrar_ventana():
        monto_resultado[0] = None
        ventana.destroy()

    ventana.bind("<Escape>", lambda e: cerrar_ventana())

    frame_main = tk.Frame(ventana, bg="#E6D9E3")
    frame_main.pack(fill="both", expand=True, padx=20, pady=20)

    # Información al usuario
    tk.Label(frame_main, text=f"Cliente: {cliente}", font=("Helvetica",12,"bold"),
             bg="#E6D9E3", fg="#1a1a1a").pack(pady=(0,10))
    tk.Label(frame_main, text=f"Total actual: ${total_actual:,.0f}".replace(",", "."),
             font=("Helvetica",14,"bold"), bg="#E6D9E3", fg="#0B6623").pack(pady=(0,15))
    tk.Label(frame_main, text=f"Monto anterior: ${monto_anterior:,.0f}".replace(",", "."),
             font=("Helvetica",11), bg="#E6D9E3", fg="#666666").pack(pady=(0,20))

    # Campo de entrada para el monto
    frame_entrada = tk.Frame(frame_main, bg="#E6D9E3")
    frame_entrada.pack(pady=(0,15))
    tk.Label(frame_entrada, text="Monto recibido:", font=("Helvetica",12,"bold"),
             bg="#E6D9E3").pack(side="left", padx=(0,10))

    def validar_numero(valor):
        return valor == "" or valor.isdigit()
    vcmd = (ventana.register(validar_numero), "%P")

    entry_monto = tk.Entry(frame_entrada, font=("Helvetica",14), width=15,
                           validate="key", validatecommand=vcmd, justify="right")
    entry_monto.pack(side="left")
    entry_monto.insert(0, f"{int(monto_anterior)}")
    entry_monto.focus_set()

    # Vuelto calculado en tiempo real
    frame_vuelto = tk.Frame(frame_main, bg="#E6D9E3")
    frame_vuelto.pack(pady=(0,20))
    tk.Label(frame_vuelto, text="Vuelto:", font=("Helvetica",12,"bold"),
             bg="#E6D9E3").pack(side="left", padx=(0,10))
    tk.Label(frame_vuelto, textvariable=var_vuelto, font=("Helvetica",14,"bold"),
             bg="#E6D9E3", fg="#0B6623", width=15).pack(side="left")

    def actualizar_vuelto(*args):
        try:
            monto_str = entry_monto.get().strip()
            monto = float(monto_str) if monto_str else 0
            vuelto = monto - total_actual
            var_vuelto.set(f"${max(0, vuelto):,.0f}".replace(",", "."))
        except:
            var_vuelto.set("$0")
    entry_monto.bind("<KeyRelease>", lambda e: actualizar_vuelto())

    def confirmar():
        try:
            monto = float(entry_monto.get().strip())
            if monto <= 0:
                messagebox.showwarning("Monto inválido", "Debe ser mayor a 0.", parent=ventana)
                return
            if monto < total_actual:
                messagebox.showerror("Monto insuficiente", f"El monto ${monto:,.0f} es menor al total ${total_actual:,.0f}.", parent=ventana)
                return
            monto_resultado[0] = monto
            ventana.destroy()
        except:
            messagebox.showwarning("Valor inválido", "Ingrese un número.", parent=ventana)

    entry_monto.bind("<Return>", lambda e: confirmar())

    frame_botones = tk.Frame(frame_main, bg="#E6D9E3")
    frame_botones.pack(pady=(0,0))
    tk.Button(frame_botones, text="Confirmar", command=confirmar,
              bg="#4CAF50", fg="white", font=("Helvetica",12,"bold"), width=12).pack(side="left", padx=5)
    tk.Button(frame_botones, text="Cancelar", command=cerrar_ventana,
              bg="#F44336", fg="white", font=("Helvetica",12,"bold"), width=12).pack(side="left", padx=5)

    ventana.wait_window()
    return monto_resultado[0]


# ---------------------------------------------------------------------------
# SELECTOR DE ACCIONES (EDITAR FACTURA / AGREGAR PRODUCTOS)
# ---------------------------------------------------------------------------
def _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks):
    """
    Muestra una ventana modal con dos botones: "Editar factura" y "Agregar productos".
    Al hacer clic en cualquiera, se destruye el selector y se abre la ventana correspondiente.
    """
    selector = tk.Toplevel(ventana_padre)
    selector.title("Opciones de factura")
    selector.geometry("420x220+500+200")
    selector.configure(bg="#E6D9E3")
    selector.resizable(False, False)
    selector.maxsize(420, 220)
    selector.transient(ventana_padre)

    tk.Label(selector, text="¿Qué deseas hacer con esta factura?",
             font=("Helvetica", 14, "bold"), bg="#E6D9E3", pady=14).pack(fill="x")

    frame_botones = tk.Frame(selector, bg="#E6D9E3")
    frame_botones.pack(fill="x", padx=20, pady=10)

    def abrir_editar():
        selector.destroy()
        _abrir_ventana_editar_factura(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)

    def abrir_agregar():
        selector.destroy()
        _abrir_ventana_agregar_productos(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)

    tk.Button(frame_botones, text="Editar factura", font=("Helvetica",12,"bold"),
              bg="#1976D2", fg="white", width=16, height=2, command=abrir_editar
             ).pack(side="left", expand=True, padx=10)

    tk.Button(frame_botones, text="Agregar productos", font=("Helvetica",12,"bold"),
              bg="#4CAF50", fg="white", width=16, height=2, command=abrir_agregar
             ).pack(side="right", expand=True, padx=10)

    tk.Button(selector, text="Cancelar", font=("Helvetica",10,"bold"),
              bg="#F44336", fg="white", width=12, command=selector.destroy
             ).pack(side="bottom", pady=12)


# ---------------------------------------------------------------------------
# VENTANA DE EDICIÓN DE FACTURA (permite modificar cantidades y eliminar productos)
# ---------------------------------------------------------------------------
def _abrir_ventana_editar_factura(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks):
    """
    Abre la ventana principal para editar los productos de la factura.
    Muestra una tabla con los productos actuales, permite filtrar,
    editar cantidades (doble clic), eliminar productos y refrescar.
    """
    top = tk.Toplevel(ventana_padre)
    top.title(f"Editar factura - {cliente}")
    top.geometry("950x650+150+30")
    top.configure(bg="#F4F6F8")
    # Bloquear redimensionamiento para mantener la integridad del diseño
    top.resizable(False, False)
    top.maxsize(950, 650)
    top.transient(ventana_padre)
    top.lift()
    top.focus_force()

    conn_edicion = get_connection()
    cursor_edicion = conn_edicion.cursor()
    cambios_realizados = False

    def cancelar_edicion():
        nonlocal cambios_realizados
        if cambios_realizados:
            if not messagebox.askyesno(
                "Cambios sin confirmar",
                "Hay cambios sin confirmar.\n¿Desea descartarlos y regresar al selector?",
                parent=top
            ):
                return
            conn_edicion.rollback()
        else:
            conn_edicion.rollback()
        conn_edicion.close()
        top.destroy()
        _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)

    def confirmar_cambios():
        nonlocal cambios_realizados
        if not messagebox.askyesno(
            "Confirmar cambios",
            "¿Desea confirmar los cambios realizados en esta factura?\n\nEsta acción cerrará la edición y actualizará el listado principal.",
            parent=top
        ):
            return
        try:
            conn_edicion.commit()
            cambios_realizados = False
            conn_edicion.close()
            top.destroy()
            _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)
            _notificar_cambios(callbacks)
        except Exception as err:
            messagebox.showerror("Error", f"No se pudieron confirmar los cambios:\n{err}", parent=top)

    def on_close():
        if cambios_realizados:
            if messagebox.askyesno(
                "Confirmar salida",
                "Hay cambios pendientes.\n¿Desea confirmar antes de salir?\n\nSi no confirma, los cambios se descartarán.",
                parent=top
            ):
                confirmar_cambios()
            else:
                conn_edicion.rollback()
                conn_edicion.close()
                top.destroy()
                _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)
        else:
            conn_edicion.rollback()
            conn_edicion.close()
            top.destroy()
            _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)

    top.protocol("WM_DELETE_WINDOW", on_close)

    # Panel informativo con totales
    frame_info = tk.Frame(top, bg="#F4F6F8", pady=8)
    frame_info.pack(fill="x", padx=15, pady=(10,5))

    tk.Label(frame_info, text="Total deuda:", font=("Helvetica",14,"bold"), bg="#F4F6F8").pack(side="left", padx=(0,8))
    var_total = tk.StringVar(value="$0")
    tk.Label(frame_info, textvariable=var_total, font=("Helvetica",18,"bold"), bg="#F4F6F8", fg="#0B6623").pack(side="left", padx=(0,30))

    tk.Label(frame_info, text="Monto recibido:", font=("Helvetica",14,"bold"), bg="#F4F6F8").pack(side="left", padx=(0,8))
    var_monto = tk.StringVar(value=f"${monto_recibido:,.0f}".replace(",", "."))
    tk.Label(frame_info, textvariable=var_monto, font=("Helvetica",18,"bold"), bg="#F4F6F8", fg="#0D47A1").pack(side="left", padx=(0,30))

    tk.Label(frame_info, text="Vuelto:", font=("Helvetica",14,"bold"), bg="#F4F6F8").pack(side="left", padx=(0,8))
    var_vuelto = tk.StringVar(value="$0")
    tk.Label(frame_info, textvariable=var_vuelto, font=("Helvetica",18,"bold"), bg="#F4F6F8", fg="#0B6623").pack(side="left")

    # Filtro de productos (sobre la tabla actual)
    frame_buscar = tk.Frame(top, bg="#F4F6F8")
    frame_buscar.pack(fill="x", padx=15, pady=(0,10))
    tk.Label(frame_buscar, text="Filtrar producto:", font=("Helvetica",12,"bold"), bg="#F4F6F8").pack(side="left", padx=(0,10))
    entry_filtro = ttk.Entry(frame_buscar, font=("Helvetica",12), width=35)
    entry_filtro.pack(side="left", fill="x", expand=True, padx=5)
    tk.Button(frame_buscar, text="Limpiar", command=lambda: (entry_filtro.delete(0, tk.END), filtrar_tabla()),
              bg="#757575", fg="white", font=("Helvetica",11,"bold"), padx=12, pady=3).pack(side="left", padx=(10,0))

    # Tabla de productos
    frame_tabla = tk.Frame(top, bg="#FFFFFF", bd=1, relief="solid")
    frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0,10))

    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure("EditarVenta.Treeview.Heading", font=("Helvetica",12,"bold"), background="#2196F3", foreground="#ffffff")
    style.configure("EditarVenta.Treeview", font=("Helvetica",11), rowheight=40, background="#F8FAFB")
    style.map("EditarVenta.Treeview", background=[("selected", "#105A65")])

    tree = ttk.Treeview(frame_tabla, columns=("id_detalle","producto","cantidad","precio","subtotal"),
                        show="headings", style="EditarVenta.Treeview")
    tree.heading("id_detalle", text="ID")
    tree.heading("producto", text="Producto")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("precio", text="Precio Unit.")
    tree.heading("subtotal", text="Subtotal")
    tree.column("id_detalle", width=0, stretch=False)
    tree.column("producto", width=370, stretch=True, anchor="w")
    tree.column("cantidad", width=100, anchor="center")
    tree.column("precio", width=130, anchor="center")
    tree.column("subtotal", width=150, anchor="e")

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Botones de acción
    frame_acciones = tk.Frame(top, bg="#F4F6F8")
    frame_acciones.pack(fill="x", padx=15, pady=(0,10))
    btn_eliminar = tk.Button(frame_acciones, text="Eliminar producto seleccionado", bg="#F44336", fg="white",
                             font=("Helvetica",12,"bold"), padx=12, pady=6, command=lambda: eliminar_producto())
    btn_eliminar.pack(side="left", padx=5)
    btn_regresar = tk.Button(frame_acciones, text="Regresar", bg="#607D8B", fg="white",
                             font=("Helvetica",12,"bold"), padx=12, pady=6, command=cancelar_edicion)
    btn_regresar.pack(side="left", padx=5)
    btn_confirmar = tk.Button(frame_acciones, text="Confirmar", bg="#4CAF50", fg="white",
                              font=("Helvetica",12,"bold"), padx=18, pady=6, command=confirmar_cambios)
    btn_confirmar.pack(side="right", padx=5)

    # Funciones internas de la ventana
    def cargar_datos():
        try:
            detalles = ServicioEdicionVentas.obtener_detalles_factura(id_ventas, conn=conn_edicion)
            total_actual, _, _ = ServicioEdicionVentas.obtener_info_factura(id_ventas, conn=conn_edicion)
            tree.delete(*tree.get_children())
            for d in detalles:
                tree.insert("", "end", iid=str(d['id_detalle']),
                            values=(d['id_detalle'], d['producto'], d['cantidad'],
                                    f"${d['precio_unit']:,.0f}".replace(",", "."),
                                    f"${d['subtotal']:,.0f}".replace(",", ".")))
            var_total.set(f"${total_actual:,.0f}".replace(",", "."))
            var_vuelto.set(f"${monto_recibido - total_actual:,.0f}".replace(",", "."))
        except Exception as err:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{err}", parent=top)

    def eliminar_producto():
        nonlocal cambios_realizados
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto.", parent=top)
            return
        id_detalle = int(seleccion[0])
        item = tree.item(seleccion[0])
        producto = item['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{producto}'?", parent=top):
            try:
                trashed_timestamp = ServicioEdicionVentas.eliminar_detalle_venta(
                    id_detalle,
                    usuario_actual,
                    monto_recibido,
                    conn=conn_edicion,
                    cursor=cursor_edicion
                )
                if trashed_timestamp:
                    conn_edicion.commit()
                    cambios_realizados = False
                    messagebox.showinfo(
                        "Factura enviada a papelera",
                        f"La factura quedó vacía y se envió a la papelera\ncon fecha y hora: {trashed_timestamp}",
                        parent=top
                    )
                    conn_edicion.close()
                    top.destroy()
                    _notificar_cambios(callbacks)
                    return
                cambios_realizados = True
                cargar_datos()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo eliminar el producto:\n{err}", parent=top)

    def editar_cantidad(event):
        seleccion = tree.selection()
        if not seleccion:
            return
        iid = seleccion[0]
        id_detalle = int(iid)
        item = tree.item(iid)
        producto = item['values'][1]
        cantidad_actual = int(item['values'][2])
        precio_unit_str = item['values'][3].replace("$", "").replace(".", "")
        precio_unit = float(precio_unit_str)
        subtotal_actual = float(item['values'][4].replace("$", "").replace(".", ""))
        total_actual = float(var_total.get().replace("$", "").replace(".", ""))

        cantidad_permitida = calcular_cantidad_maxima(
            total_actual - subtotal_actual, precio_unit, monto_recibido
        )
        limite_final = cantidad_actual + cantidad_permitida

        popup = tk.Toplevel(top)
        popup.title(f"Editar cantidad - {producto}")
        popup.geometry("380x320+500+250")
        popup.configure(bg="#F4F6F8")
        popup.resizable(False, False)
        popup.maxsize(380, 320)
        popup.transient(top)
        popup.grab_set()

        # Mostrar información ordenada
        tk.Label(popup, text=producto, font=("Helvetica",14,"bold"), bg="#F4F6F8").pack(pady=(15,8))
        
        info_frame = tk.Frame(popup, bg="#F4F6F8")
        info_frame.pack(pady=(0,15))
        
        tk.Label(info_frame, text=f"Cantidad actual: {cantidad_actual}", font=("Helvetica",12),
                 bg="#F4F6F8").pack(anchor="w", padx=10)
        tk.Label(info_frame, text=f"Cantidad permitida: {cantidad_permitida}",
                 font=("Helvetica",12), bg="#F4F6F8", fg="#0D47A1").pack(anchor="w", padx=10)
        if cantidad_permitida == 0:
            tk.Label(info_frame, text="No puede aumentar la cantidad adicional con el monto recibido actual.",
                     font=("Helvetica",12, "italic"), bg="#F4F6F8", fg="#C62828").pack(anchor="w", padx=10)

        tk.Label(popup, text="Nueva cantidad:", font=("Helvetica",12), bg="#F4F6F8").pack(pady=(0,6))
        entry_cant = tk.Entry(popup, font=("Helvetica",13), width=10, justify="center")
        entry_cant.pack()
        entry_cant.insert(0, str(cantidad_actual))
        entry_cant.focus()
        entry_cant.select_range(0, tk.END)

        lbl_mensaje = tk.Label(popup, text="", font=("Helvetica",10), bg="#F4F6F8", fg="#C62828")
        lbl_mensaje.pack(pady=(5,0))

        def validar_entero(valor):
            return valor == "" or valor.isdigit()

        vcmd = (popup.register(validar_entero), "%P")
        entry_cant.config(validate="key", validatecommand=vcmd)

        def guardar():
            nonlocal cambios_realizados
            texto = entry_cant.get().strip()
            if not texto:
                messagebox.showwarning("Cantidad inválida", "Ingrese un número entero mayor a 0.", parent=popup)
                return
            if not texto.isdigit():
                messagebox.showwarning("Cantidad inválida", "Ingrese un número entero válido mayor a 0.", parent=popup)
                return
            nueva = int(texto)
            if nueva <= 0:
                messagebox.showwarning("Cantidad inválida", "Ingrese un número mayor a 0.", parent=popup)
                return
            if nueva == cantidad_actual:
                messagebox.showinfo("Sin cambios", "No se realizó ningún cambio porque la cantidad es igual a la actual.", parent=popup)
                popup.destroy()
                return
            if nueva > limite_final:
                messagebox.showerror(
                    "Cantidad no permitida",
                    f"No puede poner {nueva} unidades.\n"
                    f"Ingrese un valor entre {cantidad_actual} y {limite_final} para no superar lo recibido.",
                    parent=popup
                )
                return
            try:
                ServicioEdicionVentas.editar_cantidad_detalle(id_detalle, nueva, usuario_actual, monto_recibido,
                                                               conn=conn_edicion, cursor=cursor_edicion)
                cambios_realizados = True
                if nueva == limite_final and cantidad_permitida > 0:
                    messagebox.showinfo("Límite utilizado", "Ha usado la cantidad permitida completa. No quedan unidades adicionales disponibles.", parent=popup)
                else:
                    messagebox.showinfo("Éxito", "Cantidad actualizada correctamente.", parent=popup)
                cargar_datos()
                popup.destroy()
            except Exception as err:
                messagebox.showerror("Error", f"No se pudo actualizar la cantidad:\n{err}", parent=popup)

        def actualizar_mensaje(*args):
            texto = entry_cant.get().strip()
            if not texto:
                lbl_mensaje.config(text="")
                return
            if not texto.isdigit():
                lbl_mensaje.config(text=f"⚠️ Solo se permiten números enteros entre 1 y {limite_final}")
                return
            nueva = int(texto)
            if nueva > limite_final:
                lbl_mensaje.config(text=f"⚠️ Ingrese un valor entre 1 y {limite_final}")
            else:
                lbl_mensaje.config(text="")

        entry_cant.bind("<KeyRelease>", actualizar_mensaje)
        entry_cant.bind("<Return>", lambda e: guardar())
        tk.Button(popup, text="Guardar", command=guardar, bg="#4CAF50", fg="white",
                  font=("Helvetica",11,"bold"), padx=12, pady=4).pack(pady=18)

    def filtrar_tabla():
        texto = entry_filtro.get().strip().lower()
        for item in tree.get_children():
            prod = tree.item(item, "values")[1].lower()
            if texto in prod:
                tree.reattach(item, "", "end")
            else:
                tree.detach(item)

    tree.bind("<Double-1>", editar_cantidad)
    entry_filtro.bind("<KeyRelease>", lambda e: filtrar_tabla())
    cargar_datos()


# ---------------------------------------------------------------------------
# VENTANA PARA AGREGAR PRODUCTOS (canvas con paginación y buscador)
# ---------------------------------------------------------------------------
def _abrir_ventana_agregar_productos(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks):
    """
    Abre una ventana que muestra todos los productos disponibles en el inventario
    organizados en un canvas con paginación, buscador y tarjetas con imagen.
    Al hacer doble clic en un producto, se abre un diálogo para elegir cantidad,
    mostrando la cantidad máxima permitida según el monto recibido.
    """
    top = tk.Toplevel(ventana_padre)
    top.title(f"Agregar productos - {cliente}")
    top.geometry("900x650+130+20")
    top.configure(bg="#E6D9E3")
    top.minsize(900, 650)
    top.resizable(True, True)
    top.transient(ventana_padre)
    top.lift()

    # Buscador de productos
    frame_buscar = tk.Frame(top, bg="#E6D9E3")
    frame_buscar.pack(fill="x", padx=10, pady=10)
    tk.Label(frame_buscar, text="Buscar producto:", font=("Helvetica",13,"bold"), bg="#E6D9E3").pack(side="left", padx=5)
    entry_buscar = ttk.Combobox(frame_buscar, font=("Helvetica",12), state="normal", width=40)
    entry_buscar.pack(side="left", fill="x", expand=True, padx=5, ipady=6)

    # Canvas con scroll para mostrar productos en tarjetas
    frame_canvas = tk.LabelFrame(top, text="Productos disponibles", font=("Helvetica",12,"bold"), bg="#E6D9E3")
    frame_canvas.pack(fill="both", expand=True, padx=10, pady=(0,10))

    canvas = tk.Canvas(frame_canvas, bg="#E6D9E3", highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_contenedor = tk.Frame(canvas, bg="#E6D9E3")
    canvas.create_window((0,0), window=frame_contenedor, anchor="nw")
    frame_contenedor.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Paginación
    frame_paginacion = tk.Frame(top, bg="#E6D9E3")
    frame_paginacion.pack(fill="x", padx=10, pady=(0,10))
    btn_anterior = tk.Button(frame_paginacion, text="◀ Anterior", bg="#2196F3", fg="white", relief="flat",
                             padx=12, pady=4, font=("Helvetica",11,"bold"))
    btn_anterior.pack(side="left", padx=5)
    label_pagina = tk.Label(frame_paginacion, text="Página 1 de 1", font=("Helvetica",11,"bold"), bg="#E6D9E3")
    label_pagina.pack(side="left", padx=20, expand=True)
    btn_siguiente = tk.Button(frame_paginacion, text="Siguiente ▶", bg="#2196F3", fg="white", relief="flat",
                              padx=12, pady=4, font=("Helvetica",11,"bold"))
    btn_siguiente.pack(side="right", padx=5)

    pagina_actual = 1
    productos_por_pagina = 12
    total_paginas = 1
    filtro_actual = ""

    def cargar_productos_pagina():
        nonlocal pagina_actual, total_paginas
        total = ServicioEdicionVentas.contar_productos_con_filtro(filtro_actual)
        total_paginas = max(1, (total + productos_por_pagina - 1) // productos_por_pagina)
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        offset = (pagina_actual - 1) * productos_por_pagina
        productos = ServicioEdicionVentas.obtener_productos_paginado(filtro_actual, offset, productos_por_pagina)

        for widget in frame_contenedor.winfo_children():
            widget.destroy()

        for idx, prod in enumerate(productos):
            row = idx // 4
            col = idx % 4
            frame_prod = tk.Frame(frame_contenedor, bg="white", width=210, height=210, bd=1, relief="solid")
            frame_prod.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            frame_prod.grid_propagate(False)

            try:
                ruta_imagen = prod.get("imagen", "default.png")
                if not ruta_imagen:
                    ruta_imagen = "default.png"
                if not os.path.isabs(ruta_imagen):
                    ruta_imagen = rutas(os.path.join("fotos", ruta_imagen))
                img = Image.open(ruta_imagen)
                img.thumbnail((140,140), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(frame_prod, image=img_tk, bg="white")
                lbl_img.image = img_tk
                lbl_img.pack(pady=(5,2))
            except:
                lbl_img = tk.Label(frame_prod, text="Sin imagen", bg="white", font=("Helvetica",9))
                lbl_img.pack(pady=(30,2))

            tk.Label(frame_prod, text=prod["producto"], font=("Helvetica",11,"bold"), bg="white",
                     wraplength=190, justify="center").pack(pady=(2,2))
            tk.Label(frame_prod, text=f"${prod['precio']:,.0f}".replace(",", "."),
                     font=("Helvetica",12,"bold"), bg="white", fg="#1B5E20").pack(pady=(0,4))

            def on_double_click(p=prod):
                if p["stock"] <= 0:
                    messagebox.showwarning("Sin stock", "Este producto no tiene stock disponible.", parent=top)
                    return
                _agregar_producto_a_venta(p, top, id_ventas, monto_recibido, usuario_actual, callbacks, cargar_productos_pagina)

            frame_prod.bind("<Double-1>", lambda e, p=prod: on_double_click(p))
            lbl_img.bind("<Double-1>", lambda e, p=prod: on_double_click(p))

        canvas.yview_moveto(0)
        label_pagina.config(text=f"Página {pagina_actual} de {total_paginas}")
        btn_anterior.config(state="normal" if pagina_actual>1 else "disabled")
        btn_siguiente.config(state="normal" if pagina_actual<total_paginas else "disabled")

    def pagina_anterior():
        nonlocal pagina_actual
        if pagina_actual > 1:
            pagina_actual -= 1
            cargar_productos_pagina()

    def pagina_siguiente():
        nonlocal pagina_actual
        if pagina_actual < total_paginas:
            pagina_actual += 1
            cargar_productos_pagina()

    def aplicar_filtro(event=None):
        nonlocal filtro_actual, pagina_actual
        filtro_actual = entry_buscar.get().strip()
        pagina_actual = 1
        cargar_productos_pagina()
        try:
            nombres = VentasServicio.obtener_nombres_productos_para_busqueda(filtro_actual)
            entry_buscar["values"] = nombres
        except:
            pass

    btn_anterior.config(command=pagina_anterior)
    btn_siguiente.config(command=pagina_siguiente)
    entry_buscar.bind("<KeyRelease>", aplicar_filtro)
    entry_buscar.bind("<<ComboboxSelected>>", aplicar_filtro)

    cargar_productos_pagina()

    btn_regresar = tk.Button(top, text="Regresar", command=lambda: (top.destroy(), _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)),
                             bg="#1976D2", fg="white", font=("Helvetica",12,"bold"), padx=18, pady=6)
    btn_regresar.pack(pady=(0,10))


def _agregar_producto_a_venta(producto, parent, id_ventas, monto_recibido, usuario, callbacks, recargar_callback):
    """
    Diálogo para agregar un producto específico a la factura.
    Solicita la cantidad, valida stock y monto recibido, mostrando la cantidad máxima permitida.
    Los botones están dispuestos horizontalmente.
    """
    total_actual, _, _ = ServicioEdicionVentas.obtener_info_factura(id_ventas)
    precio_unit = producto["precio"]
    cantidad_maxima = calcular_cantidad_maxima(total_actual, precio_unit, monto_recibido)

    # Ventana más grande para que los botones quepan bien
    popup = tk.Toplevel(parent)
    popup.title(f"Agregar {producto['producto']}")
    popup.geometry("420x360+400+200")
    popup.configure(bg="#F4F6F8")
    popup.resizable(False, False)
    popup.transient(parent)
    popup.grab_set()

    tk.Label(popup, text=producto["producto"], font=("Helvetica",14,"bold"), bg="#F4F6F8").pack(pady=(15,8))
    
    info_frame = tk.Frame(popup, bg="#F4F6F8")
    info_frame.pack(fill="x", padx=10, pady=(0,15))
    
    tk.Label(info_frame, text=f"Stock disponible: {producto['stock']}", font=("Helvetica",12),
             bg="#F4F6F8", fg="#008B8B", anchor="w", justify="left").pack(fill="x", pady=(0,4))
    tk.Label(info_frame, text=f"Cantidad permitida: {cantidad_maxima}",
             font=("Helvetica",12, "bold"), bg="#F4F6F8", fg="#0D47A1", anchor="w", justify="left").pack(fill="x", pady=(0,4))
    if cantidad_maxima > 0:
        tk.Label(info_frame, text="Si usa toda la cantidad permitida, quedarán 0 unidades adicionales disponibles.",
                 font=("Helvetica",11, "italic"), bg="#F4F6F8", fg="#008B8B", wraplength=380,
                 justify="left", anchor="w").pack(fill="x", pady=(0,4))
    else:
        tk.Label(info_frame, text="⚠️ No puede agregar más unidades con el monto recibido actual.",
                 font=("Helvetica",11, "italic"), bg="#F4F6F8", fg="#C62828", wraplength=380,
                 justify="left", anchor="w").pack(fill="x", pady=(0,4))
    
    tk.Label(popup, text="Cantidad a agregar:", font=("Helvetica",12), bg="#F4F6F8").pack(pady=(0,6))
    entry_cant = tk.Entry(popup, font=("Helvetica",13), width=10, justify="center")
    entry_cant.pack()
    entry_cant.focus()

    lbl_mensaje = tk.Label(popup, text="", font=("Helvetica",10), bg="#F4F6F8", fg="#C62828",
                            wraplength=380, justify="left")
    lbl_mensaje.pack(fill="x", padx=10, pady=(5,0))

    # Frame para los botones en horizontal
    frame_botones = tk.Frame(popup, bg="#F4F6F8")
    frame_botones.pack(fill="x", padx=10, pady=15)

    def confirmar():
        try:
            cantidad = int(entry_cant.get())
            if cantidad <= 0:
                lbl_mensaje.config(text="Cantidad inválida: ingrese un número mayor a cero.")
                return
            if cantidad > producto["stock"]:
                lbl_mensaje.config(text=f"Stock insuficiente: solo hay {producto['stock']} unidades disponibles.")
                return
            if cantidad > cantidad_maxima:
                lbl_mensaje.config(
                    text=(
                        f"Cantidad no permitida: ha ingresado {cantidad}.\n"
                        f"La cantidad máxima con el monto recibido (${monto_recibido:,.0f}) es {cantidad_maxima}."
                    )
                )
                return
            nuevo_total = total_actual + (cantidad * precio_unit)
            if nuevo_total > monto_recibido:
                lbl_mensaje.config(
                    text=(
                        f"Operación rechazada: el nuevo total (${nuevo_total:,.0f}) "
                        f"supera el monto recibido (${monto_recibido:,.0f})."
                    )
                )
                return

            ServicioEdicionVentas.agregar_producto_a_venta(id_ventas, producto["id_producto"], cantidad, usuario, monto_recibido)
            if cantidad == cantidad_maxima and cantidad_maxima > 0:
                messagebox.showinfo("Límite utilizado", "Ha usado la cantidad permitida completa. No quedan unidades adicionales disponibles.", parent=popup)
            else:
                messagebox.showinfo("Éxito", "Producto agregado correctamente.", parent=popup)
            popup.destroy()
            recargar_callback()
            _notificar_cambios(callbacks)
        except ValueError:
            lbl_mensaje.config(text="Ingrese una cantidad válida en números.")
        except Exception as err:
            messagebox.showerror("Error", str(err), parent=popup)

    def actualizar_mensaje(*args):
        try:
            cant = int(entry_cant.get()) if entry_cant.get().strip() else 0
            if cant <= 0:
                lbl_mensaje.config(text="")
            elif cant > producto["stock"]:
                lbl_mensaje.config(text=f"Stock insuficiente: solo hay {producto['stock']} unidades disponibles.")
            elif cant > cantidad_maxima:
                lbl_mensaje.config(text=f"⚠️ El máximo permitido con el monto actual es {cantidad_maxima}.")
            else:
                lbl_mensaje.config(text="")
        except ValueError:
            lbl_mensaje.config(text="")
        except:
            lbl_mensaje.config(text="")

    entry_cant.bind("<KeyRelease>", actualizar_mensaje)
    entry_cant.bind("<Return>", lambda e: confirmar())

    btn_agregar = tk.Button(frame_botones, text="Agregar", command=confirmar, bg="#4CAF50", fg="white",
                            font=("Helvetica",11,"bold"), padx=15, pady=5, width=10)
    btn_agregar.pack(side="left", padx=10)

    btn_cancelar = tk.Button(frame_botones, text="Cancelar", command=popup.destroy, bg="#F44336", fg="white",
                             font=("Helvetica",11,"bold"), padx=15, pady=5, width=10)
    btn_cancelar.pack(side="left", padx=10)


# ---------------------------------------------------------------------------
# NOTIFICACIÓN DE CAMBIOS
# ---------------------------------------------------------------------------
def _notificar_cambios(callbacks):
    """Ejecuta los callbacks proporcionados para refrescar la ventana principal de facturas."""
    if callbacks:
        callbacks.get('cargar_facturas', lambda: None)()
        callbacks.get('actualizar_total_facturas', lambda: None)()


# ---------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL (PUNTO DE ENTRADA)
# ---------------------------------------------------------------------------
def abrir_ventana_edicion_factura(ventana_padre, id_ventas, cliente, usuario_actual, callbacks):
    """
    Punto de entrada para la edición de una factura de venta.
    """
    total_actual, monto_anterior, _ = ServicioEdicionVentas.obtener_info_factura(id_ventas)

    monto_recibido = _solicitar_monto_recibido(ventana_padre, cliente, total_actual, monto_anterior)
    if monto_recibido is None or monto_recibido < total_actual:
        return

    _mostrar_selector(ventana_padre, id_ventas, cliente, monto_recibido, usuario_actual, callbacks)