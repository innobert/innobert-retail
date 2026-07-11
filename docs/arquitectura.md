# Arquitectura de Innobert Retail

## Índice
1. [Visión general](#1-visión-general)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Arquitectura en capas](#3-arquitectura-en-capas)
4. [Flujo de la aplicación](#4-flujo-de-la-aplicación)
5. [Base de datos](#5-base-de-datos)
6. [Módulos y sus ciclos de vida](#6-módulos-y-sus-ciclos-de-vida)
7. [Diagramas de flujo por acción](#7-diagramas-de-flujo-por-acción)
8. [Patrones de diseño](#8-patrones-de-diseño)
9. [Seguridad](#9-seguridad)
10. [Glosario de términos](#10-glosario-de-términos)

---

## 1. Visión general

Innobert Retail es un sistema de punto de venta (POS) de escritorio para pequeños comercios colombianos. Está construido con **Python 3.11+**, **Tkinter** para la interfaz gráfica, **SQLite3** como base de datos embebida, **Pillow** para procesamiento de imágenes y **ReportLab** para generación de PDFs.

### Principios arquitectónicos

- **Separación de responsabilidades**: UI, lógica de negocio y acceso a datos están en capas distintas.
- **Sin dependencia de internet**: 100% offline, base de datos local.
- **Auditoría completa**: Cada acción queda registrada en tablas de historial.
- **Recuperación de datos**: Sistema de papelera con eliminación suave (soft delete).

---

## 2. Estructura del proyecto

```
innobert-retail/
├── inicio.py                     # Punto de entrada
├── requirements.txt              # Dependencias
├── icono.ico                     # Ícono de la aplicación
├── img/                          # Recursos gráficos
├── fotos/                        # Imágenes de productos
│   └── default.png               # Imagen por defecto
├── docs/                         # Documentación
│   ├── gifs/                     # GIFs demostrativos
│   └── arquitectura.md           # Este archivo
└── retail/                       # Código fuente
    ├── inicio.py                 # Inicialización de la app
    ├── vistas/                   # Capa de presentación (UI)
    │   ├── acceso.py             # Login y registro
    │   ├── contenedor.py         # Navegación principal
    │   ├── ventas.py             # Módulo de ventas
    │   ├── deudas.py             # Módulo de deudas
    │   ├── inventario.py         # Módulo de inventario
    │   └── clientes.py           # Módulo de clientes
    ├── nucleo/                   # Capa de lógica de negocio
    │   ├── base_datos.py         # Acceso a datos (SQLite)
    │   ├── configuraciones.py    # Configuración y rutas
    │   ├── principal.py         # Ventana principal (controlador)
    │   └── servicios/            # Servicios por módulo
    │       ├── ventas/
    │       ├── deudas/
    │       ├── clientes/
    │       ├── inventario/
    │       ├── ganancias/
    │       └── sesion/
    ├── utilidades/               # Funciones auxiliares
    │   └── logo.py
    ├── sesion/                   # Autenticación
    │   ├── login.py
    │   └── usuarios.py
    ├── ganancias/                # Reportes
    │   ├── diario.py
    │   ├── semanal.py
    │   ├── mensual.py
    │   └── anual.py
    └── inventario/
        └── historial_inventario.py
```

---

## 2. Arquitectura en capas

```
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN (UI)                  │
│  retail/vistas/     retail/ventas/     retail/deudas/       │
│  retail/ganancias/  retail/inventario/ retail/sesion/       │
│  Tkinter Frames, Toplevels, Canvas, Treeview                │
├─────────────────────────────────────────────────────────────┤
│                   CAPA DE SERVICIOS (Lógica)                │
│  retail/nucleo/servicios/{ventas,deudas,clientes,...}/      │
│  Validación, cálculos, reglas de negocio                     │
├─────────────────────────────────────────────────────────────┤
│                   CAPA DE ACCESO A DATOS                     │
│  retail/nucleo/base_datos.py                                 │
│  Conexión SQLite, consultas CRUD, transacciones              │
├─────────────────────────────────────────────────────────────┤
│                   ALMACENAMIENTO                              │
│  SQLite (pos.db) + Sistema de archivos (imágenes, PDFs)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Flujo de la aplicación

### 3.1 Inicio de sesión

```
inicio.py
  │
  ├── retail/inicio.py
  │     └── importa retail.nucleo.principal.Principal
  │
  └── Principal (tk.Tk)
        ├── Crea Acceso (login frame)
        │     ├── Usuario ingresa credenciales
        │     ├── ServicioAcceso.verificar_acceso(usuario, contrasena)
        │     │     ├── Busca en tabla `desarrollador` (admin)
        │     │     └── Busca en tabla `usuarios` (usuarios registrados)
        │     └── Si éxito → self.mostrar_contenedor()
        │
        └── Crea Contenedor (navegación principal)
              ├── Ventas (tab)
              ├── Deudas (tab)
              ├── Inventario (tab)
              └── Clientes (tab)
```

### 3.1 Flujo detallado: Inicio de sesión

```
Usuario ingresa credenciales
  → Acceso._iniciar_sesion()
    → ServicioAcceso.verificar_acceso(usuario, contrasena)
      → base_datos.verificar_acceso(usuario, hash(contrasena))
        → Busca en tabla `desarrollador` (admin fijo)
        → Busca en tabla `usuarios` (usuarios registrados)
        → Retorna (True, tipo_usuario) o (False, mensaje_error)
    → Si éxito:
      → Principal.usuario_actual = datos_usuario
      → Principal.mostrar_contenedor()
      → Contenedor carga los 4 tabs (Ventas, Deudas, Inventario, Clientes)
    → Si fallo:
      → messagebox.showerror("Error", mensaje)
```

### 3.2 Flujo detallado: Registro de usuario

```
Usuario completa formulario de registro
  → Acceso._registrar_usuario()
    → ServicioRegistro.registrar_usuario(nombre, usuario, contrasena, serial)
      → Valida que usuario no exista
      → Valida formato del serial (UUID4)
      → Valida que el serial no esté ya registrado
      → Valida fecha de expiración de la licencia
      → Hash de contraseña (SHA-256)
      → base_datos.registrar_usuario(...)
        → INSERT INTO usuarios
      → Retorna (True, mensaje) o (False, mensaje_error)
    → Si éxito: messagebox.showinfo("Éxito", mensaje)
    → Si fallo: messagebox.showerror("Error", mensaje)
```

### 3.2 Flujo detallado: Módulo Ventas

```
Usuario selecciona pestaña Ventas
  → Ventas.__init__()
    → Carga canvas de productos (paginado, 12 por página)
    → Carga combobox de clientes
    → Inicializa carrito vacío

Usuario selecciona cliente (opcional)
  → _on_cliente_seleccionado()
    → self.cliente_seleccionado_id = cliente.id

Usuario hace doble clic en producto
  → _on_producto_double_click(producto_id)
    → Solicita cantidad (Toplevel con Entry)
    → Valida cantidad > 0 y <= stock disponible
    → Agrega al carrito: self.carrito.append({...})
    → Actualiza badge de carrito

Usuario abre carrito
  → CarritoVentas(self, carrito, ...)
    → Muestra tabla con productos, cantidades, subtotales
    → Muestra total general
    → Campo "Monto Recibido" para calcular vuelto
    → Botón "Confirmar Venta"

Usuario confirma venta
  → CarritoVentas._confirmar_venta()
    → Valida que haya productos en carrito
    → Valida monto recibido >= total
    → ServicioVentas.crear_venta(carrito, cliente_id, monto_recibido, usuario)
      → base_datos.crear_venta(...)
        → Genera número de factura único
        → INSERT INTO ventas
        → INSERT INTO detalle_venta (por cada producto)
        → UPDATE inventario SET stock = stock - cantidad
        → INSERT INTO historial_ventas
        → actualizar_cuentas() (recalcula tabla ganancias)
        → Retorna numero_factura
    → Genera PDF de factura
    → messagebox.showinfo("Éxito", "Venta registrada")
```

### 3.3 Flujo detallado: Módulo Deudas

```
Usuario selecciona pestaña Deudas
  → Deudas.__init__()
    → Carga canvas de productos (paginado)
    → Carga combobox de clientes
    → Inicializa carrito de deuda vacío

Usuario selecciona cliente (OBLIGATORIO)
  → _on_cliente_seleccionado()
    → self.cliente_seleccionado_id = cliente.id

Usuario hace doble clic en producto
  → _on_producto_double_click(producto_id)
    → Solicita cantidad
    → Valida cantidad > 0 y <= stock
    → Agrega al carrito_deuda

Usuario abre carrito de deuda
  → CarritoDeudas(self, carrito_deuda, ...)
    → Muestra tabla con productos y montos
    → Muestra total de la deuda
    → Botón "Confirmar Deuda"

Usuario confirma deuda
  → CarritoDeudas._confirmar_deuda()
    → ServicioDeudas.crear_deuda(carrito, cliente_id, usuario)
      → base_datos.crear_deuda(...)
        → Genera número de factura único
        → INSERT INTO deudas
        → INSERT INTO detalle_deuda (por cada producto)
        → UPDATE inventario SET stock = stock - cantidad
        → INSERT INTO historial_deudas
        → Retorna numero_factura
    → messagebox.showinfo("Éxito", "Deuda registrada")

Usuario paga abono a deuda existente
  → Deudas._pagar_deuda(deuda_id)
    → Solicita monto del abono
    → ServicioDeudas.registrar_pago(deuda_id, monto, usuario)
      → base_datos.registrar_pago(deuda_id, monto, usuario)
        → INSERT INTO pagos_deuda
        → UPDATE deudas SET saldo = saldo - monto
        → Si saldo <= 0: UPDATE deudas SET estado = 'PAGADA'
        → INSERT INTO historial_deudas
    → Refresca vista de deudas
```

### 3.4 Flujo detallado: Módulo Inventario

```
Usuario selecciona pestaña Inventario
  → Inventario.__init__()
    → Carga canvas de productos (paginado, 12 por página)
    → Inicializa filtros de búsqueda

Usuario agrega producto
  → Inventario._agregar_producto()
    → Abre formulario (Toplevel) con campos:
      → Nombre, Precio, Costo, Stock, Imagen
    → Usuario completa y presiona Guardar
    → ServicioInventario.crear_producto(nombre, precio, costo, stock, imagen)
      → Valida que nombre no exista
      → Valida precio > 0, costo > 0, stock >= 0
      → base_datos.crear_producto(...)
        → INSERT INTO inventario
        → INSERT INTO historial_inventario
      → Retorna (True, mensaje) o (False, mensaje_error)
    → Si éxito: Refresca canvas y notifica a otras vistas

Usuario edita producto
  → Inventario._editar_producto(producto_id)
    → Abre formulario con datos actuales
    → Usuario modifica campos
    → ServicioInventario.actualizar_producto(id, datos)
      → base_datos.actualizar_producto(id, datos)
        → UPDATE inventario SET ... WHERE id_producto = ?
        → INSERT INTO historial_inventario
    → Refresca canvas

Usuario elimina producto
  → Inventario._eliminar_producto(producto_id)
    → Confirma eliminación
    → ServicioInventario.eliminar_producto(id)
      → base_datos.eliminar_producto(id)
        → UPDATE inventario SET estado = 0 WHERE id_producto = ?
        → INSERT INTO historial_inventario
    → Refresca canvas
```

### 3.5 Flujo detallado: Módulo Clientes

```
Usuario selecciona pestaña Clientes
  → Clientes.__init__()
    → Carga tabla (Treeview) con todos los clientes
    → Inicializa campo de búsqueda

Usuario agrega cliente
  → Clientes._agregar_cliente()
    → Abre formulario (Toplevel) con campos:
      → Nombres, Apellidos, Cédula, Celular, Zona
    → ServicioClientes.crear_cliente(nombres, apellidos, cedula, celular, zona)
      → Valida que cédula no exista
      → Valida que celular no exista
      → base_datos.crear_cliente(...)
        → INSERT INTO clientes
      → Retorna (True, mensaje) o (False, mensaje_error)
    → Refresca tabla

Usuario edita cliente (doble clic en celda)
  → Clientes._on_cell_double_click(event)
    → Convierte celda en Entry editable
    → Usuario modifica valor y presiona Enter
    → ServicioClientes.actualizar_cliente(id, columna, valor)
      → base_datos.actualizar_cliente(id, columna, valor)
        → UPDATE clientes SET columna = valor WHERE id_cliente = ?
    → Refresca tabla

Usuario elimina cliente
  → Clientes._eliminar_cliente()
    → Confirma eliminación
    → ServicioClientes.eliminar_cliente(id)
      → base_datos.eliminar_cliente(id)
        → DELETE FROM clientes WHERE id_cliente = ?
    → Refresca tabla
```

### 3.6 Flujo detallado: Módulo Ganancias

```
Usuario abre Ganancias (desde Ventas)
  → Ventas._abrir_ganancias()
    → Ganancias(ventana_padre)
      → Toplevel con 4 pestañas: Diario, Semanal, Mensual, Anual

--- Pestaña Diario ---
  → ServicioDiario.cargar_datos(fecha)
    → base_datos.obtener_ventas_por_dia(fecha)
      → SELECT v.*, dv.* FROM ventas v
        JOIN detalle_venta dv ON v.numero_factura = dv.numero_factura
        WHERE v.fecha = ?
    → Calcula totales (ingresos, ganancias, cantidad productos, clientes)
    → Retorna datos para la tabla

--- Pestaña Semanal ---
  → ServicioSemanal.cargar_datos(semana, año)
    → base_datos.obtener_ventas_por_semana(semana, año)
    → Agrupa por día
    → Calcula totales semanales

--- Pestaña Mensual ---
  → ServicioMensual.cargar_datos(mes, año)
    → base_datos.obtener_ventas_por_mes(mes, año)
    → Agrupa por día
    → Calcula totales mensuales

--- Pestaña Anual ---
  → ServicioAnual.cargar_datos(año)
    → base_datos.obtener_ventas_por_año(año)
    → Agrupa por mes
    → Calcula totales anuales

--- Generación de PDF (cada pestaña) ---
  → ServicioX.generar_pdf(datos, ruta)
    → canvas.Canvas(archivo, pagesize=letter)
    → Dibuja logo, título, datos, marca de agua, pie de página
    → canvas.save()
    → abrir_archivo(ruta)  → os.startfile() en Windows
```

### 3.6 Flujo detallado: Carrito de Ventas

```
Usuario hace clic en ícono de carrito
  → Ventas._abrir_carrito()
    → CarritoVentas(self, self.carrito, self.cliente_seleccionado_id, self.usuario_actual)
      → Toplevel con:
        → Treeview: Producto | Cantidad | Precio | Subtotal
        → Label: Total
        → Entry: Monto Recibido
        → Label: Vuelto (se actualiza en tiempo real)
        → Botón: Confirmar Venta
        → Botón: Cancelar

  → _calcular_vuelto(event)
    → total = sum(item['subtotal'] for item in carrito)
    → monto_recibido = float(entry_monto.get())
    → vuelto = monto_recibido - total
    → Actualiza label de vuelto

  → _confirmar_venta()
    → Valida carrito no vacío
    → Valida monto_recibido >= total
    → ServicioVentas.crear_venta(carrito, cliente_id, monto_recibido, usuario)
      → base_datos.crear_venta(...)
        → Genera número de factura (6 dígitos aleatorios, único)
        → conn.execute("BEGIN TRANSACTION")
        → INSERT INTO ventas (numero_factura, cliente_id, ...)
        → Por cada producto en carrito:
          → INSERT INTO detalle_venta
          → UPDATE inventario SET stock = stock - cantidad
        → INSERT INTO historial_ventas
        → actualizar_cuentas()  → DELETE FROM ganancias + recálculo completo
        → conn.commit()
        → Retorna numero_factura
    → Genera PDF de factura
    → messagebox.showinfo("Éxito", f"Venta {factura} registrada")
    → Limpia carrito y refresca vista
```

### 3.4 Flujo detallado: Edición de factura de venta

```
Usuario abre Facturas → selecciona factura → Editar
  → EdicionVentas(factura_data)
    → Carga datos de la factura
    → Muestra tabla con productos editables
    → Usuario modifica cantidades o agrega productos
    → _guardar_cambios()
      → ServicioVentas.editar_factura(numero_factura, productos_nuevos)
        → base_datos.editar_factura(...)
          → conn.execute("BEGIN")
          → Por cada producto original:
            → Restaura stock original (UPDATE inventario SET stock + cantidad_original)
          → DELETE FROM detalle_venta WHERE numero_factura = ?
          → Por cada producto nuevo:
            → INSERT INTO detalle_venta
            → UPDATE inventario SET stock = stock - cantidad_nueva
          → Recalcula total y ganancia
          → UPDATE ventas SET total = ?, ganancia = ? WHERE numero_factura = ?
          → INSERT INTO historial_ventas (accion = 'EDICION')
          → conn.commit()
```

### 3.7 Flujo detallado: Papelera (recuperación de datos)

```
Usuario abre Papelera de Ventas
  → PapeleraVentas()
    → Carga lista de ventas eliminadas (con usuario y fecha de eliminación)
    → Muestra en Treeview

Usuario restaura venta
  → PapeleraVentas._restaurar()
    → ServicioVentas.restaurar_venta(numero_factura)
      → base_datos.restaurar_venta(numero_factura)
        → DELETE FROM papelera_ventas WHERE numero_factura = ?
        → Re-inserta en ventas y detalle_venta
        → Restaura stock: UPDATE inventario SET stock = stock - cantidad
    → Refresca lista

Usuario elimina permanentemente
  → PapeleraVentas._eliminar_permanentemente()
    → ServicioVentas.eliminar_venta_permanente(numero_factura)
      → base_datos.eliminar_venta_permanente(numero_factura)
        → DELETE FROM papelera_ventas WHERE numero_factura = ?
        → DELETE FROM detalle_venta WHERE numero_factura = ?
        → (NO restaura stock — es eliminación definitiva)
```

### 3.8 Flujo detallado: Papelera de Deudas

```
Usuario abre Papelera de Deudas
  → PapeleraDeudas()
    → Carga deudas eliminadas con usuario y fecha de eliminación
    → Muestra en Treeview

Usuario restaura deuda
  → PapeleraDeudas._restaurar()
    → ServicioDeudas.restaurar_deuda(numero_factura)
      → base_datos.restaurar_deuda(numero_factura)
        → DELETE FROM papelera_deudas WHERE numero_factura = ?
        → Re-inserta en deudas y detalle_deuda
        → Restaura stock: UPDATE inventario SET stock = stock - cantidad
    → Refresca lista

Usuario elimina permanentemente
  → PapeleraDeudas._eliminar_permanentemente()
    → ServicioDeudas.eliminar_deuda_permanente(numero_factura)
      → base_datos.eliminar_deuda_permanente(numero_factura)
        → DELETE FROM papelera_deudas
        → DELETE FROM detalle_deuda
        → (NO restaura stock)
```

---

## 4. Base de datos

### 4.1 Esquema completo

```sql
-- Tabla: desarrollador (admin fijo)
CREATE TABLE desarrollador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL
);

-- Tabla: usuarios (usuarios con licencia)
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    serial TEXT UNIQUE NOT NULL
);

-- Tabla: clientes
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres TEXT NOT NULL,
    apellidos TEXT,
    cedula TEXT UNIQUE NOT NULL,
    celular TEXT UNIQUE NOT NULL,
    zona TEXT
);

-- Tabla: inventario
CREATE TABLE inventario (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT UNIQUE NOT NULL,
    precio REAL NOT NULL,
    costo REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    estado INTEGER NOT NULL DEFAULT 1,
    imagen TEXT
);

-- Tabla: ventas
CREATE TABLE ventas (
    numero_factura TEXT PRIMARY KEY,
    cliente_id INTEGER,
    cliente_rapido TEXT,
    total REAL NOT NULL,
    ganancia REAL NOT NULL,
    monto_recibido REAL NOT NULL,
    vuelto REAL NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    usuario TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente)
);

-- Tabla: detalle_venta
CREATE TABLE detalle_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL,
    id_producto INTEGER NOT NULL,
    producto TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    FOREIGN KEY (numero_factura) REFERENCES ventas(numero_factura),
    FOREIGN KEY (id_producto) REFERENCES inventario(id_producto)
);

-- Tabla: deudas
CREATE TABLE deudas (
    numero_factura TEXT PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    total REAL NOT NULL,
    saldo REAL NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    usuario TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'ABIERTA',
    FOREIGN KEY (cliente_id) REFERENCES clientes(id_cliente)
);

-- Tabla: detalle_deuda
CREATE TABLE detalle_deuda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL,
    id_producto INTEGER NOT NULL,
    producto TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    FOREIGN KEY (numero_factura) REFERENCES deudas(numero_factura),
    FOREIGN KEY (id_producto) REFERENCES inventario(id_producto)
);

-- Tabla: pagos_deuda
CREATE TABLE pagos_deuda (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT NOT NULL,
    monto REAL NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    usuario TEXT NOT NULL,
    FOREIGN KEY (numero_factura) REFERENCES deudas(numero_factura)
);

-- Tabla: ganancias (precalculadas)
CREATE TABLE ganancias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT UNIQUE NOT NULL,
    total_dia REAL NOT NULL DEFAULT 0,
    total_semana REAL NOT NULL DEFAULT 0,
    total_mes REAL NOT NULL DEFAULT 0,
    total_anio REAL NOT NULL DEFAULT 0
);

-- Tablas de historial (auditoría)
CREATE TABLE historial_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT,
    accion TEXT NOT NULL,
    usuario TEXT NOT NULL,
    detalle TEXT,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL
);

CREATE TABLE historial_deudas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT,
    accion TEXT NOT NULL,
    usuario TEXT NOT NULL,
    detalle TEXT,
    abono REAL,
    recibido REAL,
    vuelto REAL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL
);

CREATE TABLE historial_inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    accion TEXT NOT NULL,
    pedido TEXT,
    stock INTEGER,
    precio REAL,
    costo REAL,
    ganancia REAL,
    total REAL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES inventario(id_producto)
);

-- Tablas de papelera (soft delete)
CREATE TABLE papelera_ventas (
    numero_factura TEXT PRIMARY KEY,
    cliente_id INTEGER,
    cliente_rapido TEXT,
    total REAL,
    ganancia REAL,
    monto_recibido REAL,
    vuelto REAL,
    fecha TEXT,
    hora TEXT,
    usuario TEXT,
    usuario_elimino TEXT,
    fecha_eliminacion TEXT
);

CREATE TABLE papelera_deudas (
    numero_factura TEXT PRIMARY KEY,
    cliente_id INTEGER,
    total REAL,
    saldo REAL,
    fecha TEXT,
    hora TEXT,
    usuario TEXT,
    estado TEXT,
    usuario_elimino TEXT,
    fecha_eliminacion TEXT
);
```

### 4.2 Relaciones entre tablas

```
clientes ──┬──< ventas (cliente_id)
           └──< deudas (cliente_id)

inventario ──┬──< detalle_venta (id_producto)
             └──< detalle_deuda (id_producto)

ventas ──< detalle_venta (numero_factura)
deudas ──< detalle_deuda (numero_factura)
deudas ──< pagos_deuda (numero_factura)
```

### 4.3 Patrón de acceso a datos

Cada operación CRUD sigue este patrón:

```python
def operacion_ejemplo(parametros):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        # ... operaciones SQL ...
        conn.commit()
        return (True, resultado)
    except Exception as e:
        conn.rollback()
        return (False, str(e))
    finally:
        conn.close()
```

---

## 5. Patrones de diseño utilizados

### 5.1 Service Layer (Capa de Servicios)

Cada módulo tiene una clase de servicio con métodos estáticos que encapsulan la lógica de negocio:

```python
class VentasServicio:
    @staticmethod
    def crear_venta(carrito, cliente_id, monto_recibido, usuario):
        # Validaciones
        # Cálculos
        # Llamada a base_datos
        return (True, numero_factura)
```

### 5.2 Frame Switching (Navegación por pestañas)

El `Contenedor` usa `tkraise()` para cambiar entre frames:

```python
class Contenedor(tk.Frame):
    def mostrar_frame(self, frame_class):
        frame = frame_class(self)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.tkraise()
```

### 5.3 Paginación

Carga diferida de productos/clientes en lotes de 12:

```python
class Paginacion:
    def __init__(self):
        self.pagina_actual = 1
        self.total_paginas = 1
        self.elementos_por_pagina = 12

    def cargar_pagina(self, offset):
        # SELECT ... LIMIT elementos_por_pagina OFFSET offset
        pass
```

### 5.4 Observer (Actualización entre vistas)

Cuando el inventario cambia, notifica a Ventas y Deudas:

```python
class Inventario(tk.Frame):
    def _actualizar_otras_vistas(self):
        if hasattr(self.master, 'ventas_frame'):
            self.master.ventas_frame._cargar_productos()
        if hasattr(self.master, 'deudas_frame'):
            self.master.deudas_frame._cargar_productos()
```

### 5.5 Toplevel para sub-módulos

Cada sub-funcionalidad (Carrito, Facturas, Historial, Edición, Papelera) abre una ventana `Toplevel` independiente con `grab_set()` para comportamiento modal.

---

## 6. Ciclo de vida de las entidades principales

### 6.1 Producto (Inventario)

```
CREACIÓN:
  Usuario completa formulario
    → ServicioInventario.crear_producto()
      → INSERT INTO inventario
      → INSERT INTO historial_inventario (accion='CREACION')
    → Refresca canvas

LECTURA:
  → SELECT * FROM inventario WHERE estado = 1
    → Paginado (12 por página)
    → Filtro por LIKE %nombre%

ACTUALIZACIÓN:
  → ServicioInventario.actualizar_producto(id, datos)
    → UPDATE inventario SET ... WHERE id_producto = ?
    → INSERT INTO historial_inventario (accion='ACTUALIZACION')

ELIMINACIÓN (lógica):
  → ServicioInventario.eliminar_producto(id)
    → UPDATE inventario SET estado = 0 WHERE id_producto = ?
    → INSERT INTO historial_inventario (accion='ELIMINACION')
```

### 6.2 Venta

```
CREACIÓN:
  Carrito → Confirmar Venta
    → ServicioVentas.crear_venta()
      → Genera número de factura
      → INSERT INTO ventas
      → INSERT INTO detalle_venta (por cada producto)
      → UPDATE inventario SET stock = stock - cantidad
      → INSERT INTO historial_ventas (accion='CREACION')
      → actualizar_cuentas() (recalcula ganancias)
    → Genera PDF

EDICIÓN:
  Facturas → Editar
    → ServicioVentas.editar_factura()
      → Restaura stock original
      → DELETE FROM detalle_venta
      → INSERT nuevos detalles
      → UPDATE stock con nuevas cantidades
      → Recalcula total y ganancia
      → INSERT INTO historial_ventas (accion='EDICION')

ELIMINACIÓN (suave):
  → ServicioVentas.eliminar_venta(numero_factura, usuario)
    → INSERT INTO papelera_ventas (copia de venta)
    → DELETE FROM ventas WHERE numero_factura = ?
    → Restaura stock: UPDATE inventario SET stock + cantidad
    → INSERT INTO historial_ventas (accion='ELIMINACION')

RECUPERACIÓN:
  → ServicioVentas.restaurar_venta(numero_factura)
    → DELETE FROM papelera_ventas
    → INSERT INTO ventas (datos originales)
    → INSERT INTO detalle_venta (datos originales)
    → UPDATE inventario SET stock - cantidad
```

### 6.3 Deuda

```
CREACIÓN:
  CarritoDeuda → Confirmar Deuda
    → ServicioDeudas.crear_deuda()
      → Genera número de factura
      → INSERT INTO deudas (saldo = total, estado = 'ABIERTA')
      → INSERT INTO detalle_deuda (por cada producto)
      → UPDATE inventario SET stock = stock - cantidad
      → INSERT INTO historial_deudas (accion='CREACION')

ABONO (pago parcial):
  → ServicioDeudas.registrar_pago(deuda_id, monto, usuario)
    → INSERT INTO pagos_deuda
    → UPDATE deudas SET saldo = saldo - monto
    → Si saldo <= 0: UPDATE deudas SET estado = 'PAGADA'
    → INSERT INTO historial_deudas (accion='ABONO')

EDICIÓN:
  → ServicioDeudas.editar_deuda(numero_factura, productos_nuevos)
    → Restaura stock original
    → DELETE FROM detalle_deuda
    → INSERT nuevos detalles
    → UPDATE stock con nuevas cantidades
    → Recalcula total y saldo
    → INSERT INTO historial_deudas (accion='EDICION')

ELIMINACIÓN (suave):
  → ServicioDeudas.eliminar_deuda(numero_factura, usuario)
    → INSERT INTO papelera_deudas
    → DELETE FROM deudas
    → Restaura stock
    → INSERT INTO historial_deudas (accion='ELIMINACION')
```

### 6.4 Cliente

```
CREACIÓN:
  Formulario → ServicioClientes.crear_cliente()
    → Valida cédula única
    → Valida celular único
    → INSERT INTO clientes

ACTUALIZACIÓN (edición directa en tabla):
  Doble clic en celda → Entry editable → Enter
    → ServicioClientes.actualizar_cliente(id, columna, valor)
      → Valida unicidad si es cédula o celular
      → UPDATE clientes SET columna = valor WHERE id_cliente = ?

ELIMINACIÓN:
  → ServicioClientes.eliminar_cliente(id)
    → DELETE FROM clientes WHERE id_cliente = ?
```

### 6.5 Ganancias (reportes)

```
CADA VENTA/DEUDA:
  → base_datos.actualizar_cuentas()
    → DELETE FROM ganancias
    → Recalcula todo desde cero:
      → Por cada fecha con ventas:
        → Calcula total_dia (ingresos)
        → Calcula total_semana (suma 7 días)
        → Calcula total_mes (suma del mes)
        → Calcula total_anio (suma del año)
        → INSERT INTO ganancias

CONSULTA (Diario):
  → ServicioDiario.cargar_datos(fecha)
    → SELECT v.*, dv.* FROM ventas v
      JOIN detalle_venta dv ON v.numero_factura = dv.numero_factura
      WHERE v.fecha = ?
    → Calcula:
      - Total ingresos
      - Total ganancia
      - Cantidad de productos vendidos
      - Cantidad de clientes atendidos
    → Retorna lista de ventas + resumen

CONSULTA (Semanal):
  → ServicioSemanal.cargar_datos(semana, año)
    → SELECT v.*, dv.* FROM ventas v
      JOIN detalle_venta dv ON v.numero_factura = dv.numero_factura
      WHERE v.fecha BETWEEN ? AND ?
    → Agrupa por día
    → Calcula totales por día y total semanal

CONSULTA (Mensual):
  → ServicioMensual.cargar_datos(mes, año)
    → SELECT v.*, dv.* FROM ventas v
      JOIN detalle_venta dv ON v.numero_factura = dv.numero_factura
      WHERE strftime('%m', v.fecha) = ? AND strftime('%Y', v.fecha) = ?
    → Agrupa por día
    → Calcula totales

CONSULTA (Anual):
  → ServicioAnual.cargar_datos(año)
    → SELECT v.*, dv.* FROM ventas v
      JOIN detalle_venta dv ON v.numero_factura = dv.numero_factura
      WHERE strftime('%Y', v.fecha) = ?
    → Agrupa por mes
    → Calcula totales
```

---

## 7. Diagramas de flujo por acción

### 7.1 Acción: Realizar una venta

```
[Usuario]                    [UI/Ventas]              [ServicioVentas]           [base_datos]
   │                            │                          │                        │
   ├── Doble clic producto ─────┤                          │                        │
   │                            ├── Solicita cantidad ─────┤                        │
   │                            │                          │                        │
   │                            │  Valida cantidad         │                        │
   │                            │  ( > 0 y <= stock )     │                        │
   │                            │                          │                        │
   │                            ├── Agrega al carrito ────┤                        │
   │                            │                          │                        │
   ├── Abre carrito ────────────┤                          │                        │
   │                            │                          │                        │
   ├── Ingresa monto recibido ──┤                          │                        │
   │                            ├── Calcula vuelto ────────┤                        │
   │                            │                          │                        │
   ├── Confirma venta ──────────┤                          │                        │
   │                            ├── crear_venta() ────────►│                        │
   │                            │                          ├── crear_venta() ───────►│
   │                            │                          │                        ├── BEGIN
   │                            │                          │                        ├── Genera factura
   │                            │                          │                        ├── INSERT ventas
   │                            │                          │                        ├── INSERT detalle_venta
   │                            │                          │                        ├── UPDATE stock
   │                            │                          │                        ├── INSERT historial
   │                            │                          │                        ├── actualizar_cuentas()
   │                            │                          │                        ├── COMMIT
   │                            │                          │                        └── Retorna factura
   │                            │                          │                        │
   │                            │◄─────────────────────────┤                        │
   │                            ├── Genera PDF ────────────┤                        │
   │                            │                          │                        │
   │◄── messagebox "Venta OK" ──┤                          │                        │
```

### 7.2 Acción: Registrar abono a deuda

```
[Usuario]                    [UI/Deudas]              [ServicioDeudas]           [base_datos]
   │                            │                          │                        │
   ├── Selecciona deuda ────────┤                          │                        │
   │                            │                          │                        │
   ├── Clic "Pagar" ────────────┤                          │                        │
   │                            ├── Solicita monto ────────┤                        │
   │                            │                          │                        │
   ├── Ingresa monto ───────────┤                          │                        │
   │                            ├── registrar_pago() ─────►│                        │
   │                            │                          ├── registrar_pago() ───►│
   │                            │                          │                        ├── INSERT pagos_deuda
   │                            │                          │                        ├── UPDATE saldo
   │                            │                          │                        ├── Si saldo <= 0:
   │                            │                          │                        │     UPDATE estado='PAGADA'
   │                            │                          │                        ├── INSERT historial
   │                            │                          │                        └── Retorna (True, ...)
   │                            │                          │                        │
   │◄── messagebox "Abono OK" ──┤                          │                        │
   │                            ├── Refresca vista ────────┤                        │
```

### 7.3 Acción: Generar reporte de ganancias (PDF)

```
[Usuario]                    [UI/Ganancias]            [ServicioGanancias]        [ReportLab]
   │                            │                          │                        │
   ├── Abre Ganancias ──────────┤                          │                        │
   │                            ├── Carga datos (thread) ──►│                        │
   │                            │                          ├── Consulta BD ─────────►│
   │                            │                          │◄── Datos ─────────────┤
   │                            │◄── Datos formateados ────┤                        │
   │                            │                          │                        │
   ├── Clic "Generar PDF" ─────┤                          │                        │
   │                            ├── Solicita ruta ─────────┤                        │
   │                            │  (filedialog)            │                        │
   │                            │                          │                        │
   │                            ├── generar_pdf() ────────►│                        │
   │                            │                          ├── generar_pdf() ───────►│
   │                            │                          │                        ├── Canvas(letter)
   │                            │                          │                        ├── drawImage(logo)
   │                            │                          │                        ├── drawString(título)
   │                            │                          │                        ├── drawString(datos)
   │                            │                          │                        ├── drawString(footer)
   │                            │                          │                        ├── save()
   │                            │                          │                        └── Retorna ruta
   │                            │                          │                        │
   │                            │◄── PDF generado ─────────┤                        │
   │                            ├── abrir_archivo(ruta) ───┤                        │
   │                            │  (os.startfile)           │                        │
```

---

## 8. Seguridad

### 8.1 Autenticación

- **Contraseñas**: Almacenadas como hash SHA-256 (sin sal).
- **Dos niveles de acceso**:
  - `desarrollador`: Admin fijo con credenciales hardcodeadas en base_datos.py
  - `usuarios`: Usuarios con licencia (30 días de prueba, renovable)
- **Licencias**: Serial UUID4, validado contra tabla `usuarios` con fecha de expiración.

### 8.2 Protección contra inyección SQL

Todas las consultas usan parámetros `?` (parameterized queries):

```python
# Bien (parameterized)
cursor.execute("SELECT * FROM inventario WHERE id_producto = ?", (id_producto,))

# Mal (concatenación - NO USADO EN EL PROYECTO)
cursor.execute(f"SELECT * FROM inventario WHERE id_producto = {id_producto}")
```

### 8.3 Almacenamiento de datos

- Base de datos: `%APPDATA%/InnobertRetail/pos.db`
- Imágenes de productos: `%APPDATA%/InnobertRetail/Fotos/`
- Logo personalizado: `%APPDATA%/InnobertRetail/Logo/logo.png`
- PDFs: Carpeta seleccionada por el usuario (recordada en config)

### 8.4 Limitaciones de seguridad actuales

- Contraseñas con SHA-256 sin sal (aceptable para app local)
- Credenciales de desarrollador hardcodeadas en el código fuente
- Sin límite de intentos de inicio de sesión
- Sin cifrado de base de datos

---

## 9. Glosario de términos

| Término | Significado |
|---------|-------------|
| **Carrito** | Lista temporal de productos seleccionados para una venta o deuda |
| **Vuelto** | Cambio a devolver al cliente (monto_recibido - total) |
| **Abono** | Pago parcial a una deuda |
| **Saldo** | Monto pendiente de una deuda |
| **Papelera** | Almacenamiento temporal de registros eliminados (soft delete) |
| **Factura** | Documento PDF generado al confirmar una venta o deuda |
| **Ganancia** | (precio_venta - costo) * cantidad |
| **Paginación** | Carga de datos en lotes de 12 elementos |
| **Toplevel** | Ventana secundaria en Tkinter (modal o no modal) |
| **Canvas** | Widget de Tkinter para dibujar y contener elementos gráficos |
| **Treeview** | Widget de ttk para mostrar datos tabulares |

---

## 10. Dependencias externas

| Librería | Versión | Propósito |
|----------|---------|-----------|
| **Pillow** | 12.2.0 | Carga, redimensionamiento y conversión de imágenes de productos |
| **ReportLab** | 4.5.1 | Generación de PDFs (facturas, reportes de ganancias) |
| **charset-normalizer** | 3.4.7 | Detección de codificación de caracteres (dependencia de requests) |

**Librerías del sistema (incluidas en Python):**
- `tkinter` / `ttk`: Interfaz gráfica
- `sqlite3`: Base de datos embebida
- `hashlib`: SHA-256 para contraseñas
- `threading`: Carga asíncrona de datos en Ganancias
- `filedialog`: Diálogos de guardar/abrir archivos
- `messagebox`: Diálogos de información/error/confirmación
- `os`, `shutil`, `sys`: Operaciones del sistema
- `uuid`: Generación de seriales de licencia
- `datetime`, `time`: Manejo de fechas y horas
- `re`: Expresiones regulares para validación
- `json`: Persistencia de configuración
- `configparser`: Archivos de configuración INI
- `webbrowser`: Abrir enlaces en el navegador
- `subprocess`: Abrir archivos con programa predeterminado
- `hashlib`: SHA-256 para contraseñas
- `random`: Generación de números de factura
- `threading`: Hilos para carga de datos en Ganancias
- `inspect`: Inspección de módulos (en configuraciones.py)

---

## 11. Convenciones del proyecto

### 11.1 Nombramiento

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Archivos | snake_case, español | `base_datos.py`, `servicio_ventas.py` |
| Clases | PascalCase | `VentasServicio`, `ServicioDiario` |
| Métodos | snake_case | `obtener_stock_actual()`, `_cargar_pagina()` |
| Métodos privados | Prefijo `_` | `_on_cliente_seleccionado()` |
| Variables | snake_case | `self.carrito`, `self.producto_seleccionado_id` |
| Constantes | UPPER_CASE | `VENTANA_ANCHO`, `DESARROLLADOR_HASH` |

### 10.2 Estructura de servicios

Cada servicio retorna `Tuple[bool, Any]`:
- `(True, resultado)` en éxito
- `(False, mensaje_error)` en fallo

### 10.3 Manejo de errores

```python
# Capa de datos: try/except/rollback/finally
try:
    cursor.execute("BEGIN")
    # ... operaciones ...
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()

# Capa de UI: try/except con messagebox
try:
    resultado = servicio.operacion(datos)
    if resultado[0]:
        messagebox.showinfo("Éxito", resultado[1])
    else:
        messagebox.showerror("Error", resultado[1])
except Exception as e:
    messagebox.showerror("Error inesperado", str(e))
```

---

## 11. Mejoras planificadas

### Fase 1: Bajo riesgo
1. Agregar índices a la base de datos
2. Reemplazar `print()` por `logging`
3. Extraer constantes de configuración

### Fase 2: Refactorización segura
4. Extraer tarjeta de producto a función compartida
5. Extraer paginación a widget reutilizable

### Fase 3: Calidad
6. Agregar pruebas unitarias (pytest)
7. Validación de entrada en formularios

### Fase 4: Arquitectura
8. Refactorizar base_datos.py a clase Database con context manager
9. Layout responsivo
10. Documentación para desarrolladores
