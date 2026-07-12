#!/usr/bin/env python3
"""Script para generar ejecutable con PyInstaller."""

import subprocess
import sys


def main():
    args = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--name", "InnobertRetail",
        "--icon", "icono.ico",
        "--windowed",
        "--onefile",
        # Recursos del programa
        "--add-data", "img;img",
        "--add-data", "fotos;fotos",
        "--add-data", "icono.ico;.",
        "--add-data", "retail/traducciones/es.json;retail/traducciones",
        # Hidden imports que PyInstaller puede no detectar
        "--hidden-import", "charset_normalizer",
        "--hidden-import", "bcrypt",
        "--hidden-import", "reportlab.lib.pagesizes",
        "--hidden-import", "reportlab.lib.colors",
        "--hidden-import", "PIL._tkinter_finder",
        "inicio.py",
    ]
    print("Ejecutando:", " ".join(args))
    result = subprocess.run(args, cwd=sys.path[0] or ".")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
