"""Operaciones CRUD para la tabla de clientes."""

from __future__ import annotations

from typing import Any

from retail.nucleo.base_datos.conexion import conexion


def insertar_cliente(
    nombres: str, apellidos: str, cedula: str, celular: str, zona: str
) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nombres, apellidos, cedula, celular, zona) VALUES (?, ?, ?, ?, ?)",
            (nombres, apellidos, cedula, celular, zona),
        )


def obtener_clientes() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cliente, nombres, apellidos, cedula, celular, zona FROM clientes ORDER BY id_cliente ASC"
        )
        return cursor.fetchall()


def eliminar_cliente(id_cliente: int) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))


def actualizar_cliente(id_cliente: int, campo: str, valor: Any) -> None:
    _CAMPOS_VALIDOS = {
        "nombres", "apellidos", "cedula", "celular", "zona",
    }
    if campo not in _CAMPOS_VALIDOS:
        raise ValueError(f"Campo inválido: {campo}")
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE clientes SET {campo} = ? WHERE id_cliente = ?",
            (valor, id_cliente),
        )


def buscar_cliente_por_cedula(cedula: str) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_cliente FROM clientes WHERE cedula = ?", (cedula,)
        )
        return cursor.fetchone()


def combobox_clientes() -> list[str]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT nombres FROM clientes ORDER BY nombres ASC")
        nombres = [row[0] for row in cursor.fetchall()]
    return nombres
