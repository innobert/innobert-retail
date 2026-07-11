import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from retail.nucleo.servicios.sesion.servicio_licencias import ServicioLicencias
from retail.nucleo.servicios.sesion.servicio_registro import ServicioRegistro


class VentanaLicencias(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Licencias")
        self.geometry("820x520+300+60")
        self.resizable(False, False)
        self.config(bg="#E6D9E3")
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.widgets()

    def widgets(self):
        frame = tk.Frame(self, bg="#FFFFFF", bd=2, relief="groove")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            frame, text="Gestión de Licencias", font=("Helvetica", 18, "bold"),
            bg="#FFFFFF", fg="#333333"
        ).pack(pady=(10, 10))

        # Frame superior: estado del usuario actual y activación
        top_frame = tk.Frame(frame, bg="#FFFFFF")
        top_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Sección de activación
        act_frame = tk.Frame(top_frame, bg="#FFFFFF")
        act_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(act_frame, text="Usuario:", font=("Helvetica", 12), bg="#FFFFFF").grid(row=0, column=0, sticky="e", padx=(0, 5), pady=3)
        self.entry_usuario = ttk.Entry(act_frame, font=("Helvetica", 12), width=18)
        self.entry_usuario.grid(row=0, column=1, padx=(0, 10), pady=3)

        tk.Label(act_frame, text="Serial:", font=("Helvetica", 12), bg="#FFFFFF").grid(row=0, column=2, sticky="e", padx=(0, 5), pady=3)
        self.entry_serial = ttk.Entry(act_frame, font=("Helvetica", 12), width=30)
        self.entry_serial.grid(row=0, column=3, padx=(0, 10), pady=3)

        self.btn_activar = tk.Button(
            act_frame, text="Activar", bg="#4CAF50", fg="#fff", font=("Helvetica", 11, "bold"),
            command=self.activar_licencia, relief="flat", cursor="hand2", width=10
        )
        self.btn_activar.grid(row=0, column=4, padx=(0, 5), pady=3)

        # Botón para ver estado detallado
        self.btn_estado = tk.Button(
            act_frame, text="Ver Estado", bg="#2196F3", fg="#fff", font=("Helvetica", 11, "bold"),
            command=self.ver_estado, relief="flat", cursor="hand2", width=10
        )
        self.btn_estado.grid(row=0, column=5, pady=3)

        # Tabla
        tabla_frame = tk.Frame(frame, bg="#FFFFFF")
        tabla_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background="#E6D9E3", foreground="#333")
        style.configure("Treeview", font=("Helvetica", 13), rowheight=32, background="#fff", fieldbackground="#fff")
        style.map("Treeview", background=[("selected", "#222")], foreground=[("selected", "#fff")])

        columns = ("usuario", "fecha_inicio", "fecha_fin", "dias_restantes", "estado", "serial")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=7, style="Treeview")
        self.tabla.heading("usuario", text="Usuario")
        self.tabla.heading("fecha_inicio", text="Inicio")
        self.tabla.heading("fecha_fin", text="Fin")
        self.tabla.heading("dias_restantes", text="Días")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("serial", text="Serial")
        self.tabla.column("usuario", width=100, anchor="center")
        self.tabla.column("fecha_inicio", width=80, anchor="center")
        self.tabla.column("fecha_fin", width=80, anchor="center")
        self.tabla.column("dias_restantes", width=60, anchor="center")
        self.tabla.column("estado", width=120, anchor="center")
        self.tabla.column("serial", width=120, anchor="center")
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabla.bind("<Double-1>", self.mostrar_detalle)
        self.cargar_licencias()

    def on_close(self):
        self.grab_release()
        self.destroy()

    def cargar_licencias(self):
        self.tabla.delete(*self.tabla.get_children())
        usuarios = ServicioRegistro.obtener_todos_usuarios(excluir_desarrollador=True)
        for u in usuarios:
            estado_info = ServicioLicencias.obtener_estado_licencia(u["usuario"])
            self.tabla.insert("", tk.END, values=(
                u["usuario"],
                u["fecha_inicio"],
                u["fecha_fin"],
                u.get("dias_restantes", 0),
                estado_info.get("mensaje", ""),
                u["serial"]
            ))

    def activar_licencia(self):
        usuario = self.entry_usuario.get().strip()
        serial = self.entry_serial.get().strip()
        if not usuario or not serial:
            messagebox.showwarning("Campos requeridos", "Ingrese usuario y serial.", parent=self)
            return
        valida, mensaje = ServicioLicencias.validar_licencia(usuario, serial)
        if valida:
            messagebox.showinfo("Licencia válida", mensaje, parent=self)
        else:
            if messagebox.askyesno("Licencia inválida", f"{mensaje}\n¿Desea renovar la licencia?", parent=self):
                ServicioLicencias.renovar_licencia(usuario)
                self.cargar_licencias()
                messagebox.showinfo("Renovada", "Licencia renovada por 30 días.", parent=self)
        self.entry_usuario.delete(0, tk.END)
        self.entry_serial.delete(0, tk.END)

    def ver_estado(self):
        usuario = self.entry_usuario.get().strip()
        if not usuario:
            messagebox.showwarning("Campo requerido", "Ingrese un nombre de usuario.", parent=self)
            return
        estado = ServicioLicencias.obtener_estado_licencia(usuario)
        licencia = ServicioLicencias.obtener_licencia(usuario)
        if not licencia:
            messagebox.showinfo("Sin licencia", f"El usuario '{usuario}' no tiene licencia registrada.", parent=self)
        else:
            info = (
                f"Usuario: {usuario}\n"
                f"Estado: {estado.get('mensaje', '')}\n"
                f"Inicio: {licencia['fecha_inicio']}\n"
                f"Fin: {licencia['fecha_fin']}\n"
                f"Serial: {licencia['serial']}\n"
                f"Días restantes: {ServicioLicencias.dias_restantes(usuario)}"
            )
            messagebox.showinfo(f"Estado de Licencia - {usuario}", info, parent=self)
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
        edit_win.title(f"Licencia - {usuario}")
        edit_win.geometry("500x400+500+200")
        edit_win.config(bg="#FFFFFF")
        edit_win.transient(self)
        edit_win.grab_set()

        frame = tk.Frame(edit_win, bg="#FFFFFF", bd=2, relief="groove")
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        tk.Label(frame, text=f"Gestión de Licencia", font=("Helvetica", 16, "bold"), bg="#FFFFFF", fg="#333").pack(pady=(10, 15))

        info_text = f"Usuario: {usuario}\n\n"
        if licencia:
            info_text += (
                f"Estado: {estado.get('mensaje', '')}\n"
                f"Inicio: {licencia['fecha_inicio']}\n"
                f"Fin: {licencia['fecha_fin']}\n"
                f"Serial: {licencia['serial']}\n"
                f"Días restantes: {ServicioLicencias.dias_restantes(usuario)}"
            )
        else:
            info_text += "Sin licencia registrada."

        tk.Label(frame, text=info_text, font=("Helvetica", 12), bg="#FFFFFF", fg="#333", justify=tk.LEFT).pack(pady=10)

        def renovar():
            ServicioLicencias.renovar_licencia(usuario)
            self.cargar_licencias()
            messagebox.showinfo("Renovada", "Licencia renovada por 30 días.", parent=edit_win)
            edit_win.destroy()

        def cancelar():
            edit_win.destroy()

        btn_frame = tk.Frame(frame, bg="#FFFFFF")
        btn_frame.pack(pady=20)

        btn_renovar = tk.Button(
            btn_frame, text="Renovar Licencia", bg="#4CAF50", fg="#fff", font=("Helvetica", 13, "bold"),
            command=renovar, relief="flat", cursor="hand2", width=16
        )
        btn_renovar.pack(side=tk.LEFT, padx=10)

        btn_cancelar = tk.Button(
            btn_frame, text="Cerrar", bg="#F44336", fg="#fff", font=("Helvetica", 13, "bold"),
            command=cancelar, relief="flat", cursor="hand2", width=10
        )
        btn_cancelar.pack(side=tk.LEFT, padx=10)
