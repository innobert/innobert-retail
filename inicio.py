#!/usr/bin/env python3
import hashlib
import os
import socket
import sys
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def adquirir_instancia_unica() -> socket.socket | None:
    puerto = 50000 + int(hashlib.sha256(__file__.encode()).hexdigest(), 16) % 10000
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", puerto))
        sock.listen()
        return sock
    except (socket.error, OSError):
        return None


def main():
    sock = adquirir_instancia_unica()
    if sock is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Instancia duplicada",
            "El programa ya está en ejecución.",
        )
        root.destroy()
        sys.exit(1)

    from retail.nucleo.principal import Principal

    app = Principal()
    app.mainloop()


if __name__ == "__main__":
    main()
