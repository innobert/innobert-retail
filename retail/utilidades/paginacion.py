import tkinter as tk


class PaginacionWidget(tk.Frame):
    def __init__(self, parent, on_anterior, on_siguiente, actualizar_texto, bg="#E6D9E3", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.on_anterior = on_anterior
        self.on_siguiente = on_siguiente
        self.actualizar_texto = actualizar_texto

        self.btn_anterior = tk.Button(
            self,
            text="◀ Anterior",
            command=self._pagina_anterior,
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            font=("Helvetica", 10, "bold")
        )
        self.btn_anterior.pack(side="left", padx=5)

        self.label_paginacion = tk.Label(
            self,
            text="",
            font=("Helvetica", 10, "bold"),
            bg=bg
        )
        self.label_paginacion.pack(side="left", padx=20, expand=True)

        self.btn_siguiente = tk.Button(
            self,
            text="Siguiente ▶",
            command=self._pagina_siguiente,
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            font=("Helvetica", 10, "bold")
        )
        self.btn_siguiente.pack(side="right", padx=5)

        self.actualizar()

    def _pagina_anterior(self):
        self.on_anterior()
        self.actualizar()

    def _pagina_siguiente(self):
        self.on_siguiente()
        self.actualizar()

    def actualizar(self):
        texto = self.actualizar_texto()
        self.label_paginacion.config(text=texto)
