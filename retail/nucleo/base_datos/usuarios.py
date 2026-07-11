"""Operaciones para la tabla de usuarios y desarrollador."""

from __future__ import annotations

import logging
from typing import Any

from retail.nucleo.base_datos.conexion import conexion
from retail.nucleo.seguridad import (
    es_hash_sha256,
    hash_contrasena,
    verificar_contrasena,
)

registrador = logging.getLogger(__name__)


def _migrar_si_sha256(contrasena: str, hash_almacenado: str) -> str | None:
    if es_hash_sha256(hash_almacenado) and verificar_contrasena(contrasena, hash_almacenado):
        nuevo_hash = hash_contrasena(contrasena)
        return nuevo_hash
    return None


def verificar_usuario(usuario: str, contrasena: str) -> bool:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT contrasena FROM usuarios WHERE usuario = ?",
            (usuario,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            return False
        return verificar_contrasena(contrasena, resultado[0])


def verificar_desarrollador(usuario: str, contrasena: str) -> bool:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT contrasena FROM desarrollador WHERE usuario = ?",
            (usuario,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            return False
        return verificar_contrasena(contrasena, resultado[0])


def buscar_usuario(usuario: str, contrasena: str) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario = ?",
            (usuario,),
        )
        resultado = cursor.fetchone()
        if not resultado:
            return None
        hash_almacenado = resultado[2]
        if not verificar_contrasena(contrasena, hash_almacenado):
            return None
        nuevo_hash = _migrar_si_sha256(contrasena, hash_almacenado)
        if nuevo_hash:
            cursor.execute(
                "UPDATE usuarios SET contrasena = ? WHERE usuario = ?",
                (nuevo_hash, usuario),
            )
        return resultado


def insertar_usuario(usuario: str, contrasena: str) -> None:
    with conexion() as conn:
        cursor = conn.cursor()
        contrasena_hash = hash_contrasena(contrasena)
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
        contrasena_hash = hash_contrasena(contrasena)
        cursor.execute(
            "UPDATE usuarios SET usuario = ?, contrasena = ? WHERE id = ?",
            (usuario, contrasena_hash, usuario_id),
        )


def obtener_usuarios() -> list[tuple[Any, ...]]:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, contrasena FROM usuarios")
        return cursor.fetchall()
