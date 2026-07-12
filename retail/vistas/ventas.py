import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from retail.nucleo.servicios.ventas.servicio_ventas import VentasServicio
from retail.nucleo.configuraciones import PRODUCTOS_POR_PAGINA
from retail.utilidades.paginacion import PaginacionWidget
from retail.utilidades.producto_card import crear_producto_card


class Ventas(tk.Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre, bg="#E6D9E3")
        self.controlador = controlador
        self.producto_seleccionado_frame = None
        self.carrito = []
        self.productos_cache = []           # lista de diccionarios de productos (para referencia, no se usa en paginación)
        self.cliente_id_seleccionado = None
        self.tipo_venta_actual = "rapida"   # "rapida" o "mayorista"

        # Variables para paginación bajo demanda
        self.pagina_actual = 1
        self.productos_por_pagina = PRODUCTOS_POR_PAGINA
        self.total_paginas = 1
        self.filtro_actual = ""             # Texto de búsqueda actual

        self.widgets()
        self.actualizar_combobox_clientes()
        self.actualizar_combobox_productos()
        self.entry_stock.bind("<KeyRelease>", self.filtrar_productos_combobox)
        self.entry_stock.bind("<Return>", self.seleccionar_producto_entry)
        self.entry_cliente.bind("<KeyRelease>", self._on_cliente_entrada)
        self.entry_cliente.bind("<<ComboboxSelected>>", self._on_cliente_seleccionado)
        self.entry_cliente.bind("<Return>", self._on_cliente_seleccionado)

    def widgets(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Título Principal
        label_titulo = tk.Label(
            self,
            text="Ventas",
            font=("Helvetica", 15, "bold"),
            bg="#4CAF50",
            fg="#0A0A0A",
        )
        label_titulo.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Canvas para productos con scrollbar vertical solamente
        frame_canvas = tk.LabelFrame(
            self,
            text="Productos",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        frame_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            frame_canvas,
            bg="#E6D9E3",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar vertical (sin horizontal)
        self.scrollbar_v = ttk.Scrollbar(
            frame_canvas, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")

        # Configurar canvas solo con scroll vertical
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set)

        self.frame_contenedor = tk.Frame(self.canvas, bg="#E6D9E3")
        self.frame_window = self.canvas.create_window((0, 0), window=self.frame_contenedor, anchor="nw")

        self.frame_contenedor.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.frame_window, width=e.width))
        self.canvas.bind("<Enter>", lambda event: self._activar_scroll_canvas())
        self.canvas.bind("<Leave>", lambda event: self._desactivar_scroll_canvas())

        # Frame para controles de paginación
        self.frame_paginacion = tk.Frame(frame_canvas, bg="#E6D9E3")
        self.frame_paginacion.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.cargar_productos()  # carga la primera página
        self.crear_controles_paginacion()

        # Label Frame Detalles de Venta
        frame_detalles = tk.LabelFrame(
            self,
            text="Detalles de Venta",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        frame_detalles.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)
        frame_detalles.grid_rowconfigure(0, weight=0)
        frame_detalles.grid_rowconfigure(1, weight=1)


        # Producto
        label_stock = tk.Label(
            frame_detalles,
            text="Producto",
            font=("Calibri", 14, "bold"),
            bg="#E6D9E3",
            fg="#333333",
            anchor="w",
        )
        label_stock.pack(fill="x", padx=10)
        self.entry_stock = ttk.Combobox(
            frame_detalles,
            font=("Calibri", 14),
            foreground="#333333",
        )
        self.entry_stock.pack(fill="x", padx=10, pady=(0, 20), ipady=4)

        # Cliente
        label_cliente = tk.Label(
            frame_detalles,
            text="Cliente",
            font=("Calibri", 14, "bold"),
            bg="#E6D9E3",
            fg="#333333",
            anchor="w",
        )
        label_cliente.pack(fill="x", padx=10)

        self.entry_cliente = ttk.Combobox(
            frame_detalles,
            font=("Calibri", 14),
            foreground="#333333",
            state="normal",
        )
        self.entry_cliente.pack(fill="x", padx=10, pady=(0, 20), ipady=4)
        self.entry_cliente.bind("<<ComboboxSelected>>", self._on_cliente_seleccionado)

        # Cargar imágenes para los botones
        def cargar_img(nombre, size=(30, 30)):
            ruta = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "img", nombre))
            try:
                return ImageTk.PhotoImage(Image.open(ruta).resize(size))
            except Exception:
                return None

        self.img_carrito = cargar_img("carrito.png")
        self.img_confirm = cargar_img("confirm.png")
        self.img_facturas = cargar_img("facturas.png")
        self.img_ganancias = cargar_img("ganancias.png")

        # Botón Carrito
        self.btn_carrito = tk.Button(
            frame_detalles,
            text="CARRITO",
            image=self.img_carrito,
            compound="left",
            font=("Helvetica", 13, "bold"),
            bg="#BDFF07",
            fg="#000000",
            command=lambda: self.controlador.abrir_carrito_venta(self),
            relief="ridge",
            bd=3,
            cursor="hand2",
            padx=10,
            anchor="w",
            height=30,
            width=150
        )
        self.btn_carrito.pack(fill="x", padx=10, pady=(0, 20), ipady=4, ipadx=4)

        # Total (visual)
        self.var_total_carrito = tk.StringVar(value="$0")
        lf_total_detalles = tk.LabelFrame(
            frame_detalles,
            text="Total Carrito",
            font=("Helvetica", 11, "bold"),
            bg="#E6E5D9",
        )
        lf_total_detalles.pack(fill="x", padx=10, pady=(0, 0))
        lbl_total_det = tk.Label(
            lf_total_detalles,
            textvariable=self.var_total_carrito,
            font=("Helvetica", 16, "bold"),
            bg="#E6D9E3",
            fg="#0B6623",
        )
        lbl_total_det.pack(expand=True, fill="both", pady=6)

        # Opciones
        frame_opciones = tk.LabelFrame(
            frame_detalles,
            text="Opciones",
            font=("Helvetica", 12, "bold"),
            bg="#E6D9E3",
        )
        frame_opciones.pack(fill="x", padx=10, pady=(20, 10))

        self.btn_facturas = tk.Button(
            frame_opciones,
            text="FACTURAS",
            image=self.img_facturas,
            compound="left" if self.img_facturas else None,
            font=("Helvetica", 13, "bold"),
            bg="#4CAF50",
            fg="#000000",
            command=lambda: self.controlador.abrir_facturas_ventas(self),
            relief="ridge",
            bd=3,
            cursor="hand2",
            padx=10,
            anchor="w",
            height=30,
            width=150
        )
        self.btn_facturas.pack(fill="x", padx=10, pady=10, ipady=2, ipadx=4)

        self.btn_ganancias = tk.Button(
            frame_opciones,
            text="GANANCIAS",
            image=self.img_ganancias,
            compound="left" if self.img_ganancias else None,
            font=("Helvetica", 13, "bold"),
            bg="#855000",
            fg="#000000",
            command=lambda: self.controlador.abrir_ganancias(self),
            relief="ridge",
            bd=3,
            cursor="hand2",
            padx=10,
            anchor="w",
            height=30,
            width=150
        )
        self.btn_ganancias.pack(fill="x", padx=10, pady=10, ipady=2, ipadx=4)

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
        total_productos = VentasServicio.contar_productos(self.filtro_actual)
        self.total_paginas = max(1, (total_productos + self.productos_por_pagina - 1) // self.productos_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

    def _cargar_pagina(self):
        """Obtiene los productos de la página actual desde la BD y los muestra."""
        offset = (self.pagina_actual - 1) * self.productos_por_pagina
        productos = VentasServicio.obtener_productos_paginado(
            offset=offset,
            limit=self.productos_por_pagina,
            filtro=self.filtro_actual
        )
        self._renderizar_productos(productos)
        self._actualizar_etiqueta_paginacion()

    def _actualizar_etiqueta_paginacion(self):
        if hasattr(self, 'paginacion'):
            self.paginacion.actualizar()

    def _renderizar_productos(self, productos):
        for widget in self.frame_contenedor.winfo_children():
            widget.destroy()
        for idx, producto in enumerate(productos):
            row = idx // 3
            col = idx % 3
            crear_producto_card(
                self.frame_contenedor, producto, row, col,
                on_select=lambda f, s=self: s._seleccionar_producto_canvas(f),
                on_double_click=lambda d, f, s=self: s._solicitar_cantidad_producto(d, f),
            )
        self.canvas.yview_moveto(0)

    def _texto_paginacion(self):
        total = VentasServicio.contar_productos(self.filtro_actual)
        return f"Página {self.pagina_actual} de {self.total_paginas} ({total} productos)"

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

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._cargar_pagina()

    # ----------------------------------------------------------------------
    # Filtros y búsqueda (actualizados para usar paginación)
    # ----------------------------------------------------------------------
    def actualizar_combobox_productos(self):
        """Actualiza el combobox con los nombres de productos (todos) para autocompletado."""
        nombres = VentasServicio.obtener_nombres_productos_para_busqueda()
        self.entry_stock["values"] = nombres

    def filtrar_productos_combobox(self, event=None):
        texto = self.entry_stock.get().strip()
        self.filtro_actual = texto
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()
        # Actualizar combobox con nombres filtrados (para sugerencias)
        nombres_filtrados = VentasServicio.obtener_nombres_productos_para_busqueda(texto)
        self.entry_stock["values"] = nombres_filtrados

    def seleccionar_producto_entry(self, event=None):
        nombre = self.entry_stock.get().strip()
        if not nombre:
            self.filtro_actual = ""
        else:
            # Buscar coincidencia exacta para determinar si se debe filtrar exactamente
            todos_nombres = VentasServicio.obtener_nombres_productos_para_busqueda()
            exactos = [n for n in todos_nombres if n.lower() == nombre.lower()]
            if exactos:
                self.filtro_actual = nombre  # filtro por nombre exacto
            else:
                self.filtro_actual = nombre  # filtro parcial
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()
        # Actualizar combobox con nombres filtrados
        nombres_filtrados = VentasServicio.obtener_nombres_productos_para_busqueda(self.filtro_actual)
        self.entry_stock["values"] = nombres_filtrados

        # Si la búsqueda exacta devuelve un único producto, intentar seleccionarlo visualmente
        if exactos and len(exactos) == 1:
            self._seleccionar_producto_por_nombre(exactos[0])

    def _seleccionar_producto_por_nombre(self, nombre):
        """Busca en el canvas el frame del producto con el nombre dado y lo selecciona."""
        for frame in self.frame_contenedor.winfo_children():
            data = getattr(frame, "producto_data", None)
            if data and data["producto"] == nombre:
                self._seleccionar_producto_canvas(frame)
                self.canvas.yview_moveto(frame.winfo_y() / max(1, self.frame_contenedor.winfo_height()))
                break

    # ----------------------------------------------------------------------
    # Selección y cantidad
    # ----------------------------------------------------------------------
    def _seleccionar_producto_canvas(self, frame):
        if (hasattr(self, "producto_seleccionado_frame") and
                self.producto_seleccionado_frame and
                self.producto_seleccionado_frame.winfo_exists()):
            self.producto_seleccionado_frame.config(
                highlightbackground="#BDBDBD",
                highlightcolor="#BDBDBD",
                highlightthickness=1,
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

    def _solicitar_cantidad_producto(self, data, frame):
        """
        Abre ventana para solicitar cantidad del producto.
        """
        self._seleccionar_producto_canvas(frame)

        id_producto = data["id_producto"]
        # Obtener stock actualizado
        stock_actual = VentasServicio.obtener_stock_actual(id_producto)
        if stock_actual is None:
            messagebox.showerror("Error", "No se pudo obtener el stock actual del producto.", parent=self)
            return

        # Calcular stock real disponible (restando lo ya en carrito)
        cantidad_en_carrito = sum(
            item["cantidad"] for item in self.carrito
            if item["id_producto"] == id_producto
        )
        stock_real_disponible = stock_actual - cantidad_en_carrito

        # Determinar el cliente a usar
        cliente_carrito = ""
        es_venta_mayor = self.tipo_venta_actual == "mayorista"

        if es_venta_mayor and self.cliente_id_seleccionado:
            cliente_nombre = VentasServicio.obtener_nombre_cliente_por_id(self.cliente_id_seleccionado)
            if cliente_nombre:
                cliente_carrito = cliente_nombre

        # Verificar duplicado
        producto_en_carrito = any(
            item["producto"] == data["producto"] and item["cliente"] == cliente_carrito
            for item in self.carrito
        )
        if producto_en_carrito:
            messagebox.showinfo(
                "Producto ya agregado",
                f"El producto '{data['producto']}' ya ha sido agregado al carrito.\n"
                "Si desea modificar la cantidad, hágalo desde el carrito.\n"
                "Si lo elimina del carrito, podrá volver a agregarlo.",
                parent=self,
            )
            return

        if stock_real_disponible <= 0:
            messagebox.showwarning(
                "Producto agotado o sin stock disponible",
                f"El producto '{data['producto']}' no tiene stock disponible.\n"
                f"Stock en inventario: {stock_actual} | En carrito: {cantidad_en_carrito}\n"
                "Debe solicitar un pedido y actualizar el stock desde la sección de Inventario.",
                parent=self,
            )
            self.actualizar_canvas_productos()
            return

        # Crear ventana de diálogo
        top = tk.Toplevel(self)
        top.title(f"Agregar {data['producto']}")
        top.geometry("340x210+400+200")
        top.configure(bg="#E6D9E3")
        top.resizable(False, False)
        top.maxsize(340, 210)
        try:
            top.transient(self)
        except Exception:
            pass
        try:
            top.attributes("-topmost", True)
        except Exception:
            pass

        def set_grab():
            try:
                top.grab_set()
                top.focus_force()
            except tk.TclError:
                pass

        top.after(1, set_grab)
        top.bind("<Escape>", lambda e: top.destroy())

        frame_main = tk.Frame(top, bg="#E6D9E3")
        frame_main.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame_main,
            text=f"{data['producto']}",
            font=("Helvetica", 14, "bold"),
            bg="#E6D9E3",
            fg="#1a1a1a",
        ).pack(pady=(0, 15))

        tk.Label(
            frame_main,
            text=f"Stock Disponible: {stock_real_disponible}",
            font=("Helvetica", 15),
            bg="#E6D9E3",
            fg="#004203",
        ).pack(pady=(0, 20))

        frame_cantidad = tk.Frame(frame_main, bg="#E6D9E3")
        frame_cantidad.pack(pady=(0, 25))
        tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg="#E6D9E3",
        ).pack(side="left", padx=(0, 10))

        def validar_entero(valor):
            return valor == "" or (valor.isdigit() and int(valor) > 0)

        vcmd_entero = (self.register(validar_entero), "%P")
        entry_cantidad = tk.Entry(
            frame_cantidad,
            font=("Helvetica", 12),
            width=8,
            validate="key",
            validatecommand=vcmd_entero
        )
        entry_cantidad.pack(side="left")
        top.after(50, entry_cantidad.focus)

        frame_botones = tk.Frame(frame_main, bg="#E6D9E3")
        frame_botones.pack(pady=(0, 0))

        def agregar():
            try:
                cantidad = int(entry_cantidad.get())
                if cantidad <= 0:
                    messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad mayor a cero.", parent=top)
                    return

                # Validar stock actualizado (por si hubo cambios)
                stock_inventario_actual = VentasServicio.obtener_stock_actual(id_producto)
                if stock_inventario_actual is None:
                    messagebox.showerror("Error", "No se pudo obtener el stock actual del producto.", parent=top)
                    return

                cantidad_en_carrito_ahora = sum(
                    item["cantidad"] for item in self.carrito
                    if item["id_producto"] == id_producto
                )
                stock_real_ahora = stock_inventario_actual - cantidad_en_carrito_ahora

                if cantidad > stock_real_ahora:
                    messagebox.showwarning(
                        "Stock insuficiente",
                        f"Stock disponible para agregar: {stock_real_ahora} unidades\n"
                        f"(Stock inventario: {stock_inventario_actual} - Ya en carrito: {cantidad_en_carrito_ahora})\n\n"
                        f"Solicita: {cantidad} unidades.",
                        parent=top,
                    )
                    return

                # Agregar al carrito
                nuevo_item = {
                    "cliente": cliente_carrito,
                    "cliente_id": self.cliente_id_seleccionado,
                    "producto": data["producto"],
                    "id_producto": id_producto,
                    "cantidad": cantidad,
                    "precio": data["precio"],
                    "subtotal": cantidad * data["precio"],
                }
                self.carrito.append(nuevo_item)

                self.actualizar_total_carrito_display()
                top.destroy()
            except ValueError:
                messagebox.showwarning("Cantidad inválida", "Ingrese un número válido.", parent=top)

        entry_cantidad.bind("<Return>", lambda e: agregar())

        btn_agregar = tk.Button(
            frame_botones,
            text="Agregar",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=agregar,
            width=10,
        )
        btn_agregar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(
            frame_botones,
            text="Cancelar",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="white",
            command=top.destroy,
            width=10,
        )
        btn_cancelar.pack(side="left", padx=10)

    # ----------------------------------------------------------------------
    # Clientes
    # ----------------------------------------------------------------------
    def actualizar_combobox_clientes(self, event=None):
        """Actualiza el combobox de clientes con la lista de nombres."""
        nombres, _ = VentasServicio.obtener_clientes_formateados()
        self.entry_cliente["values"] = nombres

    def _validar_y_actualizar_tipo_venta(self, nuevo_tipo_venta):
        """Cambia el tipo de venta, limpiando el carrito si es necesario."""
        if nuevo_tipo_venta == self.tipo_venta_actual:
            return
        if not self.carrito:
            self.tipo_venta_actual = nuevo_tipo_venta
            return

        messagebox.showwarning(
            "Cambio de tipo de venta",
            "El carrito contiene productos y será limpiado.",
            parent=self
        )
        self.carrito.clear()
        self.tipo_venta_actual = nuevo_tipo_venta
        self.actualizar_total_carrito_display()

    def _on_cliente_entrada(self, event=None):
        texto = self.entry_cliente.get().strip()
        if not texto:
            self.cliente_id_seleccionado = None
            self._validar_y_actualizar_tipo_venta("rapida")
            nombres, _ = VentasServicio.obtener_clientes_formateados()
            self.entry_cliente["values"] = nombres
        else:
            clientes_filtrados = VentasServicio.filtrar_clientes_por_texto(texto)
            self.entry_cliente["values"] = [c["nombre_completo"] for c in clientes_filtrados]
            for c in clientes_filtrados:
                if c["nombre_completo"].lower() == texto.lower():
                    self.cliente_id_seleccionado = c["id_cliente"]
                    self._validar_y_actualizar_tipo_venta("mayorista")
                    break

    def _on_cliente_seleccionado(self, event=None):
        seleccion = self.entry_cliente.get().strip()
        cliente = VentasServicio.obtener_cliente_por_nombre_completo(seleccion)
        if cliente:
            self.cliente_id_seleccionado = cliente["id_cliente"]
            self._validar_y_actualizar_tipo_venta("mayorista")
        else:
            self.cliente_id_seleccionado = None
            self._validar_y_actualizar_tipo_venta("rapida")

    # ----------------------------------------------------------------------
    # Total del carrito y actualización externa
    # ----------------------------------------------------------------------
    def actualizar_total_carrito_display(self):
        total = VentasServicio.calcular_total_carrito(self.carrito)
        try:
            self.var_total_carrito.set(f"${total:,.0f}".replace(",", "."))
        except Exception:
            self.var_total_carrito.set(str(total))

    def actualizar_canvas_productos(self):
        self.cargar_productos()   # recarga la primera página sin filtro

    # ----------------------------------------------------------------------
    # Scroll del canvas (solo vertical)
    # ----------------------------------------------------------------------
    def _activar_scroll_canvas(self):
        self.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        self.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _desactivar_scroll_canvas(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel_windows(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is not None:
            current = widget
            while current:
                if current == self.canvas or current == self.frame_contenedor:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    break
                current = current.master if hasattr(current, 'master') else None

    def _on_mousewheel_linux(self, event):
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is not None:
            current = widget
            while current:
                if current == self.canvas or current == self.frame_contenedor:
                    if event.num == 4:
                        self.canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.canvas.yview_scroll(1, "units")
                    break
                current = current.master if hasattr(current, 'master') else None