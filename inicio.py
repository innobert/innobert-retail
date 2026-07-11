#!/usr/bin/env python3
"""Punto de entrada de la aplicación.

Antes de crear la GUI se asegura que no exista otra instancia en ejecución
usando un socket en localhost y un puerto determinístico.
"""
import hashlib
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tkinter import Tk, messagebox

from retail.nucleo.principal import Principal


def obtener_puerto_instancia() -> int:
    """Calcula un puerto único en función de la ruta del ejecutable."""
    ruta = os.path.abspath(sys.argv[0])
    h = hashlib.sha256(ruta.encode("utf-8")).digest()
    return 50000 + ((h[0] << 8) | h[1]) % 10000


def adquirir_instancia_unica() -> socket.socket | None:
    """Intenta adquirir la instancia única devolviendo el socket si tiene éxito."""
    puerto = obtener_puerto_instancia()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", puerto))
        sock.listen(1)
    except OSError:
        sock.close()
        return None
    return sock


def _asegurar_una_instancia_o_salir() -> None:
    sock = adquirir_instancia_unica()
    if sock is None:
        root = Tk()
        root.withdraw()
        messagebox.showinfo(
            "Innobert Retail",
            "Otra instancia ya está en ejecución. Sólo se permite una instancia.",
            parent=root,
        )
        try:
            root.destroy()
        except Exception:
            pass
        sys.exit(0)


if __name__ == "__main__":
    _asegurar_una_instancia_o_salir()
    app = Principal()
    app.mainloop()
