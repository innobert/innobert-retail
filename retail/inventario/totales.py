from __future__ import annotations

import tkinter as tk
from typing import Any
from retail.nucleo.configuraciones import COLOR_FONDO_TABLA, COLOR_VERDE, COLOR_ROJO
from retail.nucleo.base_datos import obtener_productos


def mostrar_totales_inventario(parent: Any) -> None:
    """
    Muestra una ventana con el total del inventario y las ganancias.
    """
    # Calcular totales
    productos = obtener_productos()
    total_inventario = sum(
        (p[2] or 0) * (p[4] or 0) for p in productos
    )  # precio * stock
    total_costo = sum((p[3] or 0) * (p[4] or 0) for p in productos)  # costo * stock
    total_ganancia = total_inventario - total_costo

    def peso_colombiano(value: float | int) -> str:
        return f"${value:,.0f}".replace(",", ".")

    top = tk.Toplevel(parent)
    top.title("Totales del Inventario")
    top.geometry("520x320+400+180")
    top.configure(bg=COLOR_FONDO_TABLA)
    top.resizable(False, False)
    top.maxsize(520, 320)
    # Permitir cerrar con Esc
    top.bind("<Escape>", lambda e: top.destroy())
    # Activar automáticamente la ventana
    top.focus_force()

    # Título profesional
    tk.Label(
        top,
        text="Totales del Inventario",
        font=("Helvetica", 20, "bold"),
        bg=COLOR_VERDE,
        fg="white",
        pady=18,
    ).pack(fill="x")

    frame = tk.Frame(top, bg=COLOR_FONDO_TABLA)
    frame.pack(fill="both", expand=True, padx=40, pady=40)

    # Etiquetas y valores
    tk.Label(
        frame,
        text="Total en Inventario:",
        font=("Helvetica", 15, "bold"),
        bg=COLOR_FONDO_TABLA,
        anchor="w",
    ).grid(row=0, column=0, sticky="w", pady=10)
    tk.Label(
        frame,
        text=peso_colombiano(total_inventario),
        font=("Helvetica", 15),
        bg=COLOR_FONDO_TABLA,
        fg="#1976D2",
        anchor="e",
    ).grid(row=0, column=1, sticky="e", pady=10)

    tk.Label(
        frame,
        text="Total en Costos:",
        font=("Helvetica", 15, "bold"),
        bg=COLOR_FONDO_TABLA,
        anchor="w",
    ).grid(row=1, column=0, sticky="w", pady=10)
    tk.Label(
        frame,
        text=peso_colombiano(total_costo),
        font=("Helvetica", 15),
        bg=COLOR_FONDO_TABLA,
        fg=COLOR_ROJO,
        anchor="e",
    ).grid(row=1, column=1, sticky="e", pady=10)

    tk.Label(
        frame,
        text="Ganancia Potencial:",
        font=("Helvetica", 15, "bold"),
        bg=COLOR_FONDO_TABLA,
        anchor="w",
    ).grid(row=2, column=0, sticky="w", pady=10)
    tk.Label(
        frame,
        text=peso_colombiano(total_ganancia),
        font=("Helvetica", 15, "bold"),
        bg=COLOR_FONDO_TABLA,
        fg="green" if total_ganancia >= 0 else "red",
        anchor="e",
    ).grid(row=2, column=1, sticky="e", pady=10)

    # Separador visual
    sep = tk.Frame(frame, bg="#BDBDBD", height=2)
    sep.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(20, 0))

    # No se agrega botón de cerrar, se usa solo la X de la ventana
