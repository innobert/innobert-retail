from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from pathlib import Path
import threading
from typing import Any
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

logger = logging.getLogger(__name__)

from retail.nucleo.configuraciones import (
    obtener_ruta_logo,
    cargar_ultima_carpeta_pdf,
    guardar_ultima_carpeta_pdf,
    abrir_archivo,
    COLOR_FONDO_TABLA,
    COLOR_AZUL,
    COLOR_VERDE,
    crear_boton,
    BOTON_ACCION,
    BOTON_NAV,
    FUENTE_BOTON_NEGRITA,
)
from retail.nucleo.servicios.ganancias.servicio_diario import ServicioDiario


class Dia(tk.Frame):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent, bg=COLOR_FONDO_TABLA)

        # Variables de paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_paginas = 1
        self.total_registros = 0
        self.fecha_actual = datetime.date.today().isoformat()
        self.filtro_fecha = self.fecha_actual

        # Variables para totales
        self.var_total_ganancia = tk.StringVar(value="$0")
        self.var_total_ventas = tk.StringVar(value="$0")

        # Widgets
        self.widgets()
        # Carga inicial en hilo
        threading.Thread(target=self.cargar_datos, daemon=True).start()

    def widgets(self) -> None:
        # Frame principal
        frame_main = tk.Frame(self, bg=COLOR_FONDO_TABLA)
        frame_main.pack(fill="both", expand=True, padx=18, pady=10)

        # --- Filtro de fecha ---
        frame_filtro = tk.Frame(frame_main, bg=COLOR_FONDO_TABLA)
        frame_filtro.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_filtro,
            text="Fecha (YYYY-MM-DD):",
            font=("Helvetica", 11, "bold"),
            bg=COLOR_FONDO_TABLA,
        ).pack(side="left", padx=(0, 5))

        self.entry_fecha = ttk.Entry(frame_filtro, font=("Helvetica", 11), width=12)
        self.entry_fecha.pack(side="left", padx=(0, 10))
        self.entry_fecha.insert(0, self.fecha_actual)

        btn_hoy = crear_boton(
            frame_filtro,
            texto="Hoy",
            estilo=BOTON_ACCION,
            comando=self.cargar_hoy,
            padx=8,
        )
        btn_hoy.pack(side="left", padx=2)

        btn_cargar = crear_boton(
            frame_filtro,
            texto="Cargar",
            estilo=BOTON_ACCION,
            comando=self.cargar_fecha_manual,
            padx=8,
        )
        btn_cargar.pack(side="left", padx=2)

        # --- Frame tabla ---
        frame_tabla = tk.Frame(frame_main, bg="#FFFFFF", bd=2, relief="groove")
        frame_tabla.pack(fill="both", expand=True, pady=(0, 10))

        columns = (
            "#",
            "dia_semana",
            "cliente",
            "fecha",
            "hora",
            "producto",
            "cantidad",
            "costo",
            "precio",
            "ganancia",
        )
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 13, "bold"),
            background=COLOR_FONDO_TABLA,
            foreground="#222",
        )
        style.configure(
            "Treeview",
            font=("Helvetica", 12),
            rowheight=32,
            background="#fff",
            fieldbackground="#fff",
        )
        style.map(
            "Treeview",
            background=[("selected", "#e0e0e0")],
            foreground=[("selected", "#222")],
        )

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columns,
            show="headings",
            height=12,
            style="Treeview",
        )
        anchos = [50, 90, 160, 90, 70, 180, 90, 90, 90, 110]
        for col, ancho in zip(columns, anchos):
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=ancho, anchor="center")
        self.tree.column("cliente", anchor="w")

        scroll_y = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree.yview
        )
        scroll_x = ttk.Scrollbar(
            frame_tabla, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        # --- Controles de paginación ---
        frame_paginacion = tk.Frame(frame_main, bg=COLOR_FONDO_TABLA)
        frame_paginacion.pack(fill="x", pady=(0, 5))

        btn_anterior = crear_boton(
            frame_paginacion,
            texto="◀ Anterior",
            estilo=BOTON_NAV,
            comando=self.pagina_anterior,
            padx=10,
        )
        btn_anterior.pack(side="left", padx=5)

        self.label_paginacion = tk.Label(
            frame_paginacion, text="", font=("Helvetica", 10, "bold"), bg=COLOR_FONDO_TABLA
        )
        self.label_paginacion.pack(side="left", padx=20, expand=True)

        btn_siguiente = crear_boton(
            frame_paginacion,
            texto="Siguiente ▶",
            estilo=BOTON_NAV,
            comando=self.pagina_siguiente,
            padx=10,
        )
        btn_siguiente.pack(side="right", padx=5)

        # --- Frame totales ---
        lf_totales = tk.LabelFrame(
            frame_main,
            text="Totales del Día",
            font=("Helvetica", 13, "bold"),
            bg="#FFFFFF",
            fg="#222",
            padx=18,
            pady=12,
            bd=2,
            relief="groove",
        )
        lf_totales.pack(fill="x", pady=(0, 5))

        totales_frame = tk.Frame(lf_totales, bg="#FFFFFF")
        totales_frame.pack(fill="x")

        for text, var in [
            ("Total Ganancia:", self.var_total_ganancia),
            ("Total Ventas + Pagos:", self.var_total_ventas),
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
        ruta_img = (Path(__file__).parent / ".." / ".." / "img").resolve()
        try:
            img_pdf = ImageTk.PhotoImage(
                Image.open(ruta_img / "imprimir.png").resize((28, 28))
            )
        except Exception:
            img_pdf = None

        self.btn_pdf = crear_boton(
            lf_totales,
            texto="  Imprimir PDF",
            estilo=BOTON_ACCION,
            comando=self.generar_pdf_registro,
            fuente=FUENTE_BOTON_NEGRITA,
            image=img_pdf,
            compound="left",
            cursor="hand2",
            padx=10,
            anchor="w",
        )
        self.btn_pdf.image = img_pdf
        self.btn_pdf.pack(side="right", padx=(0, 10), pady=(0, 5))

    # ========== Métodos de paginación y carga ==========
    def cargar_hoy(self) -> None:
        self.filtro_fecha = datetime.date.today().isoformat()
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, self.filtro_fecha)
        self.pagina_actual = 1
        threading.Thread(target=self.cargar_datos, daemon=True).start()

    def cargar_fecha_manual(self) -> None:
        fecha = self.entry_fecha.get().strip()
        try:
            datetime.date.fromisoformat(fecha)
            self.filtro_fecha = fecha
            self.pagina_actual = 1
            threading.Thread(target=self.cargar_datos, daemon=True).start()
        except ValueError:
            messagebox.showerror(
                "Error", "Formato de fecha inválido. Use YYYY-MM-DD", parent=self
            )

    def actualizar_etiqueta_paginacion(self) -> None:
        self.label_paginacion.config(
            text=f"Página {self.pagina_actual} de {self.total_paginas} ({self.total_registros} registros)"
        )

    def pagina_anterior(self) -> None:
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            threading.Thread(target=self.cargar_datos, daemon=True).start()

    def pagina_siguiente(self) -> None:
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            threading.Thread(target=self.cargar_datos, daemon=True).start()

    def cargar_datos(self) -> None:
        try:
            total_registros = ServicioDiario.contar_registros(self.filtro_fecha)
            self.total_registros = total_registros
            self.total_paginas = max(
                1,
                (total_registros + self.registros_por_pagina - 1)
                // self.registros_por_pagina,
            )
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas

            offset = (self.pagina_actual - 1) * self.registros_por_pagina
            registros_crudos = ServicioDiario.obtener_pagina(
                self.filtro_fecha, offset, self.registros_por_pagina
            )
            registros_tabla = ServicioDiario.formatear_registros_para_tabla(
                registros_crudos
            )

            total_ganancia, total_monto = ServicioDiario.obtener_totales_fecha(
                self.filtro_fecha
            )

            self.after(
                0, self._actualizar_tabla, registros_tabla, total_ganancia, total_monto
            )

        except Exception as e:
            logger.exception("Error cargando datos")
            self.after(
                0,
                lambda e=e: messagebox.showerror(
                    "Error", f"No se pudieron cargar los datos: {e}", parent=self
                ),
            )

    def _actualizar_tabla(self, registros_tabla: list[Any], total_ganancia: float, total_monto: float) -> None:
        self.tree.delete(*self.tree.get_children())
        for row in registros_tabla:
            self.tree.insert("", "end", values=row)
        self.var_total_ganancia.set(f"${total_ganancia:,.0f}".replace(",", "."))
        self.var_total_ventas.set(f"${total_monto:,.0f}".replace(",", "."))
        self.actualizar_etiqueta_paginacion()

    # ========== Método para generar PDF con carpeta recordada específica para GANANCIAS ==========
    def generar_pdf_registro(self) -> None:
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning(
                "Advertencia",
                "Seleccione un registro para imprimir.",
                parent=self,
            )
            return

        item = seleccionado[0]
        (
            idx,
            dia_semana,
            cliente,
            fecha,
            hora,
            producto,
            cantidad,
            costo,
            precio,
            ganancia,
        ) = self.tree.item(item, "values")

        # Cargar última carpeta usada para GANANCIAS
        carpeta_inicial = cargar_ultima_carpeta_pdf("ganancias")

        archivo_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Registro_{fecha}_{hora.replace(':','-')}.pdf",
            title="Guardar registro como PDF",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=carpeta_inicial,
            parent=self,
        )

        if archivo_pdf:
            # Guardar la carpeta usada para futuras ocasiones (GANANCIAS)
            carpeta_usada = Path(archivo_pdf).parent
            guardar_ultima_carpeta_pdf("ganancias", str(carpeta_usada))

            c = canvas.Canvas(archivo_pdf, pagesize=letter)
            width, height = letter

            ruta_logo = obtener_ruta_logo("logo.png")
            try:
                c.drawImage(
                    ruta_logo,
                    width - 180,
                    height - 150,
                    width=140,
                    height=140,
                    mask="auto",
                )
            except Exception:
                logger.warning("No se pudo insertar el logo en la factura diaria")

            c.setFont("Helvetica-Bold", 28)
            titulo = "Detalle de Registro"
            x_titulo = 40
            y_titulo = height - 70
            c.drawString(x_titulo, y_titulo, titulo)
            ancho_titulo = c.stringWidth(titulo, "Helvetica-Bold", 28)
            c.setStrokeColor(colors.black)
            c.setLineWidth(2)
            c.line(x_titulo, y_titulo - 6, x_titulo + ancho_titulo, y_titulo - 6)

            c.setFont("Helvetica-Bold", 13)
            y = height - 120
            c.drawString(40, y, f"Cliente: {cliente}")
            c.drawString(40, y - 25, f"Fecha: {fecha}")
            c.drawString(40, y - 50, f"Hora: {hora}")
            c.drawString(40, y - 75, f"Día de la semana: {dia_semana}")

            y_tabla = y - 110
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y_tabla, "Concepto")
            c.drawString(200, y_tabla, "Cantidad")
            c.drawString(270, y_tabla, "Costo")
            c.drawString(360, y_tabla, "Precio")
            c.drawString(440, y_tabla, "Ganancia")
            c.line(30, y_tabla - 5, width - 30, y_tabla - 5)

            c.setFont("Helvetica", 11)
            y_fila = y_tabla - 25
            # Truncar nombre del producto si es demasiado largo
            prod_text = str(producto)
            if len(prod_text) > 30:
                prod_text = prod_text[:27] + "..."
            c.drawString(40, y_fila, prod_text)
            c.drawString(200, y_fila, str(cantidad))
            c.drawString(270, y_fila, str(costo))
            c.drawString(360, y_fila, str(precio))
            c.drawString(440, y_fila, str(ganancia))

            c.line(30, y_fila + 10, width - 30, y_fila + 10)

            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y_fila - 20, f"Total: {precio}")
            c.drawString(240, y_fila - 20, f"Ganancia: {ganancia}")

            c.setFont("Helvetica-Oblique", 13)
            c.drawString(50, 60, "Gracias por su preferencia. ®INNOBERTDEV")
            c.setFont("Helvetica-Oblique", 12)
            c.drawString(
                50, 40, "Registro generado automáticamente por Innobert Retail"
            )

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

            messagebox.showinfo(
                "Éxito",
                f"PDF generado correctamente en:\n{archivo_pdf}",
                parent=self,
            )
