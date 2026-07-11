# Arquitecura del Sistema — Innobert Retail

## Índice

1. [Visión General](#1-visión-general)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Capa de Datos — `retail/nucleo/base_datos.py`](#3-capa-de-datos---retailnucleobase_datospy)
4. [Capa de Configuración — `retail/nucleo/configuraciones.py`](#4-capa-de-configuración---retailnucleoconfiguracionespy)
5. [Punto de Entrada — `inicio.py` y `principal.py`](#5-punto-de-entrada---iniciopy-y-principalpy)
6. [Capa de Servicios — `retail/nucleo/servicios/`](#6-capa-de-servicios---retailnucleoservicios)
7. [Sesión y Autenticación — `retail/sesion/`](#7-sesión-y-autenticación---retailsesion)
8. [Vistas Principales — `retail/vistas/`](#8-vistas-principales---retailvistas)
9. [Sub-Vistas de Ventas — `retail/ventas/`](#9-sub-vistas-de-ventas---retailventas)
10. [Sub-Vistas de Deudas — `retail/deudas/`](#10-sub-vistas-de-deudas---retaildeudas)
11. [Sub-Vistas de Ganancias — `retail/ganancias/`](#11-sub-vistas-de-ganancias---retailganancias)
12. [Sub-Vistas de Inventario — `retail/inventario/`](#12-sub-vistas-de-inventario---retailinventario)
13. [Utilidades — `retail/utilidades/`](#13-utilidades---retailutilidades)
14. [Pruebas — `tests/`](#14-pruebas---tests)
15. [Esquema de Base de Datos](#15-esquema-de-base-de-datos)
16. [Flujo de Datos](#16-flujo-de-datos)
17. [Patrones y Decisiones de Diseño](#17-patrones-y-decisiones-de-diseño)

---

## 1. Visión General

**Innobert Retail** es un sistema POS (Point of Sale) de escritorio desarrollado en Python 3.11+ con Tkinter, orientado a pequeños negocios como licorerías, mini-mercados y emprendedores en Colombia.

### Arquitectura en 3 Capas (MVC-like)

```
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN (UI)                  │
│  retail/vistas/   retail/ventas/   retail/deudas/           │
│  retail/ganancias/   retail/inventario/   retail/sesion/    │
│                   (Tkinter Frames y Toplevels)              │
├─────────────────────────────────────────────────────────────┤
│                   CAPA DE NEGOCIO (SERVICIOS)                │
│  retail/nucleo/servicios/                                   │
│  ├── clientes/   ├── deudas/   ├── ganancias/               │
│  ├── inventario/ ├── sesion/   └── ventas/                  │
│  retail/sesion/core/   (lógica de auth/licencias)           │
├─────────────────────────────────────────────────────────────┤
│                   CAPA DE DATOS                              │
│  retail/nucleo/base_datos.py   (SQLite CRUD)                │
│  retail/nucleo/configuraciones.py  (paths, temas, logging)  │
│  └── SQLite3 DB en %APPDATA%/InnobertRetail/pos.db          │
└─────────────────────────────────────────────────────────────┘
```

**Stack tecnológico:**

| Componente         | Tecnología                       |
|--------------------|----------------------------------|
| Lenguaje           | Python 3.11+                     |
| GUI                | Tkinter (ttk, tema "clam")       |
| Base de datos      | SQLite3 (stdlib)                 |
| PDF                | ReportLab 4.5.1                  |
| Imágenes           | Pillow 12.2.0                    |
| HTTP               | requests 2.32.3 (licencias)      |
| Normalización      | charset-normalizer 3.4.7         |
| Tipado             | mypy (strict mode parcial)       |
| Testing            | pytest 9.1.1                     |
| Moneda             | Peso colombiano ($1.500.000)     |
| Idioma             | Español                           |

---

## 2. Estructura del Proyecto

```
C:\Innobert-Retail/
│
├── inicio.py                       # Punto de entrada (instancia única + bootstrap)
├── pyproject.toml                  # Configuración de mypy
├── requirements.txt                # Dependencias
├── README.md                       # Documentación del proyecto
├── LICENSE.md                      # Licencia custom (30-day trial)
├── icono.ico                       # Icono de la aplicación
│
├── retail/                         # Paquete principal
│   ├── nucleo/                     # Núcleo (datos + config)
│   │   ├── base_datos.py           # (1,335 lines) CRUD SQLite + esquema
│   │   ├── configuraciones.py      # (308 lines) Config paths, logging, tema
│   │   ├── principal.py            # (68 lines) Ventana Tk principal
│   │   └── servicios/              # Capa de negocio
│   │       ├── clientes/
│   │       │   └── servicio_clientes.py
│   │       ├── deudas/
│   │       │   ├── servicio_deudas.py
│   │       │   ├── servicio_carrito_deudas.py
│   │       │   ├── servicio_edicion_deudas.py
│   │       │   ├── servicio_facturas_deudas.py
│   │       │   ├── servicio_historial_deudas.py
│   │       │   ├── servicio_pagadas.py
│   │       │   ├── servicio_papelera_deudas.py
│   │       │   └── servicio_visualizar_deudas.py
│   │       ├── ganancias/
│   │       │   ├── servicio_diario.py
│   │       │   ├── servicio_semanal.py
│   │       │   ├── servicio_mensual.py
│   │       │   └── servicio_anual.py
│   │       ├── inventario/
│   │       │   └── servicio_inventario.py
│   │       ├── sesion/             # Re-exports → retail/sesion/core/
│   │       │   ├── servicio_acceso.py
│   │       │   ├── servicio_licencias.py
│   │       │   └── servicio_registro.py
│   │       └── ventas/
│   │           ├── servicio_ventas.py
│   │           ├── servicio_carrito_ventas.py
│   │           ├── servicio_edicion_ventas.py
│   │           ├── servicio_facturas_ventas.py
│   │           ├── servicio_historial_ventas.py
│   │           ├── servicio_papelera_ventas.py
│   │           └── servicio_visualizar_ventas.py
│   │
│   ├── vistas/                     # Vistas principales (tabs)
│   │   ├── contenedor.py           # Contenedor con menú de navegación
│   │   ├── ventas.py               # Vista de ventas
│   │   ├── deudas.py               # Vista de deudas
│   │   ├── clientes.py             # Vista de clientes
│   │   ├── inventario.py           # Vista de inventario
│   │   └── ganancias.py            # Contenedor de ganancias
│   │
│   ├── ventas/                     # Sub-ventanas de ventas
│   │   ├── carrito_ventas.py
│   │   ├── edicion_ventas.py
│   │   ├── facturas_ventas.py
│   │   ├── historial_ventas.py
│   │   ├── papelera_ventas.py
│   │   └── visualizar_ventas.py
│   │
│   ├── deudas/                     # Sub-ventanas de deudas
│   │   ├── carrito_deudas.py
│   │   ├── edicion_deudas.py
│   │   ├── facturas_deudas.py
│   │   ├── historial_deudas.py
│   │   ├── pagadas.py
│   │   ├── papelera_deudas.py
│   │   └── visualizar_deudas.py
│   │
│   ├── ganancias/                  # Sub-vistas de ganancias
│   │   ├── diario.py
│   │   ├── semanal.py
│   │   ├── mensual.py
│   │   └── anual.py
│   │
│   ├── inventario/                 # Sub-vistas de inventario
│   │   ├── historial_inventario.py
│   │   └── totales.py
│   │
│   ├── sesion/                     # Auth y licencias
│   │   ├── acceso.py               # Pantalla de login
│   │   ├── registro.py             # Gestión de usuarios
│   │   ├── licencias.py            # Placeholder vacío
│   │   └── core/                   # Lógica de auth
│   │       ├── __init__.py
│   │       ├── db.py               # Re-export desde base_datos
│   │       ├── servicio_acceso.py
│   │       ├── servicio_licencias.py
│   │       └── servicio_registro.py
│   │
│   └── utilidades/
│       └── logo.py                 # Cambio de logo para PDFs
│
├── tests/                          # Pruebas unitarias
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent.py
│   ├── test_base_datos.py          # 686 lines, ~45 tests
│   ├── test_configuraciones.py     # 147 lines
│   ├── test_instancia_unica.py
│   ├── test_servicio_acceso.py
│   ├── test_servicio_clientes.py
│   ├── test_servicio_deudas.py
│   ├── test_servicio_ganancias_diario.py
│   ├── test_servicio_inventario.py
│   ├── test_servicio_licencias.py
│   ├── test_servicio_registro.py
│   └── test_servicio_ventas.py
│
├── docs/gifs/                      # GIFs demostrativos del manual
├── fotos/                          # Imágenes por defecto para productos
│   └── default.png
├── img/                            # Iconos de la UI
│   ├── add.png, cambiar.png, carrito.png, clientes.png, ...
│   └── login.png, logo.png, ...
│
└── venv/                           # Entorno virtual
```

---

## 3. Capa de Datos — `retail/nucleo/base_datos.py`

**Archivo**: `retail/nucleo/base_datos.py` (1,335 líneas)

Es el módulo más grande del proyecto y actúa como capa de acceso a datos única (God Module). Contiene:

### 3.1 Conexión a Base de Datos

```python
DB_NAME = obtener_ruta_base_datos()  # %APPDATA%/InnobertRetail/pos.db

def obtener_conexion() -> sqlite3.Connection:
    return sqlite3.connect(DB_NAME)

@contextmanager
def conexion():
    """Context manager que provee una conexión con commit automático
    y rollback en caso de excepción."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def ejecutar_consulta(query, params=()):
    """Ejecuta una consulta y retorna la primera fila."""
    with conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
```

- Usa `sqlite3` de la stdlib de Python
- `conexion()` es un context manager que maneja commit/rollback automático
- `DB_NAME` se define al importar el módulo desde `configuraciones.obtener_ruta_base_datos()`

### 3.2 Constantes de Índice y Conversión

```python
IDX_PROD_ID = 0
IDX_PROD_NOMBRE = 1
IDX_PROD_PRECIO = 2
IDX_PROD_COSTO = 3
IDX_PROD_STOCK = 4
IDX_PROD_ESTADO = 5
IDX_PROD_IMAGEN = 6

def producto_a_dict(p):
    """Convierte una tupla de producto (como viene de SQLite) a dict."""
    return {
        "id_producto": p[IDX_PROD_ID],
        "producto": p[IDX_PROD_NOMBRE],
        "precio": p[IDX_PROD_PRECIO],
        "costo": p[IDX_PROD_COSTO],
        "stock": p[IDX_PROD_STOCK],
        "estado": p[IDX_PROD_ESTADO],
        "imagen": p[IDX_PROD_IMAGEN],
    }
```

- Usa índices numéricos con nombre (`IDX_PROD_*`) para acceder a las columnas
- `producto_a_dict()` normaliza las tuplas SQLite a diccionarios para el resto del sistema

### 3.3 Función `crear_tablas()` — Bootstrap del Esquema

```python
def crear_tablas():
    asegurar_directorios()
    # En Windows: oculta la carpeta AppData
    if os.name == "nt":
        # Set FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_READONLY
        ...

    with conexion() as conn:
        cursor = conn.cursor()
        cursor.executescript("""...""")
        # Inserta usuario admin (innobertdev) y usuario de prueba (prueba)
```

Ejecuta un `executescript` que crea **todas las tablas** con `CREATE TABLE IF NOT EXISTS`:

| Tabla | Propósito |
|-------|-----------|
| `desarrollador` | Usuario admin con backdoor (`innobertdev`/`ingsoftware.99`) |
| `usuarios` | Usuarios del sistema con licencia |
| `clientes` | Catálogo de clientes |
| `inventario` | Catálogo de productos |
| `ventas` | Facturas de venta |
| `detalle_venta` | Productos en cada venta |
| `deudas` | Deudas/Créditos independientes |
| `detalle_deuda` | Productos en cada deuda |
| `pagos_deuda` | Historial de pagos/abonos |
| `ganancias` | Totales agregados por día/semana/mes/año |
| `historial_ventas` | Auditoría de cambios en ventas |
| `historial_deudas` | Auditoría de cambios en deudas |
| `papelera_ventas` | Ventas eliminadas (soft delete) |
| `papelera_deudas` | Deudas eliminadas (soft delete) |
| `historial_inventario` | Auditoría de cambios en inventario |

Además inserta dos usuarios por defecto:
- **Admin**: `innobertdev` / `ingsoftware.99` (hash SHA-256) — backdoor de desarrollo
- **Prueba**: `prueba` / `prueba` con suscripción de 30 días desde la fecha actual

### 3.4 CRUD de Clientes

| Función | Descripción |
|---------|-------------|
| `insertar_cliente(nombres, apellidos, cedula, celular, zona)` | INSERT directo |
| `obtener_clientes()` | SELECT * con ORDER BY id |
| `eliminar_cliente(id_cliente)` | DELETE por ID |
| `actualizar_cliente(id_cliente, campo, valor)` | UPDATE dinámico (string interpolation del campo) |
| `buscar_cliente_por_cedula(cedula)` | Búsqueda por cédula exacta |

### 3.5 CRUD de Inventario

| Función | Descripción |
|---------|-------------|
| `agregar_producto(...)` | INSERT completo |
| `obtener_productos()` | SELECT * (todos) |
| `actualizar_producto(...)` | UPDATE completo por ID |
| `dlt_producto(id_producto)` | DELETE por ID |
| `registrar_historial_inventario(...)` | Inserta en historial_inventario |
| `combobox_productos()` | Solo nombres para autocompletado |
| `editar_producto(id_producto)` | SELECT de un producto por ID |
| `buscar_productos_por_nombre(nombre)` | LIKE %nombre% |
| `paginar_productos(offset, limit, filtro)` | Paginación con LIMIT/OFFSET |
| `contar_productos(filtro)` | COUNT para paginación |
| `obtener_nombres_productos(filtro)` | Solo nombres para búsqueda |
| `obtener_totales_globales_ganancias()` | SUM de ventas + deudas pagadas |

### 3.6 Gestión de Ventas

**Generación de número de factura**:
```python
def generar_numero_factura_unico(cursor):
    """Genera un número aleatorio de 6 dígitos único
    (verifica en ventas y papelera_ventas)."""
    for _ in range(1000):
        numero = f"{random.randint(100000, 999999)}"
        if not existe_en_ventas(numero) and not existe_en_papelera(numero):
            return numero
    return fallback
```

**Generación de ID para venta rápida**:
```python
def generar_id_venta_rapida(cursor):
    """Formato: VR-YYYYMMDD-NNN"""
    fecha_id = datetime.now().strftime("%Y%m%d")
    count = ventas_del_dia_sin_cliente + 1
    return f"VR-{fecha_id}-{count:03d}"
```

**Función principal** `crear_venta()`:
```python
def crear_venta(cliente_id=None, items=None, monto_recibido=0, usuario="sistema"):
    """
    1. Genera número de factura único
    2. Valida stock (cada producto)
    3. Calcula total y ganancia
    4. Valida monto recibido >= total
    5. Calcula vuelto
    6. INSERT en ventas
    7. INSERT en detalle_venta (cada producto)
    8. UPDATE stock (restar)
    9. Registra historial_venta por cada producto
    """
```

- **Ventas rápidas**: `cliente_id=None` → genera ID tipo `VR-20260710-001`
- **Ventas por mayor**: `cliente_id` presente
- El vuelto se calcula automáticamente

### 3.7 Gestión de Deudas

**Función principal** `crear_deuda()`:
```python
def crear_deuda(cliente_id, items=None, usuario="sistema"):
    """
    1. Valida que cliente_id exista
    2. Genera número de factura único para deuda
    3. Calcula total
    4. INSERT en deudas (con saldo = total)
    5. INSERT en detalle_deuda
    6. Registra historial_deudas
    7. UPDATE stock (restar)
    """
```

**Funciones de papelera** (soft delete con restauración de stock):
- `mover_venta_a_papelera(id_ventas, usuario, motivo)` → respalda en papelera_ventas + restaura stock + DELETE original
- `mover_deuda_a_papelera(id_deuda, usuario, motivo)` → similar para deudas
- `obtener_papelera_ventas()` / `obtener_papelera_deudas()` → listar eliminados

### 3.8 Historiales y Reportes

**`actualizar_cuentas()`**: Calcula totales de ganancias por día, semana, mes y año usando `INSERT OR REPLACE`. Se llama después de cada venta.

Funciones de historial:
- `registrar_historial_venta()` — inserta en historial_ventas (con cursor propio o compartido)
- `registrar_historial_deuda()` — similar para deudas
- `obtener_historial_por_venta(id_ventas)` — JOIN con inventario
- `obtener_historial_deudas_por_deuda(id_deuda)` — JOIN con inventario

### 3.9 Gestión de Usuarios

```python
def buscar_usuario(usuario, contrasena):
    """Busca en tabla usuarios con hash SHA-256 de contraseña."""
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
    # SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?

def insertar_usuario(usuario, contrasena): ...
def eliminar_usuario(usuario_id): ...
def actualizar_usuario(usuario_id, usuario, contrasena): ...
def obtener_usuarios(): ...
```

### 3.10 Formateo de Moneda

```python
def peso_colombiano(value: float) -> str:
    return f"${value:,.0f}".replace(",", ".")
```
- Reemplaza comas por puntos: `1500000` → `$1.500.000`

---

## 4. Capa de Configuración — `retail/nucleo/configuraciones.py`

**Archivo**: `retail/nucleo/configuraciones.py` (308 líneas)

Gestiona todo lo relacionado con la configuración de la aplicación.

### 4.1 Rutas Multiplataforma

```python
def _obtener_ruta_datos_usuario():
    if sys.platform == "win32":
        return "%APPDATA%/InnobertRetail"
    elif sys.platform == "darwin":
        return "~/Library/Application Support/InnobertRetail"
    else:
        return "~/.local/share/InnobertRetail"
```

Rutas derivadas:
| Constante | Valor |
|-----------|-------|
| `APPDATA_PATH` | `{datos}/InnobertRetail` |
| `FOTOS_PATH` | `{APPDATA}/fotos` |
| `LOGO_PATH` | `{APPDATA}/Logo` |
| DB | `{APPDATA}/pos.db` |
| Config JSON | `{APPDATA}/config/config.json` |
| PDF Config JSON | `{APPDATA}/config/pdf_config.json` |

### 4.2 Constantes de UI

- **Colores**: `COLOR_FONDO=#E6D9E3`, `COLOR_AZUL=#2196F3`, `COLOR_VERDE=#4CAF50`, `COLOR_ROJO=#F44336`
- **Fuentes**: `FUENTE_ETIQUETA = ("Helvetica", 12, "bold")`
- **Paginación**: `PRODUCTOS_POR_PAGINA = 12`
- **Tamaño ventana**: `TAMANO_VENTANA = "1300x700"`

### 4.3 Logging con Rotación

```python
def configurar_logging():
    """Logs en {APPDATA}/logs/app.log con rotación de 5MB, 3 backups."""
    handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3)
    root.setLevel(logging.DEBUG)
```

### 4.4 Persistencia de Preferencias

- `guardar_usuario()` / `cargar_usuario()` — recuerda credenciales en `config.json`
- `guardar_ultima_carpeta_pdf()` / `cargar_ultima_carpeta_pdf()` — recuerda carpeta de exportación PDF por tipo

### 4.5 Recursos y Archivos

- `asegurar_directorios()` — crea estructura de carpetas
- `copiar_fotos_por_defecto()` — copia `fotos/` del proyecto a `APPDATA`
- `copiar_logo_por_defecto()` — copia `img/logo.png` a `APPDATA/Logo/`
- `ruta_recurso(relative_path)` — resuelve rutas relativas (compatible con PyInstaller `sys._MEIPASS`)
- `abrir_archivo(ruta)` — abre archivo con app predeterminada (soporta Win/macOS/Linux)
- `eliminar_base_datos()` / `eliminar_datos_completos()` — limpieza de datos

---

## 5. Punto de Entrada — `inicio.py` y `principal.py`

### 5.1 `inicio.py` (62 líneas)

```python
# 1. Asegura instancia única via socket en localhost
puerto = 50000 + hash(sha256(ruta_ejecutable)) % 10000
sock.bind(("127.0.0.1", puerto))
# Si falla el bind → ya hay otra instancia → muestra mensaje y sale

# 2. Arranca la app
app = Principal()
app.mainloop()
```

- Usa SHA-256 del path del ejecutable para derivar un puerto determinístico (50000-59999)
- Previene múltiples instancias del programa

### 5.2 `principal.py` — Clase `Principal(tk.Tk)` (68 líneas)

```python
class Principal(tk.Tk):
    def __init__(self):
        self.title("Innobert Retail")
        self.resizable(False, False)
        self.maxsize(1400, 850)

        configurar_logging()
        base_de_datos.crear_tablas()     # Bootstrap DB

        # Tema ttk
        style = ttk.Style(self)
        style.theme_use("clam")

        # Frames de navegación
        self.frames = {
            "Acceso": Acceso(self, self),        # Login
            "Contenedor": Contenedor(self, self)  # App principal
        }
        self.show_frame("Acceso")                # Empieza en login

    def show_frame(self, frame_name):
        # Cambia entre Acceso y Contenedor
        # Ajusta geometría según el frame
```

- Hereda de `tk.Tk` (ventana raíz)
- Inicializa logging y base de datos
- Cambia entre pantalla de login (`Acceso`) y app principal (`Contenedor`)

---

## 6. Capa de Servicios — `retail/nucleo/servicios/`

### 6.1 Servicio de Clientes — `servicio_clientes.py` (219 líneas)

**Clase**: `ClientesServicio` (todos métodos `@staticmethod`)

| Método | Descripción |
|--------|-------------|
| `obtener_todos_clientes()` | Lista completa como diccionarios |
| `agregar_cliente(nombres, apellidos, cedula, celular, zona)` | Valida duplicados antes de insertar |
| `actualizar_cliente(id_cliente, campo, valor)` | Actualiza campo individual con validación de unicidad |
| `eliminar_cliente(id_cliente)` | Elimina por ID |
| `obtener_cliente_por_id(id_cliente)` | Búsqueda por ID |
| `contar_clientes(filtro)` | COUNT para paginación |
| `obtener_clientes_paginado(offset, limit, filtro)` | Página de clientes |
| `obtener_nombres_clientes_para_busqueda(filtro)` | Autocompletado |

**Validaciones**:
- Cédula única
- Celular único
- Todos los campos obligatorios

### 6.2 Servicios de Ventas

#### `servicio_ventas.py` — `VentasServicio` (299 líneas)

| Método | Descripción |
|--------|-------------|
| `obtener_stock_actual(id_producto)` | Consulta DB |
| `validar_cantidad(id_producto, cantidad, carrito)` | Stock disponible vs carrito actual |
| `agregar_al_carrito(carrito, producto, cantidad, cliente_id, tipo_venta)` | Agrega con validación de duplicados |
| `obtener_clientes_formateados()` | Lista nombres + mapa id |
| `obtener_productos_para_busqueda(termino)` | Búsqueda por nombre |
| `calcular_total_carrito(carrito)` | Suma subtotales |
| `confirmar_venta(carrito, cliente_id, monto_recibido, usuario)` | Crea venta en DB + actualiza cuentas |
| `filtrar_clientes_por_texto(texto)` | Filtro por nombre |
| `obtener_cliente_por_nombre_completo(nombre)` | Búsqueda exacta |
| `obtener_productos_paginado(offset, limit, filtro)` | Paginación |
| `contar_productos(filtro)` | COUNT |
| `obtener_nombres_productos_para_busqueda(filtro)` | Autocompletado |
| `obtener_nombre_cliente_por_id(cliente_id)` | Nombre desde ID |

#### `servicio_carrito_ventas.py` — `ServicioCarritoVentas` (92 líneas)

| Método | Descripción |
|--------|-------------|
| `validar_cantidad_para_edicion(carrito, id_producto, nueva_cantidad, item_actual)` | Valida stock excluyendo item actual |
| `actualizar_cantidad_en_carrito(carrito, item_index, nueva_cantidad)` | Actualiza cantidad + subtotal |
| `eliminar_producto_del_carrito(carrito, item_index)` | Elimina por índice |
| `calcular_totales_por_cliente(carrito)` | Agrupación por cliente |
| `calcular_total_general(carrito)` | Suma total |

#### `servicio_edicion_ventas.py` — `ServicioEdicionVentas` (477 líneas)

Incluye la excepción personalizada `VentaVaciaError` para manejar ventas que se quedan sin productos.

| Método | Descripción |
|--------|-------------|
| `obtener_detalles_factura(id_ventas, conn=None)` | Detalles con JOIN a inventario |
| `obtener_info_factura(id_ventas, conn=None)` | (total, monto_recibido, vuelto) |
| `eliminar_detalle_venta(id_detalle, usuario, monto_recibido, conn, cursor)` | Restaura stock, elimina, recalcula total/vuelto, mueve a papelera si vacía |
| `_mover_a_papelera_si_vacia(id_ventas, usuario, conn, cursor)` | Verifica si quedan productos; si no, mueve a papelera |
| `editar_cantidad_detalle(id_detalle, nueva_cantidad, usuario, monto_recibido, conn, cursor)` | Cambia cantidad, actualiza stock/total/vuelto |
| `agregar_producto_a_venta(id_ventas, id_producto, cantidad, usuario, monto_recibido, conn, cursor)` | Agrega producto a factura existente |
| `obtener_productos_paginado(filtro, offset, limit, conn)` | Paginación con imagen |
| `contar_productos_con_filtro(filtro, conn)` | COUNT |

**Validaciones clave**:
- El nuevo total no puede superar el monto recibido
- Stock suficiente al aumentar cantidades
- Si una venta se queda sin productos → se mueve automáticamente a papelera

#### `servicio_facturas_ventas.py` — `ServicioFacturasVentas` (194 líneas)

| Método | Descripción |
|--------|-------------|
| `contar_facturas(filtro)` | COUNT con filtro por número de factura |
| `obtener_pagina_facturas(offset, limit, filtro)` | Página con GROUP_CONCAT de productos y CASE para nombre cliente |
| `calcular_total_ventas(filtro)` | SUM total |
| `eliminar_factura(id_ventas, usuario)` | Mueve a papelera |
| `obtener_detalles_para_pdf(id_ventas)` | Datos para generar PDF |
| `obtener_lista_numeros_factura(filtro)` | Autocompletado de números |

#### `servicio_historial_ventas.py` — `ServicioHistorialVentas` (135 líneas)

| Método | Descripción |
|--------|-------------|
| `obtener_por_venta(id_ventas)` | Historial de una venta (filtrado por acciones relevantes) |
| `obtener_por_cliente(id_cliente, cliente_rapido)` | Historial por cliente |
| `_procesar_filas(rows)` | Convierte filas a dicts con día de la semana y formato moneda |

#### `servicio_papelera_ventas.py` — `ServicioPapeleraVentas` (147 líneas)

| Método | Descripción |
|--------|-------------|
| `contar_papelera(filtro)` | COUNT con filtro |
| `obtener_pagina(offset, limit, filtro)` | Página con JOIN a clientes |
| `limpiar_registros_antiguos(dias=30)` | DELETE de registros > N días |
| `obtener_total_eliminado(filtro)` | SUM de totales eliminados |

#### `servicio_visualizar_ventas.py` — `ServicioVisualizarVentas` (91 líneas)

| Método | Descripción |
|--------|-------------|
| `obtener_detalles_factura(id_ventas)` | Factura completa + lista de productos |

### 6.3 Servicios de Deudas

Estructura casi idéntica a ventas (paralelismo por diseño):

#### `servicio_deudas.py` — `DeudasServicio` (267 líneas)

Similar a `VentasServicio` pero:
- No tiene `tipo_venta` (no hay "rápida" vs "mayorista" en deudas)
- El cliente es **obligatorio** para deudas
- `confirmar_deuda()` llama a `crear_deuda()` en lugar de `crear_venta()`

#### `servicio_carrito_deudas.py` — `ServicioCarritoDeudas` (79 líneas)

Idéntico a `ServicioCarritoVentas` pero sin `calcular_totales_por_cliente()`.

#### `servicio_edicion_deudas.py` — `ServicioEdicionDeudas` (358 líneas)

Similar a `ServicioEdicionVentas` pero:
- Trabaja con `detalle_deuda` y `deudas`
- Incluye manejo de saldo y pagos
- Recalcula estado (`ABIERTA`/`PAGADA`) según saldo
- No tiene excepción `VentaVaciaError` (las deudas no se auto-eliminan)

#### `servicio_facturas_deudas.py` — `ServicioFacturasDeudas` (251 líneas)

Además de listar deudas abiertas, incluye:

**`registrar_pago(id_deuda, monto, saldo_actual, usuario)`**:
```python
def registrar_pago(id_deuda, monto, saldo_actual, usuario):
    """
    3 casos:
    - monto < saldo → abono (ABIERTA)
    - monto == saldo → pago total (PAGADA)
    - monto > saldo → pago total con vuelto (PAGADA)
    
    Inserta en pagos_deuda, actualiza saldo/estado, registra historial
    """
```

#### `servicio_historial_deudas.py` — `ServicioHistorialDeudas` (225 líneas)

Similar a `ServicioHistorialVentas` pero:
- Calcula **saldo acumulado** en cada fila del historial
- Agrupa abonos por deuda
- Normaliza acciones (`DEUDA DIRECTA` → `DEUDA`)

#### `servicio_pagadas.py` — `ServicioPagadas` (192 líneas)

Gestiona deudas en estado `PAGADA`:

| Método | Descripción |
|--------|-------------|
| `contar_pagadas(filtro)` | COUNT de deudas pagadas |
| `obtener_pagina(offset, limit, filtro)` | Página con JOIN a clientes |
| `calcular_total_pagadas(filtro)` | SUM de totales |
| `obtener_detalles_para_pdf(id_deuda)` | Datos para PDF |

#### `servicio_papelera_deudas.py` — `ServicioPapeleraDeudas` (138 líneas)

Análogo a `ServicioPapeleraVentas`.

#### `servicio_visualizar_deudas.py` — `ServicioVisualizarDeudas` (74 líneas)

Análogo a `ServicioVisualizarVentas`.

### 6.4 Servicios de Ganancias

#### `servicio_diario.py` — `ServicioDiario` (207 líneas)

```python
class ServicioDiario:
    def contar_dias(filtro_fecha):
        """COUNT de días con ventas o deudas pagadas"""
    
    def obtener_pagina(offset, limit, filtro_fecha):
        """Página: fecha, total_ventas, total_deudas, total_dia, ganancia"""
    
    def calcular_total_general(filtro_fecha):
        """SUM de total_dia"""
    
    def obtener_totales_reporte(filtro_fecha):
        """Datos completos para PDF"""
    
    def _formato_pesos(valor):
        """$X.XXX.XXX"""
```

Combina ventas del día + deudas pagadas del día para calcular el total diario.

#### `servicio_semanal.py` — `ServicioSemanal` (99 líneas)

Usa CTE de SQL para agrupar por semana consecutiva:

```sql
WITH fechas_agrupadas AS (
    SELECT fecha, total_dia,
           (julianday(fecha) - julianday('2026-01-01')) / 7 AS grupo_semana
    FROM ganancias
    ORDER BY fecha
)
SELECT MIN(fecha), MAX(fecha), SUM(total_dia), ...
GROUP BY CAST(grupo_semana AS INTEGER)
```

#### `servicio_mensual.py` — `ServicioMensual` (122 líneas)

Agrupa en periodos de 30 días usando `julianday`:

```sql
WITH fechas_agrupadas AS (
    SELECT fecha, total_dia,
           CAST((julianday(fecha) - julianday('2026-01-01')) / 30 AS INTEGER) AS grupo_mes
    FROM ganancias
)
```

#### `servicio_anual.py` — `ServicioAnual` (108 líneas)

Agrupa en periodos de 365 días:

```sql
WITH fechas_agrupadas AS (
    SELECT fecha, total_dia,
           CAST((julianday(fecha) - julianday('2020-01-01')) / 365 AS INTEGER) AS grupo_anio
    FROM ganancias
)
```

### 6.5 Servicio de Inventario — `servicio_inventario.py` (265 líneas)

```python
class InventarioServicio:
    def obtener_todos_productos():
        """Lista completa como diccionarios"""
    
    def agregar_producto(producto, precio, costo, stock, estado, imagen, usuario):
        """Valida: nombre único, precio>0, costo>0, stock>=0"""
    
    def actualizar_producto(id_producto, ...):
        """Actualiza y registra historial con acción EDITADO"""
    
    def eliminar_producto(id_producto, usuario):
        """DELETE y registra historial con acción ELIMINADO"""
    
    def obtener_rentabilidad():
        """Calcula ganancia total (precio - costo) * stock para cada producto"""
    
    def contar_productos(filtro):
        """COUNT para paginación"""
    
    def obtener_productos_paginado(offset, limit, filtro):
        """Página de productos"""
    
    def obtener_nombres_productos_para_busqueda(filtro):
        """Autocompletado"""
```

**Validaciones**:
- Nombre de producto único
- Precio y costo deben ser > 0
- Stock debe ser >= 0

### 6.6 Re-exports de Sesión

Los archivos en `retail/nucleo/servicios/sesion/` son puentes de 5 líneas:

```python
# servicio_acceso.py
from retail.sesion.core.servicio_acceso import ServicioAcceso as ServicioAcceso
```

Esto permite importar desde `retail.nucleo.servicios.sesion` manteniendo consistencia.

---

## 7. Sesión y Autenticación — `retail/sesion/`

### 7.1 `core/servicio_acceso.py` (111 líneas)

**Clase**: `ServicioAcceso`

| Método | Descripción |
|--------|-------------|
| `verificar_credenciales(usuario, contrasena)` | Busca en desarrollador y usuarios con SHA-256 |
| `verificar_desarrollador(usuario, contrasena)` | Login como admin (backdoor) |
| `verificar_licencia(usuario)` | Verifica fecha_fin vs hoy |
| `guardar_sesion(usuario, contrasena, recordar)` | Persiste preferencias |
| `cargar_sesion()` | Carga preferencias guardadas |

**Flujo de autenticación**:
1. Busca primero en `desarrollador` (admin backdoor)
2. Si no, busca en `usuarios`
3. Verifica licencia (fecha_fin >= hoy)
4. Si expirado, muestra días restantes negativos

### 7.2 `core/servicio_licencias.py` (167 líneas)

**Clase**: `ServicioLicencias`

| Método | Descripción |
|--------|-------------|
| `generar_serial()` | UUID4 aleatorio |
| `crear_base_datos_licencia()` | Crea tabla desarrollador en DB aparte |
| `guardar_licencia(usuario, serial, inicio, fin)` | Inserta o actualiza |
| `obtener_licencia(usuario)` | Datos de licencia |
| `validar_licencia(usuario)` | ¿Está vigente? |
| `calcular_dias_restantes(usuario)` | Días hasta expiración |
| `renovar_licencia(usuario, dias)` | Extiende fecha_fin |
| `obtener_fecha_expiracion_mas_proxima()` | Para alertas en UI |

### 7.3 `core/servicio_registro.py` (119 líneas)

**Clase**: `ServicioRegistro`

| Método | Descripción |
|--------|-------------|
| `registrar_usuario(usuario, contrasena)` | Valida campos, hash SHA-256, INSERT |
| `listar_usuarios()` | Todos los usuarios |
| `actualizar_usuario(usuario_id, usuario, contrasena)` | UPDATE con hash |
| `eliminar_usuario(usuario_id)` | DELETE |
| `renovar_suscripcion(usuario_id, dias)` | Extiende licencia via ServicioLicencias |

### 7.4 `acceso.py` — Pantalla de Login (293 líneas)

**Clase**: `Acceso(tk.Frame)`

Componentes:
- Frame izquierdo: formulario (usuario, contraseña, recordar, botones)
- Frame derecho: imagen decorativa (`img/login.png`)
- Footer: contacto (WhatsApp, Instagram, Gmail, sitio web)

Flujo:
1. Usuario ingresa credenciales
2. `ServicioAcceso.verificar_credenciales()`
3. Si OK: `ServicioAcceso.verificar_licencia()`
4. Si licencia válida: `controlador.show_frame("Contenedor")`
5. Si falla: messagebox con error

### 7.5 `registro.py` — Gestión de Usuarios (413 líneas)

**Clase**: `VentanaRegistro(tk.Toplevel)`

Ventana modal para CRUD de usuarios:
- Formulario con usuario, contraseña, confirmar
- Tabla de usuarios existentes
- Botones: Registrar, Actualizar, Eliminar
- Muestra información de licencia (serial, fechas, días restantes)

---

## 8. Vistas Principales — `retail/vistas/`

### 8.1 `contenedor.py` — Contenedor Principal (273 líneas)

**Clase**: `Contenedor(tk.Frame)`

Es el marco principal de la aplicación después del login.

**Menú de navegación** — 4 secciones con colores distintivos:
| Sección | Clase | Color |
|---------|-------|-------|
| Ventas | `Ventas` | `#4CAF50` (verde) |
| Deudas | `Deudas` | `#F44336` (rojo) |
| Inventario | `Inventario` | `#2196F3` (azul) |
| Clientes | `Clientes` | `#FF9800` (naranja) |

**Efecto visual**: la sección activa tiene fondo oscuro (`#212121`) con texto amarillo (`#FFD600`) y subrayado.

**Registro de métodos de navegación**: El contenedor expone métodos en el controlador para que las sub-vistas puedan navegar sin acoplamiento directo:
```python
self.controlador.abrir_edicion_deuda = self.abrir_edicion_deuda
self.controlador.abrir_historial_venta = self.abrir_historial_venta
self.controlador.abrir_ganancias = self.abrir_ganancias
# ... etc
```

Cada método de navegación importa dinámicamente la vista correspondiente y la abre.

### 8.2 `ventas.py` (883 líneas)

**Clase**: `Ventas(tk.Frame)`

Vista principal del módulo de ventas. Componentes:

- **Panel izquierdo** (70%): Grid de productos con paginación (4x3 = 12 productos/página)
  - Canvas con scroll vertical
  - Botones de paginación (anterior/siguiente + números de página)
  - Cada producto se muestra con: imagen, nombre, precio, stock, botón "Agregar"

- **Panel derecho** (30%): Detalles de venta
  - Combobox de producto (búsqueda/autocompletado)
  - Combobox de cliente (opcional, para ventas por mayor)
  - Cantidad (spinbox)
  - Selector de tipo de venta: Rápida / Por Mayor
  - Botones: Carrito, Confirmar, Facturas, Ganancias

**Flujo de venta**:
1. Usuario selecciona producto (click en grid o combobox)
2. Selecciona cliente (opcional para rápida)
3. Define cantidad
4. Agrega al carrito (productos se acumulan en `self.carrito`)
5. Abre carrito (`ver_carrito()`) para revisar/resumir
6. Confirma venta → `VentasServicio.confirmar_venta()` → `crear_venta()`

### 8.3 `deudas.py` (931 líneas)

**Clase**: `Deudas(tk.Frame)`

Estructura casi idéntica a `Ventas` pero para gestión de deudas:
- Grid de productos similar
- Carrito de deudas (el cliente es obligatorio)
- Botones: Carrito Deuda, Confirmar Deuda, Facturas Deudas, Pagadas

**Flujo de deuda**:
1. Seleccionar cliente (obligatorio)
2. Seleccionar productos
3. Agregar al carrito de deuda
4. Confirmar → `DeudasServicio.confirmar_deuda()` → `crear_deuda()`

### 8.4 `clientes.py` (554 líneas)

**Clase**: `Clientes(tk.Frame)`

- **Panel izquierdo** (30%): formulario CRUD
  - Combobox de búsqueda
  - Campos: Nombres, Apellidos, Cédula, Celular, Zona
  - Botones: Agregar, Eliminar, Limpiar

- **Panel derecho** (70%): tabla paginada con Treeview
  - Columnas: ID, Nombres, Apellidos, Cédula, Celular, Zona
  - Edición inline: doble click en celda → entrada editable

**Características**:
- Búsqueda en tiempo real mientras escribe
- Edición directa en la tabla
- Paginación (20 clientes/página)

### 8.5 `inventario.py` (952 líneas)

**Clase**: `Inventario(tk.Frame)`

- **Panel izquierdo**: búsqueda, selección (muestra datos del producto seleccionado), opciones
- **Panel derecho**: grid de productos con imágenes

**Funcionalidades**:
- CRUD completo de productos
- Selección de imagen (file dialog)
- Paginación con imágenes cargadas dinámicamente
- Historial de inventario por producto
- Totales generales (valor inventario, costo total, ganancia potencial)
- Botones: Agregar, Eliminar, Historial, Totales

### 8.6 `ganancias.py` (141 líneas)

**Clase**: `GananciasContenedor(tk.Frame)`

Contenedor con sub-menú para 4 vistas de ganancias:

| Vista | Clase | Archivo | Color |
|-------|-------|---------|-------|
| Día | `Dia` | `retail/ganancias/diario.py` | `#00B8D4` |
| Semana | `Semana` | `retail/ganancias/semanal.py` | `#8E24AA` |
| Mes | `Mes` | `retail/ganancias/mensual.py` | `#FFB300` |
| Año | `Year` | `retail/ganancias/anual.py` | `#43A047` |

---

## 9. Sub-Vistas de Ventas — `retail/ventas/`

### 9.1 `carrito_ventas.py` (516 líneas)

**Función**: `ver_carrito(ventas_view)`

Ventana modal (`tk.Toplevel`) que muestra el carrito actual:
- Tabla de productos agregados
- Cantidad editable (con validación de stock en tiempo real)
- Eliminación de productos
- Total general
- Campo de monto recibido + cálculo automático de vuelto
- Botón Confirmar → `VentasServicio.confirmar_venta()`

**Agrupación por cliente**: Si hay venta por mayor, los productos se agrupan por cliente.

### 9.2 `edicion_ventas.py` (1,229 líneas)

**Función**: `abrir_ventana_edicion_factura(parent, id_ventas, cliente, usuario, callbacks)`

Ventana modal compleja para editar facturas existentes:
- Tabla de productos actuales (con edición inline)
- Grid paginado para agregar productos nuevos
- Muestra datos: total, monto recibido, vuelto
- Permite: editar cantidad, eliminar productos, agregar productos
- Valida que el nuevo total no supere el monto recibido

**Incluye generación de PDF**: Botón "Imprimir" que genera PDF con logo, datos de la empresa, productos y totales.

### 9.3 `facturas_ventas.py` (753 líneas)

**Función**: `ver_facturas(parent)`

Ventana de listado de facturas de venta:
- Tabla paginada con: factura #, cliente, productos, total, hora, fecha, zona
- Filtro por número de factura
- Botones: Ver detalle, Editar, Historial, Eliminar, Imprimir
- Generación de PDF con ReportLab
- Barra de estado con total de ventas

**Generación de PDF**: Usa `reportlab.lib.pagesizes.letter`, canvas.drawString, incluye logo (convertido a bytes PNG), productos en tabla, totales y pie de factura.

### 9.4 `historial_ventas.py` (290 líneas)

**Función**: `abrir_historial_ventas(parent, id_ventas, nombre_cliente, facturas_window)`

Ventana con historial de cambios de una venta:
- Tabla con: fecha, hora, producto, cantidad, subtotal, acción, monto recibido, vuelto
- Tooltips para texto largo
- Soporta tooltips multilínea con Tkinter

### 9.5 `papelera_ventas.py` (241 líneas)

**Función**: `ver_papelera_ventas(parent)`

Ventana de papelera (ventas eliminadas):
- Tabla paginada con filtro por número de factura
- Muestra: factura #, cliente, fecha venta, total, usuario que eliminó, fecha eliminación
- Botón "Limpiar" para eliminar registros antiguos (> 30 días)

### 9.6 `visualizar_ventas.py` (269 líneas)

**Función**: `ver_factura_detalle(parent, id_ventas)`

Ventana modal de solo lectura con detalle completo de una factura.

---

## 10. Sub-Vistas de Deudas — `retail/deudas/`

### 10.1 `carrito_deudas.py` (369 líneas)

Análogo a `carrito_ventas.py` pero para deudas. No tiene monto recibido/vuelto (las deudas son crédito).

### 10.2 `edicion_deudas.py` (776 líneas)

Análogo a `edicion_ventas.py` para deudas. Maneja saldos y estados `ABIERTA`/`PAGADA`.

### 10.3 `facturas_deudas.py` (864 líneas)

Listado de deudas abiertas con:
- Filtro por cliente
- Registro de pagos/abonos (con cálculo de vuelto si paga de más)
- Generación de PDF
- Acceso a: historial, edición, visualización, papelera

### 10.4 `historial_deudas.py` (197 líneas)

Historial de una deuda específica o de un cliente.

### 10.5 `pagadas.py` (519 líneas)

Listado de deudas pagadas con PDF.

### 10.6 `papelera_deudas.py` (240 líneas)

Papelera de deudas eliminadas.

### 10.7 `visualizar_deudas.py` (236 líneas)

Detalle de deuda en solo lectura.

---

## 11. Sub-Vistas de Ganancias — `retail/ganancias/`

### 11.1 `diario.py` (461 líneas)

**Clase**: `Dia(tk.Frame)`

- Selector de fecha (DateEntry)
- Tabla paginada con: fecha, ventas, deudas, total, ganancia
- Totales generales
- Botón PDF: genera reporte diario

### 11.2 `semanal.py` (392 líneas)

**Clase**: `Semana(tk.Frame)`

- Tabla paginada agrupada por semana
- Muestra: semana inicio-fin, total, ganancia
- PDF exportable

### 11.3 `mensual.py` (390 líneas)

**Clase**: `Mes(tk.Frame)`

- Tabla paginada en periodos de 30 días

### 11.4 `anual.py` (385 líneas)

**Clase**: `Year(tk.Frame)`

- Tabla paginada en periodos de 365 días
- Resumen anual

Todas las vistas de ganancias usan `threading.Thread(target=..., daemon=True)` para carga inicial de datos sin congelar la UI.

---

## 12. Sub-Vistas de Inventario — `retail/inventario/`

### 12.1 `historial_inventario.py` (203 líneas)

**Función**: `abrir_historial_inventario(parent, id_producto, nombre_producto)`

Ventana modal con historial de cambios de un producto específico:
- Tabla con: fecha, hora, acción (EDITADO/ELIMINADO), pedido, stock, precio, costo, ganancia, total

### 12.2 `totales.py` (101 líneas)

**Función**: `ver_totales(parent)`

Ventana con resumen de inventario:
- Total unidades
- Valor total (precio * stock)
- Costo total (costo * stock)
- Ganancia potencial (total - costo)

---

## 13. Utilidades — `retail/utilidades/`

### `logo.py` (112 líneas)

**Función**: `cambiar_logo(parent, callback)`

Ventana para cambiar el logo de la empresa que aparece en los PDFs:
- Muestra logo actual (o placeholder)
- Botón "Cambiar Logo" → file dialog para seleccionar imagen PNG/JPG
- Botón "Eliminar Logo" → vuelve al logo por defecto
- El logo se guarda en `{APPDATA}/Logo/logo.png`

---

## 14. Pruebas — `tests/`

### Configuración (`conftest.py`)

```python
@pytest.fixture
def tmp_appdata(tmp_path):
    """Crea un directorio temporal y parchea APPDATA_PATH."""
    with monkeypatch.context() as m:
        m.setattr(configuraciones, "APPDATA_PATH", str(tmp_path))
        yield tmp_path

@pytest.fixture
def db(tmp_appdata):
    """Base de datos en memoria fresca para cada test."""
    with monkeypatch.context() as m:
        m.setattr(base_datos, "DB_NAME", ":memory:")
        base_datos.crear_tablas()
        yield
```

### Resumen de Pruebas

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `test_base_datos.py` | ~45 | CRUD productos, clientes, ventas, deudas, papelera, historial, paginación, edge cases |
| `test_configuraciones.py` | ~25 | Paths, config save/load, PDF folders |
| `test_servicio_acceso.py` | ~18 | Auth (empty/reserved/wrong/valid/expired) |
| `test_servicio_clientes.py` | ~30 | CRUD, validaciones, paginación, búsqueda |
| `test_servicio_deudas.py` | ~35 | Stock, carrito, paginación, confirmación |
| `test_servicio_ventas.py` | ~30 | Stock, carrito, wholesale, confirmación |
| `test_servicio_inventario.py` | ~22 | CRUD, rentabilidad, paginación |
| `test_servicio_licencias.py` | ~18 | Generación, validación, renovación |
| `test_servicio_registro.py` | ~17 | CRUD usuarios, suscripción |
| `test_servicio_ganancias_diario.py` | ~10 | Reporte diario, totales, formato |
| `test_instancia_unica.py` | 1 | Socket binding único |

**Total**: ~250 tests, ~2,600 líneas de código de prueba.

---

## 15. Esquema de Base de Datos

### Tablas

```
desarrollador (id, usuario UNIQUE, contrasena)
usuarios (id, usuario UNIQUE, contrasena, fecha_inicio, fecha_fin, serial)

clientes (id_cliente PK, nombres, apellidos, cedula UNIQUE, celular UNIQUE, zona)
inventario (id_producto PK, producto UNIQUE, precio, costo, stock, estado CHECK(0,1), imagen)

ventas (id_ventas PK, numero_factura UNIQUE, cliente_id FK, cliente_rapido,
        fecha, hora, total, ganancia, monto_recibido, vuelto)
detalle_venta (id_detalle PK, id_ventas FK, id_producto FK, cantidad, precio_unitario, subtotal)

deudas (id_deuda PK, numero_factura UNIQUE, cliente_id FK, fecha, total, saldo,
        estado CHECK('ABIERTA','PAGADA'), usuario_creacion)
detalle_deuda (id_detalle PK, id_deuda FK, id_producto FK, cantidad, precio_unitario, subtotal)
pagos_deuda (id_pago PK, id_deuda FK, monto, fecha, hora, usuario)

ganancias (id_ganancia PK, fecha UNIQUE, total_dia, total_semana, total_mes, total_anio)

historial_ventas (id_historial PK, id_ventas, id_producto, cantidad, subtotal,
                  accion, usuario, fecha, hora, detalle, monto_recibido, vuelto)
historial_deudas (id_historial PK, id_deuda, id_producto, cantidad, subtotal,
                  accion, usuario, fecha, hora, detalle, abono, recibido, vuelto)

papelera_ventas (id_papelera PK, id_ventas, numero_factura, cliente_id, cliente_rapido,
                 fecha, hora, total, ganancia, monto_recibido, vuelto,
                 usuario_elimino, fecha_eliminacion, detalle)
papelera_deudas (id_papelera PK, id_deuda, numero_factura, cliente_id, fecha, total, saldo,
                 estado, usuario_elimino, fecha_eliminacion, detalle)

historial_inventario (id_historial PK, id_producto, dia, fecha, hora, accion,
                      pedido, stock, precio, costo, ganancia, total)
```

### Relaciones Clave

```
ventas → clientes (cliente_id FK nullable)
detalle_venta → ventas (id_ventas FK) + inventario (id_producto FK)
deudas → clientes (cliente_id FK required)
detalle_deuda → deudas (id_deuda FK) + inventario (id_producto FK)
pagos_deuda → deudas (id_deuda FK)
```

---

## 16. Flujo de Datos

### Flujo de Venta Completo

```
Usuario en UI (ventas.py)
    → click en producto del grid
    → selecciona cliente (opcional)
    → define cantidad
    → click "Agregar al Carrito"
        └→ VentasServicio.agregar_al_carrito()
            → valida stock (vs carrito actual)
            → previene duplicados
            → agrega item a self.carrito[]
    → abre Carrito (carrito_ventas.py)
        → revisa/modifica cantidades
        → confirma venta
            └→ VentasServicio.confirmar_venta()
                → transforma carrito a items[]
                → llama a crear_venta() en base_datos
                    → genera número factura único
                    → valida stock en DB
                    → INSERT ventas
                    → INSERT detalle_venta (cada producto)
                    → UPDATE stock (restar)
                    → INSERT historial_ventas
                → actualizar_cuentas() (ganancias)
```

### Flujo de Pago de Deuda

```
Usuario en facturas_deudas.py
    → selecciona deuda abierta
    → click "Pagar"
    → ingresa monto
        └→ ServicioFacturasDeudas.registrar_pago()
            → determina si es abono o pago total
            → si monto > saldo: calcula vuelto
            → INSERT pagos_deuda
            → UPDATE deudas (saldo, estado)
            → INSERT historial_deudas (acción "ABONO")
```

### Flujo de Edición de Venta

```
Usuario en facturas_ventas.py
    → selecciona factura
    → click "Editar"
        └→ edicion_ventas.py
            → ServicioEdicionVentas.obtener_detalles_factura()
            → ServicioEdicionVentas.obtener_info_factura()
    → edita cantidad
        └→ ServicioEdicionVentas.editar_cantidad_detalle()
            → valida stock
            → valida total ≤ monto_recibido
            → UPDATE stock (delta)
            → UPDATE detalle_venta
            → recalcula total/vuelto
            → INSERT historial
    → elimina producto
        └→ ServicioEdicionVentas.eliminar_detalle_venta()
            → restaura stock
            → DELETE detalle
            → recalcula
            → si queda vacío → _mover_a_papelera_si_vacia()
                → INSERT papelera_ventas
                → DELETE ventas
                → raise VentaVaciaError
```

---

## 17. Patrones y Decisiones de Diseño

### 17.1 Service Layer como Namespaces Estáticos

Todos los servicios usan `@staticmethod` y no mantienen estado de instancia. Las clases actúan como namespaces organizativos.

**Ventaja**: Simplicidad, no hay estado compartido.
**Desventaja**: No hay inyección de dependencias, difícil de testear con mocks.

### 17.2 God Module en base_datos.py

Todo el acceso a datos está centralizado en un solo archivo de 1,335 líneas.

**Decisión consciente**: Para un proyecto de este tamaño, mantener todo en un archivo evita la complejidad de múltiples DAOs/repositorios. Sin embargo, es un punto de atención para crecimiento futuro.

### 17.3 Transacciones Compartidas en Edición

Los servicios de edición (`ServicioEdicionVentas`, `ServicioEdicionDeudas`) aceptan parámetros opcionales `conn` y `cursor` para operar dentro de una transacción compartida, permitiendo que múltiples operaciones (eliminar + recalcular + historial) ocurran atómicamente.

```python
ctx = conexion() if conn is None and cursor is None else nullcontext(conn)
```

### 17.4 Paralelismo Ventas/Deudas

Los módulos de ventas y deudas son casi espejos. Esto es intencional: representan dos flujos de negocio diferentes (contado vs crédito) que comparten la misma estructura de datos base (productos, clientes) pero tienen reglas de negocio distintas.

### 17.5 Soft Delete con Papelera

Las ventas y deudas eliminadas no se borran directamente: se mueven a tablas `papelera_*` que preservan toda la información original. Un cleanup automático elimina registros > 30 días.

### 17.6 Licencias con SHA-256

El sistema de licencias usa:
- Hash SHA-256 para contraseñas
- UUID4 para seriales
- Fechas de inicio/fin para control de suscripción
- Backdoor de desarrollador con credenciales fijas

### 17.7 Carga Asíncrona en Ganancias

Las vistas de ganancias usan `threading.Thread(daemon=True)` para cargar datos iniciales sin bloquear la UI de Tkinter.

### 17.8 Autocomplete en Tiempo Real

Los combobox de búsqueda de productos y clientes actualizan su lista de valores en cada `KeyRelease`, consultando la DB con LIKE.

### 17.9 Formato de Moneda Personalizado

`peso_colombiano()` formatea números al estándar colombiano: `$1.500.000` (punto como separador de miles, sin decimales).

---

*Documento generado el Julio 2026 — Innobert Retail v1.0*
