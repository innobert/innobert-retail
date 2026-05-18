import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os

from retail.nucleo.configuraciones import rutas
from retail.nucleo.servicios.inventario.servicio_inventario import InventarioServicio, peso_colombiano


class Inventario(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="#E6D9E3")
        self.controlador = controlador

        # Carpeta de imágenes (usando ruta absoluta)
        self.img_folder = rutas("fotos")
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

        self.ultimo_directorio = os.path.expanduser("~")
        self.producto_seleccionado_frame = None
        self.producto_seleccionado_id = None

        # Variables para paginación bajo demanda
        self.pagina_actual = 1
        self.productos_por_pagina = 12  # 4x3
        self.total_paginas = 1
        self.filtro_actual = ""          # Texto de búsqueda actual

        self.widgets()
        self.cargar_productos()
        self.crear_controles_paginacion()
        self.actualizar_combobox_productos()

        # Bindings
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_productos_combobox)
        self.entry_buscar.bind("<Return>", self.seleccionar_producto_entry)

        # Eliminar bindings globales no deseados
        self.unbind_all("<Delete>")

    # ----------------------------------------------------------------------
    # Construcción de la interfaz (sin cambios)
    # ----------------------------------------------------------------------
    def widgets(self):
        # Título Principal
        label_titulo = tk.Label(
            self,
            text="Inventario",
            font=("Helvetica", 15, "bold"),
            bg="#2196F3",
            fg="#0A0A0A",
        )
        label_titulo.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Frame lateral izquierdo
        frame_datos = tk.Frame(self, bg="#E6D9E3", width=270)
        frame_datos.grid(row=1, column=0, sticky="ns", padx=(10, 5), pady=10)
        frame_datos.grid_propagate(False)

        # --- LabelFrame Buscar ---
        lf_buscar = tk.LabelFrame(
            frame_datos, text="Buscar", font=("Helvetica", 12, "bold"), bg="#E6D9E3"
        )
        lf_buscar.place(x=10, y=10, width=230, height=70)
        self.entry_buscar = ttk.Combobox(lf_buscar, font=("Helvetica", 11))
        self.entry_buscar.place(x=10, y=10, width=200, height=30)
        self.entry_buscar["values"] = []

        # --- LabelFrame Selección ---
        lf_seleccion = tk.LabelFrame(
            frame_datos,
            text="Selección",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        lf_seleccion.place(x=10, y=90, width=250, height=190)
        labels = ["Producto:", "Precio:", "Costo:", "Stock:", "Estado:"]
        self.seleccion_vars = {}
        self.estado_label = None
        for i, text in enumerate(labels):
            tk.Label(
                lf_seleccion,
                text=text,
                font=("Helvetica", 11, "bold"),
                bg="#E6D9E3",
                anchor="w",
            ).place(x=10, y=10 + i * 32)
            var = tk.StringVar(value="")
            self.seleccion_vars[text[:-1].lower()] = var
            if text == "Estado:":
                self.estado_label = tk.Label(
                    lf_seleccion,
                    textvariable=var,
                    font=("Helvetica", 11),
                    bg="#E6D9E3",
                    anchor="w",
                )
                self.estado_label.place(x=90, y=10 + i * 32)
            else:
                tk.Label(
                    lf_seleccion,
                    textvariable=var,
                    font=("Helvetica", 11),
                    bg="#E6D9E3",
                    anchor="w",
                ).place(x=90, y=10 + i * 32)

        # --- LabelFrame Opciones ---
        lf_opciones = tk.LabelFrame(
            frame_datos,
            text="Opciones",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        lf_opciones.place(x=30, y=300, width=210, height=255)

        # Cargar imágenes
        ruta_img = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img"))
        def cargar_img(nombre):
            try:
                return ImageTk.PhotoImage(Image.open(os.path.join(ruta_img, nombre)).resize((28, 28)))
            except Exception:
                return None

        img_add = cargar_img("add.png")
        img_delete = cargar_img("eliminar.png")
        img_historial = cargar_img("historial.png")
        img_total = cargar_img("total.png")

        # Botón Agregar
        self.btn_agregar = tk.Button(
            lf_opciones,
            text="  Agregar",
            image=img_add,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.agregar_producto,
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
            command=self.eliminar_producto_seleccionado,
            padx=10,
            anchor="w"
        )
        self.btn_eliminar.image = img_delete
        self.btn_eliminar.place(x=25, y=70, width=150, height=40)

        # Botón Historial
        self.btn_historial = tk.Button(
            lf_opciones,
            text="  Historial",
            image=img_historial,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#8e24aa",
            fg="white",
            activebackground="#6d1b7b",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.abrir_historial_inventario,
            padx=10,
            anchor="w"
        )
        self.btn_historial.image = img_historial
        self.btn_historial.place(x=25, y=130, width=150, height=40)

        # Botón Totales
        self.btn_totales = tk.Button(
            lf_opciones,
            text="  Totales",
            image=img_total,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.abrir_totales_inventario,
            padx=10,
            anchor="w"
        )
        self.btn_totales.image = img_total
        self.btn_totales.place(x=25, y=185, width=150, height=40)

        # --- LabelFrame Productos ---
        lf_productos = tk.LabelFrame(
            self,
            text="Productos",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        lf_productos.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)

        lf_productos.grid_rowconfigure(0, weight=1)
        lf_productos.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            lf_productos,
            bg="#E6D9E3",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Scrollbar vertical
        self.scrollbar_v = ttk.Scrollbar(lf_productos, orient="vertical", command=self.canvas.yview)
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar_v.set)

        self.frame_contenedor = tk.Frame(self.canvas, bg="#E6D9E3")
        self.canvas.create_window((0, 0), window=self.frame_contenedor, anchor="nw")

        self.frame_contenedor.bind("<Configure>", self._on_frame_configure)

        # Scroll con la rueda (solo vertical)
        self.canvas.bind("<Enter>", self._activar_scroll_canvas)
        self.canvas.bind("<Leave>", self._desactivar_scroll_canvas)
        self.frame_contenedor.bind("<Enter>", self._activar_scroll_canvas)
        self.frame_contenedor.bind("<Leave>", self._desactivar_scroll_canvas)

        # Frame para controles de paginación
        self.frame_paginacion = tk.Frame(lf_productos, bg="#E6D9E3")
        self.frame_paginacion.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    # ----------------------------------------------------------------------
    # Métodos de visualización y paginación bajo demanda
    # ----------------------------------------------------------------------
    def cargar_productos(self):
        """Reinicia la vista: sin filtro, página 1."""
        self.filtro_actual = ""
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()

    def _actualizar_totales(self):
        """Actualiza el número total de páginas según el filtro actual."""
        total_productos = InventarioServicio.contar_productos(self.filtro_actual)
        self.total_paginas = max(1, (total_productos + self.productos_por_pagina - 1) // self.productos_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

    def _cargar_pagina(self):
        """Obtiene los productos de la página actual desde la BD y los muestra."""
        offset = (self.pagina_actual - 1) * self.productos_por_pagina
        productos = InventarioServicio.obtener_productos_paginado(
            offset=offset,
            limit=self.productos_por_pagina,
            filtro=self.filtro_actual
        )
        self._renderizar_productos(productos)
        self._actualizar_etiqueta_paginacion()

    def _renderizar_productos(self, productos):
        """Muestra la lista de productos en el canvas."""
        for widget in self.frame_contenedor.winfo_children():
            widget.destroy()

        for idx, producto in enumerate(productos):
            row = idx // 4
            col = idx % 4
            self.mostrar_producto(
                id_producto=producto["id_producto"],
                producto=producto["producto"],
                precio=producto["precio"],
                imagen_path=producto["imagen"],
                costo=producto["costo"],
                stock=producto["stock"],
                estado="Disponible" if producto["estado"] == 1 else "Agotado",
                row=row,
                col=col
            )
        self.canvas.yview_moveto(0)

    def _actualizar_etiqueta_paginacion(self):
        """Actualiza el texto de la etiqueta de paginación."""
        if hasattr(self, 'label_paginacion') and self.label_paginacion:
            total_productos = InventarioServicio.contar_productos(self.filtro_actual)
            self.label_paginacion.config(
                text=f"Página {self.pagina_actual} de {self.total_paginas} ({total_productos} productos)"
            )

    # ----------------------------------------------------------------------
    # Paginación (botones)
    # ----------------------------------------------------------------------
    def crear_controles_paginacion(self):
        for widget in self.frame_paginacion.winfo_children():
            widget.destroy()

        btn_anterior = tk.Button(
            self.frame_paginacion,
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
            self.frame_paginacion,
            text="",
            font=("Helvetica", 10, "bold"),
            bg="#E6D9E3"
        )
        self.label_paginacion.pack(side="left", padx=20, expand=True)

        btn_siguiente = tk.Button(
            self.frame_paginacion,
            text="Siguiente ▶",
            command=self.pagina_siguiente,
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            font=("Helvetica", 10, "bold")
        )
        btn_siguiente.pack(side="right", padx=5)

        self._actualizar_etiqueta_paginacion()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._cargar_pagina()

    # ----------------------------------------------------------------------
    # Filtros y búsqueda
    # ----------------------------------------------------------------------
    def actualizar_combobox_productos(self):
        nombres = InventarioServicio.obtener_nombres_para_combobox()
        self.entry_buscar["values"] = nombres

    def filtrar_productos_combobox(self, event=None):
        texto = self.entry_buscar.get().strip()
        self.filtro_actual = texto
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()

    def seleccionar_producto_entry(self, event=None):
        nombre = self.entry_buscar.get().strip()
        if not nombre:
            self.filtro_actual = ""
        else:
            # Buscar coincidencia exacta para determinar si se debe filtrar exactamente
            todos = InventarioServicio.obtener_todos_productos()
            exactos = [p for p in todos if p["producto"].lower() == nombre.lower()]
            if exactos:
                self.filtro_actual = nombre  # filtro por nombre exacto
            else:
                self.filtro_actual = nombre  # filtro parcial
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()

        # Si la búsqueda exacta devuelve un único producto, intentar seleccionarlo visualmente
        if exactos and len(exactos) == 1:
            self._seleccionar_producto_por_nombre(exactos[0]["producto"])

    def _seleccionar_producto_por_nombre(self, nombre):
        """Busca en el canvas el frame del producto con el nombre dado y lo selecciona."""
        for frame in self.frame_contenedor.winfo_children():
            data = getattr(frame, "producto_data", None)
            if data and data["producto"] == nombre:
                self.mostrar_seleccion(data, frame)
                self.canvas.yview_moveto(frame.winfo_y() / max(1, self.frame_contenedor.winfo_height()))
                break

    # ----------------------------------------------------------------------
    # Mostrar producto y selección
    # ----------------------------------------------------------------------
    def mostrar_producto(self, id_producto, producto, precio, imagen_path, costo=None, stock=None, estado=None, row=0, col=0):
        ancho_producto = 220
        alto_producto = 240
        separacion_x = 8
        separacion_y = 8
        max_image_size = 150

        frame_producto = tk.Frame(
            self.frame_contenedor,
            bg="white",
            width=ancho_producto,
            height=alto_producto,
            bd=1,
            relief="solid",
            highlightbackground="#DADADA",
            highlightthickness=1
        )
        frame_producto.grid(row=row, column=col, padx=separacion_x, pady=separacion_y, sticky="nsew")
        frame_producto.grid_propagate(False)
        frame_producto.producto_data = {
            "id_producto": id_producto,
            "producto": producto,
            "precio": precio,
            "costo": costo,
            "stock": stock,
            "estado": estado,
            "imagen": imagen_path,
        }

        # Imagen
        try:
            imagen = Image.open(
                rutas(imagen_path) if not os.path.isabs(imagen_path) else imagen_path
            )
            imagen.thumbnail((max_image_size, max_image_size), Image.LANCZOS)
            imagen_tk = ImageTk.PhotoImage(imagen)
            img_label = tk.Label(frame_producto, image=imagen_tk, bg="white")
            img_label.image = imagen_tk
            img_label.pack(fill="x", pady=(10, 6))

            img_label.bind(
                "<Button-1>",
                lambda e, data=frame_producto.producto_data, f=frame_producto: self.mostrar_seleccion(data, f),
            )
            img_label.bind(
                "<Double-Button-1>",
                lambda e, data=frame_producto.producto_data, f=frame_producto: self.tl_editar(data, f),
            )
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
            img_label = tk.Label(frame_producto, text="Sin imagen", bg="white")
            img_label.pack(pady=(3, 2))

        frame_producto.bind(
            "<Button-1>",
            lambda e, data=frame_producto.producto_data, f=frame_producto: self.mostrar_seleccion(data, f),
        )
        frame_producto.bind(
            "<Double-Button-1>",
            lambda e, data=frame_producto.producto_data, f=frame_producto: self.tl_editar(data, f),
        )

        tk.Label(
            frame_producto,
            text=producto,
            font=("Helvetica", 12, "bold"),
            bg="white",
            anchor="center",
            wraplength=200,
            justify="center"
        ).pack(fill="both", expand=True, padx=6, pady=(4, 2))

        tk.Label(
            frame_producto,
            text=peso_colombiano(precio),
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg="#1B5E20",
            anchor="w"
        ).pack(fill="x", padx=6, pady=(0, 6))

    def mostrar_seleccion(self, data, frame=None):
        if (self.producto_seleccionado_frame and
                self.producto_seleccionado_frame.winfo_exists()):
            self.producto_seleccionado_frame.config(
                highlightbackground="white",
                highlightcolor="white",
                highlightthickness=0,
                bd=1,
                relief="solid"
            )
        self.producto_seleccionado_frame = None

        if frame:
            frame.config(
                highlightbackground="#2196F3",
                highlightcolor="#2196F3",
                highlightthickness=3,
                bd=1,
                relief="solid"
            )
            self.producto_seleccionado_frame = frame
            # Usar directamente el id_producto del frame
            self.producto_seleccionado_id = data.get("id_producto")

        self.seleccion_vars["producto"].set(data["producto"])
        self.seleccion_vars["precio"].set(peso_colombiano(data["precio"]))
        self.seleccion_vars["costo"].set(peso_colombiano(data["costo"]))
        self.seleccion_vars["stock"].set(str(data["stock"]))
        self.seleccion_vars["estado"].set(data["estado"])

        if self.estado_label:
            if data["estado"] == "Disponible":
                self.estado_label.config(fg="green")
            elif data["estado"] == "Agotado":
                self.estado_label.config(fg="red")
            else:
                self.estado_label.config(fg="black")

    # ----------------------------------------------------------------------
    # CRUD
    # ----------------------------------------------------------------------
    def agregar_producto(self):
        self._abrir_dialogo_producto()

    def _abrir_dialogo_producto(self, editar=False, datos=None):
        top = tk.Toplevel(self)
        top.title("Agregar Producto" if not editar else "Editar Producto")
        top.geometry("700x400+300+100")
        top.configure(bg="#E6D9E3")
        top.resizable(False, False)
        top.maxsize(700, 400)
        top.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        top.focus_force()
        top.bind("<Return>", lambda e: self._guardar_producto_desde_dialogo())
        top.bind("<Escape>", lambda e: self.cerrar_ventana())

        self.top = top
        self.top.editing = editar
        self.top.datos_originales = datos

        frame_principal = tk.Frame(top, bg="#E6D9E3")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        def validar_entero(valor):
            return valor == "" or (valor.isdigit() and int(valor) > 0)
        vcmd_entero = (self.register(validar_entero), "%P")

        frame_campos = tk.Frame(frame_principal, bg="#E6D9E3")
        frame_campos.place(x=0, y=10, width=280, height=300)

        # Botones
        lf_botones = tk.LabelFrame(frame_principal, text="Opciones", font=("Helvetica", 12, "bold"), bg="#E6D9E3")
        lf_botones.place(x=0, y=290, width=270, height=60)

        btn_guardar = tk.Button(lf_botones, text="Guardar", font=("Helvetica", 12, "bold"),
                                bg="#4CAF50", fg="white", command=self._guardar_producto_desde_dialogo)
        btn_guardar.place(x=10, y=0)

        btn_cancelar = tk.Button(lf_botones, text="Cancelar", font=("Helvetica", 12, "bold"),
                                 bg="#f44336", fg="white", command=self.cerrar_ventana)
        btn_cancelar.place(x=140, y=0)

        # Imagen
        self.frame_img = tk.Frame(frame_principal, bg="white", width=300, height=300)
        self.frame_img.place(x=300, y=10)

        # Cargar imagen por defecto o existente
        default_image_path = rutas(os.path.join("fotos", "default.png"))
        try:
            if editar and datos and datos.get("imagen"):
                img_path = datos["imagen"]
                if not os.path.isabs(img_path):
                    img_path = rutas(img_path)
                default_image = Image.open(img_path)
            else:
                default_image = Image.open(default_image_path)
            default_image = default_image.resize((300, 300), Image.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(default_image)
            img_label = tk.Label(self.frame_img, image=self.image_tk, bg="white")
            img_label.pack(fill="both", expand=True)
            self.image_path = default_image_path if not editar else datos["imagen"]
        except Exception as e:
            print(f"Error al cargar imagen por defecto: {e}")

        btn_cargar_imagen = tk.Button(frame_principal, text="Cargar Imágen", font=("Helvetica", 11, "bold"),
                                      bg="#2196F3", fg="white", command=self.cargar_imagen)
        btn_cargar_imagen.place(x=370, y=320)

        # Campos
        tk.Label(frame_campos, text="Producto", font=("Helvetica", 12, "bold"), bg="#E6D9E3").pack(anchor="w")
        self.entry_producto = tk.Entry(frame_campos, font=("Helvetica", 12))
        self.entry_producto.pack(fill="x", pady=(0, 10))
        if editar:
            self.entry_producto.insert(0, datos["producto"])

        tk.Label(frame_campos, text="Precio", font=("Helvetica", 12, "bold"), bg="#E6D9E3").pack(anchor="w")
        self.entry_precio = tk.Entry(frame_campos, font=("Helvetica", 12), validate="key", validatecommand=vcmd_entero)
        self.entry_precio.pack(fill="x", pady=(0, 10))
        if editar:
            self.entry_precio.insert(0, str(int(datos["precio"])))

        tk.Label(frame_campos, text="Costo", font=("Helvetica", 12, "bold"), bg="#E6D9E3").pack(anchor="w")
        self.entry_costo = tk.Entry(frame_campos, font=("Helvetica", 12), validate="key", validatecommand=vcmd_entero)
        self.entry_costo.pack(fill="x", pady=(0, 10))
        if editar:
            self.entry_costo.insert(0, str(int(datos["costo"])))

        tk.Label(frame_campos, text="Stock", font=("Helvetica", 12, "bold"), bg="#E6D9E3").pack(anchor="w")
        self.entry_stock = tk.Entry(frame_campos, font=("Helvetica", 12), validate="key", validatecommand=vcmd_entero)
        self.entry_stock.pack(fill="x", pady=(0, 10))
        if editar:
            self.entry_stock.insert(0, str(datos["stock"]))

        tk.Label(frame_campos, text="Estado", font=("Helvetica", 12, "bold"), bg="#E6D9E3").pack(anchor="w")
        self.entry_estado = ttk.Combobox(frame_campos, font=("Helvetica", 12), values=["Disponible", "Agotado"],
                                         state="readonly")
        self.entry_estado.pack(fill="x", pady=(0, 10))
        if editar:
            self.entry_estado.set(datos["estado"])
        else:
            self.entry_estado.set("Disponible")
        self.entry_estado.config(state="disabled")

    def _guardar_producto_desde_dialogo(self):
        try:
            producto = self.entry_producto.get().strip()
            precio_str = self.entry_precio.get().strip()
            costo_str = self.entry_costo.get().strip()
            stock_str = self.entry_stock.get().strip()

            if not all([producto, precio_str, costo_str, stock_str]):
                messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self.top)
                return

            if not (precio_str.isdigit() and int(precio_str) > 0):
                messagebox.showerror("Error", "El precio debe ser un número entero positivo", parent=self.top)
                return
            if not (costo_str.isdigit() and int(costo_str) > 0):
                messagebox.showerror("Error", "El costo debe ser un número entero positivo", parent=self.top)
                return
            if not (stock_str.isdigit() and int(stock_str) > 0):
                messagebox.showerror("Error", "El stock debe ser un número entero positivo", parent=self.top)
                return

            precio = int(precio_str)
            costo = int(costo_str)
            stock = int(stock_str)
            imagen = self.image_path if hasattr(self, "image_path") else None

            if self.top.editing:
                exito, mensaje = InventarioServicio.actualizar_producto(
                    id_producto=self.top.datos_originales["id_producto"],
                    producto=producto,
                    precio=precio,
                    costo=costo,
                    stock=stock,
                    imagen=imagen,
                    parent=self.top
                )
            else:
                exito, mensaje = InventarioServicio.agregar_producto(
                    producto, precio, costo, stock, imagen, parent=self.top
                )

            if exito:
                self.cargar_productos()
                self.actualizar_combobox_productos()
                self._actualizar_otras_vistas()
                messagebox.showinfo("Éxito", mensaje, parent=self.top)
                self.cerrar_ventana()
            else:
                messagebox.showerror("Error", mensaje, parent=self.top)
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}", parent=self.top)

    def tl_editar(self, data, frame):
        self._abrir_dialogo_producto(editar=True, datos=data)

    def eliminar_producto_seleccionado(self):
        if not self.producto_seleccionado_id:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return

        producto = self.seleccion_vars["producto"].get()
        if not producto:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar '{producto}'?"):
            exito, mensaje = InventarioServicio.eliminar_producto(self.producto_seleccionado_id)
            if exito:
                self.cargar_productos()
                self.actualizar_combobox_productos()
                self._actualizar_otras_vistas()
                for var in self.seleccion_vars.values():
                    var.set("")
                self.producto_seleccionado_id = None
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)

    def cargar_imagen(self):
        try:
            dialog = tk.Toplevel(self)
            dialog.withdraw()
            file_path = filedialog.askopenfilename(
                parent=dialog,
                initialdir=self.ultimo_directorio,
                title="Seleccionar imagen",
                filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
            )
            dialog.destroy()
            if file_path:
                self.ultimo_directorio = os.path.dirname(file_path)
                image = Image.open(file_path)
                image = image.resize((300, 300), Image.LANCZOS)

                image_name = os.path.basename(file_path)
                image_save_path = os.path.join(self.img_folder, image_name)
                image.save(image_save_path)

                self.image_tk = ImageTk.PhotoImage(image)
                for widget in self.frame_img.winfo_children():
                    widget.destroy()
                img_label = tk.Label(self.frame_img, image=self.image_tk, bg="white")
                img_label.pack(fill="both", expand=True)
                self.image_path = image_save_path
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar imagen: {e}", parent=self.top)

    def cerrar_ventana(self):
        if hasattr(self, 'top') and self.top and self.top.winfo_exists():
            self.top.destroy()
        self.top = None

    # ----------------------------------------------------------------------
    # Actualizar otras vistas
    # ----------------------------------------------------------------------
    def _actualizar_otras_vistas(self):
        parent = self.master
        while parent:
            if hasattr(parent, "frames"):
                for frame in parent.frames.values():
                    if hasattr(frame, "actualizar_canvas_productos"):
                        frame.actualizar_canvas_productos()
            if hasattr(parent, "ventas_view"):
                parent.ventas_view.actualizar_canvas_productos()
            if hasattr(parent, "deudas_view"):
                parent.deudas_view.actualizar_canvas_productos()
            parent = getattr(parent, "master", None)

    # ----------------------------------------------------------------------
    # Scroll del canvas (solo vertical)
    # ----------------------------------------------------------------------
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _activar_scroll_canvas(self, event=None):
        self.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _desactivar_scroll_canvas(self, event=None):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel_windows(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget:
            current = widget
            while current:
                if current == self.canvas or current == self.frame_contenedor:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    break
                current = current.master if hasattr(current, 'master') else None

    def _on_mousewheel_linux(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget:
            current = widget
            while current:
                if current == self.canvas or current == self.frame_contenedor:
                    if event.num == 4:
                        self.canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.canvas.yview_scroll(1, "units")
                    break
                current = current.master if hasattr(current, 'master') else None

    # ----------------------------------------------------------------------
    # Métodos para historial y totales
    # ----------------------------------------------------------------------
    def abrir_historial_inventario(self):
        from retail.inventario.historial_inventario import mostrar_historial_inventario
        mostrar_historial_inventario(self)

    def abrir_totales_inventario(self):
        from retail.inventario.totales import mostrar_totales_inventario
        mostrar_totales_inventario(self)