import tkinter as tk
import os
from tkinter import ttk, messagebox, filedialog
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from PIL import Image, ImageTk

from retail.deudas.visualizar_deudas import ver_detalle_deuda
from retail.nucleo.servicios.deudas.servicio_facturas_deudas import ServicioFacturasDeudas
from retail.utilidades.logo import cambiar_logo
from retail.nucleo.configuraciones import (
    cargar_ultima_carpeta_pdf,
    guardar_ultima_carpeta_pdf,
    abrir_archivo,
    obtener_ruta_logo,
)
# Importamos las funciones internas de edicion_deudas
from retail.deudas.edicion_deudas import _abrir_ventana_editar_factura, _abrir_ventana_agregar_productos


def peso_colombiano(value):
    return f"${value:,.0f}".replace(",", ".")


def ver_facturas_deudas(deudas_view=None):
    # --- Configuración de la ventana ---
    ventana = tk.Toplevel(deudas_view) if deudas_view else tk.Toplevel()
    ventana.title("Facturas - Deudas")
    ventana.geometry("1300x700+30+5")
    ventana.configure(bg="#E6D9E3")
    ventana.resizable(False, False)
    ventana.maxsize(1300, 700)
    if deudas_view:
        ventana.transient(deudas_view)
        ventana.grab_set()
    ventana.lift()
    ventana.focus_force()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # --- Variables de paginación y filtro ---
    pagina_actual = 1
    deudas_por_pagina = 20
    total_paginas = 1
    filtro_actual = ""

    # --- Frame principal para la tabla ---
    frame_tabla = tk.Frame(ventana, bg="#F5F5F5", padx=10, pady=10)
    frame_tabla.place(x=10, y=10, width=1050, height=680)

    # --- TreeView ---
    columnas = ("ID", "N°", "N° Factura", "Cliente", "Productos", "Fecha", "Total", "Saldo")
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

    config_columnas = [
        ("ID", 0),
        ("N°", 40),
        ("N° Factura", 120),
        ("Cliente", 180),
        ("Productos", 240),
        ("Fecha", 90),
        ("Total", 100),
        ("Saldo", 100),
    ]
    for col, width in config_columnas:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    tree.column("ID", width=0, stretch=tk.NO)
    tree.column("Cliente", anchor="w")
    tree.column("Productos", anchor="w")

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)

    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")
    frame_tabla.grid_rowconfigure(0, weight=1)
    frame_tabla.grid_columnconfigure(0, weight=1)

    def _on_mousewheel(event):
        if event.delta > 0:
            tree.yview_scroll(-3, "units")
        else:
            tree.yview_scroll(3, "units")
        return "break"
    tree.bind("<MouseWheel>", _on_mousewheel)

    # --- Funciones de carga y paginación ---
    def actualizar_totales():
        nonlocal total_paginas, pagina_actual
        total_deudas = ServicioFacturasDeudas.contar_deudas(filtro_actual)
        total_paginas = max(1, (total_deudas + deudas_por_pagina - 1) // deudas_por_pagina)
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        actualizar_etiqueta_paginacion()

    def cargar_pagina():
        tree.delete(*tree.get_children())
        offset = (pagina_actual - 1) * deudas_por_pagina
        deudas = ServicioFacturasDeudas.obtener_pagina(offset, deudas_por_pagina, filtro_actual)

        inicio_numero = (pagina_actual - 1) * deudas_por_pagina + 1
        for idx, deuda in enumerate(deudas, start=inicio_numero):
            tree.insert(
                "",
                "end",
                iid=deuda["id_deuda"],
                values=(
                    deuda["id_deuda"],
                    idx,
                    deuda["numero_factura"],
                    deuda["cliente"],
                    deuda["productos"],
                    deuda["fecha"],
                    peso_colombiano(deuda["total"]),
                    peso_colombiano(deuda["saldo"]),
                ),
                tags=("abierta",)
            )
        tree.tag_configure("abierta", foreground="#C62828")
        actualizar_total_deudas()
        actualizar_etiqueta_paginacion()

    def pagina_anterior():
        nonlocal pagina_actual
        if pagina_actual > 1:
            pagina_actual -= 1
            cargar_pagina()

    def pagina_siguiente():
        nonlocal pagina_actual
        if pagina_actual < total_paginas:
            pagina_actual += 1
            cargar_pagina()

    # --- Controles de paginación ---
    frame_paginacion = tk.Frame(frame_tabla, bg="#F5F5F5")
    frame_paginacion.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

    label_paginacion = None

    def actualizar_etiqueta_paginacion():
        if label_paginacion is not None:
            total_deudas = ServicioFacturasDeudas.contar_deudas(filtro_actual)
            label_paginacion.config(
                text=f"Página {pagina_actual} de {total_paginas} ({total_deudas} deudas abiertas)"
            )

    def crear_controles_paginacion():
        nonlocal label_paginacion
        for widget in frame_paginacion.winfo_children():
            widget.destroy()
        btn_anterior = tk.Button(
            frame_paginacion, text="◀ Anterior", command=pagina_anterior,
            bg="#2196F3", fg="white", relief="flat", padx=10, font=("Helvetica", 10, "bold")
        )
        btn_anterior.pack(side="left", padx=5)
        label_paginacion = tk.Label(frame_paginacion, text="", font=("Helvetica", 10, "bold"), bg="#F5F5F5")
        label_paginacion.pack(side="left", padx=20, expand=True)
        btn_siguiente = tk.Button(
            frame_paginacion, text="Siguiente ▶", command=pagina_siguiente,
            bg="#2196F3", fg="white", relief="flat", padx=10, font=("Helvetica", 10, "bold")
        )
        btn_siguiente.pack(side="right", padx=5)
        actualizar_etiqueta_paginacion()

    crear_controles_paginacion()

    # --- Búsqueda por cliente ---
    frame_buscar = tk.LabelFrame(ventana, text="Búsqueda", font=("Helvetica", 11, "bold"), bg="#E6D9E3")
    frame_buscar.place(x=1070, y=10, width=200, height=70)
    combo_buscar = ttk.Combobox(frame_buscar, font=("Calibri", 12), state="normal")
    combo_buscar.pack(pady=5, padx=10, fill="x")

    def actualizar_lista_clientes():
        clientes = ServicioFacturasDeudas.obtener_lista_clientes(filtro_actual)
        combo_buscar["values"] = clientes

    def aplicar_filtro(event=None):
        nonlocal filtro_actual, pagina_actual
        texto = combo_buscar.get().strip()
        filtro_actual = texto
        pagina_actual = 1
        actualizar_totales()
        cargar_pagina()
        actualizar_lista_clientes()

    combo_buscar.bind("<KeyRelease>", aplicar_filtro)
    combo_buscar.bind("<<ComboboxSelected>>", aplicar_filtro)
    combo_buscar.bind("<Return>", aplicar_filtro)

    # --- Opciones laterales (tus botones originales) ---
    lf_opciones = tk.LabelFrame(ventana, text="Opciones", font=("Helvetica", 11, "bold"), bg="#E6D9E3")
    lf_opciones.place(x=1070, y=85, width=200, height=450)

    ruta_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))
    def cargar_img(nombre):
        try:
            return ImageTk.PhotoImage(Image.open(os.path.join(ruta_img, nombre)).resize((28, 28)))
        except Exception:
            return None

    img_ver = cargar_img("visualizar.png")
    img_imprimir = cargar_img("imprimir.png")
    img_pagar = cargar_img("pagadas.png")
    img_historial = cargar_img("historial.png")
    img_eliminar = cargar_img("eliminar.png")
    img_papelera = cargar_img("papelera.png")
    img_cambiar_logo = cargar_img("cambiar.png")

    # --- Función para generar PDF (original) ---
    def generar_factura_deuda():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para generar factura.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        numero_factura = valores[2]
        cliente = valores[3]
        fecha = valores[5]
        total = float(valores[6].replace("$", "").replace(".", ""))
        saldo = float(valores[7].replace("$", "").replace(".", ""))
        estado = "ABIERTA"

        detalles = ServicioFacturasDeudas.obtener_detalles_para_pdf(id_deuda)
        productos_detalle = detalles["productos"]

        if not productos_detalle:
            messagebox.showerror("Error", f"No se encontraron productos para la deuda {id_deuda}", parent=ventana)
            return

        carpeta_inicial = cargar_ultima_carpeta_pdf('deudas')
        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Deuda_{numero_factura}.pdf",
            title="Guardar factura como",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=carpeta_inicial,
            parent=ventana
        )
        if not archivo_pdf:
            return

        guardar_ultima_carpeta_pdf('deudas', os.path.dirname(archivo_pdf))

        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        width, height = letter

        ruta_logo = obtener_ruta_logo("logo.png")
        try:
            c.drawImage(ruta_logo, width - 180, height - 150, width=140, height=140, mask='auto')
        except Exception:
            pass

        c.setFont("Helvetica-Bold", 28)
        titulo = "Factura de Deuda"
        x_titulo = 40
        y_titulo = height - 70
        c.drawString(x_titulo, y_titulo, titulo)
        ancho_titulo = c.stringWidth(titulo, "Helvetica-Bold", 28)
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(x_titulo, y_titulo - 6, x_titulo + ancho_titulo, y_titulo - 6)

        c.setFont("Helvetica-Bold", 13)
        y = height - 120
        c.drawString(40, y, f"N° Deuda: {numero_factura}")
        c.drawString(40, y - 25, f"Cliente: {cliente}")
        c.drawString(40, y - 50, f"Fecha: {fecha}")
        c.drawString(40, y - 75, f"Estado: {estado}")

        y_tabla = y - 120
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_tabla, "Producto")
        c.drawString(280, y_tabla, "Cantidad")
        c.drawString(380, y_tabla, "Subtotal")
        c.line(30, y_tabla - 5, width - 30, y_tabla - 5)

        c.setFont("Helvetica", 11)
        y_fila = y_tabla - 25
        total_calculado = 0
        for prod_id, producto, cantidad, subtotal in productos_detalle:
            prod_text = str(producto) if producto else f"Producto {prod_id}"
            if len(prod_text) > 35:
                prod_text = prod_text[:32] + "..."
            c.drawString(40, y_fila, prod_text)
            c.drawString(280, y_fila, str(cantidad))
            c.drawString(380, y_fila, peso_colombiano(subtotal))
            total_calculado += float(subtotal)
            y_fila -= 20

        c.line(30, y_fila + 10, width - 30, y_fila + 10)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y_fila - 20, f"Total: {peso_colombiano(total_calculado)}")
        c.drawString(40, y_fila - 45, f"Saldo: {peso_colombiano(saldo)}")

        c.setFont("Helvetica-Oblique", 13)
        c.drawString(50, 60, "Gracias por su preferencia. ®INNOBERTDEV")
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(50, 40, "Factura generada automáticamente por Innobert Retail")

        c.saveState()
        c.setFont("Helvetica-Bold", 60)
        c.setFillColorRGB(0.93, 0.93, 0.93)
        c.translate(width / 2, 200)
        c.rotate(30)
        c.drawCentredString(0, 0, "Innobert")
        c.restoreState()
        c.save()

        abrir_archivo(archivo_pdf)
        messagebox.showinfo("Éxito", f"Factura generada correctamente en:\n{archivo_pdf}", parent=ventana)

    # --- Pago de deuda (original) ---
    def pagar_deuda():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar deuda", "Por favor, selecciona una deuda para registrar un pago.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        cliente = valores[3]
        saldo_actual = float(valores[7].replace("$", "").replace(".", ""))

        popup = tk.Toplevel(ventana)
        popup.title(f"Registrar Pago - Deuda {id_deuda}")
        popup.geometry("350x320+400+250")
        popup.configure(bg="#F4F6F8")
        popup.resizable(False, False)
        popup.transient(ventana)
        popup.grab_set()

        frame_pago = tk.Frame(popup, bg="#F4F6F8")
        frame_pago.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame_pago, text=f"Cliente: {cliente}", font=("Helvetica", 12, "bold"), bg="#F4F6F8").pack(pady=(0,5))
        tk.Label(frame_pago, text="Saldo pendiente:", font=("Helvetica", 12, "bold"), bg="#F4F6F8").pack(pady=(0,5))
        lbl_saldo = tk.Label(frame_pago, text=peso_colombiano(saldo_actual), font=("Helvetica", 16, "bold"), bg="#F4F6F8", fg="#0B6623")
        lbl_saldo.pack(pady=(0,20))
        tk.Label(frame_pago, text="Monto a pagar:", font=("Helvetica", 12, "bold"), bg="#F4F6F8").pack(pady=(0,5))
        entry_monto = tk.Entry(frame_pago, font=("Helvetica", 14), width=25, justify="right", bg="#FFFFFF", relief="solid", bd=1)
        entry_monto.pack(pady=(0,10))
        entry_monto.focus()

        vuelto_var = tk.StringVar(value="$0")
        tk.Label(frame_pago, text="Vuelto:", font=("Helvetica", 12, "bold"), bg="#F4F6F8").pack(pady=(0,5))
        tk.Label(frame_pago, textvariable=vuelto_var, font=("Helvetica", 14, "bold"), bg="#F4F6F8", fg="#0B6623").pack(pady=(0,10))

        def actualizar_vuelto(*_):
            try:
                monto = float(entry_monto.get().strip()) if entry_monto.get().strip() else 0
            except ValueError:
                monto = 0
            vuelto = max(0, monto - saldo_actual)
            vuelto_var.set(peso_colombiano(vuelto))

        entry_monto.bind("<KeyRelease>", lambda e: actualizar_vuelto())

        def registrar():
            monto_str = entry_monto.get().strip()
            if not monto_str:
                messagebox.showerror("Error", "Ingrese un monto válido.", parent=popup)
                return
            try:
                monto = float(monto_str)
            except ValueError:
                messagebox.showerror("Error", "Monto inválido.", parent=popup)
                return
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0.", parent=popup)
                return

            usuario = deudas_view.controlador.usuario_actual if deudas_view else "usuario"
            exito, mensaje, vuelto = ServicioFacturasDeudas.registrar_pago(id_deuda, monto, saldo_actual, usuario, deudas_view)
            if exito:
                if vuelto and vuelto > 0:
                    messagebox.showinfo(
                        "Pago registrado con vuelto",
                        f"Se registró el pago por {peso_colombiano(monto)}.\n\n"
                        f"Vuelto a entregar: {peso_colombiano(vuelto)}\n\n"
                        f"La deuda ha sido pagada completamente y será movida a la sección PAGADAS.",
                        parent=popup
                    )
                elif "pagada completamente" in mensaje.lower() or "pago total" in mensaje.lower():
                    messagebox.showinfo(
                        "Deuda pagada",
                        f"{mensaje}\n\nLa deuda ha sido movida a la sección PAGADAS y ya no aparecerá en esta lista.",
                        parent=popup
                    )
                else:
                    messagebox.showinfo("Abono registrado", mensaje, parent=popup)
                popup.destroy()
                actualizar_totales()
                cargar_pagina()
                if deudas_view and hasattr(deudas_view, "cargar_deudas"):
                    deudas_view.cargar_deudas()
                if deudas_view and hasattr(deudas_view, "actualizar_total_deudas"):
                    deudas_view.actualizar_total_deudas()
            else:
                messagebox.showerror("Error", mensaje, parent=popup)

        entry_monto.bind("<Return>", lambda e: registrar())
        frame_botones = tk.Frame(frame_pago, bg="#F4F6F8")
        frame_botones.pack(pady=(10,0))
        tk.Button(frame_botones, text="Registrar Pago", command=registrar, bg="#4CAF50", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Cancelar", command=popup.destroy, bg="#F44336", fg="white", width=15).pack(side="left", padx=5)

    # --- Historial (original) ---
    def _ver_detalle_deuda():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar deuda", "Seleccione una deuda para ver el detalle.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        ver_detalle_deuda(ventana, id_deuda)

    def abrir_historial_desde_factura():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Seleccionar deuda", "Seleccione una deuda para ver su historial.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        cliente = valores[3]
        if deudas_view:
            deudas_view.controlador.abrir_historial_deuda(ventana, nombre_cliente=cliente, id_deuda=id_deuda)
        else:
            from retail.deudas.historial_deudas import abrir_historial_deudas
            abrir_historial_deudas(ventana, id_deuda=id_deuda, nombre_cliente=cliente)

    # --- Eliminar deuda (original) ---
    def eliminar_deuda():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para eliminar.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta deuda?\n\nSe moverá a la Papelera.", parent=ventana):
            from retail.nucleo.base_datos import mover_deuda_a_papelera
            exito = mover_deuda_a_papelera(id_deuda, deudas_view.controlador.usuario_actual if deudas_view else "usuario", "Eliminada desde facturas")
            if exito:
                actualizar_totales()
                cargar_pagina()
                if deudas_view and hasattr(deudas_view, "cargar_deudas"):
                    deudas_view.cargar_deudas()
                if deudas_view and hasattr(deudas_view, "actualizar_total_deudas"):
                    deudas_view.actualizar_total_deudas()
                messagebox.showinfo("Éxito", "Deuda eliminada correctamente.", parent=ventana)
            else:
                messagebox.showerror("Error", "No se pudo eliminar la deuda.", parent=ventana)

    # --- Abrir papelera de deudas (original) ---
    def abrir_papelera_deudas():
        if deudas_view:
            deudas_view.controlador.abrir_papelera_deudas(ventana)
        else:
            from retail.deudas.papelera_deudas import ver_papelera_deudas
            ver_papelera_deudas(ventana)

    # --- Botones de opciones (tus botones originales) ---
    btn_ver = tk.Button(lf_opciones, text="VER", image=img_ver, compound="left", font=("Helvetica",14,"bold"),
                        bg="#FF9800", fg="white", command=_ver_detalle_deuda, padx=12, pady=6, anchor="w")
    if img_ver:
        btn_ver.image = img_ver
    btn_ver.pack(pady=7, padx=10, fill="x")

    btn_imprimir = tk.Button(lf_opciones, text="IMPRIMIR", image=img_imprimir, compound="left", font=("Helvetica",14,"bold"),
                             bg="#0D47A1", fg="white", command=generar_factura_deuda, padx=12, pady=6, anchor="w")
    if img_imprimir:
        btn_imprimir.image = img_imprimir
    btn_imprimir.pack(pady=7, padx=10, fill="x")

    btn_pagar = tk.Button(lf_opciones, text="PAGAR", image=img_pagar, compound="left", font=("Helvetica",14,"bold"),
                          bg="#4CAF50", fg="white", command=pagar_deuda, padx=12, pady=6, anchor="w")
    if img_pagar:
        btn_pagar.image = img_pagar
    btn_pagar.pack(pady=7, padx=10, fill="x")

    btn_historial = tk.Button(lf_opciones, text="HISTORIAL", image=img_historial, compound="left", font=("Helvetica",14,"bold"),
                              bg="#6A1B9A", fg="white", command=abrir_historial_desde_factura, padx=12, pady=6, anchor="w")
    if img_historial:
        btn_historial.image = img_historial
    btn_historial.pack(pady=7, padx=10, fill="x")

    btn_eliminar = tk.Button(lf_opciones, text="ELIMINAR", image=img_eliminar, compound="left", font=("Helvetica",14,"bold"),
                             bg="#C62828", fg="white", command=eliminar_deuda, padx=12, pady=6, anchor="w")
    btn_eliminar.image = img_eliminar
    btn_eliminar.pack(pady=7, padx=10, fill="x")

    btn_papelera = tk.Button(lf_opciones, text="PAPELERA", image=img_papelera, compound="left", font=("Helvetica",14,"bold"),
                             bg="#607D8B", fg="white", command=abrir_papelera_deudas, padx=12, pady=6, anchor="w")
    if img_papelera:
        btn_papelera.image = img_papelera
    btn_papelera.pack(pady=7, padx=10, fill="x")

    btn_logo = tk.Button(lf_opciones, text="LOGO", image=img_cambiar_logo, compound="left", font=("Helvetica",14,"bold"),
                         bg="#1976D2", fg="white", command=lambda: cambiar_logo(ventana), padx=12, pady=6, anchor="w")
    if img_cambiar_logo:
        btn_logo.image = img_cambiar_logo
    btn_logo.pack(pady=7, padx=10, fill="x")

    # --- Total de deudas abiertas ---
    lf_total = tk.LabelFrame(ventana, text="Total Deudas Abiertas", font=("Helvetica",12,"bold"), bg="#E6D9E3")
    lf_total.place(x=1070, y=540, width=200, height=90)
    var_total = tk.StringVar(value="$0")
    lbl_total = tk.Label(lf_total, textvariable=var_total, font=("Helvetica",16,"bold"), bg="#E6D9E3", fg="#C62828")
    lbl_total.pack(expand=True, fill="both", pady=10)

    def actualizar_total_deudas():
        total = ServicioFacturasDeudas.calcular_total_deudas(filtro_actual)
        var_total.set(peso_colombiano(total))

    # --- Inicialización ---
    actualizar_lista_clientes()
    actualizar_totales()
    cargar_pagina()
    actualizar_total_deudas()

    # --- Edición (doble clic) con selector integrado (NUEVO) ---
    def abrir_edicion_deuda(event=None):
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para editar.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        cliente = valores[3]
        callbacks = {
            'cargar_deudas': lambda: (actualizar_totales(), cargar_pagina()),
            'actualizar_total_deudas': actualizar_total_deudas,
        }
        usuario_actual = deudas_view.controlador.usuario_actual if deudas_view else "sistema"

        top = tk.Toplevel(ventana)
        top.title("Opciones de deuda")
        top.geometry("420x200+500+200")
        top.configure(bg="#E6D9E3")
        top.resizable(False, False)
        top.grab_set()
        top.transient(ventana)

        tk.Label(
            top,
            text="¿Qué deseas hacer con esta deuda?",
            font=("Helvetica", 14, "bold"),
            bg="#E6D9E3",
            pady=14,
        ).pack(fill="x")

        frame_botones = tk.Frame(top, bg="#E6D9E3")
        frame_botones.pack(fill="x", padx=20, pady=10)

        tk.Button(
            frame_botones,
            text="Editar factura",
            font=("Helvetica", 12, "bold"),
            bg="#1976D2",
            fg="white",
            width=16,
            height=2,
            command=lambda: (top.destroy(), _abrir_ventana_editar_factura(ventana, id_deuda, cliente, usuario_actual, callbacks)),
        ).pack(side="left", expand=True, padx=10)

        tk.Button(
            frame_botones,
            text="Agregar productos",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=16,
            height=2,
            command=lambda: (top.destroy(), _abrir_ventana_agregar_productos(ventana, id_deuda, cliente, usuario_actual, callbacks)),
        ).pack(side="right", expand=True, padx=10)

        tk.Button(
            top,
            text="Cancelar",
            font=("Helvetica", 10, "bold"),
            bg="#F44336",
            fg="white",
            width=12,
            command=top.destroy
        ).pack(side="bottom", pady=12)

    # --- Binding doble clic ---
    tree.bind("<Double-1>", abrir_edicion_deuda)