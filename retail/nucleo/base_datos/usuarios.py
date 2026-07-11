"""Operaciones para la tabla de usuarios y desarrollador."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from retail.nucleo.base_datos.conexion import conexion

registrador = logging.getLogger(__name__)


def verificar_usuario(usuario: str, contrasena: str) -> bool:
    clave = hashlib.sha256(contrasena.encode()).hexdigest()
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?",
            (usuario, clave),
        )
        return cursor.fetchone() is not None


def verificar_desarrollador(usuario: str, contrasena: str) -> bool:
    clave = hashlib.sha256(contrasena.encode()).hexdigest()
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM desarrollador WHERE usuario = ? AND contrasena = ?",
            (usuario, clave),
        )
        return cursor.fetchone() is not None


def buscar_usuario(usuario: str, contrasena: str) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?",
            (usuario, contrasena_hash),
        )
        return cursor.fetchone()


def insertar_usuario(usuario: str, contrasena: str) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)",
            (usuario, contrasena_hash),
        )


def eliminar_usuario(usuario_id: int) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))


def actualizar_usuario(usuario_id: int, usuario: str, contrasena: str) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        cursor.execute(
            "UPDATE usuarios SET usuario = ?, contrasena = ? WHERE id = ?",
            (usuario, contrasena_hash, usuario_id),
        )


def obtener_usuarios() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, contrasena FROM usuarios")
        return cursor.fetchall()
