import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from PIL import Image, ImageTk

from retail.nucleo.configuraciones import (
    obtener_ruta_logo,
    cargar_ultima_carpeta_pdf,
    guardar_ultima_carpeta_pdf,
    abrir_archivo
)
from retail.nucleo.servicios.ganancias.servicio_anual import ServicioAnual


class Year(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#F5F5F5")

        # Variables de paginación
        self.pagina_actual = 1
        self.periodos_por_pagina = 10
        self.total_paginas = 1
        self.total_periodos = 0

        # Variables para totales globales
        self.var_total_ganancia = tk.StringVar(value="$0")
        self.var_total_ventas = tk.StringVar(value="$0")

        # Cache de períodos (se llena en el primer hilo)
        self.periodos_data = None

        # Widgets
        self.widgets()
        # Carga inicial en hilo
        threading.Thread(target=self.cargar_datos, daemon=True).start()

    def widgets(self):
        # Frame principal
        frame_main = tk.Frame(self, bg="#F5F5F5")
        frame_main.pack(fill="both", expand=True, padx=18, pady=10)

        # --- Frame tabla ---
        frame_tabla = tk.Frame(frame_main, bg="#FFFFFF", bd=2, relief="groove")
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))

        columns = (
            "anio",
            "desde",
            "hasta",
            "total_ventas",
            "total_ganancia",
            "productos_vendidos",
            "clientes",
        )
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 13, "bold"),
            background="#F5F5F5",
            foreground="#222",
        )
        style.configure(
            "Treeview",
            font=("Helvetica", 12),
            rowheight=32,
            background="#fff",
            fieldbackground="#fff",
        )
        style.map("Treeview", background=[("selected", "#e0e0e0")], foreground=[("selected", "#222")])

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columns,
            show="headings",
            height=12,
            style="Treeview",
        )
        self.tree.heading("anio", text="Año")
        self.tree.heading("desde", text="Desde")
        self.tree.heading("hasta", text="Hasta")
        self.tree.heading("total_ventas", text="Total Ventas")
        self.tree.heading("total_ganancia", text="Total Ganancia")
        self.tree.heading("productos_vendidos", text="P.Vendidos")
        self.tree.heading("clientes", text="Clientes")

        self.tree.column("anio", width=100, anchor="center")
        self.tree.column("desde", width=100, anchor="center")
        self.tree.column("hasta", width=100, anchor="center")
        self.tree.column("total_ventas", width=120, anchor="center")
        self.tree.column("total_ganancia", width=120, anchor="center")
        self.tree.column("productos_vendidos", width=100, anchor="center")
        self.tree.column("clientes", width=100, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # --- Controles de paginación ---
        frame_paginacion = tk.Frame(frame_main, bg="#F5F5F5")
        frame_paginacion.pack(fill="x", pady=(0, 5))

        btn_anterior = tk.Button(
            frame_paginacion,
            text="◀ Anterior",
            command=self.pagina_anterior,
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            font=("Helvetica", 10, "bold")
        )
        btn_anterior.pack(side="left", padx=5)

        self.label_paginacion = tk.Label(
            frame_paginacion,
            text="",
            font=("Helvetica", 10, "bold"),
            bg="#F5F5F5"
        )
        self.label_paginacion.pack(side="left", padx=20, expand=True)

        btn_siguiente = tk.Button(
            frame_paginacion,
            text="Siguiente ▶",
            command=self.pagina_siguiente,
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            font=("Helvetica", 10, "bold")
        )
        btn_siguiente.pack(side="right", padx=5)

        # --- Frame totales ---
        lf_totales = tk.LabelFrame(
            frame_main,
            text="Totales Globales",
            font=("Helvetica", 13, "bold"),
            bg="#FFFFFF",
            fg="#222",
            padx=18,
            pady=12,
            bd=2,
            relief="groove"
        )
        lf_totales.pack(fill="x", pady=(0, 5))

        totales_frame = tk.Frame(lf_totales, bg="#FFFFFF")
        totales_frame.pack(fill="x")

        for text, var in [
            ("Total Ganancia:", self.var_total_ganancia),
            ("Total Ventas:", self.var_total_ventas),
        ]:
            tk.Label(
                totales_frame,
                text=text,
                font=("Helvetica", 13, "bold"),
                bg="#FFFFFF",
                fg="#222",
            ).pack(side="left", padx=(0, 10))
            tk.Label(
                totales_frame,
                textvariable=var,
                font=("Helvetica", 13, "bold"),
                bg="#FFFFFF",
                fg="#222",
            ).pack(side="left", padx=(0, 30))

        # Botón PDF (imagen)
        ruta_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))
        try:
            img_pdf = ImageTk.PhotoImage(Image.open(os.path.join(ruta_img, "imprimir.png")).resize((28, 28)))
        except Exception:
            img_pdf = None

        self.btn_pdf = tk.Button(
            lf_totales,
            text="  Imprimir PDF",
            image=img_pdf,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#1976D2",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.generar_pdf_anio,
            padx=10,
            anchor="w"
        )
        self.btn_pdf.image = img_pdf
        self.btn_pdf.pack(side="right", padx=(0, 10), pady=(0, 5))

    # ========== Métodos de paginación ==========
    def actualizar_etiqueta_paginacion(self):
        self.label_paginacion.config(
            text=f"Página {self.pagina_actual} de {self.total_paginas} ({self.total_periodos} períodos)"
        )

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._mostrar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._mostrar_pagina()

    # ========== Carga optimizada ==========
    def cargar_datos(self):
        """Carga todos los períodos (una sola vez) y actualiza la primera página."""
        try:
            if self.periodos_data is None:
                self.periodos_data = ServicioAnual.obtener_periodos()
            self.total_periodos = len(self.periodos_data)
            self.total_paginas = max(1, (self.total_periodos + self.periodos_por_pagina - 1) // self.periodos_por_pagina)
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas

            self._mostrar_pagina()

            total_ganancia, total_ventas = ServicioAnual.obtener_totales_globales()
            self.after(0, self._actualizar_totales, total_ganancia, total_ventas)

        except Exception as e:
            print(f"Error cargando períodos: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}", parent=self))

    def _mostrar_pagina(self):
        start = (self.pagina_actual - 1) * self.periodos_por_pagina
        end = start + self.periodos_por_pagina
        pagina = self.periodos_data[start:end]
        self.after(0, self._actualizar_tabla, pagina)

    def _actualizar_tabla(self, periodos):
        self.tree.delete(*self.tree.get_children())
        for row in periodos:
            self.tree.insert("", "end", values=row)
        self.actualizar_etiqueta_paginacion()

    def _actualizar_totales(self, total_ganancia, total_ventas):
        self.var_total_ganancia.set(f"${total_ganancia:,.0f}".replace(",", "."))
        self.var_total_ventas.set(f"${total_ventas:,.0f}".replace(",", "."))

    # ========== Generar PDF con carpeta recordada específica para GANANCIAS ==========
    def generar_pdf_anio(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un registro anual para imprimir.",
                parent=self,
            )
            return

        item = seleccionado[0]
        (
            anio,
            fecha_de,
            fecha_hasta,
            total_ventas,
            total_ganancia,
            productos_vendidos,
            clientes,
        ) = self.tree.item(item, "values")

        # Cargar última carpeta usada para GANANCIAS
        carpeta_inicial = cargar_ultima_carpeta_pdf('ganancias')

        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Año_{fecha_de}_a_{fecha_hasta}.pdf",
            title="Guardar año como PDF",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=carpeta_inicial,
            parent=self,
        )

        if archivo_pdf:
            # Guardar la carpeta usada para futuras ocasiones (GANANCIAS)
            carpeta_usada = os.path.dirname(archivo_pdf)
            guardar_ultima_carpeta_pdf('ganancias', carpeta_usada)

            c = canvas.Canvas(archivo_pdf, pagesize=letter)
            width, height = letter

            ruta_logo = obtener_ruta_logo("logo.png")
            try:
                c.drawImage(ruta_logo, width - 180, height - 150, width=140, height=140, mask='auto')
            except Exception:
                pass

            c.setFont("Helvetica-Bold", 28)
            titulo = "Factura Anual"
            x_titulo = 40
            y_titulo = height - 70
            c.drawString(x_titulo, y_titulo, titulo)
            ancho_titulo = c.stringWidth(titulo, "Helvetica-Bold", 28)
            c.setStrokeColor(colors.black)
            c.setLineWidth(2)
            c.line(x_titulo, y_titulo - 6, x_titulo + ancho_titulo, y_titulo - 6)

            c.setFont("Helvetica-Bold", 13)
            y = height - 120
            c.drawString(40, y, f"Año: {anio}")
            c.drawString(40, y - 25, f"Desde: {fecha_de}")
            c.drawString(40, y - 50, f"Hasta: {fecha_hasta}")

            y_totales = y - 90
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y_totales, f"Total Ventas: {total_ventas}")
            c.drawString(240, y_totales, f"Ganancia: {total_ganancia}")
            c.drawString(40, y_totales - 25, f"Productos Vendidos: {productos_vendidos}")
            c.drawString(240, y_totales - 25, f"Clientes: {clientes}")

            c.setFont("Helvetica-Oblique", 13)
            c.drawString(50, 60, "Gracias por su preferencia. ®INNOBERTDEV")
            c.setFont("Helvetica-Oblique", 12)
            c.drawString(50, 40, "Factura generada automáticamente por Innobert Retail")

            c.saveState()
            c.setFont("Helvetica-Bold", 60)
            c.setFillColorRGB(0.93, 0.93, 0.93)
            c.translate(width/2, 200)
            c.rotate(30)
            c.drawCentredString(0, 0, "Innobert")
            c.restoreState()

            c.save()

            # Abrir el PDF automáticamente
            abrir_archivo(archivo_pdf)

            messagebox.showinfo(
                "Éxito",
                f"PDF generado correctamente en:\n{archivo_pdf}",
                parent=self,
            )