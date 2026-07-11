"""Gestión de conexión y transacciones con SQLite."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from typing import Any, Generator

from retail.nucleo.base_datos._config_db import config_db

registrador = logging.getLogger(__name__)


def obtener_conexion() -> sqlite3.Connection:
    return sqlite3.connect(config_db.nombre)


@contextmanager
def conexion() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(config_db.nombre)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ejecutar_consulta(query: str, params: tuple[Any, ...] = ()) -> Any:
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
