import tkinter as tk
from tkinter import ttk, messagebox, END
import os
from PIL import Image, ImageTk

from retail.nucleo.servicios.clientes.servicio_clientes import ClientesServicio
from retail.utilidades.paginacion import PaginacionWidget


class Clientes(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador

        # Variables de paginación
        self.pagina_actual = 1
        self.clientes_por_pagina = 20
        self.total_paginas = 1
        self.filtro_actual = ""
        
        self.widgets()
        self.cargar_datos()

    def widgets(self):
        # =========================
        # SECCIÓN CLIENTES
        # =========================
        # Título Principal
        label_titulo = tk.Label(
            self,
            text="Clientes",
            font=("Helvetica", 15, "bold"),
            bg="#FF9800",
            fg="#0A0A0A",
        )
        label_titulo.pack(fill="x", side="top")  # Cambiado a pack para mejor adaptación

        # Frame principal (ahora con grid para distribución flexible)
        frame_principal = tk.Frame(self, bg="#E6D9E3")
        frame_principal.pack(fill="both", expand=True)

        # Configurar grid: columna izquierda fija, columna derecha expandible
        frame_principal.grid_columnconfigure(0, weight=0, minsize=330)
        frame_principal.grid_columnconfigure(1, weight=1)
        frame_principal.grid_rowconfigure(0, weight=1)

        # Frame izquierdo (30% aprox, fijo 330px)
        frame1 = tk.Frame(frame_principal, bg="#E6D9E3", padx=10, pady=10)
        frame1.grid(row=0, column=0, sticky="nsew")

        # Frame derecho (70% expandible)
        frame2 = tk.Frame(frame_principal, bg="#E6D9E3", padx=10, pady=10)
        frame2.grid(row=0, column=1, sticky="nsew")
        frame2.grid_rowconfigure(0, weight=1)  # La tabla ocupará el espacio
        frame2.grid_columnconfigure(0, weight=1)

        # ========== Frame izquierdo ==========
        # LabelFrame Búsqueda
        lf_buscar = tk.LabelFrame(
            frame1,
            text="Búsqueda",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
            fg="#0A0A0A",
        )
        lf_buscar.pack(fill="x", pady=(0, 10))

        self.combo_clientes = ttk.Combobox(
            lf_buscar,
            font=("Helvetica", 11),
            state="normal",
            width=25,
        )
        self.combo_clientes.pack(fill="x", padx=5, pady=5)
        self.combo_clientes.bind("<KeyRelease>", self.filtrar_clientes)
        self.combo_clientes.bind("<<ComboboxSelected>>", self.filtrar_clientes)

        # Campos de entrada
        frame_form = tk.Frame(frame1, bg="#E6D9E3")
        frame_form.pack(fill="x", pady=10)

        campos = [
            ("Nombres", "entry_nombres"),
            ("Apellidos", "entry_apellidos"),
            ("Cédula", "entry_cedula"),
            ("Celular", "entry_celular"),
            ("Zona", "entry_zona"),
        ]

        self.entries = {}
        for text, key in campos:
            frame_campo = tk.Frame(frame_form, bg="#E6D9E3")
            frame_campo.pack(fill="x", pady=5)
            tk.Label(
                frame_campo,
                text=text,
                bg="#E6D9E3",
                font=("Helvetica", 12, "bold"),
                width=10,
                anchor="w",
            ).pack(side="left")
            entry = ttk.Entry(
                frame_campo,
                font=("Helvetica", 12, "bold"),
            )
            entry.pack(side="left", fill="x", expand=True, padx=5)
            self.entries[key] = entry

        # LabelFrame Opciones (botones)
        lf_opciones = tk.LabelFrame(
            frame1,
            text="Opciones",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        lf_opciones.place(x=30, y=300, width=200, height=200)

        # Cargar imágenes
        ruta_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))
        def cargar_img(nombre):
            try:
                return ImageTk.PhotoImage(Image.open(os.path.join(ruta_img, nombre)).resize((28, 28)))
            except Exception:
                return None

        img_add = cargar_img("add.png")
        img_delete = cargar_img("eliminar.png")
        img_clear = cargar_img("limpiar.png")
        self._imgs_btns = [img_add, img_delete, img_clear]

        # Botón Agregar
        self.btn_agregar = tk.Button(
            lf_opciones,
            text="  Agregar",
            image=img_add,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.agregar_cliente,
            padx=10,
            anchor="w"
        )
        self.btn_agregar.image = img_add
        self.btn_agregar.place(x=25, y=15, width=150, height=40)

        # Botón Eliminar
        self.btn_eliminar = tk.Button(
            lf_opciones,
            text="  Eliminar",
            image=img_delete,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#F44336",
            fg="white",
            activebackground="#B71C1C",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.eliminar_cliente,
            padx=10,
            anchor="w"
        )
        self.btn_eliminar.image = img_delete
        self.btn_eliminar.place(x=25, y=70, width=150, height=40)

        # Botón Limpiar
        self.btn_limpiar = tk.Button(
            lf_opciones,
            text="  Limpiar",
            image=img_clear,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#9E9E9E",
            fg="white",
            activebackground="#757575",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.limpiar_campos,
            padx=10,
            anchor="w"
        )
        self.btn_limpiar.image = img_clear
        self.btn_limpiar.place(x=25, y=125, width=150, height=40)

        # ========== Frame derecho ==========
        # Estilo de la tabla
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Calibri", 14, "bold"), background="#E6D9E3", foreground="#333")
        style.configure("Treeview", font=("Calibri", 13), rowheight=32, background="#fff", fieldbackground="#fff")
        style.map("Treeview", background=[("selected", "#222")], foreground=[("selected", "#fff")])

        # Frame contenedor de la tabla y scroll
        frame_tabla = tk.Frame(frame2, bg="#E6D9E3")
        frame_tabla.grid(row=0, column=0, sticky="nsew")
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=("id_cliente", "nombres", "apellidos", "cedula", "celular", "zona"),
            show="headings",
            selectmode="browse",
            style="Treeview"
        )

        columnas = [
            ("id_cliente", "ID", 50),
            ("nombres", "Nombres", 150),
            ("apellidos", "Apellidos", 150),
            ("cedula", "Cédula", 120),
            ("celular", "Celular", 120),
            ("zona", "Zona", 120),
        ]
        for col_id, col_text, width in columnas:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor="center")

        self.tree.bind("<Double-1>", self.editar_celda)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_formulario)
        self.tree.bind("<Delete>", self.eliminar_cliente)

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Frame para controles de paginación (debajo de la tabla)
        self.frame_paginacion = tk.Frame(frame2, bg="#E6D9E3")
        self.frame_paginacion.grid(row=1, column=0, sticky="ew", pady=5)

        self.crear_controles_paginacion()

    # --------------------------
    # Métodos de paginación
    def _texto_paginacion(self):
        total = ClientesServicio.contar_clientes(self.filtro_actual)
        return f"Página {self.pagina_actual} de {self.total_paginas} ({total} clientes)"

    def crear_controles_paginacion(self):
        for widget in self.frame_paginacion.winfo_children():
            widget.destroy()
        self.paginacion = PaginacionWidget(
            self.frame_paginacion,
            on_anterior=self.pagina_anterior,
            on_siguiente=self.pagina_siguiente,
            actualizar_texto=self._texto_paginacion,
        )
        self.paginacion.pack(fill="x")

    def _actualizar_totales(self):
        total_clientes = ClientesServicio.contar_clientes(self.filtro_actual)
        self.total_paginas = max(1, (total_clientes + self.clientes_por_pagina - 1) // self.clientes_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

    def _cargar_pagina(self):
        offset = (self.pagina_actual - 1) * self.clientes_por_pagina
        clientes = ClientesServicio.obtener_clientes_paginado(
            offset=offset,
            limit=self.clientes_por_pagina,
            filtro=self.filtro_actual
        )
        self._mostrar_clientes_en_treeview(clientes)
        if hasattr(self, 'paginacion'):
            self.paginacion.actualizar()

    def _mostrar_clientes_en_treeview(self, clientes):
        self.tree.delete(*self.tree.get_children())
        for cliente in clientes:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    cliente["id_cliente"],
                    cliente["nombres"],
                    cliente["apellidos"],
                    cliente["cedula"],
                    cliente["celular"],
                    cliente["zona"]
                )
            )

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._cargar_pagina()

    # --------------------------
    # Métodos de la interfaz (adaptados)
    # --------------------------
    def cargar_datos(self):
        """Carga la primera página de clientes y actualiza el combobox de búsqueda."""
        self.filtro_actual = ""
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()
        # Actualizar combobox con todos los nombres completos para búsqueda
        self.combo_clientes["values"] = ClientesServicio.obtener_nombres_clientes_para_busqueda()
        self.combo_clientes.set("")

    def filtrar_clientes(self, event=None):
        """Filtra la tabla por el texto ingresado en el combobox (nombre completo)."""
        texto = self.combo_clientes.get().strip()
        self.filtro_actual = texto
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()
        # Actualizar el combobox con los nombres que coinciden (autocompletado)
        nombres_filtrados = ClientesServicio.obtener_nombres_clientes_para_busqueda(texto)
        self.combo_clientes["values"] = nombres_filtrados

    def agregar_cliente(self):
        datos = [entry.get().strip() for entry in self.entries.values()]
        nombres, apellidos, cedula, celular, zona = datos

        if not all(datos):
            messagebox.showwarning("Campos vacíos", "Todos los campos son obligatorios")
            return

        exito, mensaje = ClientesServicio.agregar_cliente(
            nombres, apellidos, cedula, celular, zona
        )
        if exito:
            # Recargar la página actual (puede cambiar el total de páginas)
            self._actualizar_totales()
            self._cargar_pagina()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)

    def eliminar_cliente(self, event=None):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        id_cliente = self.tree.item(seleccionado[0], "values")[0]
        if messagebox.askyesno("Confirmar eliminación", "¿Está seguro de eliminar este cliente?"):
            exito, mensaje = ClientesServicio.eliminar_cliente(id_cliente)
            if exito:
                # Recargar la página actual. Si la página se queda vacía y no es la primera, retroceder
                self._actualizar_totales()
                self._cargar_pagina()
                if not self.tree.get_children() and self.pagina_actual > 1:
                    self.pagina_actual -= 1
                    self._cargar_pagina()
                self.limpiar_campos()
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)

    def editar_celda(self, event):
        columna = self.tree.identify_column(event.x)
        item = self.tree.selection()[0]
        columna_texto = self.tree.heading(columna)["text"]
        if columna_texto == "ID":
            return

        columnas_db = {
            "Nombres": "nombres",
            "Apellidos": "apellidos",
            "Cédula": "cedula",
            "Celular": "celular",
            "Zona": "zona",
        }
        campo_db = columnas_db.get(columna_texto)
        if not campo_db:
            messagebox.showerror("Error", "No se puede editar esta columna")
            return

        valor_actual = self.tree.item(item, "values")[int(columna[1:]) - 1]
        id_cliente = self.tree.item(item, "values")[0]

        # Ventana de edición
        popup = tk.Toplevel(self)
        popup.title(f"Editar {columna_texto}")
        popup.geometry("400x250+450+200")
        popup.resizable(False, False)
        popup.transient(self)
        popup.protocol("WM_DELETE_WINDOW", lambda: popup.destroy())
        self.after(100, lambda: popup.grab_set())
        popup.focus_force()

        frame_popup = tk.Frame(popup, bg="#F5F5F5", padx=20, pady=20)
        frame_popup.pack(fill="both", expand=True)

        tk.Label(
            frame_popup,
            text=f"Editar {columna_texto}",
            font=("Helvetica", 14, "bold"),
            bg="#F5F5F5",
            fg="#333333",
        ).pack(pady=10)

        tk.Label(
            frame_popup,
            text="Nuevo valor:",
            font=("Helvetica", 12),
            bg="#F5F5F5",
            fg="#333333",
        ).pack(anchor="w", pady=5)

        nuevo_valor = ttk.Entry(frame_popup, font=("Helvetica", 12), width=30)
        nuevo_valor.pack(pady=5)
        nuevo_valor.insert(0, valor_actual)

        frame_botones = tk.Frame(frame_popup, bg="#F5F5F5")
        frame_botones.pack(pady=20)

        def guardar_cambios(event=None):
            nuevo_texto = nuevo_valor.get().strip()
            if not nuevo_texto:
                messagebox.showwarning("Valor vacío", "El nuevo valor no puede estar vacío", parent=popup)
                return
            exito, mensaje = ClientesServicio.actualizar_cliente(id_cliente, campo_db, nuevo_texto)
            if exito:
                # Recargar la página para reflejar el cambio (puede afectar el orden/filtro)
                self._cargar_pagina()
                popup.destroy()
                messagebox.showinfo("Éxito", mensaje, parent=self)
            else:
                messagebox.showerror("Error", mensaje, parent=popup)

        popup.bind("<Return>", guardar_cambios)

        tk.Button(
            frame_botones,
            text="Guardar",
            command=guardar_cambios,
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=12,
        ).pack(side="left", padx=10)

        tk.Button(
            frame_botones,
            text="Cancelar",
            command=popup.destroy,
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="white",
            width=12,
        ).pack(side="left", padx=10)

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, END)
        self.combo_clientes.set("")
        self.cargar_datos()  # Reinicia filtro y carga primera página

    def cargar_formulario(self, event):
        seleccionado = self.tree.selection()
        if not seleccionado:
            return
        valores = self.tree.item(seleccionado[0], "values")
        for entry, valor in zip(self.entries.values(), valores[1:]):
            entry.delete(0, tk.END)
            entry.insert(0, valor)