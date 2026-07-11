"""Creación del esquema de base de datos y datos semilla."""

from __future__ import annotations

import ctypes
import datetime
import logging
import os
from pathlib import Path

from retail.nucleo.base_datos._config_db import config_db
from retail.nucleo.base_datos.conexion import conexion
from retail.nucleo.configuraciones import asegurar_directorios
from retail.nucleo.seguridad import hash_contrasena

registrador = logging.getLogger(__name__)


def crear_tablas() -> None:
    asegurar_directorios()
    ruta_appdata = Path(config_db.nombre).parent
    if os.name == "nt":
        try:
            if not ruta_appdata.exists():
                ruta_appdata.mkdir(parents=True, exist_ok=True)
            FILE_ATTRIBUTE_HIDDEN = 0x02
            FILE_ATTRIBUTE_READONLY = 0x01
            actual = ctypes.windll.kernel32.GetFileAttributesW(str(ruta_appdata))
            if actual != -1:
                nuevo = actual | FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_READONLY
                ctypes.windll.kernel32.SetFileAttributesW(str(ruta_appdata), nuevo)
        except Exception:
            registrador.warning(
                "No se pudieron ocultar los atributos de la carpeta AppData",
                exc_info=True,
            )

    with conexion() as conn:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS desarrollador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                fecha_inicio TEXT,
                fecha_fin TEXT,
                serial TEXT
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombres TEXT NOT NULL,
                apellidos TEXT,
                cedula INTEGER UNIQUE,
                celular INTEGER UNIQUE,
                zona TEXT
            );

            CREATE TABLE IF NOT EXISTS inventario (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT UNIQUE NOT NULL,
                precio REAL NOT NULL,
                costo REAL NOT NULL,
                stock INTEGER NOT NULL,
                estado INTEGER CHECK (estado IN (0,1)) NOT NULL,
                imagen TEXT DEFAULT 'default.png'
            );

            CREATE TABLE IF NOT EXISTS ventas (
                id_ventas INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT UNIQUE NOT NULL,
                cliente_id INTEGER,
                cliente_rapido TEXT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                total REAL NOT NULL,
                ganancia REAL NOT NULL,
                monto_recibido REAL DEFAULT 0,
                vuelto REAL DEFAULT 0,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id_cliente)
            );

            CREATE TABLE IF NOT EXISTS detalle_venta (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ventas INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(id_ventas) REFERENCES ventas(id_ventas),
                FOREIGN KEY(id_producto) REFERENCES inventario(id_producto)
            );

            CREATE TABLE IF NOT EXISTS deudas (
                id_deuda INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                saldo REAL NOT NULL,
                estado TEXT CHECK(estado IN ('ABIERTA','PAGADA')) DEFAULT 'ABIERTA',
                usuario_creacion TEXT,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id_cliente)
            );

            CREATE TABLE IF NOT EXISTS detalle_deuda (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_deuda INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(id_deuda) REFERENCES deudas(id_deuda),
                FOREIGN KEY(id_producto) REFERENCES inventario(id_producto)
            );

            CREATE TABLE IF NOT EXISTS pagos_deuda (
                id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                id_deuda INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                usuario TEXT NOT NULL,
                FOREIGN KEY(id_deuda) REFERENCES deudas(id_deuda)
            );

            CREATE TABLE IF NOT EXISTS ganancias (
                id_ganancia INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT UNIQUE NOT NULL,
                total_dia REAL DEFAULT 0,
                total_semana REAL DEFAULT 0,
                total_mes REAL DEFAULT 0,
                total_anio REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS historial_ventas (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ventas INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                subtotal REAL,
                accion TEXT,
                usuario TEXT,
                fecha TEXT,
                hora TEXT,
                detalle TEXT,
                monto_recibido REAL DEFAULT 0,
                vuelto REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS historial_deudas (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                id_deuda INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                subtotal REAL,
                accion TEXT,
                usuario TEXT,
                fecha TEXT,
                hora TEXT,
                detalle TEXT,
                abono REAL DEFAULT 0,
                recibido REAL DEFAULT 0,
                vuelto REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS papelera_ventas (
                id_papelera INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ventas INTEGER,
                numero_factura TEXT,
                cliente_id INTEGER,
                cliente_rapido TEXT,
                fecha TEXT,
                hora TEXT,
                total REAL,
                ganancia REAL,
                monto_recibido REAL,
                vuelto REAL,
                estado TEXT,
                usuario_elimino TEXT,
                fecha_eliminacion TEXT,
                detalle TEXT
            );

            CREATE TABLE IF NOT EXISTS papelera_deudas (
                id_papelera INTEGER PRIMARY KEY AUTOINCREMENT,
                id_deuda INTEGER,
                numero_factura TEXT,
                cliente_id INTEGER,
                fecha TEXT,
                total REAL,
                saldo REAL,
                estado TEXT,
                usuario_elimino TEXT,
                fecha_eliminacion TEXT,
                detalle TEXT
            );

            CREATE TABLE IF NOT EXISTS historial_inventario (
                id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER,
                dia TEXT,
                fecha TEXT,
                hora TEXT,
                accion TEXT,
                pedido INTEGER,
                stock INTEGER,
                precio REAL,
                costo REAL,
                ganancia REAL,
                total REAL
            );
        """)

        cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);
            CREATE INDEX IF NOT EXISTS idx_ventas_numero_factura ON ventas(numero_factura);
            CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id);

            CREATE INDEX IF NOT EXISTS idx_deudas_cliente ON deudas(cliente_id);
            CREATE INDEX IF NOT EXISTS idx_deudas_estado ON deudas(estado);
            CREATE INDEX IF NOT EXISTS idx_deudas_fecha ON deudas(fecha);

            CREATE INDEX IF NOT EXISTS idx_inventario_producto ON inventario(producto);
            CREATE INDEX IF NOT EXISTS idx_inventario_estado ON inventario(estado);

            CREATE INDEX IF NOT EXISTS idx_detalle_venta_id_ventas ON detalle_venta(id_ventas);
            CREATE INDEX IF NOT EXISTS idx_detalle_deuda_id_deuda ON detalle_deuda(id_deuda);

            CREATE INDEX IF NOT EXISTS idx_pagos_deuda_id_deuda ON pagos_deuda(id_deuda);

            CREATE INDEX IF NOT EXISTS idx_historial_ventas_id_ventas ON historial_ventas(id_ventas);
            CREATE INDEX IF NOT EXISTS idx_historial_deudas_id_deuda ON historial_deudas(id_deuda);
            CREATE INDEX IF NOT EXISTS idx_historial_inventario_id_producto ON historial_inventario(id_producto);

            CREATE INDEX IF NOT EXISTS idx_papelera_ventas_fecha ON papelera_ventas(fecha_eliminacion);
            CREATE INDEX IF NOT EXISTS idx_papelera_deudas_fecha ON papelera_deudas(fecha_eliminacion);
        """)

        clave_admin = hash_contrasena("ingsoftware.99")
        cursor.execute(
            "INSERT OR IGNORE INTO desarrollador (usuario, contrasena) VALUES (?, ?)",
            ("innobertdev", clave_admin),
        )

        fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
        fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime(
            "%Y-%m-%d"
        )
        serial = "USR-PRU-" + fecha_inicio.replace("-", "")
        clave_prueba = hash_contrasena("prueba")
        cursor.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
            ("prueba", clave_prueba, fecha_inicio, fecha_fin, serial),
        )
