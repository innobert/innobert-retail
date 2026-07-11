"""
facturas_ventas.py

Módulo que gestiona la visualización, paginación, filtrado y generación de PDF
de las facturas de ventas. Incluye funcionalidades de impresión, eliminación
(mover a papelera), historial del cliente, edición de facturas (doble clic)
y cambio del logo. La ventana sigue el mismo estilo que facturas_deudas.py.
"""

from __future__ import annotations

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk

from retail.nucleo.configuraciones import (
    COLOR_FONDO,
    COLOR_FONDO_EDITAR,
    COLOR_FONDO_TABLA,
    COLOR_AZUL,
    COLOR_VERDE,
    COLOR_ROJO,
    FUENTE_ETIQUETA,
    TAMANO_VENTANA,
    obtener_ruta_logo,
    cargar_ultima_carpeta_pdf,
    guardar_ultima_carpeta_pdf,
    abrir_archivo,
    ruta_recurso,
    crear_boton,
    VENTAS_BOTON_NAV,
    VENTAS_BOTON_ADVERTENCIA,
    VENTAS_BOTON_ACCION,
    VENTAS_BOTON_INFO,
    VENTAS_BOTON_PELIGRO,
    VENTAS_BOTON_NEUTRO,
    VENTAS_BOTON_IMPORTAR,
)
from retail.utilidades.logo import cambiar_logo
from retail.nucleo.servicios.ventas.servicio_facturas_ventas import (
    ServicioFacturasVentas,
)


# ============================================================================
# FUNCIÓN AUXILIAR PARA TEXTO ENVUELTO EN PDF
# ============================================================================
def draw_wrapped_text(
    canvas_obj: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name: str,
    font_size: float,
    line_height: float = 14,
) -> Tuple[float, int]:
    """
    Dibuja texto envuelto en múltiples líneas dentro de un ancho máximo.

    Argumentos:
        canvas_obj: Objeto canvas de reportlab.
        text: Texto a dibujar.
        x, y: Coordenadas iniciales (parte superior de la primera línea).
        max_width: Ancho máximo en puntos antes de saltar de línea.
        font_name: Nombre de la fuente.
        font_size: Tamaño de la fuente.
        line_height: Altura de cada línea.

    Retorna:
        Tupla (nueva_coordenada_y, número_de_líneas_utilizadas).
    """
    canvas_obj.setFont(font_name, font_size)
    palabras = text.split()
    lineas = []
    linea_actual: list[str] = []

    for palabra in palabras:
        linea_prueba = " ".join(linea_actual + [palabra])
        if canvas_obj.stringWidth(linea_prueba, font_name, font_size) <= max_width:
            linea_actual.append(palabra)
        else:
            if linea_actual:
                lineas.append(" ".join(linea_actual))
            linea_actual = [palabra]

    if linea_actual:
        lineas.append(" ".join(linea_actual))

    for i, linea in enumerate(lineas):
        canvas_obj.drawString(x, y - i * line_height, linea)

    nueva_y = y - (len(lineas) - 1) * line_height
    return nueva_y, len(lineas)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================
def ver_facturas(parent: tk.Tk) -> None:
    """
    Abre la ventana de gestión de facturas de ventas, con diseño similar a facturas_deudas.
    """
    # Crear ventana
    ventana = tk.Toplevel(parent)
    ventana.title("Facturas de Ventas - Innobert Retail")
    ventana.geometry(TAMANO_VENTANA + "+30+5")
    ventana.configure(bg=COLOR_FONDO)
    ventana.resizable(False, False)
    ventana.maxsize(1300, 700)
    ventana.transient(parent)
    ventana.grab_set()
    ventana.lift()
    ventana.focus_force()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # --- Variables de paginación y filtro ---
    pagina_actual = 1
    facturas_por_pagina = 20
    total_paginas = 1
    filtro_actual = ""

    # --- Frame principal para la tabla (igual que en facturas_deudas) ---
    frame_tabla = tk.Frame(ventana, bg=COLOR_FONDO_TABLA, padx=10, pady=10)
    frame_tabla.place(x=10, y=10, width=1050, height=680)

    # --- TreeView (columnas similares a facturas_deudas pero adaptadas a ventas) ---
    columnas = (
        "ID",
        "N°",
        "N° Factura",
        "Cliente",
        "Productos",
        "Recibido",
        "Vuelto",
        "Total",
        "Día",
        "Hora",
        "Fecha",
        "Zona",
    )
    # Para que quepa mejor, quitamos "Día" y "Zona"? Pero las dejamos, ajustamos anchos
    tree = ttk.Treeview(
        frame_tabla, columns=columnas, show="headings", selectmode="browse"
    )

    config_columnas = [
        ("ID", 0),
        ("N°", 40),
        ("N° Factura", 110),
        ("Cliente", 150),
        ("Productos", 200),
        ("Recibido", 80),
        ("Vuelto", 80),
        ("Total", 80),
        ("Día", 70),
        ("Hora", 70),
        ("Fecha", 80),
        ("Zona", 70),
    ]
    for col, width in config_columnas:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    tree.column("ID", width=0, stretch=tk.NO)
    tree.column("Cliente", anchor="w")
    tree.column("Productos", anchor="w")

    # Scrollbars
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

    # Rueda del mouse
    def _en_rueda_raton(event: Any) -> str:
        if event.delta > 0:
            tree.yview_scroll(-3, "units")
        else:
            tree.yview_scroll(3, "units")
        return "break"

    tree.bind("<MouseWheel>", _en_rueda_raton)

    # --- Funciones de paginación ---
    def contar_facturas() -> int:
        return ServicioFacturasVentas.contar_facturas(filtro_actual)

    def actualizar_totales() -> None:
        nonlocal total_paginas, pagina_actual
        total_facturas = contar_facturas()
        total_paginas = max(
            1, (total_facturas + facturas_por_pagina - 1) // facturas_por_pagina
        )
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        actualizar_etiqueta_paginacion()

    def cargar_pagina() -> None:
        tree.delete(*tree.get_children())
        offset = (pagina_actual - 1) * facturas_por_pagina
        facturas = ServicioFacturasVentas.obtener_pagina_facturas(
            offset, facturas_por_pagina, filtro_actual
        )

        dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]
        inicio_numero = (pagina_actual - 1) * facturas_por_pagina + 1
        for i, fact in enumerate(facturas, start=inicio_numero):
            try:
                fecha_dt = datetime.strptime(fact["fecha"], "%Y-%m-%d")
                dia_semana = dias[fecha_dt.weekday()]
            except Exception:
                logger.warning("No se pudo parsear la fecha %s", fact.get("fecha"))
                dia_semana = ""

            tree.insert(
                "",
                "end",
                values=(
                    fact["id_ventas"],
                    i,
                    fact["numero_factura"],
                    fact["cliente_nombre"],
                    fact["productos"],
                    f"${fact['monto_recibido']:,.0f}".replace(",", "."),
                    f"${fact['vuelto']:,.0f}".replace(",", "."),
                    f"${fact['total']:,.0f}".replace(",", "."),
                    dia_semana,
                    fact["hora"],
                    fact["fecha"],
                    fact["zona"],
                ),
            )
        actualizar_total_ventas()
        actualizar_etiqueta_paginacion()

    def pagina_anterior() -> None:
        nonlocal pagina_actual
        if pagina_actual > 1:
            pagina_actual -= 1
            cargar_pagina()

    def pagina_siguiente() -> None:
        nonlocal pagina_actual
        if pagina_actual < total_paginas:
            pagina_actual += 1
            cargar_pagina()

    # --- Controles de paginación (dentro del frame_tabla, igual que facturas_deudas) ---
    frame_paginacion = tk.Frame(frame_tabla, bg=COLOR_FONDO_TABLA)
    frame_paginacion.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

    label_paginacion = None

    def actualizar_etiqueta_paginacion() -> None:
        if label_paginacion is not None:
            total_facturas = contar_facturas()
            label_paginacion.config(
                text=f"Página {pagina_actual} de {total_paginas} ({total_facturas} facturas)"
            )

    def crear_controles_paginacion() -> None:
        nonlocal label_paginacion
        for widget in frame_paginacion.winfo_children():
            widget.destroy()
        btn_anterior = crear_boton(
            frame_paginacion,
            "◀ Anterior",
            estilo=VENTAS_BOTON_NAV,
            comando=pagina_anterior,
        )
        btn_anterior.pack(side="left", padx=5)
        label_paginacion = tk.Label(
            frame_paginacion, text="", font=("Helvetica", 10, "bold"), bg=COLOR_FONDO_TABLA
        )
        label_paginacion.pack(side="left", padx=20, expand=True)
        btn_siguiente = crear_boton(
            frame_paginacion,
            "Siguiente ▶",
            estilo=VENTAS_BOTON_NAV,
            comando=pagina_siguiente,
        )
        btn_siguiente.pack(side="right", padx=5)
        actualizar_etiqueta_paginacion()

    crear_controles_paginacion()

    # --- Búsqueda por número de factura ---
    frame_buscar = tk.LabelFrame(
        ventana, text="Búsqueda", font=("Helvetica", 11, "bold"), bg=COLOR_FONDO
    )
    frame_buscar.place(x=1070, y=10, width=200, height=70)
    combo_buscar = ttk.Combobox(frame_buscar, font=("Calibri", 12), state="normal")
    combo_buscar.pack(pady=5, padx=10, fill="x")

    def actualizar_lista_numeros() -> None:
        numeros = ServicioFacturasVentas.obtener_lista_numeros_factura(filtro_actual)
        combo_buscar["values"] = numeros

    def aplicar_filtro(event: Optional[Any] = None) -> None:
        nonlocal filtro_actual, pagina_actual
        texto = combo_buscar.get().strip()
        filtro_actual = texto
        pagina_actual = 1
        actualizar_totales()
        cargar_pagina()
        actualizar_lista_numeros()

    combo_buscar.bind("<KeyRelease>", aplicar_filtro)
    combo_buscar.bind("<<ComboboxSelected>>", aplicar_filtro)
    combo_buscar.bind("<Return>", aplicar_filtro)

    # --- Opciones laterales (similar a facturas_deudas) ---
    lf_opciones = tk.LabelFrame(
        ventana, text="Opciones", font=("Helvetica", 11, "bold"), bg=COLOR_FONDO
    )
    lf_opciones.place(x=1070, y=85, width=200, height=450)

    # Cargar imágenes (usando ruta_recurso para que funcione al empaquetar)
    def cargar_img(nombre: str) -> Optional[ImageTk.PhotoImage]:
        try:
            img_path = ruta_recurso(str(Path("img") / nombre))
            return ImageTk.PhotoImage(Image.open(img_path).resize((28, 28)))
        except Exception:
            logger.error("No se pudo cargar la imagen %s", nombre)
            return None

    img_visualizar = cargar_img("visualizar.png")
    img_imprimir = cargar_img("imprimir.png")
    img_eliminar = cargar_img("eliminar.png")
    img_historial = cargar_img("historial.png")
    img_cambiar = cargar_img("cambiar.png")
    img_papelera = cargar_img("papelera.png")

    # --- Función para generar PDF (con wrap de texto, igual que antes) ---
    def generar_factura() -> None:
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia", "Seleccione una factura para generar.", parent=ventana
            )
            return

        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_ventas = int(valores[0])
        numero_secuencial = valores[1]
        numero_factura_mostrado = valores[2]
        recibido = valores[5]  # índice corregido según columnas
        vuelto = valores[6]

        datos = ServicioFacturasVentas.obtener_detalles_para_pdf(id_ventas)
        productos_detalle = datos["productos"]
        cliente_nombre = datos["cliente"]

        if not productos_detalle:
            messagebox.showerror(
                "Error",
                f"No se encontraron productos para la factura {id_ventas}",
                parent=ventana,
            )
            return

        numero_factura = (
            numero_factura_mostrado
            if numero_factura_mostrado
            else f"FACT-{numero_secuencial}"
        )

        carpeta_inicial = cargar_ultima_carpeta_pdf("ventas")
        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Factura_{numero_factura}.pdf",
            title="Guardar factura como",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=carpeta_inicial,
            parent=ventana,
        )
        if not archivo_pdf:
            return

        guardar_ultima_carpeta_pdf("ventas", str(Path(archivo_pdf).parent))

        c = canvas.Canvas(archivo_pdf, pagesize=letter)
        width, height = letter

        # Logo
        ruta_logo = obtener_ruta_logo("logo.png")
        try:
            c.drawImage(
                ruta_logo, width - 180, height - 150, width=140, height=140, mask="auto"
            )
        except Exception:
            logger.warning("No se pudo dibujar el logo en el PDF")

        c.setFont("Helvetica-Bold", 28)
        titulo = "Factura de Venta"
        x_titulo = 40
        y_titulo = height - 70
        c.drawString(x_titulo, y_titulo, titulo)
        ancho_titulo = c.stringWidth(titulo, "Helvetica-Bold", 28)
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.line(x_titulo, y_titulo - 6, x_titulo + ancho_titulo, y_titulo - 6)

        c.setFont("Helvetica-Bold", 13)
        y = height - 120
        c.drawString(40, y, f"N° Factura: {numero_factura}")
        c.drawString(40, y - 25, f"Cliente: {cliente_nombre}")

        y_tabla = y - 70
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_tabla, "Producto")
        c.drawString(230, y_tabla, "Hora")
        c.drawString(300, y_tabla, "Fecha")
        c.drawString(380, y_tabla, "Cantidad")
        c.drawString(450, y_tabla, "Subtotal")
        c.line(30, y_tabla - 5, width - 30, y_tabla - 5)

        c.setFont("Helvetica", 11)
        y_fila = y_tabla - 25
        total_calculado = 0.0
        max_width_producto = 190

        def fmt_currency(val: Any) -> str:
            try:
                return "${:,.0f}".format(float(val)).replace(",", ".")
            except Exception:
                logger.warning("Error al formatear moneda %s", val)
                return str(val)

        for prod, cant, sub, hora_prod, fecha_prod, _ in productos_detalle:
            prod_text = str(prod)
            nueva_y, lineas_usadas = draw_wrapped_text(
                c,
                prod_text,
                40,
                y_fila,
                max_width_producto,
                "Helvetica",
                11,
                line_height=14,
            )
            c.drawString(230, y_fila, str(hora_prod) if hora_prod else "")
            c.drawString(300, y_fila, str(fecha_prod) if fecha_prod else "")
            c.drawString(380, y_fila, str(cant))
            c.drawString(450, y_fila, fmt_currency(sub))
            total_calculado += float(sub)
            y_fila -= lineas_usadas * 14

        c.line(30, y_fila + 10, width - 30, y_fila + 10)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y_fila - 20, f"Total: {fmt_currency(total_calculado)}")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_fila - 45, f"Recibido: {recibido}")
        c.drawString(40, y_fila - 65, f"Vuelto: {vuelto}")

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
        messagebox.showinfo(
            "Éxito",
            f"Factura generada correctamente en:\n{archivo_pdf}",
            parent=ventana,
        )

    # --- Historial del cliente ---
    def abrir_historial_cliente() -> None:
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione una factura para ver el historial.",
                parent=ventana,
            )
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_ventas = valores[0]
        cliente_nombre = valores[3]
        parent.controlador.abrir_historial_venta(
            ventana,
            id_ventas=id_ventas,
            nombre_cliente=cliente_nombre,
            facturas_window=ventana,
        )

    # --- Eliminar factura ---
    def eliminar_factura() -> None:
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia", "Seleccione una factura para eliminar.", parent=ventana
            )
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_ventas = int(valores[0])
        if messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de eliminar esta factura?\n\nSe moverá a la Papelera de Ventas.",
            parent=ventana,
        ):
            success = ServicioFacturasVentas.eliminar_factura(
                id_ventas, usuario_elimino=parent.controlador.usuario_actual
            )
            if success:
                actualizar_totales()
                cargar_pagina()
                messagebox.showinfo(
                    "Éxito", "Factura eliminada y movida a Papelera.", parent=ventana
                )
            else:
                messagebox.showerror(
                    "Error",
                    "No se pudo eliminar la factura seleccionada.",
                    parent=ventana,
                )

    # --- Abrir papelera ---
    def abrir_papelera() -> None:
        parent.controlador.abrir_papelera_ventas(ventana)

    # --- Editar factura (doble clic) ---
    def editar_factura(event: Optional[Any] = None) -> None:
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia", "Seleccione una factura para editar.", parent=ventana
            )
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_ventas = int(valores[0])
        cliente = valores[3]
        callbacks = {
            "cargar_facturas": lambda: (actualizar_totales(), cargar_pagina()),
            "actualizar_total_facturas": actualizar_total_ventas,
        }
        parent.controlador.abrir_edicion_factura(
            ventana, id_ventas, cliente, parent.controlador.usuario_actual, callbacks
        )

    # --- VER DETALLE (nuevo) ---
    def _ver_detalle_factura() -> None:
        seleccionado = tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione una factura para ver los detalles.",
                parent=ventana,
            )
            return
        item = seleccionado[0]
        valores = tree.item(item, "values")
        id_ventas = int(valores[0])
        try:
            from retail.ventas.visualizar_ventas import ver_detalle_venta

            ver_detalle_venta(ventana, id_ventas)
        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el módulo de visualización:\n{e}",
                parent=ventana,
            )

    # --- Botones de opciones ---
    btn_visualizar = crear_boton(
        lf_opciones,
        "VER",
        estilo=VENTAS_BOTON_ADVERTENCIA,
        image=img_visualizar,
        compound="left",
        anchor="w",
        comando=_ver_detalle_factura,
    )
    btn_visualizar.image = img_visualizar
    btn_visualizar.pack(pady=7, padx=10, fill="x")

    btn_imprimir = crear_boton(
        lf_opciones,
        "IMPRIMIR",
        estilo=VENTAS_BOTON_ACCION,
        image=img_imprimir,
        compound="left",
        anchor="w",
        comando=generar_factura,
    )
    if img_imprimir:
        btn_imprimir.image = img_imprimir
    btn_imprimir.pack(pady=7, padx=10, fill="x")

    btn_historial = crear_boton(
        lf_opciones,
        "HISTORIAL",
        estilo=VENTAS_BOTON_INFO,
        image=img_historial,
        compound="left",
        anchor="w",
        comando=abrir_historial_cliente,
    )
    if img_historial:
        btn_historial.image = img_historial
    btn_historial.pack(pady=7, padx=10, fill="x")

    btn_eliminar = crear_boton(
        lf_opciones,
        "ELIMINAR",
        estilo=VENTAS_BOTON_PELIGRO,
        image=img_eliminar,
        compound="left",
        anchor="w",
        comando=eliminar_factura,
    )
    btn_eliminar.image = img_eliminar
    btn_eliminar.pack(pady=7, padx=10, fill="x")

    btn_papelera = crear_boton(
        lf_opciones,
        "PAPELERA",
        estilo=VENTAS_BOTON_NEUTRO,
        image=img_papelera,
        compound="left",
        anchor="w",
        comando=abrir_papelera,
    )
    if img_papelera:
        btn_papelera.image = img_papelera
    btn_papelera.pack(pady=7, padx=10, fill="x")

    btn_logo = crear_boton(
        lf_opciones,
        "LOGO",
        estilo=VENTAS_BOTON_IMPORTAR,
        image=img_cambiar,
        compound="left",
        anchor="w",
        comando=lambda: cambiar_logo(ventana),
    )
    if img_cambiar:
        btn_logo.image = img_cambiar
    btn_logo.pack(pady=7, padx=10, fill="x")

    # --- Total de ventas (similar al total de deudas) ---
    lf_total_ventas = tk.LabelFrame(
        ventana, text="Total Ventas", font=("Helvetica", 12, "bold"), bg=COLOR_FONDO
    )
    lf_total_ventas.place(x=1070, y=540, width=200, height=90)
    var_total_ventas = tk.StringVar(value="$0")
    lbl_total_ventas = tk.Label(
        lf_total_ventas,
        textvariable=var_total_ventas,
        font=("Helvetica", 16, "bold"),
        bg=COLOR_FONDO,
        fg="#008B8B",
    )
    lbl_total_ventas.pack(expand=True, fill="both", pady=10)

    def actualizar_total_ventas() -> None:
        total = ServicioFacturasVentas.calcular_total_ventas(filtro_actual)
        var_total_ventas.set(f"${total:,.0f}".replace(",", "."))

    # --- Inicialización ---
    actualizar_lista_numeros()
    actualizar_totales()
    cargar_pagina()
    actualizar_total_ventas()

    # --- Binding doble clic para editar ---
    tree.bind("<Double-1>", editar_factura)

    # Almacenar referencias para recarga externa
    ventana.cargar_facturas = lambda: (actualizar_totales(), cargar_pagina())
    ventana.actualizar_total_facturas = actualizar_total_ventas
