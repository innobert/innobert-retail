import tkinter as tk
from tkinter import ttk, messagebox
from retail.sesion.core.servicio_licencias import ServicioLicencias
from retail.sesion.core.servicio_registro import ServicioRegistro
from retail.traducciones import _

COLOR_BG = "#E6D9E3"
COLOR_CARD = "#FFFFFF"
COLOR_PRIMARY = "#5C6BC0"
COLOR_SUCCESS = "#43A047"
COLOR_WARNING = "#FB8C00"
COLOR_DANGER = "#E53935"
COLOR_TEXT = "#37474F"
COLOR_TEXT_LIGHT = "#78909C"
COLOR_BORDER = "#E0E0E0"
COLOR_ROW_ALT = "#F5F5F5"


class VentanaLicencias(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(_("Gestión de Licencias"))
        self.geometry("920x580+300+60")
        self.resizable(False, False)
        self.config(bg=COLOR_BG)
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._crear_widgets()

    def on_close(self):
        self.grab_release()
        self.destroy()

    def _crear_widgets(self):
        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(container, bg=COLOR_CARD, bd=0, highlightthickness=0)
        header.pack(fill=tk.X, pady=(0, 16))
        tk.Label(
            header, text=_("GESTIÓN DE LICENCIAS"),
            font=("Segoe UI", 20, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT,
            anchor="w", padx=24, pady=16
        ).pack(fill=tk.X)

        card = tk.Frame(container, bg=COLOR_CARD, bd=0, highlightthickness=0)
        card.pack(fill=tk.BOTH, expand=True)

        self._crear_panel_activacion(card)
        self._crear_separador(card)
        self._crear_tabla(card)

    def _crear_panel_activacion(self, parent):
        panel = tk.Frame(parent, bg=COLOR_CARD, padx=24, pady=(16, 8))
        panel.pack(fill=tk.X)

        tk.Label(
            panel, text=_("Activar / Consultar Licencia"),
            font=("Segoe UI", 12, "bold"), bg=COLOR_CARD, fg=COLOR_PRIMARY
        ).pack(anchor="w", pady=(0, 12))

        row = tk.Frame(panel, bg=COLOR_CARD)
        row.pack(fill=tk.X)

        lbl_usuario = tk.Label(
            row, text=_("Usuario:"), font=("Segoe UI", 11), bg=COLOR_CARD, fg=COLOR_TEXT
        )
        lbl_usuario.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_usuario = ttk.Entry(row, font=("Segoe UI", 11), width=16)
        self.entry_usuario.pack(side=tk.LEFT, padx=(0, 20))

        lbl_serial = tk.Label(
            row, text=_("Serial:"), font=("Segoe UI", 11), bg=COLOR_CARD, fg=COLOR_TEXT
        )
        lbl_serial.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_serial = ttk.Entry(row, font=("Segoe UI", 11), width=28)
        self.entry_serial.pack(side=tk.LEFT, padx=(0, 16))

        self.btn_activar = tk.Button(
            row, text=_("  Activar  "), bg=COLOR_SUCCESS, fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"), command=self.activar_licencia,
            relief="flat", cursor="hand2", bd=0, padx=18, pady=6
        )
        self.btn_activar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_estado = tk.Button(
            row, text=_("  Ver Estado  "), bg=COLOR_PRIMARY, fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"), command=self.ver_estado,
            relief="flat", cursor="hand2", bd=0, padx=18, pady=6
        )
        self.btn_estado.pack(side=tk.LEFT)

    def _crear_separador(self, parent):
        sep = tk.Frame(parent, bg=COLOR_BORDER, height=1, bd=0)
        sep.pack(fill=tk.X, padx=24, pady=8)

    def _crear_tabla(self, parent):
        tabla_container = tk.Frame(parent, bg=COLOR_CARD, padx=24, pady=(8, 16))
        tabla_container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            tabla_container, text=_("Licencias Registradas"),
            font=("Segoe UI", 12, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT
        ).pack(anchor="w", pady=(0, 10))

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Licencias.Treeview.Heading",
            font=("Segoe UI", 11, "bold"),
            background=COLOR_BG,
            foreground=COLOR_TEXT,
            relief="flat",
            borderwidth=0,
        )
        style.configure(
            "Licencias.Treeview",
            font=("Segoe UI", 10),
            rowheight=36,
            background=COLOR_CARD,
            fieldbackground=COLOR_CARD,
            foreground=COLOR_TEXT,
            borderwidth=0,
        )
        style.map(
            "Licencias.Treeview",
            background=[("selected", COLOR_PRIMARY)],
            foreground=[("selected", "#FFFFFF")],
        )

        tree_frame = tk.Frame(tabla_container, bg=COLOR_CARD, bd=1, relief="solid", highlightbackground=COLOR_BORDER, highlightthickness=1)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("usuario", "fecha_inicio", "fecha_fin", "dias_restantes", "estado", "serial")
        self.tabla = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            height=8, style="Licencias.Treeview"
        )
        self.tabla.heading("usuario", text=_("Usuario"))
        self.tabla.heading("fecha_inicio", text=_("Inicio"))
        self.tabla.heading("fecha_fin", text=_("Fin"))
        self.tabla.heading("dias_restantes", text=_("Días"))
        self.tabla.heading("estado", text=_("Estado"))
        self.tabla.heading("serial", text=_("Serial"))
        self.tabla.column("usuario", width=110, anchor="center")
        self.tabla.column("fecha_inicio", width=90, anchor="center")
        self.tabla.column("fecha_fin", width=90, anchor="center")
        self.tabla.column("dias_restantes", width=60, anchor="center")
        self.tabla.column("estado", width=140, anchor="center")
        self.tabla.column("serial", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tabla.bind("<Double-1>", self.mostrar_detalle)
        self.cargar_licencias()

    def _color_estado(self, estado: str) -> str:
        if estado == "vigente":
            return COLOR_SUCCESS
        if "proxima" in estado or "próxima" in estado:
            return COLOR_WARNING
        if "vencida" in estado or "vencido" in estado:
            return COLOR_DANGER
        return COLOR_TEXT_LIGHT

    def _insertar_fila_coloreada(self, idx, valores):
        tag = "even" if idx % 2 == 0 else "odd"
        item = self.tabla.insert("", tk.END, values=valores, tags=(tag,))
        return item

    def cargar_licencias(self):
        self.tabla.delete(*self.tabla.get_children())
        usuarios = ServicioRegistro.obtener_todos_usuarios(excluir_desarrollador=True)
        for i, u in enumerate(usuarios):
            estado_info = ServicioLicencias.obtener_estado_licencia(u["usuario"])
            estado_texto = estado_info.get("mensaje", "")
            valores = (
                u["usuario"],
                u["fecha_inicio"],
                u["fecha_fin"],
                u.get("dias_restantes", 0),
                estado_texto,
                u["serial"],
            )
            tag = "even" if i % 2 == 0 else "odd"
            self.tabla.insert("", tk.END, values=valores, tags=(tag,))

        self.tabla.tag_configure("even", background=COLOR_CARD)
        self.tabla.tag_configure("odd", background=COLOR_ROW_ALT)

    def activar_licencia(self):
        usuario = self.entry_usuario.get().strip()
        serial = self.entry_serial.get().strip()
        if not usuario or not serial:
            messagebox.showwarning(_("Campos requeridos"), _("Ingrese usuario y serial."), parent=self)
            return
        valida, mensaje = ServicioLicencias.validar_licencia(usuario, serial)
        if valida:
            messagebox.showinfo(_("Licencia válida"), mensaje, parent=self)
        else:
            if messagebox.askyesno(
                _("Licencia inválida"),
                _("{0}\n¿Desea renovar la licencia?").format(mensaje),
                parent=self,
            ):
                ServicioLicencias.renovar_licencia(usuario)
                self.cargar_licencias()
                messagebox.showinfo(_("Renovada"), _("Licencia renovada por 30 días."), parent=self)
        self.entry_usuario.delete(0, tk.END)
        self.entry_serial.delete(0, tk.END)

    def ver_estado(self):
        usuario = self.entry_usuario.get().strip()
        if not usuario:
            messagebox.showwarning(_("Campo requerido"), _("Ingrese un nombre de usuario."), parent=self)
            return
        estado = ServicioLicencias.obtener_estado_licencia(usuario)
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            messagebox.showinfo(_("Sin licencia"), _("El usuario '{0}' no tiene licencia registrada.").format(usuario), parent=self)
        else:
            color_estado = self._color_estado(estado.get("estado", ""))
            icono_estado = "●"
            info = (
                _("Usuario: {0}\n"
                  "Estado: {1}\n"
                  "Inicio: {2}\n"
                  "Fin: {3}\n"
                  "Serial: {4}\n"
                  "Días restantes: {5}").format(
                    usuario,
                    f"{icono_estado} {estado.get('mensaje', '')}",
                    licencia["fecha_inicio"],
                    licencia["fecha_fin"],
                    licencia["serial"],
                    ServicioLicencias.dias_restantes(usuario),
                )
            )
            messagebox.showinfo(_("Estado de Licencia - {0}").format(usuario), info, parent=self)
        self.entry_usuario.delete(0, tk.END)

    def mostrar_detalle(self, event):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            return
        item = seleccionado[0]
        valores = self.tabla.item(item, "values")
        usuario = valores[0]

        estado = ServicioLicencias.obtener_estado_licencia(usuario)
        licencia = ServicioLicencias.obtener_licencia(usuario)

        edit_win = tk.Toplevel(self)
        edit_win.title(_("Licencia - {0}").format(usuario))
        edit_win.geometry("520x420+550+200")
        edit_win.config(bg=COLOR_BG)
        edit_win.transient(self)
        edit_win.grab_set()

        container = tk.Frame(edit_win, bg=COLOR_CARD, bd=0, padx=32, pady=32)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            container, text=_("Detalle de Licencia"),
            font=("Segoe UI", 16, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT
        ).pack(anchor="w", pady=(0, 20))

        estado_actual = estado.get("estado", "")
        color_estado = self._color_estado(estado_actual)
        estado_texto = estado.get("mensaje", "")

        estado_badge = tk.Frame(container, bg=color_estado, bd=0, padx=14, pady=6)
        estado_badge.pack(anchor="w", pady=(0, 20))
        tk.Label(
            estado_badge, text=estado_texto,
            font=("Segoe UI", 11, "bold"), bg=color_estado, fg="#FFFFFF"
        ).pack()

        info_frame = tk.Frame(container, bg=COLOR_CARD)
        info_frame.pack(fill=tk.X, pady=(0, 24))

        campos = [
            (_("Usuario:"), usuario),
            (_("Inicio:"), licencia["fecha_inicio"] if licencia else "-"),
            (_("Fin:"), licencia["fecha_fin"] if licencia else "-"),
            (_("Serial:"), licencia["serial"] if licencia else "-"),
            (_("Días restantes:"), str(ServicioLicencias.dias_restantes(usuario))),
        ]
        for i, (label, valor) in enumerate(campos):
            f = tk.Frame(info_frame, bg=COLOR_CARD)
            f.pack(fill=tk.X, pady=3)
            tk.Label(
                f, text=label, font=("Segoe UI", 11, "bold"),
                bg=COLOR_CARD, fg=COLOR_TEXT_LIGHT, width=14, anchor="w"
            ).pack(side=tk.LEFT)
            tk.Label(
                f, text=valor, font=("Segoe UI", 11),
                bg=COLOR_CARD, fg=COLOR_TEXT, anchor="w"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        def renovar():
            ServicioLicencias.renovar_licencia(usuario)
            self.cargar_licencias()
            messagebox.showinfo(_("Renovada"), _("Licencia renovada por 30 días."), parent=edit_win)
            edit_win.destroy()

        btn_frame = tk.Frame(container, bg=COLOR_CARD)
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        btn_renovar = tk.Button(
            btn_frame, text=_("Renovar Licencia"), bg=COLOR_SUCCESS, fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"), command=renovar,
            relief="flat", cursor="hand2", bd=0, padx=22, pady=8
        )
        btn_renovar.pack(side=tk.LEFT, padx=(0, 12))

        btn_cancelar = tk.Button(
            btn_frame, text=_("Cerrar"), bg=COLOR_DANGER, fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"), command=edit_win.destroy,
            relief="flat", cursor="hand2", bd=0, padx=22, pady=8
        )
        btn_cancelar.pack(side=tk.LEFT)
