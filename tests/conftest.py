from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Generator
import pytest


# ── Helpers compartidos para pruebas ────────────────────────────────────


def insertar_producto(db: Any, nombre: str, precio: float, costo: float, stock: int) -> Any:
    """Inserta un producto en la BD temporal y retorna su id."""
    db.agregar_producto(nombre, precio, costo, stock, 1, "default.png")
    with db.conexion() as conn:
        return conn.execute(
            "SELECT id_producto FROM inventario WHERE producto = ?", (nombre,)
        ).fetchone()[0]


def insertar_cliente(db: Any, nombres: str, apellidos: str, cedula: str, celular: str, zona: str = "Test") -> Any:
    """Inserta un cliente en la BD temporal y retorna su id."""
    db.insertar_cliente(nombres, apellidos, cedula, celular, zona)
    with db.conexion() as conn:
        return conn.execute(
            "SELECT id_cliente FROM clientes WHERE cedula = ?", (cedula,)
        ).fetchone()[0]


@pytest.fixture
def tmp_appdata(tmp_path: Path, monkeypatch: Any) -> Generator[Path, None, None]:
    """Crea un directorio temporal para APPDATA y parchea las rutas de configuraciones."""
    appdata_dir = tmp_path / "InnobertRetail"
    appdata_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr("sys.platform", "win32")

    import importlib
    import retail.nucleo.configuraciones as cfg
    importlib.reload(cfg)

    # Crear directorios que las funciones esperan que existan
    (appdata_dir / "config").mkdir(parents=True, exist_ok=True)
    (appdata_dir / "fotos").mkdir(parents=True, exist_ok=True)
    (appdata_dir / "Logo").mkdir(parents=True, exist_ok=True)

    yield appdata_dir

    importlib.reload(cfg)


@pytest.fixture
def cfg(tmp_appdata: Any) -> Any:
    """Referencia directa al módulo configuraciones con paths parcheados."""
    import retail.nucleo.configuraciones
    return retail.nucleo.configuraciones


@pytest.fixture
def db(cfg: Any, tmp_appdata: Path) -> Any:
    """Crea una BD temporal vacía usando base_datos."""
    import importlib
    from retail.nucleo import base_datos
    importlib.reload(base_datos)
    assert base_datos.obtener_ruta_base_datos().startswith(str(tmp_appdata.parent))
    base_datos.crear_tablas()
    return base_datos
