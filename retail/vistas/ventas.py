from __future__ import annotations

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

from retail.nucleo.servicios.ventas.servicio_ventas import VentasServicio
from retail.nucleo.configuraciones import (
    rutas,
    COLOR_FONDO,
    COLOR_FONDO_EDITAR,
    COLOR_FONDO_TABLA,
    COLOR_AZUL,
    COLOR_VERDE,
    COLOR_ROJO,
    FUENTE_ETIQUETA,
    PRODUCTOS_POR_PAGINA,
    TAMANO_VENTANA,
    crear_boton,
    BOTON_MENU,
    VENTAS_BOTON_ACCION,
    VENTAS_BOTON_EXITO,
    VENTAS_BOTON_PELIGRO,
    VENTAS_BOTON_INFO,
    VENTAS_BOTON_NEUTRO,
    VENTAS_BOTON_NAV,
    VENTAS_BOTON_ADVERTENCIA,
    VENTAS_BOTON_CARITO,
    VENTAS_BOTON_CERRAR,
    VENTAS_BOTON_IMPORTAR,
    FUENTE_BOTON,
    FUENTE_BOTON_NEGRITA,
    FUENTE_BOTON_GRANDE,
)


class Ventas(tk.Frame):
    def __init__(self, padre: Any, controlador: Any) -> None:
        super().__init__(padre, bg=COLOR_FONDO)
        self.controlador = controlador
        self.producto_seleccionado_frame = None
        self.carrito: list[dict[str, Any]] = []
        self.productos_cache: list[dict[str, Any]] = (
            []
        )  # lista de diccionarios de productos (para referencia, no se usa en paginación)
        self.cliente_id_seleccionado = None
        self.tipo_venta_actual = "rapida"  # "rapida" o "mayorista"

        # Variables para paginación bajo demanda
        self.pagina_actual = 1
        self.productos_por_pagina = PRODUCTOS_POR_PAGINA  # 4x3
        self.total_paginas = 1
        self.filtro_actual = ""  # Texto de búsqueda actual

        self.widgets()
        self.actualizar_combobox_clientes()
        self.actualizar_combobox_productos()
        self.entry_stock.bind("<KeyRelease>", self.filtrar_productos_combobox)
        self.entry_stock.bind("<Return>", self.seleccionar_producto_entry)
        self.entry_cliente.bind("<KeyRelease>", self._al_entrar_cliente)
        self.entry_cliente.bind("<<ComboboxSelected>>", self._al_seleccionar_cliente)
        self.entry_cliente.bind("<Return>", self._al_seleccionar_cliente)

    def widgets(self) -> None:
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Título Principal
        label_titulo = tk.Label(
            self,
            text="Ventas",
            font=("Helvetica", 15, "bold"),
            bg=COLOR_VERDE,
            fg="#0A0A0A",
        )
        label_titulo.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Canvas para productos con scrollbar vertical solamente
        frame_canvas = tk.LabelFrame(
            self,
            text="Productos",
            font=FUENTE_ETIQUETA,
            bg=COLOR_FONDO,
        )
        frame_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            frame_canvas, bg=COLOR_FONDO, highlightthickness=0, relief="flat"
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Scrollbar vertical (sin horizontal)
        self.scrollbar_v = ttk.Scrollbar(
            frame_canvas, orient="vertical", command=self.canvas.yview
        )
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")

        # Configurar canvas solo con scroll vertical
        self.canvas.configure(yscrollcommand=self.scrollbar_v.set)

        self.frame_contenedor = tk.Frame(self.canvas, bg=COLOR_FONDO)
        self.frame_window = self.canvas.create_window(
            (0, 0), window=self.frame_contenedor, anchor="nw"
        )

        self.frame_contenedor.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.frame_window, width=e.width),
        )
        self.canvas.bind("<Enter>", lambda event: self._activar_scroll_canvas())
        self.canvas.bind("<Leave>", lambda event: self._desactivar_scroll_canvas())

        # Frame para controles de paginación
        self.frame_paginacion = tk.Frame(frame_canvas, bg=COLOR_FONDO)
        self.frame_paginacion.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )

        self.cargar_productos()  # carga la primera página
        self.crear_controles_paginacion()

        # Label Frame Detalles de Venta
        frame_detalles = tk.LabelFrame(
            self,
            text="Detalles de Venta",
            font=FUENTE_ETIQUETA,
            bg=COLOR_FONDO,
        )
        frame_detalles.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)
        frame_detalles.grid_rowconfigure(0, weight=0)
        frame_detalles.grid_rowconfigure(1, weight=1)

        # Producto
        label_stock = tk.Label(
            frame_detalles,
            text="Producto",
            font=("Calibri", 14, "bold"),
            bg=COLOR_FONDO,
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
            bg=COLOR_FONDO,
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
        self.entry_cliente.bind("<<ComboboxSelected>>", self._al_seleccionar_cliente)

        # Cargar imágenes para los botones
        def cargar_img(nombre: str, size: tuple[int, int] = (30, 30)) -> ImageTk.PhotoImage | None:
            ruta = (Path(__file__).parent / ".." / ".." / "img" / nombre).resolve()
            try:
                return ImageTk.PhotoImage(Image.open(ruta).resize(size))
            except Exception:
                logger.error("No se pudo cargar la imagen %s", nombre)
                return None

        self.img_carrito = cargar_img("carrito.png")
        self.img_confirm = cargar_img("confirm.png")
        self.img_facturas = cargar_img("facturas.png")
        self.img_ganancias = cargar_img("ganancias.png")

        # Botón Carrito
        self.btn_carrito = crear_boton(
            frame_detalles,
            "CARRITO",
            estilo=VENTAS_BOTON_CARITO,
            image=self.img_carrito,
            compound="left",
            comando=lambda: self.controlador.abrir_carrito_venta(self),
            padx=10,
            anchor="w",
            height=30,
            width=150,
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
            bg=COLOR_FONDO,
            fg="#0B6623",
        )
        lbl_total_det.pack(expand=True, fill="both", pady=6)

        # Opciones
        frame_opciones = tk.LabelFrame(
            frame_detalles,
            text="Opciones",
            font=FUENTE_ETIQUETA,
            bg=COLOR_FONDO,
        )
        frame_opciones.pack(fill="x", padx=10, pady=(20, 10))

        self.btn_facturas = crear_boton(
            frame_opciones,
            "FACTURAS",
            estilo=VENTAS_BOTON_ACCION,
            image=self.img_facturas,
            compound="left" if self.img_facturas else None,
            comando=lambda: self.controlador.abrir_facturas_ventas(self),
            padx=10,
            anchor="w",
            height=30,
            width=150,
        )
        self.btn_facturas.pack(fill="x", padx=10, pady=10, ipady=2, ipadx=4)

        self.btn_ganancias = crear_boton(
            frame_opciones,
            "GANANCIAS",
            estilo=VENTAS_BOTON_EXITO,
            image=self.img_ganancias,
            compound="left" if self.img_ganancias else None,
            comando=lambda: self.controlador.abrir_ganancias(self),
            padx=10,
            anchor="w",
            height=30,
            width=150,
        )
        self.btn_ganancias.pack(fill="x", padx=10, pady=10, ipady=2, ipadx=4)

    # ----------------------------------------------------------------------
    # Métodos de visualización y paginación bajo demanda
    # ----------------------------------------------------------------------
    def cargar_productos(self) -> None:
        """Reinicia la vista: sin filtro, página 1."""
        self.filtro_actual = ""
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()

    def _actualizar_totales(self) -> None:
        """Actualiza el número total de páginas según el filtro actual."""
        total_productos = VentasServicio.contar_productos(self.filtro_actual)
        self.total_paginas = max(
            1,
            (total_productos + self.productos_por_pagina - 1)
            // self.productos_por_pagina,
        )
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

    def _cargar_pagina(self) -> None:
        """Obtiene los productos de la página actual desde la BD y los muestra."""
        offset = (self.pagina_actual - 1) * self.productos_por_pagina
        productos = VentasServicio.obtener_productos_paginado(
            offset=offset, limit=self.productos_por_pagina, filtro=self.filtro_actual
        )
        self._renderizar_productos(productos)
        self._actualizar_etiqueta_paginacion()

    def _renderizar_productos(self, productos: list[dict[str, Any]]) -> None:
        """Muestra la lista de productos en el canvas."""
        for widget in self.frame_contenedor.winfo_children():
            widget.destroy()

        columnas = 0
        row = 0
        ancho_producto = 220
        alto_producto = 240
        separacion_x = 8
        separacion_y = 8
        max_image_size = 150

        for producto in productos:
            frame_producto = tk.Frame(
                self.frame_contenedor,
                bg="white",
                width=ancho_producto,
                height=alto_producto,
                bd=1,
                relief="solid",
                highlightbackground="#DADADA",
                highlightthickness=1,
            )
            frame_producto.grid(
                row=row,
                column=columnas,
                padx=separacion_x,
                pady=separacion_y,
                sticky="nsew",
            )
            frame_producto.grid_propagate(False)
            frame_producto.producto_data = {
                "id_producto": producto["id_producto"],
                "producto": producto["producto"],
                "precio": producto["precio"],
                "costo": producto["costo"],
                "stock": producto["stock"],
                "estado": producto["estado"],
                "imagen": producto["imagen"],
            }

            # Imagen (usar rutas() para resolver APPDATA y fallback a default.png)
            try:
                img_path = producto.get("imagen") or "default.png"
                img_file = rutas(img_path) if not Path(img_path).is_absolute() else img_path
                imagen = Image.open(img_file)
            except Exception:
                logger.warning("No se pudo cargar imagen del producto, intentando default")
                try:
                    imagen = Image.open(rutas(str(Path("fotos") / "default.png")))
                except Exception:
                    logger.warning("Tampoco se pudo cargar la imagen default")
                    imagen = None

            if imagen:
                try:
                    imagen.thumbnail((max_image_size, max_image_size), Image.Resampling.LANCZOS)
                    imagen_tk = ImageTk.PhotoImage(imagen)
                    img_label = tk.Label(frame_producto, image=imagen_tk, bg="white")
                    img_label.image = imagen_tk
                    img_label.pack(fill="x", pady=(10, 6))
                except Exception:
                    logger.warning("No se pudo generar miniatura para el producto")
                    img_label = tk.Label(
                        frame_producto,
                        text="Sin imagen",
                        bg="white",
                        font=("Helvetica", 10),
                    )
                    img_label.pack(fill="x", pady=(20, 6))
            else:
                img_label = tk.Label(
                    frame_producto,
                    text="Sin imagen",
                    bg="white",
                    font=("Helvetica", 10),
                )
                img_label.pack(fill="x", pady=(20, 6))

            img_label.bind(
                "<Button-1>",
                lambda e, frame=frame_producto: self._seleccionar_producto_canvas(
                    frame
                ),
            )
            img_label.bind(
                "<Double-Button-1>",
                lambda e, data=frame_producto.producto_data, frame=frame_producto: self._solicitar_cantidad_producto(
                    data, frame
                ),
            )
            frame_producto.bind(
                "<Button-1>",
                lambda e, frame=frame_producto: self._seleccionar_producto_canvas(
                    frame
                ),
            )
            frame_producto.bind(
                "<Double-Button-1>",
                lambda e, data=frame_producto.producto_data, frame=frame_producto: self._solicitar_cantidad_producto(
                    data, frame
                ),
            )

            tk.Label(
                frame_producto,
                text=producto["producto"].upper(),
                font=("Helvetica", 11, "bold"),
                bg="white",
                anchor="center",
                wraplength=180,
                justify="center",
            ).pack(fill="both", expand=True, padx=6, pady=(4, 2))

            tk.Label(
                frame_producto,
                text=f"${producto['precio']:,.0f}".replace(",", "."),
                font=FUENTE_ETIQUETA,
                bg="white",
                fg="#1B5E20",
                anchor="w",
            ).pack(fill="x", padx=6, pady=(0, 6))

            columnas += 1
            if columnas >= 3:
                columnas = 0
                row += 1

        self.canvas.yview_moveto(0)

    def _actualizar_etiqueta_paginacion(self) -> None:
        """Actualiza el texto de la etiqueta de paginación."""
        if hasattr(self, "label_paginacion") and self.label_paginacion:
            total_productos = VentasServicio.contar_productos(self.filtro_actual)
            self.label_paginacion.config(
                text=f"Página {self.pagina_actual} de {self.total_paginas} ({total_productos} productos)"
            )

    # ----------------------------------------------------------------------
    # Paginación (botones)
    # ----------------------------------------------------------------------
    def crear_controles_paginacion(self) -> None:
        for widget in self.frame_paginacion.winfo_children():
            widget.destroy()

        btn_anterior = crear_boton(
            self.frame_paginacion,
            "◀ Anterior",
            estilo=VENTAS_BOTON_NAV,
            comando=self.pagina_anterior,
            padx=10,
        )
        btn_anterior.pack(side="left", padx=5)

        self.label_paginacion = tk.Label(
            self.frame_paginacion, text="", font=("Helvetica", 10, "bold"), bg=COLOR_FONDO
        )
        self.label_paginacion.pack(side="left", padx=20, expand=True)

        btn_siguiente = crear_boton(
            self.frame_paginacion,
            "Siguiente ▶",
            estilo=VENTAS_BOTON_NAV,
            comando=self.pagina_siguiente,
            padx=10,
        )
        btn_siguiente.pack(side="right", padx=5)

        self._actualizar_etiqueta_paginacion()

    def pagina_anterior(self) -> None:
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pagina()

    def pagina_siguiente(self) -> None:
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self._cargar_pagina()

    # ----------------------------------------------------------------------
    # Filtros y búsqueda (actualizados para usar paginación)
    # ----------------------------------------------------------------------
    def actualizar_combobox_productos(self) -> None:
        """Actualiza el combobox con los nombres de productos (todos) para autocompletado."""
        nombres = VentasServicio.obtener_nombres_productos_para_busqueda()
        self.entry_stock["values"] = nombres

    def filtrar_productos_combobox(self, event: Any | None = None) -> None:
        texto = self.entry_stock.get().strip()
        self.filtro_actual = texto
        self.pagina_actual = 1
        self._actualizar_totales()
        self._cargar_pagina()
        # Actualizar combobox con nombres filtrados (para sugerencias)
        nombres_filtrados = VentasServicio.obtener_nombres_productos_para_busqueda(
            texto
        )
        self.entry_stock["values"] = nombres_filtrados

    def seleccionar_producto_entry(self, event: Any | None = None) -> None:
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
        nombres_filtrados = VentasServicio.obtener_nombres_productos_para_busqueda(
            self.filtro_actual
        )
        self.entry_stock["values"] = nombres_filtrados

        # Si la búsqueda exacta devuelve un único producto, intentar seleccionarlo visualmente
        if exactos and len(exactos) == 1:
            self._seleccionar_producto_por_nombre(exactos[0])

    def _seleccionar_producto_por_nombre(self, nombre: str) -> None:
        """Busca en el canvas el frame del producto con el nombre dado y lo selecciona."""
        for frame in self.frame_contenedor.winfo_children():
            data = getattr(frame, "producto_data", None)
            if data and data["producto"] == nombre:
                self._seleccionar_producto_canvas(frame)
                self.canvas.yview_moveto(
                    frame.winfo_y() / max(1, self.frame_contenedor.winfo_height())
                )
                break

    # ----------------------------------------------------------------------
    # Selección y cantidad
    # ----------------------------------------------------------------------
    def _seleccionar_producto_canvas(self, frame: Any) -> None:
        if (
            hasattr(self, "producto_seleccionado_frame")
            and self.producto_seleccionado_frame
            and self.producto_seleccionado_frame.winfo_exists()
        ):
            self.producto_seleccionado_frame.config(
                highlightbackground="#BDBDBD",
                highlightcolor="#BDBDBD",
                highlightthickness=1,
                bd=1,
                relief="solid",
            )
        self.producto_seleccionado_frame = None

        if frame:
            frame.config(
                highlightbackground=COLOR_AZUL,
                highlightcolor=COLOR_AZUL,
                highlightthickness=3,
                bd=1,
                relief="solid",
            )
            self.producto_seleccionado_frame = frame

    def _solicitar_cantidad_producto(self, data: dict[str, Any], frame: Any) -> None:
        """
        Abre ventana para solicitar cantidad del producto.
        """
        self._seleccionar_producto_canvas(frame)

        id_producto = data["id_producto"]
        # Obtener stock actualizado
        stock_actual = VentasServicio.obtener_stock_actual(id_producto)
        if stock_actual is None:
            messagebox.showerror(
                "Error", "No se pudo obtener el stock actual del producto.", parent=self
            )
            return

        # Calcular stock real disponible (restando lo ya en carrito)
        cantidad_en_carrito = sum(
            item["cantidad"]
            for item in self.carrito
            if item["id_producto"] == id_producto
        )
        stock_real_disponible = stock_actual - cantidad_en_carrito

        # Determinar el cliente a usar
        cliente_carrito = ""
        es_venta_mayor = self.tipo_venta_actual == "mayorista"

        if es_venta_mayor and self.cliente_id_seleccionado:
            cliente_nombre = VentasServicio.obtener_nombre_cliente_por_id(
                self.cliente_id_seleccionado
            )
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
        top.configure(bg=COLOR_FONDO)
        top.resizable(False, False)
        top.maxsize(340, 210)
        try:
            top.transient(self)
        except Exception:
            logger.warning("No se pudo establecer transient para la ventana")
        try:
            top.attributes("-topmost", True)
        except Exception:
            logger.warning("No se pudo establecer topmost para la ventana")

        def set_grab() -> None:
            try:
                top.grab_set()
                top.focus_force()
            except tk.TclError:
                logger.warning("No se pudo establecer grab_set para la ventana")

        top.after(1, set_grab)
        top.bind("<Escape>", lambda e: top.destroy())

        frame_main = tk.Frame(top, bg=COLOR_FONDO)
        frame_main.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            frame_main,
            text=f"{data['producto']}",
            font=("Helvetica", 14, "bold"),
            bg=COLOR_FONDO,
            fg="#1a1a1a",
        ).pack(pady=(0, 15))

        tk.Label(
            frame_main,
            text=f"Stock Disponible: {stock_real_disponible}",
            font=("Helvetica", 15),
            bg=COLOR_FONDO,
            fg="#004203",
        ).pack(pady=(0, 20))

        frame_cantidad = tk.Frame(frame_main, bg=COLOR_FONDO)
        frame_cantidad.pack(pady=(0, 25))
        tk.Label(
            frame_cantidad,
            text="Cantidad:",
            font=("Helvetica", 12),
            bg=COLOR_FONDO,
        ).pack(side="left", padx=(0, 10))

        def validar_entero(valor: str) -> bool:
            return valor == "" or (valor.isdigit() and int(valor) > 0)

        vcmd_entero = (self.register(validar_entero), "%P")
        entry_cantidad = tk.Entry(
            frame_cantidad,
            font=("Helvetica", 12),
            width=8,
            validate="key",
            validatecommand=vcmd_entero,
        )
        entry_cantidad.pack(side="left")
        top.after(50, entry_cantidad.focus)

        frame_botones = tk.Frame(frame_main, bg=COLOR_FONDO)
        frame_botones.pack(pady=(0, 0))

        def agregar() -> None:
            try:
                cantidad = int(entry_cantidad.get())
                if cantidad <= 0:
                    messagebox.showwarning(
                        "Cantidad inválida",
                        "Ingrese una cantidad mayor a cero.",
                        parent=top,
                    )
                    return

                # Validar stock actualizado (por si hubo cambios)
                stock_inventario_actual = VentasServicio.obtener_stock_actual(
                    id_producto
                )
                if stock_inventario_actual is None:
                    messagebox.showerror(
                        "Error",
                        "No se pudo obtener el stock actual del producto.",
                        parent=top,
                    )
                    return

                cantidad_en_carrito_ahora = sum(
                    item["cantidad"]
                    for item in self.carrito
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
                messagebox.showwarning(
                    "Cantidad inválida", "Ingrese un número válido.", parent=top
                )

        entry_cantidad.bind("<Return>", lambda e: agregar())

        btn_agregar = crear_boton(
            frame_botones,
            "Agregar",
            estilo=VENTAS_BOTON_EXITO,
            comando=agregar,
            width=10,
        )
        btn_agregar.pack(side="left", padx=10)

        btn_cancelar = crear_boton(
            frame_botones,
            "Cancelar",
            estilo=VENTAS_BOTON_PELIGRO,
            comando=top.destroy,
            width=10,
        )
        btn_cancelar.pack(side="left", padx=10)

    # ----------------------------------------------------------------------
    # Clientes
    # ----------------------------------------------------------------------
    def actualizar_combobox_clientes(self, event: Any | None = None) -> None:
        """Actualiza el combobox de clientes con la lista de nombres."""
        nombres, _ = VentasServicio.obtener_clientes_formateados()
        self.entry_cliente["values"] = nombres

    def _validar_y_actualizar_tipo_venta(self, nuevo_tipo_venta: str) -> None:
        """Cambia el tipo de venta, limpiando el carrito si es necesario."""
        if nuevo_tipo_venta == self.tipo_venta_actual:
            return
        if not self.carrito:
            self.tipo_venta_actual = nuevo_tipo_venta
            return

        messagebox.showwarning(
            "Cambio de tipo de venta",
            "El carrito contiene productos y será limpiado.",
            parent=self,
        )
        self.carrito.clear()
        self.tipo_venta_actual = nuevo_tipo_venta
        self.actualizar_total_carrito_display()

    def _al_entrar_cliente(self, event: Any | None = None) -> None:
        texto = self.entry_cliente.get().strip()
        if not texto:
            self.cliente_id_seleccionado = None
            self._validar_y_actualizar_tipo_venta("rapida")
            nombres, _ = VentasServicio.obtener_clientes_formateados()
            self.entry_cliente["values"] = nombres
        else:
            clientes_filtrados = VentasServicio.filtrar_clientes_por_texto(texto)
            self.entry_cliente["values"] = [
                c["nombre_completo"] for c in clientes_filtrados
            ]
            for c in clientes_filtrados:
                if c["nombre_completo"].lower() == texto.lower():
                    self.cliente_id_seleccionado = c["id_cliente"]
                    self._validar_y_actualizar_tipo_venta("mayorista")
                    break

    def _al_seleccionar_cliente(self, event: Any | None = None) -> None:
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
    def actualizar_total_carrito_display(self) -> None:
        total = VentasServicio.calcular_total_carrito(self.carrito)
        try:
            self.var_total_carrito.set(f"${total:,.0f}".replace(",", "."))
        except Exception:
            logger.warning("Error al formatear total del carrito, usando valor crudo")
            self.var_total_carrito.set(str(total))

    def actualizar_canvas_productos(self) -> None:
        self.cargar_productos()  # recarga la primera página sin filtro

    # ----------------------------------------------------------------------
    # Scroll del canvas (solo vertical)
    # ----------------------------------------------------------------------
    def _activar_scroll_canvas(self) -> None:
        self.bind_all("<MouseWheel>", self._en_rueda_raton_windows)
        self.bind_all("<Button-4>", self._en_rueda_raton_linux)
        self.bind_all("<Button-5>", self._en_rueda_raton_linux)

    def _desactivar_scroll_canvas(self) -> None:
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _en_rueda_raton_windows(self, event: Any) -> None:
        widget = self.winfo_containing(event.x_root, event.y_root)
        if widget is not None:
            current = widget
            while current:
                if current == self.canvas or current == self.frame_contenedor:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    break
                current = current.master if hasattr(current, "master") else None

    def _en_rueda_raton_linux(self, event: Any) -> None:
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
                current = current.master if hasattr(current, "master") else None

    
