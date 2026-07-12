from __future__ import annotations

import datetime
import logging
import os
import shutil
import sqlite3
import uuid
from typing import List

from retail.nucleo.base_datos._config_db import config_db
from retail.nucleo.configuraciones import APPDATA_PATH

BACKUP_DIR = os.path.join(APPDATA_PATH, "backups")
logger = logging.getLogger(__name__)


def _asegurar_directorio() -> None:
    os.makedirs(BACKUP_DIR, exist_ok=True)


def crear_backup() -> str:
    _asegurar_directorio()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    nombre = f"backup_{timestamp}_{uid}.db"
    ruta_destino = os.path.join(BACKUP_DIR, nombre)

    origen = config_db.nombre
    if not os.path.exists(origen):
        raise FileNotFoundError(f"No se encontró la base de datos: {origen}")

    shutil.copy2(origen, ruta_destino)
    logger.info("Backup creado: %s", ruta_destino)
    return ruta_destino


def listar_backups() -> List[dict[str, object]]:
    _asegurar_directorio()
    archivos = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        ruta = os.path.join(BACKUP_DIR, f)
        if os.path.isfile(ruta) and f.endswith(".db"):
            archivos.append({
                "nombre": f,
                "ruta": ruta,
                "tamano": os.path.getsize(ruta),
                "fecha": datetime.datetime.fromtimestamp(
                    os.path.getmtime(ruta)
                ).isoformat(),
            })
    return archivos


def restaurar_backup(ruta_backup: str) -> None:
    if not os.path.exists(ruta_backup):
        raise FileNotFoundError(f"No se encontró el archivo de backup: {ruta_backup}")

    origen = config_db.nombre
    if not os.path.exists(origen):
        raise FileNotFoundError(f"No se encontró la base de datos activa: {origen}")

    backup_previo = ruta_backup + ".prev"
    shutil.copy2(origen, backup_previo)
    logger.info("Respaldo previo guardado: %s", backup_previo)

    conn = sqlite3.connect(origen)
    try:
        backup_conn = sqlite3.connect(ruta_backup)
        backup_conn.backup(conn)
        backup_conn.close()
        conn.commit()
        logger.info("Base de datos restaurada desde: %s", ruta_backup)
    except Exception:
        conn.close()
        shutil.copy2(backup_previo, origen)
        logger.error("Error al restaurar, revirtiendo al respaldo previo")
        raise
    finally:
        conn.close()


def limpiar_backups(max_backups: int = 20) -> int:
    _asegurar_directorio()
    backups = sorted(
        [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")],
        key=os.path.getmtime,
    )
    eliminados = 0
    while len(backups) > max_backups:
        os.remove(backups.pop(0))
        eliminados += 1
    if eliminados:
        logger.info("Backups antiguos eliminados: %d", eliminados)
    return eliminados


def obtener_ruta_backup_dir() -> str:
    return BACKUP_DIR
