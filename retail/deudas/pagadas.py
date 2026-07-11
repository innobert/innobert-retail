import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from retail.nucleo.configuraciones import (
    obtener_ruta_logo,
    cargar_ultima_carpeta_pdf,
    guardar_ultima_carpeta_pdf,
    abrir_archivo
)
from retail.utilidades.logo import cambiar_logo
from retail.deudas.visualizar_deudas import ver_detalle_deuda
from retail.nucleo.servicios.deudas.servicio_pagadas import ServicioPagadas


def peso_colombiano(value):
    return f"${value:,.0f}".replace(",", ".")


def ver_deudas_pagadas(deudas_view=None):
    ventana = tk.Toplevel(deudas_view) if deudas_view else tk.Toplevel()
    ventana.title("Deudas Pagadas")
    ventana.geometry("1300x700+30+5")
    ventana.configure(bg="#E6D9E3")
    ventana.resizable(False, False)
    ventana.maxsize(1300, 700)
    ventana.state('normal')
    if deudas_view:
        ventana.transient(deudas_view)
        ventana.grab_set()
    ventana.lift()
    ventana.focus_force()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # ========== PAGINACIÓN ==========
    pagina_actual = 1
    registros_por_pagina = 20
    total_paginas = 1
    filtro_actual = ""

    # ========== Frame principal para la tabla ==========
    frame_tabla = tk.Frame(ventana, bg="#F5F5F5", padx=10, pady=10)
    frame_tabla.place(x=10, y=10, width=1050, height=680)

    columnas = ("ID", "N°", "N° Factura", "Cliente", "Productos", "Fecha", "Total", "Saldo Pagado")
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

    config_columnas = [
        ("ID", 0),
        ("N°", 40),
        ("N° Factura", 120),
        ("Cliente", 180),
        ("Productos", 240),
        ("Fecha", 90),
        ("Total", 100),
        ("Saldo Pagado", 100),
    ]
    for col, width in config_columnas:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    tree.column("ID", width=0, stretch=tk.NO)
    tree.column("Cliente", anchor="w")
    tree.column("Productos", anchor="w")

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")
    scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
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

    # ========== Funciones de paginación ==========
    def actualizar_totales():
        nonlocal total_paginas, pagina_actual
        total_registros = ServicioPagadas.contar_pagadas(filtro_actual)
        total_paginas = max(1, (total_registros + registros_por_pagina - 1) // registros_por_pagina)
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        actualizar_etiqueta_paginacion()

    def cargar_pagina():
        tree.delete(*tree.get_children())
        offset = (pagina_actual - 1) * registros_por_pagina
        pagadas = ServicioPagadas.obtener_pagina(offset, registros_por_pagina, filtro_actual)

        inicio_numero = (pagina_actual - 1) * registros_por_pagina + 1
        for idx, deuda in enumerate(pagadas, start=inicio_numero):
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
                    peso_colombiano(deuda["saldo_pagado"]),
                ),
                tags=("pagada",)
            )
        tree.tag_configure("pagada", foreground="#0B6623")
        actualizar_total_pagado()
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

    # ========== Controles de paginación ==========
    frame_paginacion = tk.Frame(frame_tabla, bg="#F5F5F5")
    frame_paginacion.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

    label_paginacion = None

    def actualizar_etiqueta_paginacion():
        if label_paginacion is not None:
            total_registros = ServicioPagadas.contar_pagadas(filtro_actual)
            label_paginacion.config(
                text=f"Página {pagina_actual} de {total_paginas} ({total_registros} deudas pagadas)"
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

    # ========== Búsqueda ==========
    frame_buscar = tk.LabelFrame(ventana, text="Búsqueda", font=("Helvetica", 11, "bold"), bg="#E6D9E3")
    frame_buscar.place(x=1070, y=10, width=200, height=70)
    combo_buscar = ttk.Combobox(frame_buscar, font=("Calibri", 12), state="normal")
    combo_buscar.pack(pady=5, padx=10, fill="x")

    def actualizar_lista_clientes():
        clientes = ServicioPagadas.obtener_lista_clientes(filtro_actual)
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

    # ========== Opciones laterales ==========
    lf_opciones = tk.LabelFrame(ventana, text="Opciones", font=("Helvetica", 11, "bold"), bg="#E6D9E3")
    lf_opciones.place(x=1070, y=85, width=200, height=450)

    ruta_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))
    def cargar_img(nombre):
        try:
            return ImageTk.PhotoImage(Image.open(os.path.join(ruta_img, nombre)).resize((28, 28)))
        except Exception:
            return None

    img_visualizar = cargar_img("visualizar.png")
    img_imprimir = cargar_img("imprimir.png")
    img_historial = cargar_img("historial.png")
    img_cambiar = cargar_img("cambiar.png")

    def _ver_detalle_deuda():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para ver los detalles.", parent=ventana)
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_deuda = int(valores[0])
        ver_detalle_deuda(ventana, id_deuda)

    # ========== Generar PDF con carpeta recordada específica para deudas pagadas ==========
    def generar_factura_deuda_pagada():
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
        saldo_pagado = float(valores[7].replace("$", "").replace(".", ""))
        estado = "PAGADA"

        productos_detalle, cliente_nombre = ServicioPagadas.obtener_detalles_para_pdf(id_deuda)

        if not productos_detalle:
            messagebox.showerror("Error", f"No se encontraron productos para la deuda {id_deuda}", parent=ventana)
            return

        # Cargar última carpeta usada para DEUDAS (comparte con deudas activas)
        # Si prefieres carpeta separada para pagadas, cambia 'deudas' por 'pagadas'
        carpeta_inicial = cargar_ultima_carpeta_pdf('pagadas')

        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Deuda_Pagada_{numero_factura}.pdf",
            title="Guardar factura como",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=carpeta_inicial,
            parent=ventana
        )
        if not archivo_pdf:
            return

        # Guardar la carpeta usada para futuras ocasiones (DEUDAS)
        carpeta_usada = os.path.dirname(archivo_pdf)
        guardar_ultima_carpeta_pdf('pagadas', carpeta_usada)

        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        width, height = letter

        ruta_logo = obtener_ruta_logo("logo.png")
        try:
            c.drawImage(ruta_logo, width - 180, height - 150, width=140, height=140, mask='auto')
        except Exception:
            pass

        c.setFont("Helvetica-Bold", 28)
        titulo = "Factura de Deuda Pagada"
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
            # Truncar nombre del producto si es demasiado largo
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
        c.drawString(40, y_fila - 45, f"Pagado: {peso_colombiano(saldo_pagado)}")

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

        # Abrir el PDF automáticamente
        abrir_archivo(archivo_pdf)

        messagebox.showinfo("Éxito", f"Factura generada correctamente en:\n{archivo_pdf}", parent=ventana)

    # ========== Historial de deuda pagada ==========
    def abrir_historial_deuda_pagada():
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione una deuda para ver su historial.", parent=ventana)
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

    def cambiar_logo_ventana():
        cambiar_logo(ventana)

    # ========== Botones ==========
    btn_visualizar = tk.Button(
        lf_opciones, text="VER", image=img_visualizar, compound="left",
        font=("Helvetica", 14, "bold"), bg="#FF9800", fg="white",
        relief="ridge", bd=3, cursor="hand2", padx=12, pady=6, anchor="w",
        command=_ver_detalle_deuda
    )
    if img_visualizar:
        btn_visualizar.image = img_visualizar
    btn_visualizar.pack(pady=7, padx=10, fill="x")

    btn_imprimir = tk.Button(
        lf_opciones, text="IMPRIMIR", image=img_imprimir, compound="left",
        font=("Helvetica", 14, "bold"), bg="#0D47A1", fg="white",
        command=generar_factura_deuda_pagada, padx=12, pady=6, anchor="w"
    )
    btn_imprimir.image = img_imprimir
    btn_imprimir.pack(pady=7, padx=10, fill="x")

    btn_historial = tk.Button(
        lf_opciones, text="HISTORIAL", image=img_historial, compound="left",
        font=("Helvetica", 14, "bold"), bg="#6A1B9A", fg="white",
        command=abrir_historial_deuda_pagada, padx=12, pady=6, anchor="w"
    )
    btn_historial.image = img_historial
    btn_historial.pack(pady=7, padx=10, fill="x")

    btn_logo = tk.Button(
        lf_opciones, text="LOGO", image=img_cambiar, compound="left",
        font=("Helvetica", 14, "bold"), bg="#1976D2", fg="white",
        command=cambiar_logo_ventana, padx=12, pady=6, anchor="w"
    )
    btn_logo.image = img_cambiar
    btn_logo.pack(pady=7, padx=10, fill="x")

    # ========== Total pagado ==========
    lf_total = tk.LabelFrame(ventana, text="Total Pagado", font=("Helvetica", 12, "bold"), bg="#E6D9E3")
    lf_total.place(x=1070, y=540, width=200, height=90)
    var_total = tk.StringVar(value="$0")
    lbl_total = tk.Label(lf_total, textvariable=var_total, font=("Helvetica", 16, "bold"), bg="#E6D9E3", fg="#0B6623")
    lbl_total.pack(expand=True, fill="both", pady=10)

    def actualizar_total_pagado():
        total = ServicioPagadas.calcular_total_pagado(filtro_actual)
        var_total.set(peso_colombiano(total))

    # ========== Inicialización ==========
    actualizar_lista_clientes()
    actualizar_totales()
    cargar_pagina()
    actualizar_total_pagado()

    ventana.mainloop()