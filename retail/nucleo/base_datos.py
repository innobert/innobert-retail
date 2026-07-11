"""
database.py

Módulo para gestionar la conexión y operaciones básicas con la base de datos SQLite
para el sistema de gestión de licorería.

Incluye funciones para conectar y obtener un cursor.
"""

# =========================
# CONFIGURACIÓN Y CONEXIÓN
# =========================

import sqlite3
import os
import datetime
import hashlib
import ctypes
import random
from retail.nucleo.configuraciones import (
    obtener_ruta_base_datos,
    asegurar_directorios,
)

DB_NAME = obtener_ruta_base_datos()  # Usar siempre la ruta absoluta desde config.py


def get_connection():
    return sqlite3.connect(DB_NAME)


def ejecutar_consulta(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    resultado = cursor.fetchone()
    conn.close()
    return resultado


# =========================
# CREATE_TABLES()
# =========================

def create_tables():
    asegurar_directorios()  # <-- Crea carpetas si no existen
    # Protección de carpeta en Windows: oculta y solo lectura
    appdata_path = os.path.dirname(DB_NAME)
    if os.name == "nt":
        try:
            # Intentar usar la API de Windows para no abrir consolas
            FILE_ATTRIBUTE_HIDDEN = 0x02
            FILE_ATTRIBUTE_READONLY = 0x01
            # Asegurar que la carpeta existe antes de ajustar atributos
            if not os.path.exists(appdata_path):
                os.makedirs(appdata_path, exist_ok=True)
            # Obtener atributos actuales
            GetFileAttributesW = ctypes.windll.kernel32.GetFileAttributesW
            SetFileAttributesW = ctypes.windll.kernel32.SetFileAttributesW
            current = GetFileAttributesW(appdata_path)
            if current != -1:
                new_attrs = current | FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_READONLY
                SetFileAttributesW(appdata_path, new_attrs)
        except Exception:
            # Fallback a os.system solo si falla (aunque esto puede abrir consola)
            try:
                os.system(f'attrib +h "{appdata_path}"')
                os.system(f'attrib +r "{appdata_path}"')
            except Exception:
                pass
    conn = get_connection()
    cursor = conn.cursor()

    # Crear tablas (con IF NOT EXISTS para evitar errores si se ejecuta varias veces)
    cursor.executescript(
        """
        -- =========================
        -- SEGURIDAD / USUARIOS
        -- =========================
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

        -- =========================
        -- CATÁLOGOS
        -- =========================
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

        -- =========================
        -- TRANSACCIONES
        -- =========================
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

        -- =========================
        -- CRÉDITOS/DEUDAS (INDEPENDIENTE)
        -- =========================
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

        -- =========================
        -- FINANZAS
        -- =========================
        CREATE TABLE IF NOT EXISTS ganancias (
            id_ganancia INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT UNIQUE NOT NULL,
            total_dia REAL DEFAULT 0,
            total_semana REAL DEFAULT 0,
            total_mes REAL DEFAULT 0,
            total_anio REAL DEFAULT 0
        );

        -- =========================
        -- HISTORIALES
        -- =========================

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

        -- =========================
        -- PAPELERA (ELIMINADOS)
        -- =========================
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
        """
    )
    """)

    # Insertar usuario admin solo si existe (encriptado)
    admin_pass = hashlib.sha256("ingsoftware.99".encode()).hexdigest()
    cursor.execute(
        "INSERT OR IGNORE INTO desarrollador (usuario, contrasena) VALUES (?, ?)",
        ("innobertdev", admin_pass),
    )

    # Insertar usuario de prueba con suscripción gratuita de un mes desde hoy (encriptado)
    fecha_inicio = datetime.datetime.now().strftime("%Y-%m-%d")
    fecha_fin = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    serial = "USR-PRU-" + fecha_inicio.replace("-", "")
    prueba_pass = hashlib.sha256("prueba".encode()).hexdigest()
    cursor.execute(
        "INSERT OR IGNORE INTO usuarios (usuario, contrasena, fecha_inicio, fecha_fin, serial) VALUES (?, ?, ?, ?, ?)",
        (
            "prueba",
            prueba_pass,
            fecha_inicio,
            fecha_fin,
            serial
        ),
    )

    conn.commit()
    conn.close()


# =========================
# FUNCIONES CLIENTES
# =========================


def insertar_cliente(nombres, apellidos, cedula, celular, zona):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO clientes (nombres, apellidos, cedula, celular, zona)
        VALUES (?, ?, ?, ?, ?)
        """,
        (nombres, apellidos, cedula, celular, zona),
    )
    conn.commit()
    conn.close()


def obtener_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_cliente, nombres, apellidos, cedula, celular, zona FROM clientes ORDER BY id_cliente ASC"
    )
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def eliminar_cliente(id_cliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    conn.commit()
    conn.close()


def actualizar_cliente(id_cliente, campo, valor):
    conn = get_connection()
    cursor = conn.cursor()
    query = f"UPDATE clientes SET {campo} = ? WHERE id_cliente = ?"
    cursor.execute(query, (valor, id_cliente))
    conn.commit()
    conn.close()


def buscar_cliente_por_cedula(cedula):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente FROM clientes WHERE cedula = ?", (cedula,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado


# =========================
# FUNCIONES INVENTARIO
# =========================


def add_producto(producto, precio, costo, stock, estado, imagen):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO inventario (producto, precio, costo, stock, estado, imagen)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (producto, precio, costo, stock, estado, imagen),
    )
    conn.commit()
    conn.close()


def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventario")
    productos = cursor.fetchall()
    conn.close()
    return productos


def actualizar_producto(id_producto, producto, precio, costo, stock, estado, imagen):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE inventario
        SET producto = ?, precio = ?, costo = ?, stock = ?, estado = ?, imagen = ?
        WHERE id_producto = ?
        """,
        (producto, precio, costo, stock, estado, imagen, id_producto),
    )
    conn.commit()
    conn.close()


def dlt_producto(id_producto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventario WHERE id_producto = ?", (id_producto,))
    conn.commit()
    conn.close()


def registrar_historial_inventario(id_producto, accion, pedido, stock, precio, costo, ganancia, total):
    """
    Registra un evento en el historial del inventario.
    """
    conn = get_connection()
    cursor = conn.cursor()

    dia = datetime.datetime.now().strftime("%A")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        INSERT INTO historial_inventario (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_producto, dia, fecha, hora, accion, pedido, stock, precio, costo, ganancia, total),
    )

    conn.commit()
    conn.close()


def combobox_productos():
    """
    Devuelve una lista de nombres de productos para usar en el combobox de búsqueda.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT producto FROM inventario")
    productos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return productos


def editar_producto(id_producto):
    """
    Devuelve los datos de un producto específico por su id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM inventario WHERE id_producto = ?",
        (id_producto,),
    )
    producto = cursor.fetchone()
    conn.close()
    return producto


def buscar_productos_por_nombre(nombre):
    """
    Devuelve los productos que coinciden parcialmente con el nombre dado.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM inventario WHERE producto LIKE ?",
        (f"%{nombre}%",),
    )
    productos = cursor.fetchall()
    conn.close()
    return productos


# =========================
# FUNCIONES VENTAS
# =========================

def generar_numero_factura_unico(cursor):
    max_intentos = 1000
    for _ in range(max_intentos):
        numero = f"{random.randint(100000, 999999)}"
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE numero_factura = ?", (numero,))
        if cursor.fetchone()[0] > 0:
            continue
        cursor.execute("SELECT COUNT(*) FROM papelera_ventas WHERE numero_factura = ?", (numero,))
        if cursor.fetchone()[0] > 0:
            continue
        return numero
    return f"{random.randint(100000, 999999)}"


def generar_id_venta_rapida(cursor):
    fecha_db = datetime.datetime.now().strftime("%Y-%m-%d")
    fecha_id = datetime.datetime.now().strftime("%Y%m%d")
    cursor.execute("""
        SELECT COUNT(*)
        FROM ventas
        WHERE fecha = ?
          AND cliente_id IS NULL
          AND cliente_rapido LIKE ?
    """, (fecha_db, f"VR-{fecha_id}-%"))
    count = cursor.fetchone()[0] + 1
    return f"VR-{fecha_id}-{count:03d}"


def crear_venta(cliente_id=None, items=None, monto_recibido=0, usuario="sistema"):
    """
    Crear una venta directa (RÁPIDA o x Mayor).
    
    - Las ventas son SIEMPRE de contado (se realiza el pago en el momento)
    - El cliente es OPCIONAL (ventas rápidas sin cliente)
    - Cliente es REQUERIDO solo para facturas al por mayor    
 
    """
    if not items or len(items) == 0:
        raise ValueError("No hay items para crear la venta")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Generate numero_factura - ÚNICO Y ALEATORIO
        numero_factura = generar_numero_factura_unico(cursor)

        # Validate and gather latest product info
        total = 0
        total_ganancia = 0
        item_rows = []
        for it in items:
            pid = int(it.get("id_producto"))
            cant = int(it.get("cantidad", 0))
            if cant <= 0:
                raise ValueError(f"Cantidad inválida para producto {pid}")
            cursor.execute("SELECT producto, precio, costo, stock FROM inventario WHERE id_producto = ?", (pid,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Producto ID {pid} no existe")
            nombre, precio_db, costo_db, stock_db = row
            if cant > stock_db:
                raise ValueError(f"Stock insuficiente para {nombre}: {stock_db} disponibles, se solicita {cant}")
            precio_unit = float(it.get("precio", precio_db))
            subtotal = precio_unit * cant
            ganancia = (precio_unit - costo_db) * cant
            total += subtotal
            total_ganancia += ganancia
            item_rows.append({"id_producto": pid, "cantidad": cant, "precio_unit": precio_unit, "subtotal": subtotal})

        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        hora = datetime.datetime.now().strftime("%H:%M:%S")

        # Generate cliente_rapido if no cliente_id (para ventas sin cliente)
        cliente_rapido = None
        if cliente_id is None:
            cliente_rapido = generar_id_venta_rapida(cursor)

        # Validar que monto_recibido sea suficiente
        if float(monto_recibido) < total:
            raise ValueError("Monto recibido insuficiente para esta venta")

        # Insert venta (SOLO CONTADO)
        vuelto_calculado = float(monto_recibido) - total
        cursor.execute(
            "INSERT INTO ventas (numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (numero_factura, cliente_id, cliente_rapido, fecha, hora, total, total_ganancia, float(monto_recibido), vuelto_calculado),
        )
        id_ventas = cursor.lastrowid

        # Insert detalle_venta and update stock, register historial
        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            cursor.execute(
                "INSERT INTO detalle_venta (id_ventas, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_ventas, pid, cant, precio_unit, subtotal),
            )
            # Update stock
            cursor.execute("UPDATE inventario SET stock = stock - ? WHERE id_producto = ?", (cant, pid))
            # Registrar historial venta con acción diferenciada
            accion = "X MAYOR" if cliente_id else "VENTA"
            registrar_historial_venta(
                id_ventas=id_ventas,
                id_producto=pid,
                cantidad=cant,
                subtotal=subtotal,
                accion=accion,
                usuario=usuario,
                detalle=f"Venta ID {id_ventas}",
                cursor=cursor,
                monto_recibido=monto_recibido,
                vuelto=vuelto_calculado
            )

        conn.commit()
        return {"id_ventas": id_ventas, "total": total, "vuelto": vuelto_calculado}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =========================
# FUNCIONES DEUDAS
# =========================

# --- NUEVA FUNCIÓN GENERADORA DE NÚMERO DE FACTURA PARA DEUDAS ---
def generar_numero_factura_unico_deuda(cursor):
    """Genera un número de factura aleatorio de 6 dígitos único para deudas."""
    max_intentos = 1000
    for _ in range(max_intentos):
        numero = f"{random.randint(100000, 999999)}"
        cursor.execute("SELECT COUNT(*) FROM deudas WHERE numero_factura = ?", (numero,))
        if cursor.fetchone()[0] > 0:
            continue
        cursor.execute("SELECT COUNT(*) FROM papelera_deudas WHERE numero_factura = ?", (numero,))
        if cursor.fetchone()[0] > 0:
            continue
        return numero
    return f"{random.randint(100000, 999999)}"


def obtener_historial_deudas_por_deuda(id_deuda):
    """
    Obtiene el historial de una deuda específica por su id_deuda.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
        FROM historial_deudas h
        LEFT JOIN inventario i ON h.id_producto = i.id_producto
        WHERE h.id_deuda = ?
        ORDER BY h.fecha DESC, h.hora DESC
        """,
        (id_deuda,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def obtener_historial_deudas(nombre_cliente):
    """
    Obtiene el historial de deudas para un cliente específico.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
        FROM historial_deudas h
        JOIN inventario i ON h.id_producto = i.id_producto
        LEFT JOIN deudas d ON h.id_deuda = d.id_deuda
        LEFT JOIN clientes c ON d.cliente_id = c.id_cliente
        WHERE (c.nombres || ' ' || c.apellidos = ? OR d.cliente_rapido = ?)
        ORDER BY h.fecha DESC, h.hora DESC
        """,
        (nombre_cliente, nombre_cliente),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# FUNCIÓN HISTORIAL DEUDAS (ACTUALIZADA CON recibido y vuelto)
# =========================
def registrar_historial_deuda(
    id_deuda, id_producto, cantidad, subtotal, accion, usuario, detalle,
    cursor=None, abono=0, recibido=0, vuelto=0
):
    """
    Registra una acción en el historial de deudas.
    """
    close_conn = False
    if cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_conn = True

    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        INSERT INTO historial_deudas (id_deuda, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, abono, recibido, vuelto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_deuda, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, abono, recibido, vuelto)
    )

    if close_conn:
        conn.commit()
        conn.close()


def crear_deuda(cliente_id, items=None, usuario="sistema"):
    """
    Crear una deuda independiente para un cliente.
    
    - Las deudas son créditos sin relación con ventas
    - Se usan para registrar deudas de clientes al por mayor
    - El cliente_id es OBLIGATORIO
    
    items: list of dicts {id_producto, cantidad, precio (optional)}
    Returns dict with id_deuda, total, saldo, numero_factura
    Raises Exception on validation errors
    """
    if not cliente_id:
        raise ValueError("Cliente es obligatorio para crear una deuda")
    
    if not items or len(items) == 0:
        raise ValueError("No hay items para crear la deuda")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Validate client exists
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_cliente = ?", (cliente_id,))
        if not cursor.fetchone():
            raise ValueError(f"Cliente ID {cliente_id} no existe")
        
        # Validate and gather product info
        total = 0
        item_rows = []
        for it in items:
            pid = int(it.get("id_producto"))
            cant = int(it.get("cantidad", 0))
            if cant <= 0:
                raise ValueError(f"Cantidad inválida para producto {pid}")
            cursor.execute("SELECT producto, precio, costo, stock FROM inventario WHERE id_producto = ?", (pid,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Producto ID {pid} no existe")
            nombre, precio_db, costo_db, stock_db = row
            
            precio_unit = float(it.get("precio", precio_db))
            subtotal = precio_unit * cant
            total += subtotal
            item_rows.append({"id_producto": pid, "cantidad": cant, "precio_unit": precio_unit, "subtotal": subtotal})
        
        fecha = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # --- Generar número de factura único para la deuda ---
        numero_factura = generar_numero_factura_unico_deuda(cursor)
        
        # Insert deuda
        cursor.execute(
            "INSERT INTO deudas (numero_factura, cliente_id, fecha, total, saldo, usuario_creacion) VALUES (?, ?, ?, ?, ?, ?)",
            (numero_factura, cliente_id, fecha, total, total, usuario),
        )
        id_deuda = cursor.lastrowid
        
        # Insert detalle_deuda (productos actuales)
        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            cursor.execute(
                "INSERT INTO detalle_deuda (id_deuda, id_producto, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                (id_deuda, pid, cant, precio_unit, subtotal)
            )
        
        # Insert historial_deudas (registro de la acción)
        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            precio_unit = ir["precio_unit"]
            subtotal = ir["subtotal"]
            registrar_historial_deuda(
                id_deuda=id_deuda,
                id_producto=pid,
                cantidad=cant,
                subtotal=subtotal,
                accion="DEUDA",
                usuario=usuario,
                detalle=f"Deuda ID {id_deuda} - Producto agregado",
                cursor=cursor,
                abono=0  # no es abono
            )
        
        # Actualizar stock (restar)
        for ir in item_rows:
            pid = ir["id_producto"]
            cant = ir["cantidad"]
            cursor.execute("UPDATE inventario SET stock = stock - ? WHERE id_producto = ?", (cant, pid))
        
        conn.commit()
        return {"id_deuda": id_deuda, "total": total, "saldo": total, "numero_factura": numero_factura}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def mover_venta_a_papelera(id_ventas, usuario_elimino, detalle_motivo=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtener venta (sin estado)
        cursor.execute(
            "SELECT numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia, monto_recibido, vuelto FROM ventas WHERE id_ventas = ?",
            (id_ventas,),
        )
        venta = cursor.fetchone()
        if not venta:
            conn.close()
            return False

        (numero_factura, cliente_id, cliente_rapido, fecha, hora,
         total, ganancia, monto_recibido, vuelto) = venta

        # Obtener detalles para restaurar stock
        cursor.execute(
            "SELECT id_producto, cantidad FROM detalle_venta WHERE id_ventas = ?",
            (id_ventas,),
        )
        detalles = cursor.fetchall()
        detalles_text = ", ".join([f"Producto ID {p} x{c}" for p, c in detalles]) if detalles else ""

        # Restaurar stock
        for id_producto, cantidad in detalles:
            cursor.execute(
                "UPDATE inventario SET stock = stock + ? WHERE id_producto = ?",
                (cantidad, id_producto)
            )

        fecha_elim = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar en papelera (sin estado)
        cursor.execute(
            """
            INSERT INTO papelera_ventas 
            (id_ventas, numero_factura, cliente_id, cliente_rapido, fecha, hora, total, ganancia,
             monto_recibido, vuelto, usuario_elimino, fecha_eliminacion, detalle)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (id_ventas, numero_factura, cliente_id, cliente_rapido, fecha, hora, total,
             ganancia, monto_recibido, vuelto, usuario_elimino, fecha_elim,
             detalle_motivo or detalles_text),
        )

        # Eliminar detalles y venta original
        cursor.execute("DELETE FROM detalle_venta WHERE id_ventas = ?", (id_ventas,))
        cursor.execute("DELETE FROM ventas WHERE id_ventas = ?", (id_ventas,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error al mover venta a papelera: {e}")
        return False


def obtener_papelera_ventas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_papelera, id_ventas, numero_factura, cliente_rapido, fecha, hora, total, usuario_elimino, fecha_eliminacion, detalle FROM papelera_ventas ORDER BY id_papelera DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def mover_deuda_a_papelera(id_deuda, usuario_elimino, detalle_motivo=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Obtener deuda completa (incluyendo numero_factura)
        cursor.execute(
            "SELECT numero_factura, cliente_id, fecha, total, saldo, estado FROM deudas WHERE id_deuda = ?",
            (id_deuda,),
        )
        deuda = cursor.fetchone()
        if not deuda:
            conn.close()
            return False

        numero_factura, cliente_id, fecha, total, saldo, estado = deuda

        # Obtener detalle desde historial_deudas
        cursor.execute(
            "SELECT i.producto, hd.cantidad FROM historial_deudas hd JOIN inventario i ON hd.id_producto = i.id_producto WHERE hd.id_deuda = ? AND UPPER(hd.accion) != 'ABONO'",
            (id_deuda,),
        )
        detalles = cursor.fetchall()
        detalles_text = ", ".join([f"{row[0]} x{row[1]}" for row in detalles]) if detalles else ""

        fecha_elim = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar en papelera_deudas con numero_factura
        cursor.execute(
            "INSERT INTO papelera_deudas (id_deuda, numero_factura, cliente_id, fecha, total, saldo, estado, usuario_elimino, fecha_eliminacion, detalle) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id_deuda, numero_factura, cliente_id, fecha, total, saldo, estado, usuario_elimino, fecha_elim, detalle_motivo or detalles_text),
        )

        # Eliminar historial_deudas y deudas
        cursor.execute("DELETE FROM historial_deudas WHERE id_deuda = ?", (id_deuda,))
        cursor.execute("DELETE FROM detalle_deuda WHERE id_deuda = ?", (id_deuda,))
        cursor.execute("DELETE FROM deudas WHERE id_deuda = ?", (id_deuda,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error al mover deuda a papelera: {e}")
        return False


def obtener_papelera_deudas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_papelera, id_deuda, numero_factura, cliente_id, fecha, total, saldo, usuario_elimino, fecha_eliminacion, detalle FROM papelera_deudas ORDER BY id_papelera DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def eliminar_venta(id_ventas, usuario_elimino, motivo=None):
    """Convenience wrapper: mueve a papelera y borra."""
    return mover_venta_a_papelera(id_ventas, usuario_elimino, detalle_motivo=motivo)


def eliminar_deuda(id_deuda, usuario_elimino, motivo=None):
    return mover_deuda_a_papelera(id_deuda, usuario_elimino, detalle_motivo=motivo)


# =========================
# FUNCIONES REPORTES
# =========================


def actualizar_cuentas():
    """
    Actualiza la tabla ganancias con los totales de ventas por día, semana, mes y año.
    Debe llamarse cada vez que se agrega una venta.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener todas las fechas de ventas
    cursor.execute(
        """
        SELECT fecha, SUM(total)
        FROM ventas        
        GROUP BY fecha
        ORDER BY fecha DESC
    """
    )
    ventas_por_dia = cursor.fetchall()

    # Limpiar la tabla ganancias y recalcular todo
    cursor.execute("DELETE FROM ganancias")

    for fecha, total_dia in ventas_por_dia:
        # Calcular semana, mes, año
        fecha_dt = datetime.datetime.strptime(fecha, "%Y-%m-%d")
        # Sumar ventas pagadas de la semana
        semana_inicio = (
            fecha_dt - datetime.timedelta(days=fecha_dt.weekday())
        ).strftime("%Y-%m-%d")
        semana_fin = (
            fecha_dt + datetime.timedelta(days=6 - fecha_dt.weekday())
        ).strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT SUM(total) FROM ventas
            WHERE fecha BETWEEN ? AND ?            
        """,
            (semana_inicio, semana_fin),
        )
        total_semana = cursor.fetchone()[0] or 0

        # Sumar ventas pagadas del mes
        mes_inicio = fecha_dt.replace(day=1).strftime("%Y-%m-%d")
        mes_fin = (fecha_dt.replace(day=28) + datetime.timedelta(days=4)).replace(
            day=1
        ) - datetime.timedelta(days=1)
        mes_fin = mes_fin.strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT SUM(total) FROM ventas
            WHERE fecha BETWEEN ? AND ?            
        """,
            (mes_inicio, mes_fin),
        )
        total_mes = cursor.fetchone()[0] or 0

        # Sumar ventas pagadas del año
        anio_inicio = fecha_dt.replace(month=1, day=1).strftime("%Y-%m-%d")
        anio_fin = fecha_dt.replace(month=12, day=31).strftime("%Y-%m-%d")
        cursor.execute(
            """
            SELECT SUM(total) FROM ventas
            WHERE fecha BETWEEN ? AND ?            
        """,
            (anio_inicio, anio_fin),
        )
        total_anio = cursor.fetchone()[0] or 0

        cursor.execute(
            """
            INSERT OR REPLACE INTO ganancias (fecha, total_dia, total_semana, total_mes, total_anio)
            VALUES (?, ?, ?, ?, ?)
        """,
            (fecha, total_dia, total_semana, total_mes, total_anio),
        )

    conn.commit()
    conn.close()


# =========================
# FUNCIONES HISTORIALES
# =========================


def registrar_historial_venta(
    id_ventas, id_producto, cantidad, subtotal, accion, usuario, detalle, cursor=None,
    monto_recibido=0, vuelto=0
):
    """
    Registra una acción en el historial de ventas.
    Ahora incluye monto_recibido y vuelto para mantener datos históricos.
    """
    close_conn = False
    if cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_conn = True

    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        """
        INSERT INTO historial_ventas (id_ventas, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, monto_recibido, vuelto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id_ventas, id_producto, cantidad, subtotal, accion, usuario, fecha, hora, detalle, monto_recibido, vuelto),
    )

    if close_conn:
        conn.commit()
        conn.close()


def obtener_historial_por_venta(id_ventas):
    """
    Obtiene el historial de una venta específica por su id_ventas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT h.id_historial, i.producto, h.fecha, h.hora, h.cantidad, h.subtotal, h.accion
        FROM historial_ventas h
        LEFT JOIN inventario i ON h.id_producto = i.id_producto
        WHERE h.id_ventas = ?
        ORDER BY h.fecha DESC, h.hora DESC
        """,
        (id_ventas,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# =========================
# FUNCIONES USUARIOS
# =========================


def buscar_usuario(usuario, contrasena):
    conn = get_connection()
    cursor = conn.cursor()
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
    cursor.execute(
        "SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?",
        (usuario, contrasena_hash),
    )
    resultado = cursor.fetchone()
    conn.close()
    return resultado


def insertar_usuario(usuario, contrasena):
    conn = get_connection()
    cursor = conn.cursor()
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)",
        (usuario, contrasena_hash),
    )
    conn.commit()
    conn.close()


def eliminar_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()


def actualizar_usuario(usuario_id, usuario, contrasena):
    conn = get_connection()
    cursor = conn.cursor()
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
    cursor.execute(
        "UPDATE usuarios SET usuario = ?, contrasena = ? WHERE id = ?",
        (usuario, contrasena_hash, usuario_id),
    )
    conn.commit()
    conn.close()


def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, contrasena FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios


def combobox_clientes():
    """
    Devuelve una lista de nombres de clientes para usar en el combobox de búsqueda.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT nombres FROM clientes ORDER BY nombres ASC")
    nombres = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nombres


if __name__ == "__main__":
    create_tables()
    print("Base de datos creada/actualizada.")