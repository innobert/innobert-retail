"""
edicion_deudas.py

Módulo para gestionar la edición de deudas de forma dinámica e interactiva.
Permite:
- Editar factura: ver productos de la deuda, editar cantidades (doble clic), eliminar productos.
- Agregar productos: mostrar canvas con inventario, buscar, paginación, y añadir nuevos productos a la deuda.
Los cambios se aplican directamente a la base de datos y se registran en el historial con la acción "EDITADO".
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Any

from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

from retail.nucleo.base_datos import obtener_conexion
from retail.nucleo.servicios.deudas.servicio_edicion_deudas import ServicioEdicionDeudas
from retail.nucleo.servicios.deudas.servicio_deudas import DeudasServicio
from retail.nucleo.configuraciones import (
    rutas,
    COLOR_FONDO,
    COLOR_FONDO_EDITAR,
    COLOR_AZUL,
    COLOR_VERDE,
    COLOR_ROJO,
    crear_boton,
    DEUDAS_BOTON_EXITO,
    DEUDAS_BOTON_PELIGRO,
    DEUDAS_BOTON_NAV,
    DEUDAS_BOTON_CERRAR,
    DEUDAS_BOTON_NEUTRO,
    FUENTE_BOTON_NEGRITA,
    FUENTE_BOTON_GRANDE,
)


# ----------------------------------------------------------------------
# Función principal (selector de acción)
# ----------------------------------------------------------------------
def abrir_ventana_edicion_deuda(
    ventana_padre: Any, id_deuda: int, cliente: str, usuario_actual: str, callbacks: dict[str, Any]
) -> None:
    """Muestra selector de acción (editar factura / agregar productos)."""
    top = tk.Toplevel(ventana_padre)
    top.title("Editar deuda")
    top.geometry("420x220+500+200")
    top.configure(bg=COLOR_FONDO)
    top.resizable(False, False)
    top.maxsize(420, 220)
    top.grab_set()
    top.transient(ventana_padre)

    tk.Label(
        top,
        text="¿Qué deseas hacer con esta deuda?",
        font=("Helvetica", 14, "bold"),
        bg=COLOR_FONDO,
        pady=14,
    ).pack(fill="x")

    frame_botones = tk.Frame(top, bg=COLOR_FONDO)
    frame_botones.pack(fill="x", padx=20, pady=10)

    btn_editar = crear_boton(
        frame_botones,
        texto="Editar factura",
        estilo=DEUDAS_BOTON_EXITO,
        fuente=FUENTE_BOTON_GRANDE,
        width=16,
        height=2,
        comando=lambda: (
            top.destroy(),
            _abrir_ventana_editar_factura(
                ventana_padre, id_deuda, cliente, usuario_actual, callbacks
            ),
        ),
    )
    btn_editar.pack(side="left", expand=True, padx=10)

    btn_agregar = crear_boton(
        frame_botones,
        texto="Agregar productos",
        estilo=DEUDAS_BOTON_EXITO,
        fuente=FUENTE_BOTON_GRANDE,
        width=16,
        height=2,
        comando=lambda: (
            top.destroy(),
            _abrir_ventana_agregar_productos(
                ventana_padre, id_deuda, cliente, usuario_actual, callbacks
            ),
        ),
    )
    btn_agregar.pack(side="right", expand=True, padx=10)

    crear_boton(
        top,
        texto="Cancelar",
        estilo=DEUDAS_BOTON_PELIGRO,
        fuente=FUENTE_BOTON_NEGRITA,
        width=12,
        comando=top.destroy,
    ).pack(side="bottom", pady=12)


# ----------------------------------------------------------------------
# VENTANA DE EDICIÓN DE FACTURA (diseño mejorado con elementos más grandes)
# ----------------------------------------------------------------------
def _abrir_ventana_editar_factura(parent: Any, id_deuda: int, cliente: str, usuario_actual: str, callbacks: dict[str, Any]) -> None:
    top = tk.Toplevel(parent)
    top.title(f"Editar factura - {cliente}")
    top.geometry("950x650+150+30")  # Ancho aumentado para dar espacio al filtro
    top.configure(bg=COLOR_FONDO_EDITAR)
    # Bloquear redimensionamiento para mantener la integridad del diseño
    top.resizable(False, False)
    top.maxsize(950, 650)
    top.grab_set()
    top.transient(parent)

    conn = obtener_conexion()
    cursor = conn.cursor()
    cambios_realizados = False

    def _cerrar_conexion() -> None:
        nonlocal conn
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        finally:
            conn = None  # type: ignore[assignment]

    def cancelar_edicion() -> None:
        nonlocal cambios_realizados
        if cambios_realizados:
            if not messagebox.askyesno(
                "Cambios sin confirmar",
                "Hay cambios sin confirmar.\n¿Desea descartarlos y regresar al selector?",
                parent=top,
            ):
                return
            conn.rollback()
        else:
            conn.rollback()
        top.destroy()
        _cerrar_conexion()
        abrir_ventana_edicion_deuda(
            parent, id_deuda, cliente, usuario_actual, callbacks
        )

    def confirmar_cambios() -> None:
        nonlocal cambios_realizados
        if not messagebox.askyesno(
            "Confirmar cambios",
            "¿Desea confirmar los cambios realizados en esta deuda?\n\nEsta acción cerrará la edición y actualizará el listado principal.",
            parent=top,
        ):
            return
        try:
            cambios_realizados = False
            top.destroy()
            _cerrar_conexion()
            abrir_ventana_edicion_deuda(
                parent, id_deuda, cliente, usuario_actual, callbacks
            )
            _notificar_cambios(callbacks)
        except Exception as err:
            messagebox.showerror(
                "Error", f"No se pudieron confirmar los cambios:\n{err}", parent=top
            )

    def on_close() -> None:
        if cambios_realizados:
            if messagebox.askyesno(
                "Confirmar salida",
                "Hay cambios pendientes.\n¿Desea confirmar antes de salir?\n\nSi no confirma, los cambios se descartarán.",
                parent=top,
            ):
                confirmar_cambios()
            else:
                conn.rollback()
                top.destroy()
                _cerrar_conexion()
        else:
            conn.rollback()
            top.destroy()
            _cerrar_conexion()

    top.protocol("WM_DELETE_WINDOW", on_close)

    main_frame = tk.Frame(top, bg=COLOR_FONDO_EDITAR)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Panel de totales
    frame_info = tk.Frame(main_frame, bg=COLOR_FONDO_EDITAR, pady=8)
    frame_info.pack(fill="x")
    tk.Label(
        frame_info, text="Total deuda:", font=("Helvetica", 14, "bold"), bg=COLOR_FONDO_EDITAR
    ).pack(side="left", padx=(0, 8))
    var_total = tk.StringVar(value="$0")
    tk.Label(
        frame_info,
        textvariable=var_total,
        font=("Helvetica", 18, "bold"),
        bg=COLOR_FONDO_EDITAR,
        fg="#0B6623",
    ).pack(side="left", padx=(0, 30))
    tk.Label(
        frame_info,
        text="Saldo pendiente:",
        font=("Helvetica", 14, "bold"),
        bg=COLOR_FONDO_EDITAR,
    ).pack(side="left", padx=(0, 8))
    var_saldo = tk.StringVar(value="$0")
    tk.Label(
        frame_info,
        textvariable=var_saldo,
        font=("Helvetica", 18, "bold"),
        bg=COLOR_FONDO_EDITAR,
        fg="#C62828",
    ).pack(side="left")

    # Filtro de productos (más grande)
    frame_buscar = tk.Frame(main_frame, bg=COLOR_FONDO_EDITAR)
    frame_buscar.pack(fill="x", pady=(5, 12))
    lbl_filtro = tk.Label(
        frame_buscar,
        text="Filtrar producto:",
        font=("Helvetica", 12, "bold"),
        bg=COLOR_FONDO_EDITAR,
    )
    lbl_filtro.pack(side="left", padx=(0, 10))
    entry_filtro = ttk.Entry(frame_buscar, font=("Helvetica", 12), width=35)
    entry_filtro.pack(side="left", fill="x", expand=True, padx=5)
    btn_limpiar = crear_boton(
        frame_buscar,
        texto="Limpiar",
        comando=lambda: (entry_filtro.delete(0, tk.END), filtrar_tabla()),
        estilo=DEUDAS_BOTON_NEUTRO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=3,
    )
    btn_limpiar.pack(side="left", padx=(10, 0))

    # Tabla de productos (estilo más alto)
    frame_tabla = tk.Frame(main_frame, bg="#FFFFFF", bd=1, relief="solid")
    frame_tabla.pack(fill="both", expand=True, pady=(0, 12))

    style = ttk.Style(top)
    style.theme_use("clam")
    style.configure(
        "EditarDeuda.Treeview.Heading",
        font=("Helvetica", 12, "bold"),
        background=COLOR_AZUL,
        foreground="#ffffff",
    )
    style.configure(
        "EditarDeuda.Treeview",
        font=("Helvetica", 11),
        rowheight=40,
        background="#F8FAFB",
    )
    style.map("EditarDeuda.Treeview", background=[("selected", "#105A65")])

    tree = ttk.Treeview(
        frame_tabla,
        columns=("id", "producto", "cantidad", "precio", "subtotal"),
        show="headings",
        style="EditarDeuda.Treeview",
    )
    tree.heading("id", text="ID")
    tree.heading("producto", text="Producto")
    tree.heading("cantidad", text="Cantidad")
    tree.heading("precio", text="Precio Unit.")
    tree.heading("subtotal", text="Subtotal")
    tree.column("id", width=0, stretch=False)
    tree.column("producto", width=370, stretch=True, anchor="w")
    tree.column("cantidad", width=100, anchor="center")
    tree.column("precio", width=130, anchor="center")
    tree.column("subtotal", width=150, anchor="e")

    scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    # Botones de acción (más grandes)
    frame_acciones = tk.Frame(main_frame, bg=COLOR_FONDO_EDITAR)
    frame_acciones.pack(fill="x")
    btn_eliminar = crear_boton(
        frame_acciones,
        texto="Eliminar producto seleccionado",
        estilo=DEUDAS_BOTON_PELIGRO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=6,
        comando=lambda: eliminar_producto(),
    )
    btn_eliminar.pack(side="left", padx=5)
    btn_regresar = crear_boton(
        frame_acciones,
        texto="Regresar",
        estilo=DEUDAS_BOTON_CERRAR,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=6,
        comando=cancelar_edicion,
    )
    btn_regresar.pack(side="left", padx=5)
    btn_confirmar = crear_boton(
        frame_acciones,
        texto="Confirmar",
        estilo=DEUDAS_BOTON_EXITO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=18,
        pady=6,
        comando=confirmar_cambios,
    )
    btn_confirmar.pack(side="right", padx=5)

    # Funciones internas
    def cargar_datos() -> None:
        try:
            detalles = ServicioEdicionDeudas.obtener_detalles_deuda(
                id_deuda, conn=conn
            )
            total, saldo = ServicioEdicionDeudas.obtener_info_deuda(
                id_deuda, conn=conn
            )
            tree.delete(*tree.get_children())
            for d in detalles:
                tree.insert(
                    "",
                    "end",
                    iid=str(d["id_detalle"]),
                    values=(
                        d["id_detalle"],
                        d["producto"],
                        d["cantidad"],
                        f"${d['precio_unit']:,.0f}".replace(",", "."),
                        f"${d['subtotal']:,.0f}".replace(",", "."),
                    ),
                )
            var_total.set(f"${total:,.0f}".replace(",", "."))
            var_saldo.set(f"${saldo:,.0f}".replace(",", "."))
        except Exception as err:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos:\n{err}", parent=top
            )

    def eliminar_producto() -> None:
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning(
                "Advertencia", "Seleccione un producto para eliminar.", parent=top
            )
            return
        iid = seleccion[0]
        id_detalle = int(iid)
        item = tree.item(iid)
        producto = item["values"][1]
        if messagebox.askyesno(
            "Confirmar", f"¿Eliminar '{producto}' de la deuda?", parent=top
        ):
            try:
                ServicioEdicionDeudas.eliminar_producto_deuda(
                    id_detalle, usuario_actual, conn=conn, cursor=cursor
                )
                messagebox.showinfo(
                    "Éxito", "Producto eliminado correctamente.", parent=top
                )
                cargar_datos()
            except Exception as err:
                messagebox.showerror("Error", str(err), parent=top)

    def editar_cantidad(event: Any) -> None:
        seleccion = tree.selection()
        if not seleccion:
            return
        iid = seleccion[0]
        id_detalle = int(iid)
        item = tree.item(iid)
        producto = item["values"][1]
        cantidad_actual = item["values"][2]
        popup = tk.Toplevel(top)
        popup.title(f"Editar cantidad - {producto}")
        popup.geometry("340x230+500+250")
        popup.configure(bg=COLOR_FONDO_EDITAR)
        popup.resizable(False, False)
        popup.maxsize(340, 230)
        popup.transient(top)
        popup.grab_set()

        tk.Label(
            popup, text=producto, font=("Helvetica", 14, "bold"), bg=COLOR_FONDO_EDITAR
        ).pack(pady=(15, 8))
        tk.Label(
            popup,
            text=f"Cantidad actual: {cantidad_actual}",
            font=("Helvetica", 12),
            bg=COLOR_FONDO_EDITAR,
        ).pack(pady=(0, 12))
        tk.Label(
            popup, text="Nueva cantidad:", font=("Helvetica", 12), bg=COLOR_FONDO_EDITAR
        ).pack(pady=(0, 6))
        entry_cant = tk.Entry(popup, font=("Helvetica", 13), width=10, justify="center")
        entry_cant.pack()
        entry_cant.insert(0, str(cantidad_actual))
        entry_cant.focus()
        entry_cant.select_range(0, tk.END)

        def guardar() -> None:
            try:
                nueva = int(entry_cant.get())
                if nueva <= 0:
                    messagebox.showwarning(
                        "Cantidad inválida", "Debe ser mayor a cero.", parent=popup
                    )
                    return
                ServicioEdicionDeudas.editar_cantidad_detalle(
                    id_detalle,
                    nueva,
                    usuario_actual,
                    conn=conn,
                    cursor=cursor,
                )
                messagebox.showinfo("Éxito", "Cantidad actualizada.", parent=popup)
                cargar_datos()
                popup.destroy()
            except ValueError:
                messagebox.showwarning(
                    "Error", "Ingrese un número válido.", parent=popup
                )
            except Exception as err:
                messagebox.showerror("Error", str(err), parent=popup)

        entry_cant.bind("<Return>", lambda e: guardar())
        crear_boton(
            popup,
            texto="Guardar",
            comando=guardar,
            estilo=DEUDAS_BOTON_EXITO,
            fuente=FUENTE_BOTON_NEGRITA,
            padx=12,
            pady=4,
        ).pack(pady=18)

    def filtrar_tabla() -> None:
        texto = entry_filtro.get().strip().lower()
        for item in tree.get_children():
            valores = tree.item(item, "values")
            producto = valores[1].lower()
            if texto in producto:
                tree.reattach(item, "", "end")
            else:
                tree.detach(item)

    tree.bind("<Double-1>", editar_cantidad)
    entry_filtro.bind("<KeyRelease>", lambda e: filtrar_tabla())
    cargar_datos()


# ----------------------------------------------------------------------
# VENTANA PARA AGREGAR PRODUCTOS (con canvas y paginación)
# ----------------------------------------------------------------------
def _abrir_ventana_agregar_productos(
    parent: Any, id_deuda: int, cliente: str, usuario_actual: str, callbacks: dict[str, Any]
) -> None:
    top = tk.Toplevel(parent)
    top.title(f"Agregar productos - {cliente}")
    top.geometry("900x650+130+20")
    top.configure(bg=COLOR_FONDO)
    # Bloquear redimensionamiento para mantener la integridad del diseño
    top.resizable(False, False)
    top.maxsize(900, 650)
    top.grab_set()
    top.transient(parent)

    frame_buscar = tk.Frame(top, bg=COLOR_FONDO)
    frame_buscar.pack(fill="x", padx=10, pady=10)
    tk.Label(
        frame_buscar,
        text="Buscar producto:",
        font=("Helvetica", 13, "bold"),
        bg=COLOR_FONDO,
    ).pack(side="left", padx=5)
    entry_buscar = ttk.Combobox(
        frame_buscar, font=("Helvetica", 12), state="normal", width=40
    )
    entry_buscar.pack(side="left", fill="x", expand=True, padx=5, ipady=6)

    frame_canvas = tk.LabelFrame(
        top, text="Productos disponibles", font=("Helvetica", 12, "bold"), bg=COLOR_FONDO
    )
    frame_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    canvas = tk.Canvas(frame_canvas, bg=COLOR_FONDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_contenedor = tk.Frame(canvas, bg=COLOR_FONDO)
    canvas.create_window((0, 0), window=frame_contenedor, anchor="nw")
    frame_contenedor.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    frame_paginacion = tk.Frame(top, bg=COLOR_FONDO)
    frame_paginacion.pack(fill="x", padx=10, pady=(0, 10))
    btn_anterior = crear_boton(
        frame_paginacion,
        texto="◀ Anterior",
        estilo=DEUDAS_BOTON_NAV,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=4,
    )
    btn_anterior.pack(side="left", padx=5)
    label_pagina = tk.Label(
        frame_paginacion,
        text="Página 1 de 1",
        font=("Helvetica", 11, "bold"),
        bg=COLOR_FONDO,
    )
    label_pagina.pack(side="left", padx=20, expand=True)
    btn_siguiente = crear_boton(
        frame_paginacion,
        texto="Siguiente ▶",
        estilo=DEUDAS_BOTON_NAV,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=4,
    )
    btn_siguiente.pack(side="right", padx=5)

    pagina_actual = 1
    productos_por_pagina = 12
    total_paginas = 1
    filtro_actual = ""

    def cargar_productos_pagina() -> None:
        nonlocal pagina_actual, total_paginas
        total = ServicioEdicionDeudas.contar_productos_con_filtro(filtro_actual)
        total_paginas = max(
            1, (total + productos_por_pagina - 1) // productos_por_pagina
        )
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        offset = (pagina_actual - 1) * productos_por_pagina
        productos = ServicioEdicionDeudas.obtener_productos_paginado(
            filtro_actual, offset, productos_por_pagina
        )

        for widget in frame_contenedor.winfo_children():
            widget.destroy()

        ancho_producto = 220
        alto_producto = 240
        separacion = 8
        columnas = 4
        max_image_size = 150
        for idx, prod in enumerate(productos):
            row = idx // columnas
            col = idx % columnas
            frame_producto = tk.Frame(
                frame_contenedor,
                bg="white",
                width=ancho_producto,
                height=alto_producto,
                bd=1,
                relief="solid",
                highlightbackground="#DADADA",
                highlightthickness=1,
            )
            frame_producto.grid(
                row=row, column=col, padx=separacion, pady=separacion, sticky="nsew"
            )
            frame_producto.grid_propagate(False)

            # Cargar imagen (iguala al inventario)
            try:
                ruta_imagen = prod.get("imagen", "default.png")
                if not ruta_imagen or ruta_imagen.strip() == "":
                    ruta_imagen = "default.png"
                if not Path(ruta_imagen).is_absolute():
                    ruta_imagen = rutas(Path("fotos") / ruta_imagen)
                img = Image.open(ruta_imagen)
                img.thumbnail((max_image_size, max_image_size), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                lbl_img = tk.Label(frame_producto, image=img_tk, bg="white")
                lbl_img.image = img_tk
                lbl_img.pack(fill="x", pady=(10, 6))
            except Exception as e:
                logger.exception("Error cargando imagen para %s", prod["producto"])
                lbl_img = tk.Label(
                    frame_producto, text="Sin imagen", bg="white", font=("Helvetica", 9)
                )
                lbl_img.pack(pady=(30, 2))

            tk.Label(
                frame_producto,
                text=prod["producto"],
                font=("Helvetica", 11, "bold"),
                bg="white",
                wraplength=190,
                justify="center",
            ).pack(pady=(2, 2))
            tk.Label(
                frame_producto,
                text=f"${prod['precio']:,.0f}".replace(",", "."),
                font=("Helvetica", 12, "bold"),
                bg="white",
                fg="#1B5E20",
            ).pack(pady=(0, 4))

            def on_double_click(p: dict[str, Any] = prod) -> None:
                if p["stock"] <= 0:
                    messagebox.showwarning(
                        "Sin stock",
                        "Este producto no tiene stock disponible.",
                        parent=top,
                    )
                    return
                _agregar_producto_a_deuda(
                    p, top, id_deuda, usuario_actual, callbacks, cargar_productos_pagina
                )

            frame_producto.bind("<Double-1>", lambda e, p=prod: on_double_click(p))
            lbl_img.bind("<Double-1>", lambda e, p=prod: on_double_click(p))

        canvas.yview_moveto(0)
        label_pagina.config(text=f"Página {pagina_actual} de {total_paginas}")
        btn_anterior.config(state="normal" if pagina_actual > 1 else "disabled")
        btn_siguiente.config(
            state="normal" if pagina_actual < total_paginas else "disabled"
        )

    def pagina_anterior() -> None:
        nonlocal pagina_actual
        if pagina_actual > 1:
            pagina_actual -= 1
            cargar_productos_pagina()

    def pagina_siguiente() -> None:
        nonlocal pagina_actual
        if pagina_actual < total_paginas:
            pagina_actual += 1
            cargar_productos_pagina()

    def aplicar_filtro(event: Any = None) -> None:
        nonlocal filtro_actual, pagina_actual
        filtro_actual = entry_buscar.get().strip()
        pagina_actual = 1
        cargar_productos_pagina()
        try:
            nombres = DeudasServicio.obtener_nombres_productos_para_busqueda(
                filtro_actual
            )
            entry_buscar["values"] = nombres
        except Exception:
            logger.exception("Error al obtener nombres de productos para búsqueda")

    btn_anterior.config(command=pagina_anterior)
    btn_siguiente.config(command=pagina_siguiente)
    entry_buscar.bind("<KeyRelease>", aplicar_filtro)
    entry_buscar.bind("<<ComboboxSelected>>", aplicar_filtro)

    cargar_productos_pagina()
    btn_cerrar = crear_boton(
        top,
        texto="Cerrar",
        comando=top.destroy,
        estilo=DEUDAS_BOTON_CERRAR,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=18,
        pady=6,
    )
    btn_cerrar.pack(pady=(0, 10))


def _agregar_producto_a_deuda(
    producto: dict[str, Any], parent: Any, id_deuda: int, usuario: str, callbacks: dict[str, Any], recargar_callback: Any
) -> None:
    popup = tk.Toplevel(parent)
    popup.title(f"Agregar {producto['producto']}")
    popup.geometry("380x250+400+200")
    popup.configure(bg=COLOR_FONDO_EDITAR)
    popup.minsize(360, 250)
    popup.resizable(True, True)
    popup.transient(parent)
    popup.grab_set()

    tk.Label(
        popup, text=producto["producto"], font=("Helvetica", 14, "bold"), bg=COLOR_FONDO_EDITAR
    ).pack(pady=(15, 8))
    tk.Label(
        popup,
        text=f"Stock disponible: {producto['stock']}",
        font=("Helvetica", 12),
        bg=COLOR_FONDO_EDITAR,
        fg="#008B8B",
    ).pack(pady=(0, 12))
    tk.Label(
        popup, text="Cantidad a agregar:", font=("Helvetica", 12), bg=COLOR_FONDO_EDITAR
    ).pack(pady=(0, 6))
    entry_cant = tk.Entry(popup, font=("Helvetica", 13), width=10, justify="center")
    entry_cant.pack()
    entry_cant.focus()

    def confirmar() -> None:
        try:
            cantidad = int(entry_cant.get())
            if cantidad <= 0:
                messagebox.showwarning(
                    "Cantidad inválida", "Debe ser mayor a cero.", parent=popup
                )
                return
            if cantidad > producto["stock"]:
                messagebox.showwarning(
                    "Stock insuficiente",
                    f"Solo hay {producto['stock']} unidades.",
                    parent=popup,
                )
                return
            ServicioEdicionDeudas.agregar_producto_a_deuda(
                id_deuda, producto["id_producto"], cantidad, usuario
            )
            messagebox.showinfo(
                "Éxito", "Producto agregado correctamente.", parent=popup
            )
            popup.destroy()
            recargar_callback()
            _notificar_cambios(callbacks)
        except ValueError:
            messagebox.showwarning("Error", "Ingrese un número válido.", parent=popup)
        except Exception as err:
            messagebox.showerror("Error", str(err), parent=popup)

    entry_cant.bind("<Return>", lambda e: confirmar())

    frame_botones = tk.Frame(popup, bg=COLOR_FONDO_EDITAR)
    frame_botones.pack(pady=15)
    crear_boton(
        frame_botones,
        texto="Agregar",
        comando=confirmar,
        estilo=DEUDAS_BOTON_EXITO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=4,
        width=12,
    ).pack(side="left", padx=8)
    crear_boton(
        frame_botones,
        texto="Cancelar",
        comando=popup.destroy,
        estilo=DEUDAS_BOTON_PELIGRO,
        fuente=FUENTE_BOTON_NEGRITA,
        padx=12,
        pady=4,
        width=12,
    ).pack(side="left", padx=8)


def _notificar_cambios(callbacks: dict[str, Any]) -> None:
    if not callbacks:
        return
    if "cargar_deudas" in callbacks and callable(callbacks["cargar_deudas"]):
        callbacks["cargar_deudas"]()
    if "actualizar_total_deudas" in callbacks and callable(
        callbacks["actualizar_total_deudas"]
    ):
        callbacks["actualizar_total_deudas"]()
