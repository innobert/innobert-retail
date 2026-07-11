"""
papelera_deudas.py

Ventana para visualizar las deudas eliminadas (papelera de reciclaje).
Incluye paginación, filtro por número de factura y limpieza automática de registros antiguos.
Diseño compacto: buscador arriba, tabla central, paginación abajo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from retail.nucleo.servicios.deudas.servicio_papelera_deudas import ServicioPapeleraDeudas


def peso_colombiano(value):
    return f"${value:,.0f}".replace(",", ".")


def ver_papelera_deudas(parent):
    ventana = tk.Toplevel(parent)
    ventana.title("Papelera de Deudas")
    ventana.geometry("1100x650+50+20")
    ventana.configure(bg="#E6D9E3")
    ventana.resizable(False, False)
    ventana.transient(parent)
    ventana.grab_set()
    ventana.focus_force()
    ventana.bind("<Escape>", lambda e: ventana.destroy())

    # Limpieza automática al abrir (registros >30 días)
    eliminados = ServicioPapeleraDeudas.limpiar_registros_antiguos(dias=30)
    if eliminados > 0:
        print(f"[Papelera Deudas] {eliminados} registros antiguos eliminados automáticamente.")

    # ========== PAGINACIÓN ==========
    pagina_actual = 1
    registros_por_pagina = 20
    total_paginas = 1
    filtro_actual = ""

    # ========== FRAME SUPERIOR (BÚSQUEDA) ==========
    frame_superior = tk.Frame(ventana, bg="#E6D9E3")
    frame_superior.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(frame_superior, text="N° Factura:", font=("Helvetica", 11, "bold"), bg="#E6D9E3").pack(side=tk.LEFT, padx=(0,5))
    entry_filtro = ttk.Entry(frame_superior, font=("Helvetica", 11), width=20)
    entry_filtro.pack(side=tk.LEFT, padx=(0,10))

    def aplicar_filtro(event=None):
        nonlocal filtro_actual, pagina_actual
        filtro_actual = entry_filtro.get().strip()
        pagina_actual = 1
        actualizar_totales()
        cargar_pagina()

    entry_filtro.bind("<KeyRelease>", aplicar_filtro)
    entry_filtro.bind("<Return>", aplicar_filtro)

    btn_limpiar = tk.Button(frame_superior, text="Limpiar Filtro", font=("Helvetica", 10, "bold"),
                            bg="#757575", fg="white", command=lambda: (entry_filtro.delete(0, tk.END), aplicar_filtro()))
    btn_limpiar.pack(side=tk.LEFT, padx=5)

    btn_cerrar = tk.Button(frame_superior, text="Cerrar", font=("Helvetica", 10, "bold"),
                           bg="#F44336", fg="white", command=ventana.destroy)
    btn_cerrar.pack(side=tk.RIGHT, padx=5)

    # ========== FRAME TABLA ==========
    frame_tabla = tk.Frame(ventana, bg="#F5F5F5")
    frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

    # Columnas sin "Detalle"
    columnas = ("ID", "N°", "N° Factura", "Cliente", "Fecha", "Total", "Saldo", "Usuario", "Eliminada")
    tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")

    config_columnas = [
        ("ID", 0),
        ("N°", 40),
        ("N° Factura", 120),
        ("Cliente", 180),
        ("Fecha", 100),
        ("Total", 100),
        ("Saldo", 100),
        ("Usuario", 120),
        ("Eliminada", 150),  # Ancho suficiente para fecha y hora completa
    ]
    for col, width in config_columnas:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")
    tree.column("ID", width=0, stretch=tk.NO)
    tree.column("Cliente", anchor="w")

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

    # ========== CONTROLES DE PAGINACIÓN ==========
    frame_paginacion = tk.Frame(ventana, bg="#E6D9E3")
    frame_paginacion.pack(fill=tk.X, padx=10, pady=(0,10))

    btn_anterior = tk.Button(frame_paginacion, text="◀ Anterior", command=lambda: pagina_anterior(),
                             bg="#2196F3", fg="white", relief="flat", padx=10, font=("Helvetica", 10, "bold"))
    btn_anterior.pack(side=tk.LEFT, padx=5)

    label_paginacion = tk.Label(frame_paginacion, text="", font=("Helvetica", 10, "bold"), bg="#E6D9E3")
    label_paginacion.pack(side=tk.LEFT, padx=20, expand=True)

    btn_siguiente = tk.Button(frame_paginacion, text="Siguiente ▶", command=lambda: pagina_siguiente(),
                              bg="#2196F3", fg="white", relief="flat", padx=10, font=("Helvetica", 10, "bold"))
    btn_siguiente.pack(side=tk.RIGHT, padx=5)

    # ========== FUNCIONES DE PAGINACIÓN Y CARGA ==========
    def actualizar_totales():
        nonlocal total_paginas, pagina_actual
        total_registros = ServicioPapeleraDeudas.contar_papelera(filtro_actual)
        total_paginas = max(1, (total_registros + registros_por_pagina - 1) // registros_por_pagina)
        if pagina_actual > total_paginas:
            pagina_actual = total_paginas
        actualizar_etiqueta()

    def cargar_pagina():
        tree.delete(*tree.get_children())
        offset = (pagina_actual - 1) * registros_por_pagina
        registros = ServicioPapeleraDeudas.obtener_pagina(offset, registros_por_pagina, filtro_actual)

        inicio_numero = (pagina_actual - 1) * registros_por_pagina + 1
        for idx, reg in enumerate(registros, start=inicio_numero):
            tree.insert(
                "",
                "end",
                iid=reg["id_papelera"],
                values=(
                    reg["id_papelera"],
                    idx,
                    reg["numero_factura"],
                    reg["cliente"],
                    reg["fecha"],
                    peso_colombiano(reg["total"]),
                    peso_colombiano(reg["saldo"]),
                    reg["usuario_elimino"],
                    reg["fecha_eliminacion"],  # Se muestra completo, sin truncar
                ),
            )
        actualizar_etiqueta()

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

    def actualizar_etiqueta():
        total_registros = ServicioPapeleraDeudas.contar_papelera(filtro_actual)
        label_paginacion.config(
            text=f"Página {pagina_actual} de {total_paginas} ({total_registros} registros)"
        )

    # ========== INICIALIZACIÓN ==========
    actualizar_totales()
    cargar_pagina()

    ventana.mainloop()