from __future__ import annotations

import os
import sqlite3
import tempfile

import pytest

from retail.nucleo.base_datos._config_db import config_db
from retail.nucleo.base_datos.backup import (
    crear_backup,
    limpiar_backups,
    listar_backups,
    obtener_ruta_backup_dir,
    restaurar_backup,
)


@pytest.fixture(autouse=True)
def _db_temp():
    ruta_original = config_db.nombre
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE prueba (id INTEGER PRIMARY KEY, valor TEXT)")
        conn.execute("INSERT INTO prueba (valor) VALUES ('original')")
        conn.commit()
        conn.close()
        config_db.nombre = db_path
        backup_dir = os.path.join(tmp, "backups")
        import retail.nucleo.base_datos.backup as bkp
        bkp.BACKUP_DIR = backup_dir
        yield db_path
    config_db.nombre = ruta_original


def test_crear_backup():
    ruta = crear_backup()
    assert os.path.exists(ruta)
    assert ruta.endswith(".db")


def test_crear_backup_sin_origen():
    config_db.nombre = "/no/existe/db.db"
    with pytest.raises(FileNotFoundError):
        crear_backup()


def test_listar_backups():
    crear_backup()
    crear_backup()
    lista = listar_backups()
    assert len(lista) == 2
    for b in lista:
        assert "nombre" in b
        assert "ruta" in b
        assert "tamano" in b
        assert "fecha" in b


def test_listar_backups_vacio():
    lista = listar_backups()
    assert lista == []


def test_restaurar_backup():
    ruta_bkp = crear_backup()
    conn = sqlite3.connect(config_db.nombre)
    conn.execute("UPDATE prueba SET valor = 'modificado'")
    conn.commit()
    conn.close()
    restaurar_backup(ruta_bkp)
    conn = sqlite3.connect(config_db.nombre)
    valor = conn.execute("SELECT valor FROM prueba WHERE id = 1").fetchone()[0]
    conn.close()
    assert valor == "original"


def test_restaurar_backup_inexistente():
    with pytest.raises(FileNotFoundError):
        restaurar_backup("/no/existe/backup.db")


def test_limpiar_backups():
    for _ in range(5):
        crear_backup()
    assert len(listar_backups()) == 5
    assert limpiar_backups(max_backups=3) == 2
    assert len(listar_backups()) == 3


def test_limpiar_backups_sin_exceso():
    crear_backup()
    assert limpiar_backups(max_backups=20) == 0


def test_obtener_ruta_backup_dir():
    ruta = obtener_ruta_backup_dir()
    assert isinstance(ruta, str)
    assert ruta.endswith("backups")
